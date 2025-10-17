#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB数据库连接和操作
"""

import motor.motor_asyncio
from pymongo import DESCENDING
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

class Database:
    """MongoDB数据库操作类"""
    
    def __init__(self):
        # MongoDB连接配置 - 无认证直连模式
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database_name = "novel_analysis"
        
        # 集合名称
        self.novels_collection = "novels"
        self.chapter_analysis_collection = "chapter_analysis" 
        self.group_analysis_collection = "group_analysis"
        self.book_analysis_collection = "book_analysis"
        
        self.client = None
        self.db = None
    
    async def init_database(self):
        """初始化数据库连接"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client[self.database_name]
            
            # 测试连接
            await self.client.admin.command('ping')
            print("MongoDB连接成功")
            
            # 创建索引
            await self._create_indexes()
            
        except Exception as e:
            print(f"MongoDB连接失败: {e}")
            print("提示: 系统将在无数据库模式下运行，功能受限")
            print("请参考 config_guide.md 配置MongoDB数据库")
            self.client = None
            self.db = None
    
    async def close_database(self):
        """关闭数据库连接"""
        if self.client is not None:
            self.client.close()
    
    async def _create_indexes(self):
        """创建数据库索引"""
        try:
            # 小说集合索引
            await self.db[self.novels_collection].create_index("title")
            await self.db[self.novels_collection].create_index("created_at")
            
            # 分析结果索引
            for collection in [self.chapter_analysis_collection, 
                             self.group_analysis_collection, 
                             self.book_analysis_collection]:
                await self.db[collection].create_index("novel_id")
                await self.db[collection].create_index("created_at")
            
            print("数据库索引创建完成")
        except Exception as e:
            print(f"创建索引失败: {e}")
    
    # 小说相关操作
    async def create_novel(self, novel_info: Dict[str, Any]) -> str:
        """创建小说记录"""
        if self.db is None:
            print("数据库未连接，无法保存小说记录")
            return novel_info.get('_id', 'temp-id')
        
        try:
            result = await self.db[self.novels_collection].insert_one(novel_info)
            return str(result.inserted_id)
        except Exception as e:
            print(f"创建小说记录失败: {e}")
            raise
    
    async def get_novel_by_id(self, novel_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取小说信息"""
        if self.db is None:
            return None
        
        try:
            novel = await self.db[self.novels_collection].find_one({"_id": novel_id})
            return self.clean_mongodb_data(novel) if novel else None
        except Exception as e:
            print(f"获取小说信息失败: {e}")
            return None
    
    async def get_all_novels(self) -> List[Dict[str, Any]]:
        """获取所有小说列表"""
        if self.db is None:
            return []
        
        try:
            cursor = self.db[self.novels_collection].find().sort("created_at", DESCENDING)
            novels = await cursor.to_list(length=None)
            return [self.clean_mongodb_data(novel) for novel in novels]
        except Exception as e:
            print(f"获取小说列表失败: {e}")
            return []
    
    async def update_novel_status(self, novel_id: str, status: str) -> bool:
        """更新小说状态"""
        if self.db is None:
            print(f"数据库未连接，无法更新小说状态: {novel_id} -> {status}")
            return False
        
        try:
            result = await self.db[self.novels_collection].update_one(
                {"_id": novel_id},
                {"$set": {"status": status, "updated_at": datetime.now().isoformat()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"更新小说状态失败: {e}")
            return False
    
    async def delete_novel_and_analysis(self, novel_id: str) -> bool:
        """删除小说及其所有分析结果"""
        try:
            # 删除小说记录
            novel_result = await self.db[self.novels_collection].delete_one({"_id": novel_id})
            
            # 删除所有分析结果
            await self.db[self.chapter_analysis_collection].delete_many({"novel_id": novel_id})
            await self.db[self.group_analysis_collection].delete_many({"novel_id": novel_id})
            await self.db[self.book_analysis_collection].delete_many({"novel_id": novel_id})
            
            return novel_result.deleted_count > 0
        except Exception as e:
            print(f"删除小说失败: {e}")
            return False
    
    # 分析结果相关操作
    async def save_chapter_analysis(self, novel_id: str, analysis_data: List[Dict[str, Any]]) -> bool:
        """保存章节级分析结果"""
        if self.db is None:
            print(f"❌ 数据库未连接，无法保存章节分析结果: {len(analysis_data)}条")
            return False
        
        try:
            # 为每个分析结果添加novel_id和创建时间
            for item in analysis_data:
                item["novel_id"] = novel_id
                item["created_at"] = datetime.now().isoformat()
            
            result = await self.db[self.chapter_analysis_collection].insert_many(analysis_data)
            print(f"[SUCCESS] 章节分析结果已保存: {len(result.inserted_ids)} 条记录")
            return len(result.inserted_ids) > 0
        except Exception as e:
            print(f"❌ 保存章节分析失败: {e}")
            return False
    
    async def save_group_analysis(self, novel_id: str, analysis_data: List[Dict[str, Any]]) -> bool:
        """保存中层汇总分析结果"""
        if self.db is None:
            print(f"❌ 数据库未连接，无法保存中层分析结果: {len(analysis_data)}条")
            return False
        
        try:
            for item in analysis_data:
                item["novel_id"] = novel_id
                item["created_at"] = datetime.now().isoformat()
            
            result = await self.db[self.group_analysis_collection].insert_many(analysis_data)
            print(f"✅ 中层分析结果已保存: {len(result.inserted_ids)} 条记录")
            return len(result.inserted_ids) > 0
        except Exception as e:
            print(f"❌ 保存中层分析失败: {e}")
            return False
    
    async def save_book_analysis(self, novel_id: str, analysis_data: Dict[str, Any]) -> bool:
        """保存全书级分析结果"""
        if self.db is None:
            print(f"❌ 数据库未连接，无法保存全书分析结果")
            return False
        
        try:
            analysis_data["novel_id"] = novel_id
            analysis_data["created_at"] = datetime.now().isoformat()
            
            result = await self.db[self.book_analysis_collection].insert_one(analysis_data)
            print(f"✅ 全书分析结果已保存: {result.inserted_id}")
            return result.inserted_id is not None
        except Exception as e:
            print(f"❌ 保存全书分析失败: {e}")
            return False
    
    def clean_mongodb_data(self, data):
        """清理MongoDB数据，转换ObjectId等不可序列化对象"""
        if data is None:
            return None
        
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                if key == "_id" and hasattr(value, '__str__'):
                    # 保留_id字段，转换为字符串
                    cleaned[key] = str(value)
                elif isinstance(value, dict):
                    cleaned[key] = self.clean_mongodb_data(value)
                elif isinstance(value, list):
                    cleaned[key] = [self.clean_mongodb_data(item) for item in value]
                elif hasattr(value, '__str__') and not isinstance(value, (str, int, float, bool, type(None))):
                    cleaned[key] = str(value)
                else:
                    cleaned[key] = value
            return cleaned
        elif isinstance(data, list):
            return [self.clean_mongodb_data(item) for item in data]
        elif hasattr(data, '__str__') and not isinstance(data, (str, int, float, bool, type(None))):
            return str(data)
        else:
            return data
    
    async def get_analysis_by_level(self, novel_id: str, level: str) -> List[Dict[str, Any]]:
        """根据层级获取分析结果"""
        if self.db is None:
            return [] if level != "book" else None
        
        try:
            collection_map = {
                "chapter": self.chapter_analysis_collection,
                "group": self.group_analysis_collection,
                "book": self.book_analysis_collection
            }
            
            collection_name = collection_map.get(level)
            if not collection_name:
                return []
            
            if level == "book":
                # 全书分析只有一个结果
                result = await self.db[collection_name].find_one({"novel_id": novel_id})
                return self.clean_mongodb_data(result) if result else None
            else:
                # 章节和中层分析有多个结果
                cursor = self.db[collection_name].find({"novel_id": novel_id})
                results = await cursor.to_list(length=None)
                return [self.clean_mongodb_data(result) for result in results]
                
        except Exception as e:
            print(f"获取分析结果失败: {e}")
            return []
    
    async def get_novel_statistics(self, novel_id: str) -> Dict[str, Any]:
        """获取小说分析统计信息"""
        try:
            stats = {
                "chapter_count": await self.db[self.chapter_analysis_collection].count_documents({"novel_id": novel_id}),
                "group_count": await self.db[self.group_analysis_collection].count_documents({"novel_id": novel_id}),
                "book_count": await self.db[self.book_analysis_collection].count_documents({"novel_id": novel_id})
            }
            return self.clean_mongodb_data(stats)
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {"chapter_count": 0, "group_count": 0, "book_count": 0}
