#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说结构化分析分层总结工具 - MongoDB集成版
"""

import os
import json
import time
import re
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, Any, Optional, List

class NovelAnalyzer:
    """小说分层结构化分析工具 - 支持MongoDB存储"""
    
    def __init__(self, database):
        """初始化分析器
        
        Args:
            database: Database实例，用于存储分析结果
        """
        self.db = database
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
16. 主要人物列表（提取全书中的核心人物）
17. 主题标签（提取全书的核心主题和情感标签）

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
    "interest_matching": "高",
    "main_characters": ["主角张三", "女主角李四", "反派王五"],
    "themes": ["成长", "复仇", "友情", "爱情"]
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
    
    async def call_llm(self, prompt: str, max_tokens: int = 6000) -> Optional[str]:
        """调用大模型API - 异步版本"""
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
                print(f"   🔄 调用模型 (尝试 {attempt + 1}/{self.model_config['max_retries']})...")
                
                # 使用asyncio在线程池中运行requests
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        f"{self.model_config['base_url']}/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=self.model_config["timeout"]
                    )
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        print(f"   ✅ 模型调用成功! (响应长度: {len(content)} 字符)")
                        return content
                    else:
                        print(f"   ❌ 模型响应格式错误: {result}")
                else:
                    print(f"   ❌ API请求失败: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ 请求超时 (尝试 {attempt + 1}/{self.model_config['max_retries']})")
            except Exception as e:
                print(f"   ❌ 请求失败: {e}")
            
            if attempt < self.model_config["max_retries"] - 1:
                wait_time = (attempt + 1) * 3
                print(f"   ⏳ 等待 {wait_time} 秒后重试...")
                await asyncio.sleep(wait_time)
        
        print("   ❌ 所有重试均失败")
        return None
    
    def clean_data_for_serialization(self, data):
        """清理数据，确保可以序列化为JSON"""
        if isinstance(data, dict):
            return {key: self.clean_data_for_serialization(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.clean_data_for_serialization(item) for item in data]
        elif hasattr(data, '__str__') and not isinstance(data, (str, int, float, bool, type(None))):
            return str(data)
        else:
            return data
    
    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """从模型响应中提取JSON"""
        try:
            # 尝试直接解析
            result = json.loads(response)
            return self.clean_data_for_serialization(result)
        except:
            # 尝试提取```json```块中的内容
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    return self.clean_data_for_serialization(result)
                except:
                    pass
            
            # 尝试提取{}块
            brace_match = re.search(r'\{.*\}', response, re.DOTALL)
            if brace_match:
                try:
                    result = json.loads(brace_match.group(0))
                    return self.clean_data_for_serialization(result)
                except:
                    pass
            
            print("无法从响应中提取有效JSON")
            return None
    
    async def step1_chapter_analysis(self, novel_id: str, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Step 1: 章节级总结并保存到MongoDB"""
        print(f"\n📄 开始章节级分析 ({len(segments)} 个段落)")
        print(f"{'─'*50}")
        
        chapter_results = []
        total_segments = len(segments)
        
        for i, segment in enumerate(segments):
            # 更新详细进度
            progress = 30 + int((i / total_segments) * 20)  # 30-50%
            self.update_progress(novel_id, progress, f"分析章节 {i+1}/{total_segments}", 
                               f"正在分析第{i+1}个段落，字数: {segment['word_count']:,}")
            
            print(f"\n🔄 处理第 {i + 1}/{len(segments)} 个段落...")
            print(f"   📊 段落字数: {segment['word_count']:,} 字符")
            print(f"   📍 位置: {segment['start_pos']:,} - {segment['end_pos']:,}")
            
            # 构建提示词
            prompt = self.chapter_summary_prompt + f"""

段落信息：
- 段落编号: S{i+1:03d}
- 字数: {segment['word_count']}
- 时间戳: {datetime.now().isoformat()}

{segment['content']}"""
            
            # 调用模型
            print(f"   🤖 调用大模型API...")
            self.update_progress(novel_id, progress, f"调用AI分析章节 {i+1}", 
                               f"正在调用AI分析第{i+1}个段落...")
            
            response = await self.call_llm(prompt, max_tokens=4000)
            if response:
                print(f"   📝 解析模型响应...")
                self.update_progress(novel_id, progress, f"解析AI响应 {i+1}", 
                                   f"正在解析AI对第{i+1}个段落的分析结果...")
                
                result = self.extract_json_from_response(response)
                if result:
                    # 添加实际的UUID和小说ID
                    if 'meta' not in result:
                        result['meta'] = {}
                    
                    result['meta']['source_id'] = f"uuid-S{i+1:03d}-{str(uuid.uuid4())[:8]}"
                    result['segment_id'] = f"S{i+1:03d}"
                    result['novel_id'] = novel_id
                    result['segment_number'] = i + 1
                    
                    # 确保所有数据都是可序列化的
                    if 'meta' in result and isinstance(result['meta'], dict):
                        for key, value in result['meta'].items():
                            if hasattr(value, '__str__'):
                                result['meta'][key] = str(value)
                    
                    chapter_results.append(result)
                    print(f"   ✅ 段落 {i + 1} 分析完成")
                    self.update_progress(novel_id, progress, f"章节 {i+1} 分析完成", 
                                       f"第{i+1}个段落分析完成，已分析 {len(chapter_results)} 个段落")
                else:
                    print(f"   ❌ 段落 {i + 1} JSON解析失败")
                    self.update_progress(novel_id, progress, f"章节 {i+1} 解析失败", 
                                       f"第{i+1}个段落的AI响应解析失败，正在重试...")
            else:
                print(f"   ❌ 段落 {i + 1} 模型调用失败")
                self.update_progress(novel_id, progress, f"章节 {i+1} 调用失败", 
                                   f"第{i+1}个段落的AI调用失败，正在重试...")
            
            # 添加延迟
            if i < len(segments) - 1:
                print(f"   ⏳ 等待 3 秒后继续...")
                self.update_progress(novel_id, progress, f"等待处理下一章节", 
                                   f"第{i+1}个段落处理完成，等待3秒后处理第{i+2}个段落...")
                await asyncio.sleep(3)
        
        # 保存到MongoDB
        if chapter_results:
            print(f"\n[SAVE] 保存章节分析结果到数据库...", flush=True)
            # 清理数据确保可序列化
            cleaned_results = [self.clean_data_for_serialization(result) for result in chapter_results]
            await self.db.save_chapter_analysis(novel_id, cleaned_results)
            print(f"[SUCCESS] 章节级分析完成，成功分析并保存 {len(chapter_results)} 个段落", flush=True)
        else:
            print(f"[WARNING] 没有章节分析结果需要保存", flush=True)
        
        return chapter_results
    
    async def step2_group_analysis(self, novel_id: str, chapter_results: List[Dict[str, Any]], group_size: int = 10) -> List[Dict[str, Any]]:
        """Step 2: 中层汇总总结并保存到MongoDB"""
        print(f"\n📑 开始中层汇总分析 (每组 {group_size} 个段落)")
        print(f"{'─'*50}")
        
        # 分组
        groups = []
        for i in range(0, len(chapter_results), group_size):
            group = chapter_results[i:i + group_size]
            groups.append(group)
        
        print(f"📊 章节已分为 {len(groups)} 组进行汇总")
        
        group_results = []
        total_groups = len(groups)
        
        for i, group in enumerate(groups):
            # 更新详细进度
            progress = 60 + int((i / total_groups) * 15)  # 60-75%
            self.update_progress(novel_id, progress, f"汇总组 {i+1}/{total_groups}", 
                               f"正在汇总第{i+1}组，包含{len(group)}个段落")
            
            print(f"\n🔄 处理第 {i + 1}/{len(groups)} 组...")
            print(f"   📊 组内段落数: {len(group)} 个")
            print(f"   📍 段落范围: {group[0].get('segment_number', 1)} - {group[-1].get('segment_number', len(group))}")
            
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
                
                # 安全地获取字数，确保是数字
                word_count = meta.get('word_count', 0)
                if isinstance(word_count, str):
                    try:
                        word_count = int(word_count)
                    except (ValueError, TypeError):
                        word_count = 0
                elif not isinstance(word_count, (int, float)):
                    word_count = 0
                total_word_count += word_count
                
                # 安全地获取genre信息
                genre = meta.get('genre', [])
                if isinstance(genre, list):
                    all_genres.update(genre)
                elif isinstance(genre, str):
                    all_genres.add(genre)
            
            # 构建提示词
            group_data = json.dumps(group, ensure_ascii=False, indent=2)
            prompt = self.group_summary_prompt + f"""

组信息：
- 组编号: G{i+1:03d}
- 父节点ID: {parent_ids}
- 章节范围: {group[0].get('segment_number', 1)}-{group[-1].get('segment_number', len(group))}
- 总字数: {total_word_count}
- 类型: {list(all_genres)}
- 时间戳: {datetime.now().isoformat()}

章节数据：
{group_data}"""
            
            # 调用模型
            print(f"   🤖 调用大模型API进行汇总...")
            self.update_progress(novel_id, progress, f"调用AI汇总组 {i+1}", 
                               f"正在调用AI汇总第{i+1}组，包含{len(group)}个段落...")
            
            response = await self.call_llm(prompt, max_tokens=5000)
            if response:
                print(f"   📝 解析模型响应...")
                self.update_progress(novel_id, progress, f"解析AI汇总响应 {i+1}", 
                                   f"正在解析AI对第{i+1}组的汇总结果...")
                result = self.extract_json_from_response(response)
                if result:
                    # 添加实际的UUID和小说ID
                    if 'meta' not in result:
                        result['meta'] = {}
                    
                    result['meta']['source_id'] = f"uuid-G{i+1:03d}-{str(uuid.uuid4())[:8]}"
                    result['group_id'] = f"G{i+1:03d}"
                    result['novel_id'] = novel_id
                    result['group_number'] = i + 1
                    result['content_refs'] = content_refs
                    
                    group_results.append(result)
                    print(f"   ✅ 组 {i + 1} 汇总完成")
                else:
                    print(f"   ❌ 组 {i + 1} JSON解析失败")
            else:
                print(f"   ❌ 组 {i + 1} 模型调用失败")
            
            # 添加延迟
            if i < len(groups) - 1:
                print(f"   ⏳ 等待 5 秒后继续...")
                await asyncio.sleep(5)
        
        # 保存到MongoDB
        if group_results:
            print(f"\n[SAVE] 保存中层汇总结果到数据库...", flush=True)
            # 清理数据确保可序列化
            cleaned_results = [self.clean_data_for_serialization(result) for result in group_results]
            await self.db.save_group_analysis(novel_id, cleaned_results)
            print(f"[SUCCESS] 中层汇总完成，成功汇总并保存 {len(group_results)} 组", flush=True)
        else:
            print(f"[WARNING] 没有中层汇总结果需要保存", flush=True)
        
        return group_results
    
    async def step3_book_analysis(self, novel_id: str, group_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Step 3: 全书级整合总结并保存到MongoDB"""
        print(f"\n📚 开始全书级整合分析")
        print(f"{'─'*50}")
        print(f"📊 基于 {len(group_results)} 个中层汇总结果进行全书分析")
        
        # 更新进度
        self.update_progress(novel_id, 85, "开始全书分析", 
                           f"正在整合{len(group_results)}个中层汇总结果进行全书分析...")
        
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
            
            # 安全地获取字数，确保是数字
            word_count = meta.get('word_count', 0)
            if isinstance(word_count, str):
                try:
                    word_count = int(word_count)
                except (ValueError, TypeError):
                    word_count = 0
            elif not isinstance(word_count, (int, float)):
                word_count = 0
            total_word_count += word_count
            
            # 安全地获取genre信息
            genre = meta.get('genre', [])
            if isinstance(genre, list):
                all_genres.update(genre)
            elif isinstance(genre, str):
                all_genres.add(genre)
            
            # 获取章节数量
            group_number = group.get('group_number', 0)
            if isinstance(group_number, str):
                try:
                    group_number = int(group_number)
                except (ValueError, TypeError):
                    group_number = 0
            elif not isinstance(group_number, (int, float)):
                group_number = 0
            total_chapters = max(total_chapters, group_number)
        
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
        print(f"🤖 调用大模型API进行全书分析...")
        self.update_progress(novel_id, 90, "调用AI全书分析", 
                           f"正在调用AI进行全书级整合分析，基于{len(group_results)}个中层汇总...")
        
        response = await self.call_llm(prompt, max_tokens=6000)
        if response:
            print(f"📝 解析模型响应...")
            self.update_progress(novel_id, 95, "解析AI全书响应", 
                               f"正在解析AI的全书级分析结果...")
            result = self.extract_json_from_response(response)
            if result:
                # 添加实际的UUID和小说ID
                if 'meta' not in result:
                    result['meta'] = {}
                
                result['meta']['source_id'] = f"uuid-BOOK-{str(uuid.uuid4())[:8]}"
                result['novel_id'] = novel_id
                result['content_refs'] = content_refs
                
                # 保存到MongoDB
                print(f"[SAVE] 保存全书分析结果到数据库...", flush=True)
                # 清理数据确保可序列化
                cleaned_result = self.clean_data_for_serialization(result)
                await self.db.save_book_analysis(novel_id, cleaned_result)
                print("[SUCCESS] 全书分析完成并已保存", flush=True)
                return result
            else:
                print("[ERROR] 全书分析JSON解析失败", flush=True)
        else:
            print("[ERROR] 全书分析模型调用失败", flush=True)
        
        return None
    
    def update_progress(self, novel_id: str, progress: int, step: str, message: str = ""):
        """更新分析进度"""
        try:
            from main import analysis_progress
            analysis_progress[novel_id] = {
                "status": "processing",
                "progress": progress,
                "current_step": step,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            print(f"[PROGRESS] {novel_id}: {progress}% - {step} - {message}", flush=True)
        except Exception as e:
            print(f"[PROGRESS ERROR] 更新进度失败: {e}", flush=True)

    async def analyze_novel_async(self, novel_id: str, file_path: str):
        """异步分析小说的完整流程"""
        try:
            print(f"\n{'='*60}", flush=True)
            print(f"[TASK] 后台任务启动: 分析小说", flush=True)
            print(f"[ID] 小说ID: {novel_id}", flush=True)
            print(f"[FILE] 文件路径: {file_path}", flush=True)
            print(f"[TIME] 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            print(f"[DB] 数据库状态: {'已连接' if self.db.client is not None else '未连接'}", flush=True)
            print(f"{'='*60}", flush=True)
            
            # 初始化进度
            self.update_progress(novel_id, 0, "初始化", "开始分析小说")
            
            # 更新状态为处理中
            await self.db.update_novel_status(novel_id, "processing")
            print("[STATUS] 小说状态已更新为: processing", flush=True)
            
            # 读取小说内容
            print("\n[STEP1] 读取小说文件...", flush=True)
            self.update_progress(novel_id, 10, "读取文件", "正在读取小说文件...")
            novel_content = self.read_novel(file_path)
            if not novel_content:
                await self.db.update_novel_status(novel_id, "failed")
                self.update_progress(novel_id, 0, "失败", "无法读取小说内容")
                print("[ERROR] 无法读取小说内容", flush=True)
                return
            print(f"[SUCCESS] 小说内容读取成功，总字数: {len(novel_content):,} 字符", flush=True)
            self.update_progress(novel_id, 20, "文件读取完成", f"成功读取 {len(novel_content):,} 字符")
            
            # Step 1: 拆分并分析章节
            print("\n[STEP2] 章节级分析...", flush=True)
            self.update_progress(novel_id, 25, "拆分章节", "正在拆分小说为章节...")
            segments = self.split_into_segments(novel_content, segment_size=50000)
            print(f"[INFO] 小说已拆分为 {len(segments)} 个段落，每段约5万字", flush=True)
            
            self.update_progress(novel_id, 30, "分析章节", f"开始分析 {len(segments)} 个章节...")
            chapter_results = await self.step1_chapter_analysis(novel_id, segments)
            
            if not chapter_results:
                await self.db.update_novel_status(novel_id, "failed")
                self.update_progress(novel_id, 0, "失败", "章节级分析失败")
                print("[ERROR] 章节级分析失败", flush=True)
                return
            print(f"[SUCCESS] 章节级分析完成，共分析 {len(chapter_results)} 个段落", flush=True)
            self.update_progress(novel_id, 50, "章节分析完成", f"成功分析 {len(chapter_results)} 个章节")
            
            # Step 2: 中层汇总
            print("\n[STEP3] 中层汇总分析...", flush=True)
            self.update_progress(novel_id, 60, "中层汇总", "正在进行中层汇总分析...")
            group_results = await self.step2_group_analysis(novel_id, chapter_results, group_size=10)
            
            if not group_results:
                await self.db.update_novel_status(novel_id, "failed")
                self.update_progress(novel_id, 0, "失败", "中层汇总失败")
                print("[ERROR] 中层汇总失败", flush=True)
                return
            print(f"[SUCCESS] 中层汇总完成，共汇总 {len(group_results)} 组", flush=True)
            self.update_progress(novel_id, 75, "中层汇总完成", f"成功汇总 {len(group_results)} 组")
            
            # Step 3: 全书整合
            print("\n[STEP4] 全书级整合分析...", flush=True)
            self.update_progress(novel_id, 85, "全书分析", "正在进行全书级整合分析...")
            book_result = await self.step3_book_analysis(novel_id, group_results)
            
            if not book_result:
                await self.db.update_novel_status(novel_id, "failed")
                self.update_progress(novel_id, 0, "失败", "全书分析失败")
                print("[ERROR] 全书分析失败", flush=True)
                return
            print("[SUCCESS] 全书级分析完成", flush=True)
            
            # 更新状态为完成
            await self.db.update_novel_status(novel_id, "completed")
            self.update_progress(novel_id, 100, "分析完成", "小说分析全部完成！")
            
            print(f"\n{'='*60}", flush=True)
            print(f"[COMPLETE] 小说分析完成!", flush=True)
            print(f"[ID] 小说ID: {novel_id}", flush=True)
            print(f"[TIME] 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            print(f"[STATS] 分析统计:", flush=True)
            print(f"   - 章节段落: {len(chapter_results)} 个", flush=True)
            print(f"   - 中层组数: {len(group_results)} 组", flush=True)
            print(f"   - 全书分析: 1 个", flush=True)
            print(f"{'='*60}", flush=True)
            
        except Exception as e:
            print(f"\n[ERROR] 分析过程中发生错误: {e}", flush=True)
            print(f"[ID] 小说ID: {novel_id}", flush=True)
            print(f"[TIME] 错误时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
            await self.db.update_novel_status(novel_id, "failed")
            print("[STATUS] 小说状态已更新为: failed", flush=True)
    
    def analyze_novel_sync(self, novel_id: str, file_path: str):
        """同步版本的小说分析（用于直接调用）"""
        return asyncio.run(self.analyze_novel_async(novel_id, file_path))
