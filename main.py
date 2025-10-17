#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说分析系统 - FastAPI 后端
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from database import Database
from novel_analyzer import NovelAnalyzer

# 创建FastAPI应用
app = FastAPI(
    title="小说分析系统",
    description="基于大模型的小说分层结构化分析系统",
    version="1.0.0"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
db = Database()
analyzer = NovelAnalyzer(db)

# 分析进度存储
analysis_progress = {}

# 创建static目录
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic模型
class NovelInfo(BaseModel):
    id: Optional[str] = None
    title: str
    file_path: str
    word_count: Optional[int] = None
    status: str = "pending"
    created_at: Optional[datetime] = None

class AnalysisResponse(BaseModel):
    message: str
    novel_id: str
    status: str

class NovelListResponse(BaseModel):
    novels: List[Dict[str, Any]]
    total_count: int

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    await db.init_database()
    if db.client is not None:
        print("数据库连接已初始化")
    else:
        print("系统在无数据库模式下运行")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    await db.close_database()
    print("数据库连接已关闭")

@app.get("/")
async def read_root():
    """返回前端页面"""
    return FileResponse("static/index.html")

@app.get("/api/novels", response_model=NovelListResponse)
async def get_novels():
    """获取所有小说列表"""
    if db.client is None:
        # 返回演示数据
        demo_novels = [{
            "_id": "demo-novel-1",
            "title": "演示小说",
            "status": "pending",
            "word_count": 500000,
            "created_at": "2024-01-01T10:00:00Z"
        }]
        return NovelListResponse(
            novels=demo_novels,
            total_count=len(demo_novels)
        )
    
    try:
        novels = await db.get_all_novels()
        return NovelListResponse(
            novels=novels,
            total_count=len(novels)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取小说列表失败: {str(e)}")

@app.get("/api/novels/{novel_id}")
async def get_novel(novel_id: str):
    """获取特定小说的详细信息"""
    try:
        novel = await db.get_novel_by_id(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说未找到")
        return novel
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取小说信息失败: {str(e)}")

@app.get("/api/novels/{novel_id}/analysis/{level}")
async def get_novel_analysis(novel_id: str, level: str):
    """获取小说分析结果
    
    Args:
        novel_id: 小说ID
        level: 分析层级 (chapter|group|book)
    """
    if level not in ["chapter", "group", "book"]:
        raise HTTPException(status_code=400, detail="无效的分析层级，必须是 chapter, group 或 book")
    
    try:
        analysis = await db.get_analysis_by_level(novel_id, level)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"未找到{level}级分析结果")
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析结果失败: {str(e)}")

@app.get("/api/system/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "database_connected": db.client is not None,
        "database_url": db.mongodb_url if db.client is not None else "未连接",
        "system_mode": "完整功能" if db.client is not None else "演示模式",
        "features": {
            "upload": db.client is not None,
            "analysis": db.client is not None,
            "storage": db.client is not None
        }
    }

@app.get("/api/debug/logs")
async def get_debug_logs():
    """获取调试日志"""
    import os
    uploads_files = []
    if os.path.exists("uploads"):
        uploads_files = [f for f in os.listdir("uploads") if f.endswith('.txt')]
    
    return {
        "uploads_directory": "uploads" if os.path.exists("uploads") else "不存在",
        "uploads_files": uploads_files,
        "database_connected": db.client is not None,
        "analyzer_initialized": analyzer is not None
    }

@app.get("/api/novels/{novel_id}/progress")
async def get_analysis_progress(novel_id: str):
    """获取分析进度"""
    progress = analysis_progress.get(novel_id, {
        "status": "not_found",
        "progress": 0,
        "current_step": "",
        "message": "未找到分析进度"
    })
    return progress

@app.post("/api/novels/upload", response_model=AnalysisResponse)
async def upload_novel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = None
):
    """上传小说文件并开始分析"""
    if db.client is None:
        raise HTTPException(
            status_code=503, 
            detail="数据库未连接，无法上传小说。请配置MongoDB数据库后重试。"
        )
    
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="仅支持.txt格式的文件")
    
    try:
        # 生成小说ID
        novel_id = str(uuid.uuid4())
        
        # 保存文件
        file_path = f"uploads/{novel_id}_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # 创建小说记录
        novel_info = {
            "_id": novel_id,
            "title": title or file.filename.replace('.txt', ''),
            "file_path": file_path,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "word_count": len(contents.decode('utf-8', errors='ignore'))
        }
        
        await db.create_novel(novel_info)
        print(f"[SUCCESS] 小说记录已创建: {novel_id}", flush=True)
        
        # 后台运行分析任务
        print(f"[START] 启动后台分析任务: {novel_id}", flush=True)
        background_tasks.add_task(analyzer.analyze_novel_async, novel_id, file_path)
        print(f"[QUEUE] 分析任务已添加到后台队列", flush=True)
        
        return AnalysisResponse(
            message="文件上传成功，分析任务已开始",
            novel_id=novel_id,
            status="processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.post("/api/novels/analyze/{novel_id}")
async def analyze_existing_novel(novel_id: str, background_tasks: BackgroundTasks):
    """重新分析已存在的小说"""
    try:
        novel = await db.get_novel_by_id(novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="小说未找到")
        
        print(f"[TRIGGER] 手动触发分析: {novel_id}")
        print(f"[FILE] 文件路径: {novel['file_path']}")
        
        # 更新状态为处理中
        await db.update_novel_status(novel_id, "processing")
        print(f"[STATUS] 状态已更新为: processing")
        
        # 后台运行分析任务
        print(f"[START] 启动后台分析任务: {novel_id}")
        background_tasks.add_task(analyzer.analyze_novel_async, novel_id, novel['file_path'])
        print(f"[QUEUE] 分析任务已添加到后台队列")
        
        return AnalysisResponse(
            message="分析任务已开始",
            novel_id=novel_id,
            status="processing"
        )
        
    except Exception as e:
        print(f"[ERROR] 启动分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动分析失败: {str(e)}")

@app.post("/api/test/analyze")
async def test_analyze():
    """测试分析功能 - 直接运行分析任务"""
    try:
        # 检查是否有测试文件
        test_files = []
        for file in os.listdir("uploads"):
            if file.endswith('.txt'):
                test_files.append(file)
        
        if not test_files:
            return {"error": "没有找到测试文件，请先上传一个.txt文件"}
        
        # 使用第一个找到的文件
        test_file = test_files[0]
        file_path = f"uploads/{test_file}"
        novel_id = f"test-{str(uuid.uuid4())[:8]}"
        
        print(f"[TEST] 开始测试分析...")
        print(f"[FILE] 测试文件: {file_path}")
        print(f"[ID] 测试ID: {novel_id}")
        
        # 直接运行分析（同步）
        await analyzer.analyze_novel_async(novel_id, file_path)
        
        return {
            "message": "测试分析完成",
            "novel_id": novel_id,
            "test_file": test_file
        }
        
    except Exception as e:
        print(f"[ERROR] 测试分析失败: {str(e)}")
        return {"error": f"测试失败: {str(e)}"}

@app.delete("/api/novels/{novel_id}")
async def delete_novel(novel_id: str):
    """删除小说及其所有分析结果"""
    try:
        result = await db.delete_novel_and_analysis(novel_id)
        if not result:
            raise HTTPException(status_code=404, detail="小说未找到")
        
        return {"message": "小说删除成功", "novel_id": novel_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
