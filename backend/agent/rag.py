

import os
import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from data.data_manager import get_data_manager
import config


class TravelRAG:
    """旅游攻略RAG检索系统"""
    
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self._init_embeddings()
        self._init_vectorstore()
    
    def _init_embeddings(self):
        """初始化Embedding模型"""
        self.embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            openai_api_key=config.EMBEDDING_API_KEY,
            openai_api_base=config.EMBEDDING_BASE_URL,
        )
    
    def _init_vectorstore(self):
        """初始化向量数据库"""
        persist_dir = config.CHROMA_PERSIST_DIR
        
        # 检查是否已有数据
        if os.path.exists(persist_dir) and os.listdir(persist_dir):
            self.vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
                collection_name=config.COLLECTION_NAME,
            )
        else:
            # 首次运行，构建向量库
            self._build_vectorstore()
        
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
        )
    
    def _build_vectorstore(self):
        """从JSON数据构建向量数据库"""
        dm = get_data_manager()
        guides = dm.get_all_guides()
        
        documents = []
        for guide in guides:
            # 将每个攻略转换为文档
            doc_text = self._guide_to_text(guide)
            doc = Document(
                page_content=doc_text,
                metadata={
                    "id": guide["id"],
                    "destination": guide["destination"],
                    "title": guide["title"],
                    "days": guide["days"],
                    "budget": guide["budget"],
                    "tags": ",".join(guide.get("tags", [])),
                }
            )
            documents.append(doc)
        
        # 文本分割
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", "；", "，", " "],
        )
        split_docs = splitter.split_documents(documents)
        
        # 创建向量库
        self.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory=config.CHROMA_PERSIST_DIR,
            collection_name=config.COLLECTION_NAME,
        )
    
    def _guide_to_text(self, guide: Dict) -> str:
        """将攻略转换为可检索的文本"""
        parts = [
            f"目的地: {guide['destination']}",
            f"标题: {guide['title']}",
            f"天数: {guide['days']}天",
            f"预算: {guide['budget']}",
            f"季节: {guide['season']}",
            f"标签: {', '.join(guide.get('tags', []))}",
            f"简介: {guide['summary']}",
        ]
        
        for day in guide.get("itinerary", []):
            parts.append(f"Day{day['day']} {day['title']}: {day['details']}")
            if day.get("food"):
                parts.append(f"美食推荐: {day['food']}")
            if day.get("tips"):
                parts.append(f"贴士: {day['tips']}")
        
        if guide.get("transport"):
            parts.append(f"交通: {guide['transport']}")
        if guide.get("accommodation"):
            parts.append(f"住宿: {guide['accommodation']}")
        if guide.get("estimated_cost"):
            parts.append(f"费用: {guide['estimated_cost']}")
        
        return "\n".join(parts)
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        """语义检索"""
        if not self.retriever:
            return []
        
        docs = self.retriever.invoke(query)
        results = []
        for doc in docs[:k]:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
            })
        return results
    
    def add_document(self, guide: Dict):
        """添加新文档到向量库"""
        doc_text = self._guide_to_text(guide)
        doc = Document(
            page_content=doc_text,
            metadata={
                "id": guide["id"],
                "destination": guide["destination"],
                "title": guide["title"],
            }
        )
        self.vectorstore.add_documents([doc])


# 单例
_rag_instance = None

def get_rag() -> TravelRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = TravelRAG()
    return _rag_instance
