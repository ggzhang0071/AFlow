#!/usr/bin/env python3
"""
本地模型 API 服务器 - 兼容 Python 3.9
使用 transformers + accelerate 提供 OpenAI 兼容 API
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

class ModelServer:
    """模型服务器"""
    def __init__(self, model_path: str, device: str = "auto"):
        self.model_path = model_path
        self.device = device
        self.tokenizer = None
        self.model = None
        self.load_model()
    
    def load_model(self):
        """加载模型"""
        print(f"🔄 正在加载模型: {self.model_path}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # 根据显存自动选择加载方式
        if self.device == "auto":
            try:
                # 尝试使用 accelerate 自动分配
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    max_memory={0: "6GiB", "cpu": "30GiB"},
                    trust_remote_code=True
                )
                print("✅ 使用 device_map='auto' 加载（GPU+CPU混合）")
            except Exception as e:
                print(f"⚠️ 自动分配失败: {e}")
                print("🔄 使用 CPU 加载...")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float32,
                    device_map="cpu",
                    trust_remote_code=True
                )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=self.device,
                trust_remote_code=True
            )
        
        self.model.eval()
        print("✅ 模型加载完成！")
    
    def generate(self, messages: List[Dict], temperature: float = 0.7, 
                 max_tokens: int = 512, **kwargs) -> str:
        """生成回复"""
        # 构建 prompt
        prompt = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # 编码输入
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        # 移动到模型所在设备
        if hasattr(self.model, 'device'):
            device = self.model.device
        else:
            device = next(self.model.parameters()).device
        
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # 生成配置
        generation_config = GenerationConfig(
            temperature=temperature,
            max_new_tokens=max_tokens,
            do_sample=temperature > 0,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            **kwargs
        )
        
        # 生成
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                generation_config=generation_config
            )
        
        # 解码输出
        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:], 
            skip_special_tokens=True
        )
        
        return response


class APIHandler(BaseHTTPRequestHandler):
    """API 请求处理器"""
    model_server = None
    
    def log_message(self, format, *args):
        """自定义日志"""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == "/v1/models":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "object": "list",
                "data": [{"id": "local-model", "object": "model"}]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == "/v1/chat/completions":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                messages = data.get('messages', [])
                temperature = data.get('temperature', 0.7)
                max_tokens = data.get('max_tokens', 512)
                model_id = data.get('model', 'local-model')
                
                # 生成回复
                content = self.model_server.generate(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # 构建 OpenAI 格式响应
                response = {
                    "id": "chatcmpl-local",
                    "object": "chat.completion",
                    "created": int(__import__('time').time()),
                    "model": model_id,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ 生成错误: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()


def run_server(model_path: str, port: int = 8000, device: str = "auto"):
    """运行服务器"""
    # 加载模型
    server = ModelServer(model_path, device)
    APIHandler.model_server = server
    
    # 启动 HTTP 服务
    httpd = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"\n🚀 模型 API 服务已启动!")
    print(f"   地址: http://localhost:{port}")
    print(f"   模型: {model_path}")
    print(f"   按 Ctrl+C 停止\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="本地模型 API 服务器")
    parser.add_argument("--model", type=str, required=True, help="模型路径")
    parser.add_argument("--port", type=int, default=8000, help="服务端口")
    parser.add_argument("--device", type=str, default="auto", help="设备 (auto/cpu/cuda)")
    
    args = parser.parse_args()
    run_server(args.model, args.port, args.device)
