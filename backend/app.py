"""
旅游攻略智能体 - 主应用入口
基于Flask的Web服务，集成LangChain Agent
"""

import os
import sys
from pathlib import Path

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, send_from_directory, render_template
from flask_cors import CORS

import config
from api.routes import api


def create_app():
    """创建Flask应用"""
    app = Flask(
        __name__,
        static_folder=str(PROJECT_ROOT.parent / "frontend" / "static"),
        template_folder=str(PROJECT_ROOT.parent / "frontend" / "templates"),
    )
    
    # 配置
    app.config['SECRET_KEY'] = 'travel-agent-secret-key'
    
    # 启用CORS
    CORS(app)
    
    # 注册API蓝图
    app.register_blueprint(api, url_prefix='/api')
    
    # 前端路由
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)
    
    return app


def main():
    """启动服务"""
    print("=" * 50)
    print("🗺️  旅游攻略智能体 v1.0")
    print("=" * 50)
    print(f"📍 服务地址: http://{config.HOST}:{config.PORT}")
    print(f"🤖 模型: {config.LLM_MODEL}")
    print(f"📊 数据目录: {config.CHROMA_PERSIST_DIR}")
    print("=" * 50)
    print("按 Ctrl+C 停止服务")
    print()
    
    app = create_app()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )


if __name__ == '__main__':
    main()
