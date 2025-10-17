#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分析功能 - 直接运行分析任务
"""

import asyncio
import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from novel_analyzer import NovelAnalyzer

async def test_analysis():
    """测试分析功能"""
    print("🧪 开始测试分析功能...")
    print("=" * 60)
    
    # 初始化数据库和分析器
    db = Database()
    analyzer = NovelAnalyzer(db)
    
    # 初始化数据库连接
    await db.init_database()
    
    if db.client is None:
        print("❌ 数据库未连接，无法进行测试")
        return
    
    print("✅ 数据库连接成功")
    
    # 检查uploads目录
    if not os.path.exists("uploads"):
        print("❌ uploads目录不存在")
        return
    
    # 查找测试文件
    test_files = []
    for file in os.listdir("uploads"):
        if file.endswith('.txt'):
            test_files.append(file)
    
    if not test_files:
        print("❌ 没有找到测试文件，请先上传一个.txt文件到uploads目录")
        return
    
    # 使用第一个找到的文件
    test_file = test_files[0]
    file_path = f"uploads/{test_file}"
    novel_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print(f"📁 测试文件: {test_file}")
    print(f"📚 测试ID: {novel_id}")
    print(f"📊 文件大小: {os.path.getsize(file_path):,} 字节")
    print("=" * 60)
    
    try:
        # 直接运行分析
        await analyzer.analyze_novel_async(novel_id, file_path)
        print("\n🎉 测试分析完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        await db.close_database()

if __name__ == "__main__":
    asyncio.run(test_analysis())
