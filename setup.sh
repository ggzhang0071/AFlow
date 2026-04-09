#!/bin/bash
# AFlow 环境一键配置脚本
# 使用方法: ./setup.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "=============================================================="
echo "  AFlow 环境配置脚本"
echo "=============================================================="
echo -e "${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "工作目录: $(pwd)"
echo ""

# ==================== 步骤 1: 检查 Python ====================
echo -e "${YELLOW}[1/6] 检查 Python 版本...${NC}"

if ! command -v python &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python${NC}"
    echo "请先安装 Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Python 版本: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -ne 3 ] || [ "$PYTHON_MINOR" -lt 9 ]; then
    echo -e "${RED}错误: 需要 Python 3.9+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 版本符合要求${NC}"
echo ""

# ==================== 步骤 2: 检查虚拟环境 ====================
echo -e "${YELLOW}[2/6] 检查虚拟环境...${NC}"

if [ -z "$VIRTUAL_ENV" ] && [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${YELLOW}警告: 未检测到虚拟环境${NC}"
    echo ""
    echo "建议使用虚拟环境:"
    echo "  conda 用户: conda create -n aflow python=3.9 -y && conda activate aflow"
    echo "  venv 用户:  python3.9 -m venv aflow_env && source aflow_env/bin/activate"
    echo ""
    read -p "是否继续安装到当前环境? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    if [ -n "$CONDA_DEFAULT_ENV" ]; then
        echo -e "${GREEN}✓ Conda 环境已激活: $CONDA_DEFAULT_ENV${NC}"
    else
        echo -e "${GREEN}✓ 虚拟环境已激活: $VIRTUAL_ENV${NC}"
    fi
fi
echo ""

# ==================== 步骤 3: 安装依赖 ====================
echo -e "${YELLOW}[3/6] 安装依赖...${NC}"

if [ -f "requirements.txt" ]; then
    echo "从 requirements.txt 安装..."
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${YELLOW}警告: 未找到 requirements.txt${NC}"
    echo "安装核心依赖..."
    pip install -q openai pandas pyyaml tenacity tqdm numpy
fi
echo ""

# ==================== 步骤 4: 检查 GPU ====================
echo -e "${YELLOW}[4/6] 检查 GPU 支持...${NC}"

python -c "
import sys
try:
    import torch
    if torch.cuda.is_available():
        print(f'✓ GPU 可用: {torch.cuda.get_device_name(0)}')
        print(f'  显存: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
        print(f'  CUDA 版本: {torch.version.cuda}')
        sys.exit(0)
    else:
        print('✗ GPU 不可用，将使用 CPU')
        sys.exit(1)
except ImportError:
    print('✗ PyTorch 未安装')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    GPU_AVAILABLE=true
else
    GPU_AVAILABLE=false
fi
echo ""

# ==================== 步骤 5: 配置检查 ====================
echo -e "${YELLOW}[5/6] 检查配置文件...${NC}"

if [ ! -f "config/config2.yaml" ]; then
    if [ -f "config/config2.example.yaml" ]; then
        echo "从示例创建配置文件..."
        cp config/config2.example.yaml config/config2.yaml
        echo -e "${YELLOW}⚠ 请编辑 config/config2.yaml 添加你的 API 密钥${NC}"
    else
        echo -e "${RED}错误: 未找到配置文件${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 配置文件已存在${NC}"
    
    # 检查配置是否有效
    python -c "
import yaml
try:
    with open('config/config2.yaml') as f:
        config = yaml.safe_load(f)
    models = list(config.get('models', {}).keys())
    print(f'✓ 配置有效，可用模型: {models}')
except Exception as e:
    print(f'✗ 配置文件错误: {e}')
    exit(1)
"
fi
echo ""

# ==================== 步骤 6: 验证安装 ====================
echo -e "${YELLOW}[6/6] 验证安装...${NC}"

python -c "
import sys
errors = []

try:
    import openai
except ImportError:
    errors.append('openai')

try:
    import pandas
except ImportError:
    errors.append('pandas')

try:
    import yaml
except ImportError:
    errors.append('yaml')

try:
    import tenacity
except ImportError:
    errors.append('tenacity')

if errors:
    print(f'✗ 缺少依赖: {', '.join(errors)}')
    sys.exit(1)
else:
    print('✓ 所有核心依赖已安装')
"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 依赖验证失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 验证通过${NC}"
echo ""

# ==================== 完成 ====================
echo -e "${GREEN}==============================================================${NC}"
echo -e "${GREEN}  ✅ 环境配置完成!${NC}"
echo -e "${GREEN}==============================================================${NC}"
echo ""
echo "配置摘要:"
echo "  Python: $PYTHON_VERSION"
if [ "$GPU_AVAILABLE" = true ]; then
    echo "  GPU: 可用"
else
    echo "  GPU: 不可用（将使用 CPU）"
fi
echo "  配置文件: config/config2.yaml"
echo ""
echo "下一步:"
echo "  1. 编辑 config/config2.yaml 添加你的 API 密钥"
echo "     或设置环境变量: export OPENAI_API_KEY=your-key"
echo ""
echo "  2. 运行快速测试:"
echo "     ./test.sh quick"
echo ""
echo "  3. 开始优化:"
echo "     ./test.sh run --dataset GSM8K --sample 2 --max_rounds 3"
echo ""

if [ "$GPU_AVAILABLE" = true ]; then
    echo "  或使用本地 GPU 模型:"
    echo "     ./test.sh gpu"
    echo ""
fi

echo "更多帮助:"
echo "  ./test.sh help"
echo "  cat ENVIRONMENT_SETUP.md"
