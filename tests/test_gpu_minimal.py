#!/usr/bin/env python3
"""GPU 最小测试"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print("加载模型...")
model_path = "/mnt/newdisk/agent/models/qwen2.5-7b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

if torch.cuda.is_available():
    print("使用 CUDA...")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True
    ).cuda()
else:
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )

print(f"设备: {next(model.parameters()).device}")
print(f"显存: {torch.cuda.memory_allocated()/1e9:.2f} GB")

# 单次推理
question = "1+1="
print(f"\n问题: {question}")
inputs = tokenizer(question, return_tensors="pt").to(model.device)

print("推理中...")
with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=10)

answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"答案: {answer}")
print("\n✅ GPU 测试成功!")
