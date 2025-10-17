#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检查脚本 - 验证系统依赖和配置
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("[Python] 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   [OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   [ERROR] Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要Python 3.8或更高版本")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n[Dependencies] 检查依赖包...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pymongo', 
        'motor',
        'pydantic',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"   [OK] {package}")
        except ImportError:
            print(f"   [MISSING] {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n请安装缺失的依赖: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_directories():
    """检查必要目录"""
    print("\n[Directories] 检查目录结构...")
    
    required_dirs = [
        'static',
        'uploads'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   [OK] {directory}/")
        else:
            print(f"   [MISSING] {directory}/ 目录不存在")
            os.makedirs(directory, exist_ok=True)
            print(f"   [CREATED] 已创建 {directory}/ 目录")

def check_files():
    """检查必要文件"""
    print("\n[Files] 检查核心文件...")
    
    required_files = [
        'main.py',
        'database.py', 
        'novel_analyzer.py',
        'start_server.py',
        'static/index.html',
        'requirements.txt'
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   [OK] {file_path}")
        else:
            print(f"   [MISSING] {file_path} 文件不存在")
            all_exist = False
    
    return all_exist

def check_mongodb_config():
    """检查MongoDB配置"""
    print("\n[MongoDB] 检查MongoDB配置...")
    
    try:
        from database import Database
        print("   [OK] 数据库模块导入成功")
        
        # 检查连接字符串格式
        db = Database()
        mongodb_url = db.mongodb_url
        print(f"   [CONFIG] 连接字符串: {mongodb_url}")
        
        if "@" not in mongodb_url:
            print("   [OK] 使用无认证直连模式")
        else:
            print("   [WARNING] 使用认证连接模式")
            
        return True
        
    except Exception as e:
        print(f"   [ERROR] 数据库配置检查失败: {e}")
        return False

def check_model_config():
    """检查大模型配置"""
    print("\n[Model] 检查大模型配置...")
    
    try:
        from novel_analyzer import NovelAnalyzer
        
        # 创建临时分析器实例检查配置
        analyzer = NovelAnalyzer(None)  # 传入None因为只检查配置
        config = analyzer.model_config
        
        print(f"   [API] API地址: {config['base_url']}")
        print(f"   [KEY] API密钥: {'*' * len(config['api_key'][:8])}...")
        print(f"   [MODEL] 模型名称: {config['model_name']}")
        print("   [OK] 模型配置加载成功")
        
        return True
        
    except Exception as e:
        print(f"   [ERROR] 模型配置检查失败: {e}")
        return False

def main():
    """主检查函数"""
    print("[SYSTEM] 小说分析系统环境检查")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_dependencies,
        check_directories, 
        check_files,
        check_mongodb_config,
        check_model_config
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"   [ERROR] 检查过程中出错: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("[RESULT] 检查结果总览:")
    
    if all(results):
        print("[SUCCESS] 所有检查通过！系统可以正常运行")
        print("\n[START] 启动命令:")
        print("   python start_server.py")
        print("\n[URL] 访问地址:")
        print("   http://localhost:8000")
    else:
        print("[WARNING] 发现问题，请根据上述提示修复后重试")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
