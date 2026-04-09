# AFlow 快速开始指南

## 🚀 5分钟快速上手

### 第1步：配置 Conda 环境（2分钟）

```bash
cd /mnt/newdisk/agent/AFlow

# 一键配置conda环境
./setup_conda.sh
```

### 第2步：配置 API 密钥（1分钟）

方式1 - 环境变量：
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
# 添加到 ~/.bashrc 永久生效
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
```

方式2 - 配置文件：
```bash
nano config/config2.yaml
# 修改 api_key 字段
```

### 第3步：运行测试（2分钟）

```bash
# 激活环境
conda activate aflow

# 快速测试
./test.sh quick

# 或运行完整优化
./test.sh run --dataset GSM8K --sample 2 --max_rounds 3
```

---

## 📋 日常使用命令

### 激活环境
```bash
conda activate aflow
```

### 运行测试
```bash
# 快速验证
./test.sh quick

# GPU测试
./test.sh gpu

# MCTS演示
./test.sh demo

# 完整优化
./test.sh run --dataset GSM8K --sample 4 --max_rounds 10
```

### 退出环境
```bash
conda deactivate
```

---

## 🔧 常用配置

### 切换模型

编辑 `config/config2.yaml`：

```yaml
# 使用 OpenAI（推荐）
models:
  gpt-4o:
    api_type: "openai"
    api_key: "${OPENAI_API_KEY}"  # 从环境变量读取
    model: "gpt-4o"

# 使用本地模型（无需API）
  qwen2.5-7b:
    api_type: "openai"
    base_url: "http://localhost:8000/v1"
    api_key: "EMPTY"
    model: "Qwen/Qwen2.5-7B-Instruct"
```

### 运行参数

```bash
python run.py \
  --dataset GSM8K \           # 数据集: GSM8K, MATH, HumanEval, MBPP, HotpotQA, DROP
  --sample 4 \                # 每轮采样数
  --max_rounds 20 \           # 最大迭代轮数
  --opt_model_name gpt-4o \   # 优化模型
  --exec_model_name gpt-4o-mini  # 执行模型
```

---

## 🐛 常见问题

### Q: 未找到conda命令
```bash
# 添加conda到PATH
export PATH="$HOME/miniconda3/bin:$PATH"
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
```

### Q: 提示未在conda环境中
```bash
# 激活环境
conda activate aflow

# 验证
which python
# 应显示: /home/.../miniconda3/envs/aflow/bin/python
```

### Q: API密钥无效
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 测试API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 📚 更多文档

- `ENVIRONMENT_SETUP.md` - 完整环境配置
- `CONDA_SETUP.md` - Conda环境详细说明
- `AFLOW_GUIDE.md` - AFlow使用指南
- `README.md` - 项目主文档

---

## 💡 提示

1. **每次使用前激活环境**: `conda activate aflow`
2. **不要混用环境**: base环境可能缺少依赖
3. **保存API密钥到环境变量**: 比写在配置文件更安全
4. **小样本测试**: 先用 `--sample 2 --max_rounds 3` 测试

---

**现在可以开始使用AFlow了！** 🎉
