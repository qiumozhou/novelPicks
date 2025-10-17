#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据清理功能
"""

import json
from data_cleaner import clean_for_frontend, clean_analysis_data, ensure_string_list

def test_basic_cleaning():
    """测试基础清理功能"""
    print("=" * 60)
    print("测试基础数据清理")
    print("=" * 60)
    
    test_data = {
        "_id": "507f1f77bcf86cd799439011",
        "title": "测试小说",
        "main_characters": [
            {"name": "张三", "role": "主角"},
            {"name": "李四", "role": "配角"},
            "王五"
        ],
        "themes": ["爱情", "冒险"],
        "word_count": 12345,
        "created_at": "2024-01-01T10:00:00Z"
    }
    
    print("原始数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    
    cleaned = clean_for_frontend(test_data)
    print("\n清理后数据:")
    print(json.dumps(cleaned, ensure_ascii=False, indent=2))
    
    return cleaned

def test_analysis_cleaning():
    """测试分析数据清理"""
    print("\n" + "=" * 60)
    print("测试分析数据清理")
    print("=" * 60)
    
    analysis_data = {
        "summary": "这是一个关于爱情的故事",
        "main_characters": [
            {"name": "张三", "role": "主角", "description": "勇敢的年轻人"},
            {"name": "李四", "role": "女主角", "description": "美丽的女孩"},
            {"name": "王五", "role": "反派", "description": "邪恶的巫师"}
        ],
        "themes": ["爱情", "冒险", {"name": "成长", "description": "主角的成长历程"}],
        "word_count": "12345",
        "meta": {
            "_id": "507f1f77bcf86cd799439012",
            "created_at": "2024-01-01T10:00:00Z"
        }
    }
    
    print("原始分析数据:")
    print(json.dumps(analysis_data, ensure_ascii=False, indent=2))
    
    cleaned = clean_analysis_data(analysis_data)
    print("\n清理后分析数据:")
    print(json.dumps(cleaned, ensure_ascii=False, indent=2))
    
    return cleaned

def test_string_list():
    """测试字符串列表处理"""
    print("\n" + "=" * 60)
    print("测试字符串列表处理")
    print("=" * 60)
    
    test_cases = [
        ["张三", "李四", "王五"],
        [{"name": "张三"}, {"name": "李四"}, "王五"],
        [{"title": "张三", "role": "主角"}, {"title": "李四", "role": "配角"}],
        "单个字符串",
        None,
        []
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n测试用例 {i+1}: {case}")
        result = ensure_string_list(case)
        print(f"结果: {result}")

def main():
    """主测试函数"""
    print("开始数据清理测试...")
    
    # 基础清理测试
    basic_result = test_basic_cleaning()
    
    # 分析数据清理测试
    analysis_result = test_analysis_cleaning()
    
    # 字符串列表测试
    test_string_list()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
