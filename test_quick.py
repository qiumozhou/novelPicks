#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证系统是否正常工作
"""

import asyncio
import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_basic():
    """基础测试"""
    print("=" * 60)
    print("快速测试 - 验证系统基础功能")
    print("=" * 60)
    
    try:
        # 测试数据库连接
        from database import Database
        db = Database()
        await db.init_database()
        
        if db.client is None:
            print("[ERROR] 数据库连接失败")
            return False
        
        print("[SUCCESS] 数据库连接成功")
        
        # 测试分析器初始化
        from novel_analyzer import NovelAnalyzer
        analyzer = NovelAnalyzer(db)
        print("[SUCCESS] 分析器初始化成功")
        
        # 检查uploads目录
        if not os.path.exists("uploads"):
            os.makedirs("uploads", exist_ok=True)
            print("[INFO] 创建uploads目录")
        
        # 查找测试文件
        test_files = [f for f in os.listdir("uploads") if f.endswith('.txt')]
        if test_files:
            print(f"[INFO] 找到测试文件: {test_files[0]}")
        else:
            print("[WARNING] 没有找到测试文件")
        
        await db.close_database()
        print("[SUCCESS] 基础测试通过")
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_upload_simulation():
    """模拟上传测试"""
    print("\n" + "=" * 60)
    print("模拟上传测试")
    print("=" * 60)
    
    try:
        from database import Database
        from novel_analyzer import NovelAnalyzer
        
        db = Database()
        await db.init_database()
        
        if db.client is None:
            print("[ERROR] 数据库未连接，跳过上传测试")
            return False
        
        # 模拟创建小说记录
        novel_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        novel_info = {
            "_id": novel_id,
            "title": "测试小说",
            "file_path": "uploads/test.txt",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "word_count": 1000
        }
        
        print(f"[INFO] 创建测试小说记录: {novel_id}")
        await db.create_novel(novel_info)
        print("[SUCCESS] 小说记录创建成功")
        
        # 更新状态
        await db.update_novel_status(novel_id, "processing")
        print("[SUCCESS] 状态更新成功")
        
        await db.close_database()
        print("[SUCCESS] 上传模拟测试通过")
        return True
        
    except Exception as e:
        print(f"[ERROR] 上传测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始快速测试...")
    
    # 运行基础测试
    result1 = asyncio.run(test_basic())
    
    # 运行上传测试
    result2 = asyncio.run(test_upload_simulation())
    
    print("\n" + "=" * 60)
    if result1 and result2:
        print("[SUCCESS] 所有测试通过！系统可以正常使用")
        print("[INFO] 现在可以启动服务器: python simple_start.py")
    else:
        print("[ERROR] 部分测试失败，请检查配置")
    print("=" * 60)

if __name__ == "__main__":
    main()
