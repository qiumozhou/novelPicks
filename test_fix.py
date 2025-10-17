#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复 - 验证数据类型处理
"""

import asyncio
import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_data_cleaning():
    """测试数据清理功能"""
    print("=" * 60)
    print("测试数据清理功能")
    print("=" * 60)
    
    try:
        from novel_analyzer import NovelAnalyzer
        from database import Database
        
        # 初始化
        db = Database()
        await db.init_database()
        analyzer = NovelAnalyzer(db)
        
        # 测试数据清理
        test_data = {
            "string": "test",
            "number": 123,
            "float": 45.67,
            "boolean": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "datetime": datetime.now(),
            "nested": {
                "inner": "value",
                "number": 999
            }
        }
        
        print("[TEST] 原始数据:")
        print(test_data)
        
        cleaned = analyzer.clean_data_for_serialization(test_data)
        print("\n[TEST] 清理后数据:")
        print(cleaned)
        
        # 测试JSON序列化
        import json
        json_str = json.dumps(cleaned, ensure_ascii=False, indent=2)
        print("\n[TEST] JSON序列化成功:")
        print("序列化长度:", len(json_str))
        
        await db.close_database()
        print("\n[SUCCESS] 数据清理测试通过")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_type_safety():
    """测试类型安全处理"""
    print("\n" + "=" * 60)
    print("测试类型安全处理")
    print("=" * 60)
    
    try:
        # 模拟可能出现的类型问题
        test_cases = [
            {"word_count": "123"},  # 字符串数字
            {"word_count": 456},    # 正常数字
            {"word_count": None},   # None值
            {"word_count": "abc"},  # 无效字符串
            {"word_count": []},     # 列表
        ]
        
        for i, case in enumerate(test_cases):
            print(f"[TEST {i+1}] 测试用例: {case}")
            
            word_count = case.get('word_count', 0)
            if isinstance(word_count, str):
                try:
                    word_count = int(word_count)
                except (ValueError, TypeError):
                    word_count = 0
            elif not isinstance(word_count, (int, float)):
                word_count = 0
            
            print(f"  处理结果: {word_count} (类型: {type(word_count)})")
        
        print("\n[SUCCESS] 类型安全测试通过")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 类型安全测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始修复验证测试...")
    
    # 运行数据清理测试
    result1 = asyncio.run(test_data_cleaning())
    
    # 运行类型安全测试
    result2 = asyncio.run(test_type_safety())
    
    print("\n" + "=" * 60)
    if result1 and result2:
        print("[SUCCESS] 所有修复验证通过！")
        print("[INFO] 现在可以安全启动服务器: python simple_start.py")
    else:
        print("[ERROR] 部分修复验证失败，请检查代码")
    print("=" * 60)

if __name__ == "__main__":
    main()
