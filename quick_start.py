#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 一键启动MongoDB和小说分析系统
"""

import os
import subprocess
import time
import sys

def print_step(step, message):
    """打印步骤信息"""
    print(f"[STEP {step}] {message}")

def run_command(cmd, description):
    """执行命令并处理结果"""
    try:
        print(f"[RUN] {description}...")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {description}完成")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description}失败: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr}")
        return False, e.stderr

def check_prerequisites():
    """检查必要条件"""
    print_step(1, "检查系统环境")
    
    # 检查Docker
    success, _ = run_command("docker --version", "检查Docker")
    if not success:
        print("[ERROR] 请先安装Docker")
        return False
    
    # 检查Python依赖
    try:
        import fastapi, pymongo, motor
        print("[OK] Python依赖检查通过")
    except ImportError as e:
        print(f"[ERROR] 缺少Python依赖: {e}")
        print("[INFO] 请运行: pip install -r requirements.txt")
        return False
    
    return True

def start_mongodb():
    """启动MongoDB"""
    print_step(2, "启动MongoDB数据库")
    
    # 检查容器是否已存在
    success, output = run_command("docker ps -a --filter name=novel_mongodb", "检查MongoDB容器")
    
    if "novel_mongodb" in output:
        print("[INFO] MongoDB容器已存在，尝试启动...")
        success, _ = run_command("docker start novel_mongodb", "启动现有MongoDB容器")
    else:
        print("[INFO] 创建新的MongoDB容器...")
        success, _ = run_command("docker compose up -d mongodb", "创建并启动MongoDB容器")
    
    if not success:
        return False
    
    # 等待MongoDB启动
    print("[WAIT] 等待MongoDB初始化...")
    time.sleep(10)
    
    # 检查MongoDB状态
    for i in range(5):
        success, _ = run_command(
            "docker exec novel_mongodb mongosh --eval \"db.adminCommand('ping')\"",
            f"检查MongoDB连接 (尝试 {i+1}/5)"
        )
        if success:
            print("[SUCCESS] MongoDB启动成功")
            return True
        time.sleep(3)
    
    print("[WARNING] MongoDB可能仍在启动中，继续下一步...")
    return True

def start_novel_system():
    """启动小说分析系统"""
    print_step(3, "启动小说分析系统")
    
    print("[INFO] 系统将在新终端窗口中启动...")
    print("[INFO] 如果需要手动启动，请运行: python start_server.py")
    
    # 在Windows上启动新的cmd窗口
    if os.name == 'nt':
        cmd = 'start "小说分析系统" cmd /k "python start_server.py"'
        subprocess.Popen(cmd, shell=True)
    else:
        # Linux/Mac
        subprocess.Popen(['python', 'start_server.py'])
    
    return True

def show_access_info():
    """显示访问信息"""
    print_step(4, "系统启动完成")
    
    print("\n" + "=" * 60)
    print("🎉 小说分析系统启动成功!")
    print("=" * 60)
    print("📱 前端界面: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔧 系统状态: http://localhost:8000/api/system/status")
    print("🗄️ MongoDB: mongodb://localhost:27017")
    print("=" * 60)
    print("\n📋 快速操作:")
    print("  - 停止MongoDB: python start_mongodb.py stop")
    print("  - 查看MongoDB日志: python start_mongodb.py logs")
    print("  - 环境检查: python check_environment.py")
    print("  - 停止系统: 在服务器窗口中按 Ctrl+C")
    print("\n📚 使用指南:")
    print("  1. 访问 http://localhost:8000 打开前端界面")
    print("  2. 在上传页面选择小说文件(.txt格式)")
    print("  3. 系统会自动进行三层分析")
    print("  4. 在分析详情页查看结果")
    print("=" * 60)

def main():
    """主函数"""
    print("🚀 小说分析系统 - 快速启动")
    print("=" * 60)
    
    try:
        # 检查必要条件
        if not check_prerequisites():
            sys.exit(1)
        
        # 启动MongoDB
        if not start_mongodb():
            print("[ERROR] MongoDB启动失败")
            sys.exit(1)
        
        # 启动小说分析系统
        if not start_novel_system():
            print("[ERROR] 小说分析系统启动失败")
            sys.exit(1)
        
        # 显示访问信息
        show_access_info()
        
    except KeyboardInterrupt:
        print("\n[STOP] 用户中断启动过程")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] 启动过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
