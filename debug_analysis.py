#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试分析数据 - 直接检查数据库中的实际数据
"""

import asyncio
import os
import sys
import json

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_analysis_data():
    """调试分析数据"""
    print("=" * 60)
    print("调试分析数据")
    print("=" * 60)
    
    try:
        from database import Database
        
        # 初始化数据库
        db = Database()
        await db.init_database()
        
        if db.client is None:
            print("[ERROR] 数据库未连接")
            return
        
        # 获取所有小说
        novels = await db.get_all_novels()
        print(f"[INFO] 找到 {len(novels)} 本小说")
        
        for novel in novels:
            novel_id = novel.get('_id')
            novel_title = novel.get('title', '未知标题')
            
            print(f"\n[小说] {novel_title} (ID: {novel_id})")
            print(f"[状态] {novel.get('status', '未知')}")
            
            # 检查全书分析
            book_analysis = await db.get_analysis_by_level(novel_id, 'book')
            if book_analysis:
                print("\n[全书分析数据]:")
                print(json.dumps(book_analysis, ensure_ascii=False, indent=2))
                
                # 检查是否有analysis字段
                if 'analysis' in book_analysis:
                    analysis = book_analysis['analysis']
                    print(f"\n[analysis字段内容]:")
                    print(json.dumps(analysis, ensure_ascii=False, indent=2))
                else:
                    print("\n[警告] 没有analysis字段，直接使用book_analysis")
            else:
                print("[全书分析] 无数据")
            
            # 只检查第一本小说
            break
        
        await db.close_database()
        
    except Exception as e:
        print(f"[ERROR] 调试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    asyncio.run(debug_analysis_data())

if __name__ == "__main__":
    main()
