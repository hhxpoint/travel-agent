"""
旅游攻略智能体 - API路由
定义Flask应用的RESTful API接口
"""

from flask import Blueprint, request, jsonify
import json

api = Blueprint('api', __name__)


# 延迟导入以避免循环引用
def get_agent():
    from agent.travel_agent import TravelAgent, SimpleTravelAgent
    try:
        return TravelAgent()
    except Exception:
        return SimpleTravelAgent()


def get_data_manager():
    from data.data_manager import get_data_manager as _get_dm
    return _get_dm()


# 全局Agent实例（延迟初始化）
_agent = None

def get_or_create_agent():
    global _agent
    if _agent is None:
        _agent = get_agent()
    return _agent


@api.route('/chat', methods=['POST'])
def chat():
    """
    聊天接口
    
    请求体:
    {
        "message": "用户消息",
        "session_id": "会话ID（可选）"
    }
    
    响应:
    {
        "success": true,
        "response": "智能体回复",
        "tool_calls": [...]
    }
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"success": False, "response": "请提供message参数"}), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({"success": False, "response": "消息不能为空"}), 400
        
        agent = get_or_create_agent()
        result = agent.chat(message)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "response": f"服务器错误: {str(e)}",
            "tool_calls": []
        }), 500


@api.route('/welcome', methods=['GET'])
def welcome():
    """获取欢迎消息"""
    agent = get_or_create_agent()
    return jsonify({"message": agent.get_welcome()})


@api.route('/clear', methods=['POST'])
def clear_history():
    """清空聊天历史"""
    agent = get_or_create_agent()
    agent.clear_history()
    return jsonify({"success": True, "message": "聊天历史已清空"})


@api.route('/guides', methods=['GET'])
def list_guides():
    """获取所有攻略列表"""
    dm = get_data_manager()
    guides = dm.get_all_guides()
    # 返回简要信息
    summary = []
    for g in guides:
        summary.append({
            "id": g["id"],
            "destination": g["destination"],
            "title": g["title"],
            "days": g["days"],
            "budget": g["budget"],
            "season": g["season"],
            "tags": g.get("tags", []),
        })
    return jsonify({"success": True, "guides": summary})


@api.route('/guides/<int:guide_id>', methods=['GET'])
def get_guide(guide_id):
    """获取单个攻略详情"""
    dm = get_data_manager()
    guide = dm.get_guide_by_id(guide_id)
    if not guide:
        return jsonify({"success": False, "message": "攻略不存在"}), 404
    return jsonify({"success": True, "guide": guide})


@api.route('/guides', methods=['POST'])
def add_guide():
    """添加新攻略"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请提供攻略数据"}), 400
        
        dm = get_data_manager()
        new_guide = dm.add_guide(data)
        
        return jsonify({
            "success": True,
            "message": f"攻略'{new_guide['title']}'添加成功",
            "guide": new_guide,
        }), 201
        
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"添加失败: {str(e)}"}), 500


@api.route('/search', methods=['GET'])
def search():
    """搜索攻略"""
    keyword = request.args.get('q', '').strip()
    if not keyword:
        return jsonify({"success": False, "message": "请提供搜索关键词"}), 400
    
    dm = get_data_manager()
    results = dm.fuzzy_search(keyword)
    
    summary = []
    for g in results:
        summary.append({
            "id": g["id"],
            "destination": g["destination"],
            "title": g["title"],
            "days": g["days"],
            "budget": g["budget"],
            "tags": g.get("tags", []),
            "summary": g["summary"][:100],
        })
    
    return jsonify({"success": True, "results": summary, "count": len(summary)})


@api.route('/stats', methods=['GET'])
def stats():
    """获取数据统计"""
    dm = get_data_manager()
    return jsonify({"success": True, "stats": dm.get_stats()})


@api.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "service": "旅游攻略智能体"})
