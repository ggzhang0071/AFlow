# AFlow 环境配置完整指南

本文档详细介绍如何配置 AFlow 项目的运行环境。

## 📋 目录

1. [系统要求](#1-系统要求)
2. [虚拟环境配置](#2-虚拟环境配置)
3. [依赖安装](#3-依赖安装)
4. [配置文件设置](#4-配置文件设置)
5. [验证安装](#5-验证安装)
6. [常见问题](#6-常见问题)

---

## 1. 系统要求

### 最低配置

| 项目 | 要求 |
|------|------|
| 操作系统 | Linux (Ubuntu 18.04+) / macOS 10.14+ / Windows 10+ |
| Python | 3.9 - 3.11 |
| 内存 | 8 GB |
| 存储 | 10 GB 可用空间 |

### 推荐配置

| 项目 | 要求 |
|------|------|
| Python | 3.9 |
| 内存 | 16 GB+ |
| 存储 | 50 GB+ SSD |
| GPU | NVIDIA RTX 3070 8GB+ (可选但推荐) |

---

## 2. 虚拟环境配置

### 2.1 使用 Conda（推荐）

```bash
# 安装 Miniconda（如果未安装）
# 下载地址: https://docs.conda.io/en/latest/miniconda.html

# 创建 Python 3.9 环境
conda create -n aflow python=3.9 -y

# 激活环境
conda activate aflow

# 验证 Python 版本
python --version
# 输出: Python 3.9.x
```

### 2.2 使用 venv

```bash
# 创建虚拟环境
python3.9 -m venv aflow_env

# 激活环境 (Linux/Mac)
source aflow_env/bin/activate

# 激活环境 (Windows)
aflow_env\Scripts\activate

# 验证
python --version
```

### 2.3 退出和删除环境

```bash
# 退出 conda 环境
conda deactivate

# 删除 conda 环境（如需重新创建）
conda remove -n aflow --all

# 退出 venv
# 直接执行 deactivate 或关闭终端
```

---

## 3. 依赖安装

### 3.1 基础依赖

```bash
# 确保在虚拟环境中
conda activate aflow  # 或 source aflow_env/bin/activate

# 进入 AFlow 目录
cd /mnt/newdisk/agent/AFlow

# 方式 1: 使用 requirements.txt 安装
pip install -r requirements.txt

# 方式 2: 手动安装核心依赖
pip install openai==1.82.0 \
            pandas==2.2.3 \
            pyaml==25.1.0 \
            pydantic==2.11.5 \
            PyYAML==6.0.2 \
            tenacity==9.1.2 \
            tqdm==4.67.1
```

### 3.2 GPU 支持（可选）

如果需要使用本地 GPU 模型：

```bash
# 安装 PyTorch (CUDA 12.1)
pip install torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu121

# 安装 Transformers 和相关库
pip install transformers accelerate \
            sentencepiece protobuf

# 验证 CUDA 可用
python -c "import torch; print(f'CUDA 可用: {torch.cuda.is_available()}')"
```

### 3.3 国内镜像加速

如果下载速度慢，使用清华镜像：

```bash
# 临时使用镜像
pip install -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或设置默认镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 4. 配置文件设置

### 4.1 LLM API 配置

编辑 `config/config2.yaml`：

```yaml
models:
  # OpenAI GPT-4o
  gpt-4o:
    api_type: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "sk-your-openai-api-key-here"  # 替换为你的 API 密钥
    model: "gpt-4o"
    temperature: 0
  
  # OpenAI GPT-4o-mini (成本低，推荐用于执行)
  gpt-4o-mini:
    api_type: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "sk-your-openai-api-key-here"
    model: "gpt-4o-mini"
    temperature: 0
  
  # Azure OpenAI (可选)
  azure-gpt-4:
    api_type: "azure"
    base_url: "https://your-resource.openai.azure.com/"
    api_key: "your-azure-api-key"
    model: "gpt-4"
    api_version: "2024-02-01"
    temperature: 0
  
  # 本地 vLLM 服务 (可选)
  local-qwen:
    api_type: "openai"
    base_url: "http://localhost:8000/v1"
    api_key: "EMPTY"
    model: "Qwen/Qwen2.5-7B-Instruct"
    temperature: 0
```

### 4.2 配置本地模型路径

如果使用本地模型（不需要 API）：

```yaml
models:
  local-model:
    api_type: "openai"
    base_url: "http://localhost:8000/v1"  # vLLM/LM Studio 服务地址
    api_key: "EMPTY"
    model: "/mnt/newdisk/agent/models/qwen2.5-7b-instruct"
    temperature: 0
```

### 4.3 使用环境变量

更安全的方式是使用环境变量：

```bash
# 设置环境变量（推荐添加到 ~/.bashrc 或 ~/.zshrc）
export OPENAI_API_KEY="sk-your-api-key"

# 然后 config2.yaml 可以简化为
models:
  gpt-4o:
    api_type: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"  # 从环境变量读取
    model: "gpt-4o"
    temperature: 0
```

---

## 5. 验证安装

### 5.1 基础验证

```bash
# 在 AFlow 目录下
cd /mnt/newdisk/agent/AFlow

# 验证 Python 环境
python --version

# 验证依赖安装
python -c "import openai, pandas, yaml; print('✓ 核心依赖安装成功')"

# 验证配置文件
python -c "
import yaml
with open('config/config2.yaml') as f:
    config = yaml.safe_load(f)
print('✓ 配置文件格式正确')
print('可用模型:', list(config.get('models', {}).keys()))
"
```

### 5.2 快速功能测试

```bash
# 运行快速测试
python tests/test_aflow_quick.py

# 或使用入口脚本
./test.sh quick
```

### 5.3 GPU 验证（如果使用本地模型）

```bash
# 运行 GPU 测试
python tests/test_gpu_auto.py

# 或使用入口脚本
./test.sh gpu
```

---

## 6. 常见问题

### Q1: 依赖冲突怎么办？

```bash
# 方法 1: 创建全新的虚拟环境
conda create -n aflow_new python=3.9 -y
conda activate aflow_new
pip install -r requirements.txt

# 方法 2: 使用 conda 解决冲突
conda install -c conda-forge openai pandas pyyaml
```

### Q2: pip 安装超时？

```bash
# 增加超时时间和重试次数
pip install --default-timeout=300 -r requirements.txt --retries 5

# 或使用国内镜像
pip install -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn
```

### Q3: CUDA 版本不匹配？

```bash
# 查看 CUDA 版本
nvidia-smi

# 安装对应版本的 PyTorch
# CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121

# CUDA 11.8
pip install torch --index-url https://download.pytorch.org/whl/cu118

# CPU 版本
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Q4: API 密钥无效？

```bash
# 验证 API 密钥
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 如果返回模型列表，说明密钥有效
```

### Q5: 权限错误？

```bash
# 不要以 root 身份运行
# 使用普通用户

# 确保目录权限正确
chmod -R 755 /mnt/newdisk/agent/AFlow
chmod +x /mnt/newdisk/agent/AFlow/test.sh
chmod +x /mnt/newdisk/agent/AFlow/tests/test_aflow.sh
```

---

## 🚀 一键配置脚本

保存为 `setup_env.sh`：

```bash
#!/bin/bash
# AFlow 环境一键配置脚本

set -e

echo "======================================================"
echo "  AFlow 环境配置脚本"
echo "======================================================"

# 检查 Python 版本
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python 版本: $PYTHON_VERSION"

# 检查虚拟环境
if [ -z "$VIRTUAL_ENV" ] && [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "警告: 未检测到虚拟环境"
    echo "建议先创建虚拟环境:"
    echo "  conda create -n aflow python=3.9 -y"
    echo "  conda activate aflow"
    exit 1
fi

# 安装依赖
echo ""
echo "[1/4] 安装依赖..."
pip install -q -r requirements.txt

# 检查 GPU
echo ""
echo "[2/4] 检查 GPU..."
python -c "
import torch
if torch.cuda.is_available():
    print(f'✓ GPU 可用: {torch.cuda.get_device_name(0)}')
    print(f'  显存: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
else:
    print('✗ GPU 不可用，将使用 CPU')
"

# 验证配置
echo ""
echo "[3/4] 验证配置..."
python -c "
import yaml
with open('config/config2.yaml') as f:
    config = yaml.safe_load(f)
models = list(config.get('models', {}).keys())
print(f'✓ 配置有效，可用模型: {models}')
"

# 运行测试
echo ""
echo "[4/4] 运行验证测试..."
python tests/test_aflow_quick.py

echo ""
echo "======================================================"
echo "  ✅ 环境配置完成!"
echo "======================================================"
echo ""
echo "可以开始使用 AFlow:"
echo "  ./test.sh run --dataset GSM8K --sample 2 --max_rounds 3"
```

使用方法：
```bash
chmod +x setup_env.sh
./setup_env.sh
```

---

## 📚 相关文档

- [AFlow README](README.md)
- [AFlow 详细指南](AFLOW_GUIDE.md)
- [项目根目录 README](../README.md)

---

**最后更新**: 2026-04-09
