#!/bin/bash
# AFlow Conda 环境一键配置脚本
# 使用方法: ./setup_conda.sh

set -e

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Banner
echo -e "${BLUE}"
echo "=============================================================="
echo "  AFlow Conda 环境配置脚本"
echo "=============================================================="
echo -e "${NC}"

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "工作目录: $(pwd)"
echo ""

# ==================== 检查 Conda ====================
echo -e "${YELLOW}[1/7] 检查 Conda 安装...${NC}"

if ! command -v conda &> /dev/null; then
    echo -e "${RED}错误: 未找到 Conda${NC}"
    echo "请先安装 Miniconda:"
    echo "  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    echo "  bash Miniconda3-latest-Linux-x86_64.sh"
    exit 1
fi

CONDA_VERSION=$(conda --version)
echo -e "${GREEN}✓ Conda 已安装: $CONDA_VERSION${NC}"

# 初始化conda（如果未初始化）
if [ ! -f "$HOME/.conda/environments.txt" ]; then
    echo "初始化 Conda..."
    conda init bash
fi
echo ""

# ==================== 创建环境 ====================
echo -e "${YELLOW}[2/7] 创建 Conda 环境...${NC}"

ENV_NAME="aflow"
PYTHON_VERSION="3.9"

# 检查环境是否已存在
if conda env list | grep -q "^$ENV_NAME "; then
    echo -e "${YELLOW}环境 '$ENV_NAME' 已存在${NC}"
    read -p "是否删除并重新创建? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除旧环境..."
        conda remove -n $ENV_NAME --all -y
        echo "创建新环境..."
        conda create -n $ENV_NAME python=$PYTHON_VERSION -y
    else
        echo "使用现有环境"
    fi
else
    echo "创建环境: $ENV_NAME (Python $PYTHON_VERSION)"
    conda create -n $ENV_NAME python=$PYTHON_VERSION -y
fi
echo -e "${GREEN}✓ 环境创建完成${NC}"
echo ""

# ==================== 激活环境 ====================
echo -e "${YELLOW}[3/7] 激活环境...${NC}"

# 激活环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

# 验证
if [ "$CONDA_DEFAULT_ENV" != "$ENV_NAME" ]; then
    echo -e "${RED}错误: 环境激活失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 环境已激活: $CONDA_DEFAULT_ENV${NC}"
echo "Python: $(which python)"
echo "版本: $(python --version)"
echo ""

# ==================== 安装依赖 ====================
echo -e "${YELLOW}[4/7] 安装基础依赖...${NC}"

pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${YELLOW}未找到 requirements.txt，安装核心依赖${NC}"
    pip install openai pandas pyyaml tenacity tqdm numpy
fi

echo -e "${GREEN}✓ 基础依赖安装完成${NC}"
echo ""

# ==================== 安装 GPU 支持 ====================
echo -e "${YELLOW}[5/7] 安装 GPU 支持 (可选)...${NC}"

# 检查CUDA
if command -v nvidia-smi &> /dev/null; then
    echo "检测到 NVIDIA GPU:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    
    read -p "是否安装 PyTorch GPU 版本? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "安装 PyTorch (CUDA 12.1)..."
        conda install pytorch pytorch-cuda=12.1 -c pytorch -c nvidia -y
        pip install transformers accelerate sentencepiece protobuf
        echo -e "${GREEN}✓ GPU 支持已安装${NC}"
    else
        echo "跳过 GPU 安装"
    fi
else
    echo "未检测到 NVIDIA GPU，跳过 GPU 安装"
fi
echo ""

# ==================== 配置检查 ====================
echo -e "${YELLOW}[6/7] 检查配置文件...${NC}"

if [ ! -f "config/config2.yaml" ]; then
    if [ -f "config/config2.example.yaml" ]; then
        echo "从示例创建配置文件..."
        cp config/config2.example.yaml config/config2.yaml
        echo -e "${YELLOW}⚠ 请编辑 config/config2.yaml 添加你的 API 密钥${NC}"
    else
        echo -e "${RED}错误: 未找到配置文件模板${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 配置文件已存在${NC}"
fi

# 验证配置
python -c "
import yaml
try:
    with open('config/config2.yaml') as f:
        config = yaml.safe_load(f)
    models = list(config.get('models', {}).keys())
    print(f'✓ 配置有效，可用模型: {models}')
except Exception as e:
    print(f'✗ 配置错误: {e}')
    exit(1)
"
echo ""

# ==================== 验证安装 ====================
echo -e "${YELLOW}[7/7] 验证安装...${NC}"

python -c "
import sys
packages = ['openai', 'pandas', 'yaml', 'tenacity', 'tqdm']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f'✗ 缺少包: {missing}')
    sys.exit(1)
else:
    print('✓ 所有核心包已安装')

# 检查GPU
try:
    import torch
    if torch.cuda.is_available():
        print(f'✓ GPU 可用: {torch.cuda.get_device_name(0)}')
    else:
        print('⚠ GPU 不可用')
except ImportError:
    print('⚠ PyTorch 未安装')
"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 验证失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 验证通过${NC}"
echo ""

# ==================== 完成 ====================
echo -e "${GREEN}==============================================================${NC}"
echo -e "${GREEN}  ✅ Conda 环境配置完成!${NC}"
echo -e "${GREEN}==============================================================${NC}"
echo ""
echo "环境信息:"
echo "  名称: $ENV_NAME"
echo "  Python: $(python --version)"
echo "  路径: $(which python)"
echo ""
echo "使用方法:"
echo "  1. 激活环境: conda activate $ENV_NAME"
echo "  2. 运行测试: ./test.sh quick"
echo "  3. 运行优化: ./test.sh run --dataset GSM8K --sample 2 --max_rounds 3"
echo ""
echo "注意:"
echo "  • 每次使用前需先激活环境: conda activate $ENV_NAME"
echo "  • 编辑 config/config2.yaml 配置 API 密钥"
echo "  • 或设置环境变量: export OPENAI_API_KEY=your-key"
echo ""
echo "文档:"
echo "  • 详细说明: cat CONDA_SETUP.md"
echo "  • 快速开始: cat ENVIRONMENT_SETUP.md"
