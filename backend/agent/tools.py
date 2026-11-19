

from langchain_core.tools import tool
from typing import List, Dict, Optional
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.data_manager import get_data_manager


@tool
def search_destination(destination: str) -> str:
    """根据目的地搜索旅游攻略。
    
    Args:
        destination: 目的地名称，如"北京"、"成都"、"云南"等
    
    Returns:
        该目的地的完整旅游攻略信息
    """
    dm = get_data_manager()
    results = dm.search_by_destination(destination)
    if not results:
        return f"未找到关于'{destination}'的旅游攻略。您可以尝试添加该目的地的攻略。"
    
    output = []
    for guide in results:
        output.append(format_guide(guide))
    return "\n\n".join(output)


@tool
def search_by_tags(tags: str) -> str:
    """根据标签搜索旅游攻略。
    
    Args:
        tags: 标签列表，用逗号分隔，如"美食,历史文化,自然风光"
    
    Returns:
        符合标签的旅游攻略列表
    """
    dm = get_data_manager()
    tag_list = [t.strip() for t in tags.split(",")]
    results = dm.search_by_tags(tag_list)
    if not results:
        return f"未找到包含标签{tag_list}的旅游攻略。"
    
    output = []
    for guide in results:
        output.append(f"📍 {guide['title']} | 目的地: {guide['destination']} | 天数: {guide['days']}天 | 标签: {', '.join(guide.get('tags', []))}")
    return "\n".join(output)


@tool
def search_by_budget(budget: str) -> str:
    """根据预算范围搜索旅游攻略。
    
    Args:
        budget: 预算等级，如"低"、"中等"、"中高"、"较高"
    
    Returns:
        符合预算的旅游攻略列表
    """
    dm = get_data_manager()
    results = dm.search_by_budget(budget)
    if not results:
        return f"未找到预算为'{budget}'的旅游攻略。"
    
    output = []
    for guide in results:
        output.append(f"📍 {guide['title']} | 目的地: {guide['destination']} | 天数: {guide['days']}天 | 预算: {guide['budget']} | 预估费用: {guide.get('estimated_cost', '未知')}")
    return "\n".join(output)


@tool
def search_by_season(season: str) -> str:
    """根据季节搜索适合出行的旅游攻略。
    
    Args:
        season: 季节，如"春季"、"夏季"、"秋季"、"冬季"
    
    Returns:
        适合该季节出行的旅游攻略列表
    """
    dm = get_data_manager()
    results = dm.search_by_season(season)
    if not results:
        return f"未找到适合'{season}'出行的旅游攻略。"
    
    output = []
    for guide in results:
        output.append(f"📍 {guide['title']} | 目的地: {guide['destination']} | 天数: {guide['days']}天 | 适合季节: {guide['season']}")
    return "\n".join(output)


@tool
def fuzzy_search(keyword: str) -> str:
    """模糊搜索旅游攻略，可搜索目的地、标题、标签、摘要等。
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        匹配的旅游攻略列表
    """
    dm = get_data_manager()
    results = dm.fuzzy_search(keyword)
    if not results:
        return f"未找到与'{keyword}'相关的旅游攻略。"
    
    output = []
    for guide in results:
        output.append(f"📍 {guide['title']} | 目的地: {guide['destination']} | 天数: {guide['days']}天 | 摘要: {guide['summary'][:80]}...")
    return "\n".join(output)


@tool
def get_travel_guide(guide_id: int) -> str:
    """根据攻略ID获取完整的旅游攻略详情。
    
    Args:
        guide_id: 攻略的唯一ID编号
    
    Returns:
        完整的旅游攻略信息，包括每日行程、美食推荐、交通建议等
    """
    dm = get_data_manager()
    guide = dm.get_guide_by_id(guide_id)
    if not guide:
        return f"未找到ID为{guide_id}的攻略。"
    return format_guide(guide)


@tool
def list_all_guides() -> str:
    """列出所有可用的旅游攻略概览。
    
    Returns:
        所有旅游攻略的简要列表
    """
    dm = get_data_manager()
    guides = dm.get_all_guides()
    if not guides:
        return "当前没有任何旅游攻略数据。"
    
    output = ["📋 所有旅游攻略列表："]
    for guide in guides:
        output.append(f"  [{guide['id']}] {guide['title']} | {guide['destination']} | {guide['days']}天 | {guide['budget']} | 标签: {', '.join(guide.get('tags', []))}")
    return "\n".join(output)


@tool
def add_travel_guide(
    destination: str,
    title: str,
    days: int,
    summary: str,
    budget: str = "中等",
    season: str = "四季皆宜",
    tags: str = "",
    itinerary_json: str = "",
    transport: str = "",
    accommodation: str = "",
    estimated_cost: str = ""
) -> str:
    """添加一条新的旅游攻略。
    
    Args:
        destination: 目的地名称
        title: 攻略标题
        days: 建议游玩天数
        summary: 攻略摘要介绍
        budget: 预算等级(低/中等/中高/较高)
        season: 适合季节(春季/夏季/秋季/冬季/四季皆宜)
        tags: 标签，用逗号分隔
        itinerary_json: 每日行程的JSON字符串，格式为[{"day":1,"title":"xxx","details":"xxx","food":"xxx","tips":"xxx"},...]
        transport: 交通建议
        accommodation: 住宿建议
        estimated_cost: 预估费用
    """
    dm = get_data_manager()
    
    guide = {
        "destination": destination,
        "title": title,
        "days": days,
        "budget": budget,
        "season": season,
        "tags": [t.strip() for t in tags.split(",") if t.strip()] if tags else [],
        "summary": summary,
        "itinerary": json.loads(itinerary_json) if itinerary_json else [],
        "transport": transport,
        "accommodation": accommodation,
        "estimated_cost": estimated_cost
    }
    
    try:
        new_guide = dm.add_guide(guide)
        return f"✅ 成功添加攻略：{new_guide['title']}（ID: {new_guide['id']}）"
    except Exception as e:
        return f"❌ 添加攻略失败：{str(e)}"


@tool
def get_stats() -> str:
    """获取旅游攻略数据库的统计信息。
    
    Returns:
        数据库的统计信息，包括攻略总数、目的地列表、标签列表等
    """
    dm = get_data_manager()
    stats = dm.get_stats()
    return (
        f"📊 攻略数据库统计：\n"
        f"  - 攻略总数: {stats['total_guides']}\n"
        f"  - 覆盖目的地: {', '.join(stats['destinations'])}\n"
        f"  - 所有标签: {', '.join(stats['all_tags'])}"
    )


def format_guide(guide: Dict) -> str:
    """格式化输出攻略详情"""
    output = []
    output.append(f"🗺️ {guide['title']}")
    output.append(f"📍 目的地: {guide['destination']}")
    output.append(f"📅 建议天数: {guide['days']}天")
    output.append(f"💰 预算: {guide['budget']}")
    output.append(f"🌤️ 适合季节: {guide['season']}")
    output.append(f"🏷️ 标签: {', '.join(guide.get('tags', []))}")
    output.append(f"\n📝 简介: {guide['summary']}")
    
    if guide.get("itinerary"):
        output.append("\n📅 每日行程：")
        for day in guide["itinerary"]:
            output.append(f"\n  Day {day['day']}: {day['title']}")
            output.append(f"    📋 {day['details']}")
            if day.get("food"):
                output.append(f"    🍜 美食: {day['food']}")
            if day.get("tips"):
                output.append(f"    💡 贴士: {day['tips']}")
    
    if guide.get("transport"):
        output.append(f"\n🚗 交通: {guide['transport']}")
    if guide.get("accommodation"):
        output.append(f"🏨 住宿: {guide['accommodation']}")
    if guide.get("estimated_cost"):
        output.append(f"💵 预估费用: {guide['estimated_cost']}")
    
    return "\n".join(output)


# 工具列表，供Agent使用
TOOLS = [
    search_destination,
    search_by_tags,
    search_by_budget,
    search_by_season,
    fuzzy_search,
    get_travel_guide,
    list_all_guides,
    add_travel_guide,
    get_stats,
]
