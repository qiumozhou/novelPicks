#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说分析系统服务器启动脚本
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """启动服务器"""
    print("[START] 启动小说分析系统...")
    
    # 确保必要的目录存在
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    print("[SETUP] 目录检查完成")
    print("[SERVER] 服务器启动中...")
    print("[URL] 访问地址: http://localhost:8000")
    print("[DOCS] API文档: http://localhost:8000/docs")
    print("[STOP] 按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 使用最原始的方式启动，方便查看日志
        import uvicorn
        from main import app
        
        print("[INFO] 使用原始方式启动服务器...")
        print("[INFO] 日志将直接显示在控制台")
        print("[INFO] 按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="debug",
            access_log=True,
            reload=False  # 关闭自动重载，避免日志混乱
        )
    except KeyboardInterrupt:
        print("\n[STOP] 服务器已停止")

if __name__ == "__main__":
    main()
