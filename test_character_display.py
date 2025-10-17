#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试人物显示修复
"""

def test_character_formatting():
    """测试人物数据格式化"""
    print("=" * 60)
    print("测试人物数据格式化")
    print("=" * 60)
    
    # 模拟不同格式的人物数据
    test_cases = [
        # 字符串数组
        ["张三", "李四", "王五"],
        
        # 对象数组
        [
            {"name": "张三", "role": "主角"},
            {"name": "李四", "role": "配角"},
            {"name": "王五", "role": "反派"}
        ],
        
        # 混合格式
        [
            "张三",
            {"name": "李四", "role": "配角"},
            "王五"
        ],
        
        # 单个字符串
        "张三",
        
        # 单个对象
        {"name": "张三", "role": "主角"},
        
        # 空数据
        None,
        [],
        ""
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n测试用例 {i+1}: {case}")
        
        # 模拟JavaScript的formatCharacters函数逻辑
        if case is None or case === "":
            result = "N/A"
        elif isinstance(case, str):
            result = case
        elif isinstance(case, list):
            formatted_chars = []
            for char in case:
                if isinstance(char, str):
                    formatted_chars.append(char)
                elif isinstance(char, dict):
                    name = char.get('name') or char.get('character') or char.get('title')
                    if name:
                        formatted_chars.append(name)
                    else:
                        formatted_chars.append(str(char))
                else:
                    formatted_chars.append(str(char))
            result = ", ".join(formatted_chars)
        else:
            result = str(case)
        
        print(f"格式化结果: {result}")

def main():
    """主函数"""
    test_character_formatting()
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
