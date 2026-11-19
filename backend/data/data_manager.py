"""
旅游攻略数据管理模块
负责加载、查询、添加旅游攻略数据
支持JSON文件存储和ChromaDB向量检索
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path

DATA_DIR = Path(__file__).parent
DATA_FILE = DATA_DIR / "travel_data.json"


class TravelDataManager:
    """旅游攻略数据管理器"""

    def __init__(self, data_file: str = None):
        self.data_file = Path(data_file) if data_file else DATA_FILE
        self.guides: List[Dict] = []
        self._load_data()

    def _load_data(self):
        """从JSON文件加载攻略数据"""
        if self.data_file.exists():
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.guides = json.load(f)
        else:
            self.guides = []

    def _save_data(self):
        """保存攻略数据到JSON文件"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.guides, f, ensure_ascii=False, indent=2)

    def get_all_guides(self) -> List[Dict]:
        """获取所有攻略"""
        return self.guides

    def get_guide_by_id(self, guide_id: int) -> Optional[Dict]:
        """根据ID获取攻略"""
        for guide in self.guides:
            if guide["id"] == guide_id:
                return guide
        return None

    def search_by_destination(self, destination: str) -> List[Dict]:
        """根据目的地搜索攻略"""
        results = []
        for guide in self.guides:
            if destination.lower() in guide["destination"].lower() or \
               destination.lower() in guide["title"].lower():
                results.append(guide)
        return results

    def search_by_tags(self, tags: List[str]) -> List[Dict]:
        """根据标签搜索攻略"""
        results = []
        for guide in self.guides:
            guide_tags = [t.lower() for t in guide.get("tags", [])]
            if any(tag.lower() in guide_tags for tag in tags):
                results.append(guide)
        return results

    def search_by_budget(self, budget: str) -> List[Dict]:
        """根据预算搜索攻略"""
        results = []
        for guide in self.guides:
            if budget.lower() in guide.get("budget", "").lower():
                results.append(guide)
        return results

    def search_by_season(self, season: str) -> List[Dict]:
        """根据季节搜索攻略"""
        results = []
        for guide in self.guides:
            if season.lower() in guide.get("season", "").lower() or \
               "四季皆宜" in guide.get("season", ""):
                results.append(guide)
        return results

    def fuzzy_search(self, keyword: str) -> List[Dict]:
        """模糊搜索攻略"""
        results = []
        keyword = keyword.lower()
        for guide in self.guides:
            # 搜索目的地、标题、摘要、标签
            searchable = " ".join([
                guide.get("destination", ""),
                guide.get("title", ""),
                guide.get("summary", ""),
                " ".join(guide.get("tags", []))
            ]).lower()
            if keyword in searchable:
                results.append(guide)
        return results

    def add_guide(self, guide: Dict) -> Dict:
        """添加新攻略"""
        # 自动生成ID
        if self.guides:
            max_id = max(g["id"] for g in self.guides)
            guide["id"] = max_id + 1
        else:
            guide["id"] = 1

        # 验证必要字段
        required_fields = ["destination", "title", "days", "summary", "itinerary"]
        for field in required_fields:
            if field not in guide:
                raise ValueError(f"缺少必要字段: {field}")

        # 设置默认值
        guide.setdefault("budget", "中等")
        guide.setdefault("season", "四季皆宜")
        guide.setdefault("tags", [])
        guide.setdefault("transport", "")
        guide.setdefault("accommodation", "")
        guide.setdefault("estimated_cost", "")

        self.guides.append(guide)
        self._save_data()
        return guide

    def get_all_destinations(self) -> List[str]:
        """获取所有目的地"""
        return list(set(g["destination"] for g in self.guides))

    def get_stats(self) -> Dict:
        """获取数据统计信息"""
        return {
            "total_guides": len(self.guides),
            "destinations": self.get_all_destinations(),
            "all_tags": list(set(tag for g in self.guides for tag in g.get("tags", [])))
        }


# 单例实例
_data_manager = None

def get_data_manager() -> TravelDataManager:
    """获取数据管理器单例"""
    global _data_manager
    if _data_manager is None:
        _data_manager = TravelDataManager()
    return _data_manager
