#!/bin/bash
# 旅游攻略智能体 - 启动脚本
# 使用方法: bash run.sh

echo "=========================================="
echo "🗺️  旅游攻略智能体 - 启动脚本"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

echo "✅ Python3版本: $(python3 --version)"

# 进入项目目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
echo "📁 项目目录: $SCRIPT_DIR"

# 检查并安装依赖
echo ""
echo "📦 检查依赖..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "📥 安装Python依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

# 检查API Key配置
echo ""
echo "🔑 检查API Key配置..."
if grep -q "YOUR_API_KEY_HERE" backend/config.py; then
    echo "⚠️  警告: 请先在 backend/config.py 中配置你的API Key"
    echo "   找到 LLM_API_KEY 和 EMBEDDING_API_KEY 并替换"
    echo ""
    read -p "是否仍要启动服务？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
fi

# 启动服务
echo ""
echo "🚀 启动服务..."
echo "📍 访问地址: http://localhost:8080"
echo "📍 按 Ctrl+C 停止服务"
echo ""
cd backend
python3 app.py
