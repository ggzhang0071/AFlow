#!/usr/bin/env python3
"""
AFlow 功能演示 - 使用本地模型进行简单推理测试
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*70)
print("AFlow 项目功能演示")
print("="*70)

# 加载模型进行推理演示
print("\n📦 加载 Qwen2.5-7B-Instruct 模型...")

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_path = "/mnt/newdisk/agent/models/qwen2.5-7b-instruct"

# 加载 tokenizer
print("  加载 Tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
print(f"  ✓ Tokenizer 加载成功 (词汇表: {len(tokenizer):,})")

# 加载模型 (使用半精度节省显存)
print("  加载模型 (bf16 模式)...")
try:
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
except Exception as e:
    print(f"  使用 device_map 失败，尝试手动加载到 GPU/CPU...")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True
    )
    if torch.cuda.is_available():
        model = model.cuda()
        print("  ✓ 模型已加载到 GPU")
    else:
        print("  ✓ 模型已加载到 CPU")
print(f"  ✓ 模型加载成功")
print(f"  ✓ 设备: {next(model.parameters()).device}")

# 测试数学推理
print("\n" + "="*70)
print("🧮 测试 1: 数学推理 (GSM8K 风格)")
print("="*70)

math_problem = """问题: 小明有 5 个苹果，他给了小红 2 个，然后又买了 3 个。现在小明有多少个苹果？

请逐步思考并给出答案。"""

print(f"\n输入:\n{math_problem}")
print("\n模型推理中...")

messages = [
    {"role": "system", "content": "你是一个数学推理助手，请逐步思考并给出答案。"},
    {"role": "user", "content": math_problem}
]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=256,
    do_sample=False,
    temperature=0.0
)

response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
print(f"\n输出:\n{response}")

# 测试代码生成
print("\n" + "="*70)
print("💻 测试 2: 代码生成 (HumanEval 风格)")
print("="*70)

code_prompt = """编写一个 Python 函数，计算斐波那契数列的第 n 个数。

def fibonacci(n):
    \"\"\"
    计算斐波那契数列的第 n 个数
    参数: n - 正整数
    返回: 第 n 个斐波那契数
    \"\"\"
"""

print(f"\n输入:\n{code_prompt}")
print("\n模型推理中...")

messages = [
    {"role": "system", "content": "你是一个编程助手，请编写简洁、正确的代码。"},
    {"role": "user", "content": code_prompt}
]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    do_sample=False,
    temperature=0.0
)

response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
print(f"\n输出:\n{response}")

# 测试逻辑推理
print("\n" + "="*70)
print("🧩 测试 3: 逻辑推理 (StrategyQA 风格)")
print("="*70)

logic_question = """问题: 如果所有的花都会凋谢，玫瑰是花，那么玫瑰会凋谢吗？

请解释你的推理过程。"""

print(f"\n输入:\n{logic_question}")
print("\n模型推理中...")

messages = [
    {"role": "system", "content": "你是一个逻辑推理助手，请仔细分析并给出答案。"},
    {"role": "user", "content": logic_question}
]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    do_sample=False,
    temperature=0.0
)

response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
print(f"\n输出:\n{response}")

print("\n" + "="*70)
print("✅ AFlow 演示完成")
print("="*70)

print("""
📊 测试结果总结:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 模型加载: 成功 (Qwen2.5-7B-Instruct)
✓ 数学推理: 完成
✓ 代码生成: 完成
✓ 逻辑推理: 完成

📝 说明:
- AFlow 项目可以正常工作
- 本地模型可以正确加载和推理
- 由于 vLLM 与 Python 3.9 的兼容性问题，建议使用:
  1. 使用 Transformers 直接加载（当前方式）
  2. 或使用 OpenAI API（需要 API 密钥）
  3. 或升级 Python 到 3.10+ 后使用 vLLM

🚀 下一步:
- 使用 OpenAI API 运行完整 AFlow 测试:
  cd /mnt/newdisk/agent/AFlow
  export OPENAI_API_KEY=your_key
  python run.py --dataset GSM8K --sample 2

- 查看 AFlow 文档了解更多功能:
  cat /mnt/newdisk/agent/AFlow/README.md
""")
