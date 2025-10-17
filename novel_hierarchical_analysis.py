#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说结构化分析分层总结工具 - 适用于长篇小说500万字级
"""

import os
import json
import time
import re
import uuid
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, Any, Optional, List

class NovelHierarchicalAnalyzer:
    """小说分层结构化分析工具"""
    
    def __init__(self):
        self.model_config = {
            "base_url": "http://10.60.36.76:3100/v1",
            "api_key": "sk-d8rhT8SRFuXbTL5l304c83D58bA44488A2094807Da2cEcBe",
            "model_name": "gpt-5-chat",
            "timeout": 120,
            "max_retries": 3
        }
        
        # Step 1: 章节级总结提示词
        self.chapter_summary_prompt = """你是一个小说内容结构分析专家。请阅读以下小说内容片段，提取并总结以下信息：

1. 故事情节概要（500-800字）
2. 主要人物（含性格、关系、动机）
3. 关键事件与冲突
4. 情绪与氛围变化
5. 节奏与叙事结构
6. 场景类型与呈现性（是否具备影视化潜力）
7. 标签提取（主题、情感、题材、世界观、时代背景、元素）
8. 关键反转或高潮点

请输出为JSON结构，包含以下字段：
- segment_id: 段落ID
- summary: 故事情节概要
- main_characters: 主要人物列表
- conflicts: 冲突列表
- emotional_flow: 情绪氛围变化
- tags: 标签列表
- plot_points: 关键情节点
- analysis: 分析指标
- meta: 元数据
- content_refs: 内容引用（空数组）

小说内容片段：
"""

        # Step 2: 中层汇总提示词
        self.group_summary_prompt = """你是一个小说结构与叙事分析专家。以下是小说的多个片段总结，请基于这些信息提炼更高层次的叙事逻辑和指标：

请总结：
1. 主线数量与支线特征
2. 冲突密度（每万字冲突数估计）
3. 高潮与反转点数量与分布
4. 节奏变化趋势（平稳 / 加速 / 震荡）
5. 主要人物成长或关系演变
6. 故事张力与叙事驱动力来源
7. 场景类型分布（内景/外景、战斗/情感/对话）
8. 标签集中度（核心主题是否聚焦）

请输出JSON格式，包含以下字段：
- group_id: 组ID
- summary: 该组章节的整体叙事发展
- analysis: 分析指标
- meta: 元数据
- content_refs: 内容引用

章节片段总结数据：
"""

        # Step 3: 全书级整合提示词
        self.book_summary_prompt = """你是一个小说全局内容评估专家。请综合所有中层总结信息，完成全书分析，输出全面指标。

请从以下角度提炼：
1. 主线数量
2. 冲突密度
3. 高潮/反转点数量
4. 节奏类型（平稳/起伏/快节奏/慢热）
5. 人物数量与主角鲜明度
6. 人物关系情绪度
7. 场景可呈现性（影视化程度）
8. 动作/事件比例
9. 特效需求
10. 剧情张力
11. 情绪共鸣度
12. 性别倾向
13. 年龄段
14. 标签数量、核心标签、标签集中度
15. 兴趣匹配（受众偏好）

输出为标准化JSON：

```json
{
  "book_summary": "全书讲述了...",
  "analysis": {
    "main_storylines": 3,
    "avg_conflict_density": 0.017,
    "total_climax_points": 21,
    "rhythm_pattern": "中快节奏",
    "character_count": 15,
    "protagonist_clarity": "强",
    "relationship_complexity": "复杂",
    "scene_adaptability": "高",
    "action_event_ratio": "7:3",
    "special_effects_need": "中",
    "plot_tension": "强",
    "emotional_resonance": "高",
    "gender_orientation": "男性向",
    "target_age": "16-25",
    "tag_count": 8,
    "core_tags": ["玄幻", "成长", "复仇"],
    "tag_concentration": "集中",
    "interest_matching": "高"
  },
  "meta": {
    "source_id": "uuid-BOOK",
    "parent_id": {parent_ids},
    "level": "book",
    "position": {"start_chapter": 1, "end_chapter": {total_chapters}},
    "word_count": {total_words},
    "genre": {all_genres},
    "version": "v1.0",
    "timestamp": "{timestamp}"
  },
  "content_refs": {content_refs}
}
```

中层汇总数据：
"""
    
    def read_novel(self, file_path: str) -> str:
        """读取小说文件"""
        encodings = ['gbk', 'gb2312', 'utf-8', 'utf-8-sig', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"成功读取文件: {file_path} (编码: {encoding})")
                print(f"文件大小: {len(content)} 字符")
                return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"读取文件失败 ({encoding}): {e}")
                continue
        
        print("所有编码尝试均失败")
        return ""
    
    def split_into_segments(self, content: str, segment_size: int = 50000) -> List[Dict[str, Any]]:
        """将小说内容按段落拆分（每段约5万字）"""
        print(f"正在按 {segment_size} 字符拆分小说...")
        
        segments = []
        for i in range(0, len(content), segment_size):
            segment_content = content[i:i + segment_size]
            segments.append({
                'segment_number': len(segments) + 1,
                'content': segment_content,
                'start_pos': i,
                'end_pos': min(i + segment_size, len(content)),
                'word_count': len(segment_content)
            })
        
        print(f"共分割为 {len(segments)} 个段落")
        return segments
    
    def call_llm(self, prompt: str, max_tokens: int = 6000) -> Optional[str]:
        """调用大模型API"""
        headers = {
            "Authorization": f"Bearer {self.model_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_config["model_name"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        
        for attempt in range(self.model_config["max_retries"]):
            try:
                print(f"正在调用模型 (尝试 {attempt + 1}/{self.model_config['max_retries']})...")
                response = requests.post(
                    f"{self.model_config['base_url']}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=self.model_config["timeout"]
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        print("模型调用成功!")
                        return content
                    else:
                        print(f"模型响应格式错误: {result}")
                else:
                    print(f"API请求失败: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1}/{self.model_config['max_retries']})")
            except Exception as e:
                print(f"请求失败: {e}")
            
            if attempt < self.model_config["max_retries"] - 1:
                wait_time = (attempt + 1) * 3
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        print("所有重试均失败")
        return None
    
    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """从模型响应中提取JSON"""
        try:
            # 尝试直接解析
            return json.loads(response)
        except:
            # 尝试提取```json```块中的内容
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # 尝试提取{}块
            brace_match = re.search(r'\{.*\}', response, re.DOTALL)
            if brace_match:
                try:
                    return json.loads(brace_match.group(0))
                except:
                    pass
            
            print("无法从响应中提取有效JSON")
            return None
    
    def step1_chapter_analysis(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Step 1: 章节级总结"""
        print(f"\n=== Step 1: 章节级总结 ({len(segments)} 个段落) ===")
        
        chapter_results = []
        
        for i, segment in enumerate(segments):
            print(f"\n处理第 {i + 1}/{len(segments)} 个段落...")
            
            # 构建提示词
            prompt = self.chapter_summary_prompt + f"""

段落信息：
- 段落编号: S{i+1:03d}
- 字数: {segment['word_count']}
- 时间戳: {datetime.now().isoformat()}

{segment['content']}"""
            
            # 调用模型
            response = self.call_llm(prompt, max_tokens=4000)
            if response:
                result = self.extract_json_from_response(response)
                if result:
                    # 添加实际的UUID
                    result['meta']['source_id'] = f"uuid-S{i+1:03d}-{str(uuid.uuid4())[:8]}"
                    chapter_results.append(result)
                    print(f"段落 {i + 1} 分析完成")
                else:
                    print(f"段落 {i + 1} JSON解析失败")
            else:
                print(f"段落 {i + 1} 模型调用失败")
            
            # 添加延迟
            if i < len(segments) - 1:
                time.sleep(3)
        
        print(f"\nStep 1 完成，成功分析 {len(chapter_results)} 个段落")
        return chapter_results
    
    def step2_group_analysis(self, chapter_results: List[Dict[str, Any]], group_size: int = 10) -> List[Dict[str, Any]]:
        """Step 2: 中层汇总总结"""
        print(f"\n=== Step 2: 中层汇总 (每组 {group_size} 个段落) ===")
        
        # 分组
        groups = []
        for i in range(0, len(chapter_results), group_size):
            group = chapter_results[i:i + group_size]
            groups.append(group)
        
        print(f"共分为 {len(groups)} 组")
        
        group_results = []
        
        for i, group in enumerate(groups):
            print(f"\n处理第 {i + 1}/{len(groups)} 组...")
            
            # 准备content_refs
            content_refs = []
            parent_ids = []
            total_word_count = 0
            all_genres = set()
            
            for chapter in group:
                content_refs.append({
                    "segment_id": chapter.get('segment_id'),
                    "summary": chapter.get('summary'),
                    "analysis": chapter.get('analysis')
                })
                
                # 安全地获取meta信息
                meta = chapter.get('meta', {})
                parent_ids.append(meta.get('source_id', f'unknown-{len(parent_ids)}'))
                total_word_count += meta.get('word_count', 0)
                
                # 安全地获取genre信息
                genre = meta.get('genre', [])
                if isinstance(genre, list):
                    all_genres.update(genre)
                elif isinstance(genre, str):
                    all_genres.add(genre)
            
            # 构建提示词
            group_data = json.dumps(group, ensure_ascii=False, indent=2)
            # 安全地获取章节范围
            start_ch = group[0].get('meta', {}).get('position', {}).get('start_chapter', 1)
            end_ch = group[-1].get('meta', {}).get('position', {}).get('end_chapter', len(group))
            
            prompt = self.group_summary_prompt + f"""

组信息：
- 组编号: G{i+1:03d}
- 父节点ID: {parent_ids}
- 章节范围: {start_ch}-{end_ch}
- 总字数: {total_word_count}
- 类型: {list(all_genres)}
- 时间戳: {datetime.now().isoformat()}

章节数据：
{group_data}"""
            
            # 调用模型
            response = self.call_llm(prompt, max_tokens=5000)
            if response:
                result = self.extract_json_from_response(response)
                if result:
                    # 添加实际的UUID
                    result['meta']['source_id'] = f"uuid-G{i+1:03d}-{str(uuid.uuid4())[:8]}"
                    group_results.append(result)
                    print(f"组 {i + 1} 汇总完成")
                else:
                    print(f"组 {i + 1} JSON解析失败")
            else:
                print(f"组 {i + 1} 模型调用失败")
            
            # 添加延迟
            if i < len(groups) - 1:
                time.sleep(5)
        
        print(f"\nStep 2 完成，成功汇总 {len(group_results)} 组")
        return group_results
    
    def step3_book_analysis(self, group_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Step 3: 全书级整合总结"""
        print(f"\n=== Step 3: 全书级整合 ===")
        
        # 准备content_refs
        content_refs = []
        parent_ids = []
        total_word_count = 0
        all_genres = set()
        total_chapters = 0
        
        for group in group_results:
            content_refs.append({
                "group_id": group.get('group_id'),
                "summary": group.get('summary'),
                "analysis": group.get('analysis'),
                "content_refs": group.get('content_refs', [])
            })
            
            # 安全地获取meta信息
            meta = group.get('meta', {})
            parent_ids.append(meta.get('source_id', f'unknown-group-{len(parent_ids)}'))
            total_word_count += meta.get('word_count', 0)
            
            # 安全地获取genre信息
            genre = meta.get('genre', [])
            if isinstance(genre, list):
                all_genres.update(genre)
            elif isinstance(genre, str):
                all_genres.add(genre)
            
            # 安全地获取position信息
            position = meta.get('position', {})
            end_chapter = position.get('end_chapter', 0)
            total_chapters = max(total_chapters, end_chapter)
        
        # 构建提示词
        group_data = json.dumps(group_results, ensure_ascii=False, indent=2)
        prompt = self.book_summary_prompt + f"""

全书信息：
- 父节点ID: {parent_ids}
- 总章节数: {total_chapters}
- 总字数: {total_word_count}
- 所有类型: {list(all_genres)}
- 时间戳: {datetime.now().isoformat()}

组汇总数据：
{group_data}"""
        
        # 调用模型
        response = self.call_llm(prompt, max_tokens=6000)
        if response:
            result = self.extract_json_from_response(response)
            if result:
                # 添加实际的UUID
                result['meta']['source_id'] = f"uuid-BOOK-{str(uuid.uuid4())[:8]}"
                print("全书分析完成")
                return result
            else:
                print("全书分析JSON解析失败")
        else:
            print("全书分析模型调用失败")
        
        return None
    
    def analyze_novel(self, novel_content: str) -> Dict[str, Any]:
        """完整的分层分析流程"""
        print("开始小说分层结构化分析...")
        
        # Step 1: 拆分并分析章节
        segments = self.split_into_segments(novel_content, segment_size=50000)
        chapter_results = self.step1_chapter_analysis(segments)
        
        if not chapter_results:
            return {"error": "章节级分析失败"}
        
        # 保存章节级结果
        self.save_intermediate_result(chapter_results, "chapter_analysis_results.json")
        
        # Step 2: 中层汇总
        group_results = self.step2_group_analysis(chapter_results, group_size=10)
        
        if not group_results:
            return {"error": "中层汇总失败"}
        
        # 保存中层结果
        self.save_intermediate_result(group_results, "group_analysis_results.json")
        
        # Step 3: 全书整合
        book_result = self.step3_book_analysis(group_results)
        
        if not book_result:
            return {"error": "全书分析失败"}
        
        # 构建最终结果
        final_result = {
            "timestamp": datetime.now().isoformat(),
            "original_length": len(novel_content),
            "segments_count": len(segments),
            "groups_count": len(group_results),
            "model_config": self.model_config,
            "book_analysis": book_result,
            "processing_summary": {
                "step1_segments": len(chapter_results),
                "step2_groups": len(group_results),
                "step3_book": 1 if book_result else 0
            }
        }
        
        return final_result
    
    def save_intermediate_result(self, data: Any, filename: str):
        """保存中间结果"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"中间结果已保存到: {filename}")
        except Exception as e:
            print(f"保存中间结果失败: {e}")
    
    def save_result(self, result: Dict[str, Any], output_file: str = "novel_hierarchical_analysis_result.json"):
        """保存最终分析结果"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"最终分析结果已保存到: {output_file}")
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def print_result(self, result: Dict[str, Any]):
        """打印分析结果"""
        print("\n" + "="*80)
        print("小说分层结构化分析报告")
        print("="*80)
        
        # 检查是否有错误
        if 'error' in result:
            print(f"分析失败: {result['error']}")
            print("="*80)
            return
        
        print(f"分析时间: {result.get('timestamp', '未知')}")
        print(f"原文长度: {result.get('original_length', 0)} 字符")
        print(f"分段数量: {result.get('segments_count', 0)}")
        print(f"分组数量: {result.get('groups_count', 0)}")
        
        model_config = result.get('model_config', {})
        print(f"使用模型: {model_config.get('model_name', '未知')}")
        
        if 'book_analysis' in result and result['book_analysis']:
            book = result['book_analysis']
            print("-"*80)
            print("全书分析结果:")
            print("-"*80)
            print(f"书籍概要: {book.get('book_summary', '未生成')[:200]}...")
            
            if 'analysis' in book:
                analysis = book['analysis']
                print(f"主线数量: {analysis.get('main_storylines', 'N/A')}")
                print(f"冲突密度: {analysis.get('avg_conflict_density', 'N/A')}")
                print(f"高潮点数量: {analysis.get('total_climax_points', 'N/A')}")
                print(f"节奏模式: {analysis.get('rhythm_pattern', 'N/A')}")
                print(f"核心标签: {analysis.get('core_tags', 'N/A')}")
        else:
            print("全书分析未完成或失败")
        
        print("="*80)

def main():
    """主函数"""
    print("小说分层结构化分析工具")
    print("适用于长篇小说（500万字级）")
    print("="*50)
    
    # 初始化分析工具
    analyzer = NovelHierarchicalAnalyzer()
    
    # 读取小说文件
    novel_file = "傲视天地.txt"
    if not os.path.exists(novel_file):
        print(f"错误: 找不到文件 {novel_file}")
        return
    
    novel_content = analyzer.read_novel(novel_file)
    if not novel_content:
        print("无法读取小说内容")
        return
    
    # 分析小说
    result = analyzer.analyze_novel(novel_content)
    
    # 保存结果
    analyzer.save_result(result)
    
    # 打印结果
    analyzer.print_result(result)

if __name__ == "__main__":
    main()
