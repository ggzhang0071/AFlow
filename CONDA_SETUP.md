

### 在Conda环境中运行

```bash
# 每次使用前激活环境
conda activate aflow

# 进入AFlow目录
cd /mnt/newdisk/agent/AFlow

# 运行测试
./test.sh quick

# 或运行完整优化
./test.sh run --dataset GSM8K --sample 2 --max_rounds 3
```
