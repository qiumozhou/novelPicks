#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分析数据结构 - 检查实际的分析数据格式
"""

import asyncio
import os
import sys
import json

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_analysis_structure():
    """测试分析数据结构"""
    print("=" * 60)
    print("检查分析数据结构")
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
            print(f"\n[小说] {novel.get('title', '未知标题')} (ID: {novel.get('_id', '未知ID')})")
            
            # 检查全书分析
            book_analysis = await db.get_analysis_by_level(novel['_id'], 'book')
            if book_analysis:
                print("  [全书分析] 找到数据")
                print(f"  [字段] {list(book_analysis.keys())}")
                
                if 'analysis' in book_analysis:
                    analysis = book_analysis['analysis']
                    print(f"  [分析字段] {list(analysis.keys())}")
                    
                    # 检查关键字段
                    key_fields = [
                        'main_storylines', 'total_climax_points', 'character_count',
                        'rhythm_pattern', 'protagonist_clarity', 'scene_adaptability',
                        'core_tags', 'tags', 'keywords', 'themes',
                        'avg_conflict_density', 'relationship_complexity',
                        'action_event_ratio', 'special_effects_need',
                        'emotional_resonance', 'gender_orientation', 'target_age'
                    ]
                    
                    print("  [关键字段检查]:")
                    for field in key_fields:
                        value = analysis.get(field, 'NOT_FOUND')
                        print(f"    {field}: {value}")
                else:
                    print("  [警告] 没有analysis字段")
            else:
                print("  [全书分析] 无数据")
            
            # 检查章组分析
            group_analysis = await db.get_analysis_by_level(novel['_id'], 'group')
            print(f"  [章组分析] {len(group_analysis)} 组")
            
            # 检查章节分析
            chapter_analysis = await db.get_analysis_by_level(novel['_id'], 'chapter')
            print(f"  [章节分析] {len(chapter_analysis)} 章")
            
            # 只检查第一本小说
            break
        
        await db.close_database()
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    asyncio.run(test_analysis_structure())

if __name__ == "__main__":
    main()
