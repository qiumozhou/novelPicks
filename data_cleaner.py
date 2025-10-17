#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清理工具 - 处理MongoDB数据序列化问题
"""

import json
from typing import Any, Dict, List, Union
from datetime import datetime

def clean_for_frontend(data: Any) -> Any:
    """
    清理数据，确保前端可以正确显示
    处理ObjectId、datetime、复杂对象等
    """
    if data is None:
        return None
    
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # 跳过MongoDB内部字段
            if key.startswith('_') and key != '_id':
                continue
                
            cleaned_key = clean_key(key)
            cleaned_value = clean_for_frontend(value)
            cleaned[cleaned_key] = cleaned_value
        return cleaned
    
    elif isinstance(data, list):
        return [clean_for_frontend(item) for item in data]
    
    elif isinstance(data, datetime):
        return data.isoformat()
    
    elif hasattr(data, '__dict__'):
        # 处理有__dict__属性的对象
        try:
            return clean_for_frontend(data.__dict__)
        except:
            return str(data)
    
    elif hasattr(data, '__str__') and not isinstance(data, (str, int, float, bool)):
        # 转换其他对象为字符串
        return str(data)
    
    else:
        return data

def clean_key(key: str) -> str:
    """清理键名，确保前端友好"""
    # 移除MongoDB特殊字符
    if key.startswith('_'):
        return key[1:] if len(key) > 1 else key
    return key

def ensure_string_list(data: Any) -> List[str]:
    """确保返回字符串列表，处理[object Object]问题"""
    if isinstance(data, list):
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                # 如果是字典，尝试提取有用信息
                if 'name' in item:
                    result.append(str(item['name']))
                elif 'title' in item:
                    result.append(str(item['title']))
                elif 'character' in item:
                    result.append(str(item['character']))
                else:
                    result.append(str(item))
            else:
                result.append(str(item))
        return result
    elif isinstance(data, str):
        return [data]
    else:
        return [str(data)]

def clean_analysis_data(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """专门清理分析数据"""
    if not analysis_data:
        return {}
    
    cleaned = {}
    
    # 处理主要人物列表
    if 'main_characters' in analysis_data:
        characters = analysis_data['main_characters']
        if isinstance(characters, list):
            cleaned['main_characters'] = ensure_string_list(characters)
        else:
            cleaned['main_characters'] = [str(characters)]
    
    # 处理其他列表字段
    list_fields = ['themes', 'genres', 'keywords', 'locations', 'events']
    for field in list_fields:
        if field in analysis_data:
            cleaned[field] = ensure_string_list(analysis_data[field])
    
    # 处理字符串字段
    string_fields = ['summary', 'analysis', 'title', 'author', 'genre']
    for field in string_fields:
        if field in analysis_data:
            cleaned[field] = str(analysis_data[field])
    
    # 处理数字字段
    number_fields = ['word_count', 'chapter_count', 'rating', 'score']
    for field in number_fields:
        if field in analysis_data:
            value = analysis_data[field]
            if isinstance(value, (int, float)):
                cleaned[field] = value
            elif isinstance(value, str):
                try:
                    cleaned[field] = float(value)
                except:
                    cleaned[field] = 0
            else:
                cleaned[field] = 0
    
    # 处理嵌套对象
    if 'meta' in analysis_data:
        meta = analysis_data['meta']
        if isinstance(meta, dict):
            cleaned['meta'] = clean_for_frontend(meta)
        else:
            cleaned['meta'] = {}
    
    return cleaned

def test_cleaning():
    """测试数据清理功能"""
    test_data = {
        "main_characters": [
            {"name": "张三", "role": "主角"},
            {"name": "李四", "role": "配角"},
            "王五",
            {"title": "赵六", "description": "反派"}
        ],
        "themes": ["爱情", "冒险", {"name": "成长"}],
        "summary": "这是一个故事",
        "word_count": "12345",
        "meta": {
            "_id": "some_object_id",
            "created_at": datetime.now()
        }
    }
    
    print("原始数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2, default=str))
    
    cleaned = clean_analysis_data(test_data)
    print("\n清理后数据:")
    print(json.dumps(cleaned, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_cleaning()
