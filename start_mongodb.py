#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB启动脚本 - 使用Docker
"""

import os
import subprocess
import time
import sys

def check_docker():
    """检查Docker是否安装"""
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
        print("[DOCKER] Docker已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Docker未安装或不在PATH中")
        print("请先安装Docker: https://www.docker.com/get-started")
        return False

def check_docker_compose():
    """检查Docker Compose是否可用"""
    try:
        subprocess.run(['docker', 'compose', 'version'], check=True, capture_output=True)
        print("[COMPOSE] Docker Compose已就绪")
        return True
    except subprocess.CalledProcessError:
        try:
            subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
            print("[COMPOSE] Docker Compose (standalone)已就绪")
            return 'standalone'
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ERROR] Docker Compose不可用")
            return False

def start_mongodb():
    """启动MongoDB容器"""
    print("[MONGODB] 启动MongoDB服务...")
    
    compose_type = check_docker_compose()
    if not compose_type:
        return False
    
    try:
        if compose_type == 'standalone':
            cmd = ['docker-compose', 'up', '-d', 'mongodb']
        else:
            cmd = ['docker', 'compose', 'up', '-d', 'mongodb']
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[SUCCESS] MongoDB容器启动成功")
        
        # 等待MongoDB启动
        print("[WAIT] 等待MongoDB初始化...")
        time.sleep(10)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 启动失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def check_mongodb_status():
    """检查MongoDB状态"""
    try:
        result = subprocess.run([
            'docker', 'exec', 'novel_mongodb', 
            'mongosh', '--eval', 'db.adminCommand("ping")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("[STATUS] MongoDB运行正常")
            return True
        else:
            print(f"[WARNING] MongoDB状态检查失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[WARNING] MongoDB连接超时，但容器可能正在启动")
        return True
    except Exception as e:
        print(f"[ERROR] 状态检查错误: {e}")
        return False

def stop_mongodb():
    """停止MongoDB容器"""
    print("[STOP] 停止MongoDB服务...")
    
    try:
        subprocess.run(['docker', 'stop', 'novel_mongodb'], check=True)
        print("[SUCCESS] MongoDB已停止")
        return True
    except subprocess.CalledProcessError:
        print("[WARNING] 停止失败或容器不存在")
        return False

def show_mongodb_logs():
    """显示MongoDB日志"""
    try:
        subprocess.run(['docker', 'logs', 'novel_mongodb'], check=True)
    except subprocess.CalledProcessError:
        print("[ERROR] 无法获取日志")

def main():
    """主函数"""
    print("[MONGODB] MongoDB管理工具")
    print("=" * 50)
    
    if not check_docker():
        sys.exit(1)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            if start_mongodb():
                time.sleep(5)  # 额外等待
                check_mongodb_status()
            
        elif command == 'stop':
            stop_mongodb()
            
        elif command == 'status':
            check_mongodb_status()
            
        elif command == 'logs':
            show_mongodb_logs()
            
        elif command == 'restart':
            stop_mongodb()
            time.sleep(3)
            if start_mongodb():
                time.sleep(5)
                check_mongodb_status()
                
        else:
            print(f"[ERROR] 未知命令: {command}")
            print("可用命令: start, stop, status, logs, restart")
    else:
        # 默认启动
        if start_mongodb():
            check_mongodb_status()
            print("\n" + "=" * 50)
            print("[INFO] MongoDB管理命令:")
            print("  python start_mongodb.py start    - 启动")
            print("  python start_mongodb.py stop     - 停止")  
            print("  python start_mongodb.py status   - 状态")
            print("  python start_mongodb.py logs     - 日志")
            print("  python start_mongodb.py restart  - 重启")

if __name__ == "__main__":
    main()
