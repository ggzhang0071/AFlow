# AFlow 完整使用指南

## 📖 项目简介

AFlow (Automating Agentic Workflow Generation) 是一个自动化的 Agentic 工作流生成框架，使用蒙特卡洛树搜索(MCTS)在代码表示的工作流空间中寻找有效的工作流。

## 🏗️ 核心组件

| 组件 | 说明 | 文件位置 |
|------|------|----------|
| **Node** | LLM 调用基本单元 | `metagpt_core/action_nodes/action_node.py` |
| **Operator** | 预定义的 Node 组合 | `operator.py` |
| **Workflow** | LLM 调用节点序列 | `workflow.py` |
| **Optimizer** | MCTS 优化器 | `optimizer.py` |
| **Evaluator** | 性能评估器 | `evaluator.py` |

## 🚀 快速开始

### 1. 环境准备

```bash
# 进入项目目录
cd /mnt/newdisk/agent/AFlow

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 LLM

编辑 `config/config2.yaml`:

```yaml
models:
  gpt-4o:
    api_type: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "your-openai-api-key"
    model: "gpt-4o"
    temperature: 0
  
  gpt-4o-mini:
    api_type: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "your-openai-api-key"
    model: "gpt-4o-mini"
    temperature: 0
```

### 3. 下载数据集

```bash
python -c "from data.download_data import download; download(['datasets'])"
```

### 4. 运行优化

```bash
# 基本用法
python run.py --dataset GSM8K

# 高级用法
python run.py --dataset GSM8K \
  --sample 4 \
  --max_rounds 20 \
  --initial_round 1 \
  --validation_rounds 5 \
  --opt_model_name gpt-4o \
  --exec_model_name gpt-4o-mini
```

## 📊 支持的数据集

| 数据集 | 类型 | 说明 | 操作符 |
|--------|------|------|--------|
| **GSM8K** | 数学 | 小学数学应用题 | Custom, ScEnsemble, Programmer |
| **MATH** | 数学 | 高中数学竞赛题 | Custom, ScEnsemble, Programmer |
| **HumanEval** | 代码 | 函数级代码生成 | Custom, CustomCodeGenerate, ScEnsemble, Test |
| **MBPP** | 代码 | Python 编程问题 | Custom, CustomCodeGenerate, ScEnsemble, Test |
| **HotpotQA** | 问答 | 多跳推理问答 | Custom, AnswerGenerate, ScEnsemble |
| **DROP** | 问答 | 离散推理问答 | Custom, AnswerGenerate, ScEnsemble |

## ⚙️ 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--dataset` | 必选 | 数据集类型 |
| `--sample` | 4 | 每次重采样的工作流数量 |
| `--max_rounds` | 20 | 最大迭代轮数 |
| `--initial_round` | 1 | 初始轮数 |
| `--validation_rounds` | 5 | 验证轮数 |
| `--check_convergence` | True | 是否启用早停 |
| `--optimized_path` | workspace | 优化结果保存路径 |
| `--opt_model_name` | claude-3-5-sonnet | 优化使用的模型 |
| `--exec_model_name` | gpt-4o-mini | 执行使用的模型 |

## 🔧 操作符类型

| 操作符 | 功能 |
|--------|------|
| **Custom** | 自定义生成 |
| **AnswerGenerate** | 答案生成 |
| **ScEnsemble** | 自一致性集成 |
| **Programmer** | 编程助手 |
| **CustomCodeGenerate** | 自定义代码生成 |
| **Test** | 代码测试 |

## 📝 运行示例

### 示例 1: 数学问题 (GSM8K)

```bash
python run.py --dataset GSM8K --sample 2 --max_rounds 5
```

预期输出:
```
[2024-XX-XX] 开始优化工作流...
Round 1/5: 最佳得分 0.65
Round 2/5: 最佳得分 0.72
Round 3/5: 最佳得分 0.78
...
优化完成! 最佳工作流已保存到 workspace/GSM8K/...
```

### 示例 2: 代码生成 (HumanEval)

```bash
python run.py --dataset HumanEval --sample 4 --max_rounds 10
```

### 示例 3: 问答系统 (HotpotQA)

```bash
python run.py --dataset HotpotQA --sample 3 --max_rounds 15
```

## 🎯 工作原理

1. **初始化**: 加载数据集和配置
2. **搜索空间**: 定义可能的操作符组合
3. **MCTS 优化**:
   - Selection: 选择最有潜力的节点
   - Expansion: 扩展新的工作流变体
   - Evaluation: 评估工作流性能
   - Backpropagation: 更新节点价值
4. **收敛**: 找到最优工作流或达到最大轮数
5. **保存**: 保存最佳工作流和结果

## 📁 输出结构

```
workspace/
└── {dataset}/
    ├── round_{n}/           # 每轮的结果
    │   ├── workflows/       # 生成的工作流
    │   ├── scores.json      # 得分记录
    │   └── trajectories/    # 优化轨迹
    ├── best_workflow.py     # 最佳工作流
    └── final_results.json   # 最终结果
```

## 🔍 调试与日志

日志文件位置: `logs/aflow_{timestamp}.log`

查看实时日志:
```bash
tail -f logs/aflow_*.log
```

## 💡 最佳实践

1. **从小样本开始**: 先用 `--sample 2` 测试
2. **合理设置轮数**: 通常 10-20 轮足够收敛
3. **使用轻量级模型执行**: gpt-4o-mini 成本低
4. **使用强模型优化**: gpt-4o/claude-3.5 效果更好
5. **保存中间结果**: 可以从中断处继续

## 🐛 常见问题

### Q: 没有 OpenAI API 密钥怎么办？
A: 可以使用本地模型服务（如 vLLM 或 LM Studio）

### Q: 数据集下载失败？
A: 检查网络连接，或手动从 Google Drive 下载

### Q: 显存不足？
A: 减小 batch size 或使用更小的执行模型

### Q: 如何自定义数据集？
A: 继承 `BaseBenchmark` 类并实现相关方法

## 📚 相关链接

- 论文: https://arxiv.org/abs/2410.10762
- GitHub: https://github.com/FoundationAgents/AFlow
- ICLR 2025: https://openreview.net/forum?id=z5uVAKwmjf
