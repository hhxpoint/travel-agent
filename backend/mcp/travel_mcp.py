"""
旅游攻略智能体 - MCP服务模块
基于Model Context Protocol的工具服务
允许其他AI应用通过MCP协议调用本系统的工具
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.data_manager import get_data_manager


class TravelMCPServer:
    """
    旅游攻略MCP服务
    提供标准化的工具接口，支持MCP协议调用
    """
    
    def __init__(self):
        self.dm = get_data_manager()
        self.tools = self._define_tools()
    
    def _define_tools(self):
        """定义MCP工具列表"""
        return [
            {
                "name": "search_destination",
                "description": "根据目的地搜索旅游攻略",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "destination": {
                            "type": "string",
                            "description": "目的地名称"
                        }
                    },
                    "required": ["destination"]
                }
            },
            {
                "name": "search_by_tags",
                "description": "根据标签搜索旅游攻略",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签列表"
                        }
                    },
                    "required": ["tags"]
                }
            },
            {
                "name": "search_by_budget",
                "description": "根据预算搜索旅游攻略",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "budget": {
                            "type": "string",
                            "description": "预算等级：低、中等、中高、较高"
                        }
                    },
                    "required": ["budget"]
                }
            },
            {
                "name": "search_by_season",
                "description": "根据季节搜索旅游攻略",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "season": {
                            "type": "string",
                            "description": "季节：春季、夏季、秋季、冬季"
                        }
                    },
                    "required": ["season"]
                }
            },
            {
                "name": "get_guide_detail",
                "description": "获取攻略详情",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "guide_id": {
                            "type": "integer",
                            "description": "攻略ID"
                        }
                    },
                    "required": ["guide_id"]
                }
            },
            {
                "name": "add_guide",
                "description": "添加新的旅游攻略",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string", "description": "目的地"},
                        "title": {"type": "string", "description": "攻略标题"},
                        "days": {"type": "integer", "description": "天数"},
                        "summary": {"type": "string", "description": "简介"},
                        "budget": {"type": "string", "description": "预算"},
                        "season": {"type": "string", "description": "季节"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "标签"},
                        "itinerary": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "day": {"type": "integer"},
                                    "title": {"type": "string"},
                                    "details": {"type": "string"},
                                    "food": {"type": "string"},
                                    "tips": {"type": "string"}
                                }
                            },
                            "description": "每日行程"
                        },
                        "transport": {"type": "string", "description": "交通"},
                        "accommodation": {"type": "string", "description": "住宿"},
                        "estimated_cost": {"type": "string", "description": "预估费用"}
                    },
                    "required": ["destination", "title", "days", "summary"]
                }
            },
            {
                "name": "list_all_guides",
                "description": "列出所有攻略",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_stats",
                "description": "获取数据库统计信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: dict) -> str:
        """调用MCP工具"""
        try:
            if tool_name == "search_destination":
                results = self.dm.search_by_destination(arguments["destination"])
                if not results:
                    return f"未找到关于'{arguments['destination']}'的攻略"
                return json.dumps(results, ensure_ascii=False, indent=2)
            
            elif tool_name == "search_by_tags":
                results = self.dm.search_by_tags(arguments["tags"])
                if not results:
                    return "未找到匹配的攻略"
                return json.dumps(results, ensure_ascii=False, indent=2)
            
            elif tool_name == "search_by_budget":
                results = self.dm.search_by_budget(arguments["budget"])
                if not results:
                    return "未找到匹配的攻略"
                return json.dumps(results, ensure_ascii=False, indent=2)
            
            elif tool_name == "search_by_season":
                results = self.dm.search_by_season(arguments["season"])
                if not results:
                    return "未找到匹配的攻略"
                return json.dumps(results, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_guide_detail":
                guide = self.dm.get_guide_by_id(arguments["guide_id"])
                if not guide:
                    return "攻略不存在"
                return json.dumps(guide, ensure_ascii=False, indent=2)
            
            elif tool_name == "add_guide":
                new_guide = self.dm.add_guide(arguments)
                return json.dumps({"success": True, "guide": new_guide}, ensure_ascii=False, indent=2)
            
            elif tool_name == "list_all_guides":
                guides = self.dm.get_all_guides()
                summary = [{"id": g["id"], "destination": g["destination"], "title": g["title"]} for g in guides]
                return json.dumps(summary, ensure_ascii=False, indent=2)
            
            elif tool_name == "get_stats":
                stats = self.dm.get_stats()
                return json.dumps(stats, ensure_ascii=False, indent=2)
            
            else:
                return f"未知工具: {tool_name}"
                
        except Exception as e:
            return f"工具执行出错: {str(e)}"
    
    def get_tools_manifest(self):
        """获取工具清单（用于MCP握手）"""
        return {
            "name": "travel-guide-server",
            "version": "1.0.0",
            "description": "旅游攻略智能体MCP服务",
            "tools": self.tools
        }


def run_mcp_server(host="0.0.0.0", port=9000):
    """
    启动MCP服务（HTTP模式）
    提供REST API接口供外部调用
    """
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    server = TravelMCPServer()
    
    @app.route('/mcp/manifest', methods=['GET'])
    def manifest():
        return jsonify(server.get_tools_manifest())
    
    @app.route('/mcp/call', methods=['POST'])
    def call_tool():
        data = request.get_json()
        tool_name = data.get("tool")
        arguments = data.get("arguments", {})
        
        if not tool_name:
            return jsonify({"error": "请提供tool名称"}), 400
        
        result = server.call_tool(tool_name, arguments)
        return jsonify({"result": result})
    
    @app.route('/mcp/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok", "service": "travel-guide-mcp"})
    
    print(f"🔌 MCP服务启动: http://{host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    import config
    run_mcp_server(config.MCP_HOST, config.MCP_PORT)
