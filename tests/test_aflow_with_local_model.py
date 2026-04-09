#!/usr/bin/env python3
"""
使用本地模型测试 AFlow 风格的工作流
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*70)
print("🚀 AFlow + 本地模型 (Qwen2.5-7B) 测试")
print("="*70)
print()

# 导入必要的库
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 配置
MODEL_PATH = "/mnt/newdisk/agent/models/qwen2.5-7b-instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"📦 加载模型: {MODEL_PATH}")
print(f"🖥️  设备: {DEVICE}")
print()

# 加载模型
print("加载 Tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
print(f"✓ Tokenizer 加载成功 (词汇表: {len(tokenizer):,})")

print("加载模型...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    device_map="auto" if DEVICE == "cuda" else None,
    trust_remote_code=True
)
if DEVICE == "cpu":
    model = model.to(DEVICE)
print(f"✓ 模型加载成功")
print()

# ==================== 工作流操作符 ====================

def operator_custom(question: str, model, tokenizer) -> str:
    """Custom 操作符: 直接生成答案"""
    messages = [
        {"role": "system", "content": "你是一个 helpful assistant。请回答以下问题。"},
        {"role": "user", "content": question}
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
    
    response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
    return response.strip()

def operator_programmer(question: str, model, tokenizer) -> str:
    """Programmer 操作符: 生成代码来解决问题"""
    messages = [
        {"role": "system", "content": "你是一个编程专家。请编写 Python 代码来解决以下问题。只输出代码，不需要解释。"},
        {"role": "user", "content": f"问题: {question}\n\n请编写代码解决："}
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.3,
            top_p=0.95
        )
    
    code = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
    return code.strip()

def operator_sc_ensemble(question: str, model, tokenizer, n_samples: int = 3) -> str:
    """ScEnsemble 操作符: 自一致性集成，多轮采样投票"""
    responses = []
    
    for i in range(n_samples):
        messages = [
            {"role": "system", "content": "你是一个数学专家。请逐步推理并回答。"},
            {"role": "user", "content": question}
        ]
        
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7 + i * 0.1,  # 不同的温度
                top_p=0.9
            )
        
        response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
        responses.append(response.strip())
    
    # 简单返回最常见的答案（实际应该使用答案提取和投票）
    return responses[0]  # 简化处理

# ==================== 测试工作流 ====================

def test_workflow_single(question: str, answer: str, model, tokenizer):
    """测试单一操作符工作流"""
    print(f"问题: {question}")
    print(f"正确答案: {answer}")
    print()
    
    # Custom 操作符
    print("操作符 1: Custom")
    result = operator_custom(question, model, tokenizer)
    print(f"输出: {result[:200]}...")
    print()
    
    # Programmer 操作符
    print("操作符 2: Programmer")
    result = operator_programmer(question, model, tokenizer)
    print(f"输出: {result[:200]}...")
    print()

def test_workflow_chain(question: str, answer: str, model, tokenizer):
    """测试链式工作流 (Programmer -> Custom)"""
    print(f"问题: {question}")
    print(f"正确答案: {answer}")
    print()
    
    # 链式操作: 先用 Programmer 生成代码，然后用 Custom 解释结果
    print("链式工作流: Programmer -> Custom")
    
    # Step 1: Programmer
    code = operator_programmer(question, model, tokenizer)
    print(f"Step 1 (Programmer) 生成代码:\n{code[:300]}...")
    print()
    
    # Step 2: Custom 解释
    explanation_prompt = f"代码:\n{code}\n\n请解释这段代码如何解决原问题: {question}"
    explanation = operator_custom(explanation_prompt, model, tokenizer)
    print(f"Step 2 (Custom) 解释:\n{explanation[:300]}...")
    print()

# ==================== 主函数 ====================

def main():
    # 测试问题
    test_problems = [
        {
            "question": "小明有 5 个苹果，他给了小红 2 个，然后又买了 3 个。现在小明有多少个苹果？",
            "answer": "6",
            "type": "math"
        },
        {
            "question": "一个长方形的长是 8 厘米，宽是 5 厘米，它的面积是多少？",
            "answer": "40",
            "type": "math"
        }
    ]
    
    print("="*70)
    print("测试 1: 单一操作符工作流")
    print("="*70)
    print()
    
    problem = test_problems[0]
    test_workflow_single(problem["question"], problem["answer"], model, tokenizer)
    
    print("="*70)
    print("测试 2: 链式工作流")
    print("="*70)
    print()
    
    problem = test_problems[1]
    test_workflow_chain(problem["question"], problem["answer"], model, tokenizer)
    
    print("="*70)
    print("✅ 测试完成!")
    print("="*70)
    print()
    print("💡 说明:")
    print("  • 以上展示了 AFlow 中不同操作符的工作方式")
    print("  • 实际 AFlow 使用 MCTS 自动组合这些操作符")
    print("  • 通过多次迭代找到最优的工作流结构")
    print()
    print("🚀 要运行完整的 AFlow，需要:")
    print("  1. 配置 OpenAI API 密钥")
    print("  2. 下载数据集")
    print("  3. 运行: python run.py --dataset GSM8K")

if __name__ == "__main__":
    main()
