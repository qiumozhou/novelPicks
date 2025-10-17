#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单启动脚本 - 无emoji字符，方便查看日志
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """简单启动服务器"""
    print("=" * 60)
    print("小说分析系统 - 简单启动模式")
    print("=" * 60)
    
    # 确保必要的目录存在
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    print("[SETUP] 目录检查完成")
    
    print("[INFO] 启动服务器...")
    print("[URL] 访问地址: http://localhost:8001")
    print("[DOCS] API文档: http://localhost:8001/docs")
    print("[DEBUG] 调试信息: http://localhost:8001/api/debug/logs")
    print("[STATUS] 系统状态: http://localhost:8001/api/system/status")
    print("[STOP] 按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        # 直接导入并运行
        from main import app
        
        print("[SERVER] 服务器启动中...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8001,
            log_level="info",
            access_log=True,
            reload=False
        )
        
    except KeyboardInterrupt:
        print("\n[STOP] 服务器已停止")
    except Exception as e:
        print(f"\n[ERROR] 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
