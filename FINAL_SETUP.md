# 🎉 小说分析系统 - 完整安装指南

## ✅ 系统已完成功能

- ✅ FastAPI后端API
- ✅ MongoDB数据存储
- ✅ 原生JavaScript前端
- ✅ 小说分层分析功能
- ✅ 无认证MongoDB直连
- ✅ Docker一键部署
- ✅ 错误处理和容错机制

## 🚀 快速启动 (三步完成)

### 步骤1: 环境检查
```bash
# 检查系统环境
python check_environment.py
```

### 步骤2: 启动MongoDB (选择其中一种方式)

#### 方式A: 一键启动 (推荐)
```bash
python quick_start.py
```

#### 方式B: 手动启动
```bash
# 启动MongoDB容器
docker compose up -d mongodb

# 启动小说分析系统
python start_server.py
```

#### 方式C: 使用管理脚本
```bash
# 启动MongoDB
python start_mongodb.py start

# 启动系统
python start_server.py
```

### 步骤3: 访问系统
- 🌐 **前端界面**: http://localhost:8000
- 📖 **API文档**: http://localhost:8000/docs  
- 🔧 **系统状态**: http://localhost:8000/api/system/status

## 📋 系统功能说明

### 1. 小说上传与分析
- 支持`.txt`格式文件上传
- 自动进行三层递进分析:
  - **章节级**: 每5万字一个段落的详细分析
  - **中层汇总**: 每10个章节的汇总分析  
  - **全书级**: 整本书的综合评估

### 2. 分析指标
- 主线数量与支线特征
- 冲突密度计算
- 高潮反转点识别
- 节奏模式分析
- 人物关系评估
- 影视化潜力评估
- 受众画像分析

### 3. 数据管理
- MongoDB持久化存储
- 分层数据结构
- 完整的CRUD操作
- 实时状态监控

## 🔧 系统管理命令

### MongoDB管理
```bash
python start_mongodb.py start     # 启动MongoDB
python start_mongodb.py stop      # 停止MongoDB
python start_mongodb.py status    # 查看状态
python start_mongodb.py logs      # 查看日志
python start_mongodb.py restart   # 重启MongoDB
```

### 系统管理
```bash
python check_environment.py       # 环境检查
python start_server.py           # 启动系统
python quick_start.py            # 一键启动全部
```

## ⚙️ 配置说明

### 大模型API配置
编辑 `novel_analyzer.py` 第22-27行:
```python
self.model_config = {
    "base_url": "http://你的API地址:端口/v1",
    "api_key": "你的API密钥",
    "model_name": "模型名称",
    "timeout": 120,
    "max_retries": 3
}
```

### MongoDB连接配置  
编辑 `database.py` 第18行:
```python
# 默认无认证连接
self.mongodb_url = "mongodb://localhost:27017"

# 如需认证连接
self.mongodb_url = "mongodb://用户名:密码@主机:端口/?authSource=admin"
```

## 🐛 故障排除

### 常见问题

1. **MongoDB连接失败**
   ```bash
   # 检查Docker是否运行
   docker ps
   
   # 检查MongoDB容器状态
   docker logs novel_mongodb
   
   # 重启MongoDB
   python start_mongodb.py restart
   ```

2. **API调用失败**
   - 检查 `novel_analyzer.py` 中的API配置
   - 验证网络连接和API密钥
   - 查看服务器日志输出

3. **端口被占用**
   ```bash
   # Windows查看端口占用
   netstat -ano | findstr :8000
   
   # 修改端口: 编辑 start_server.py 第31行
   port=9000,  # 改为其他端口
   ```

4. **上传文件失败**
   - 确认文件格式为`.txt`
   - 检查文件编码(UTF-8/GBK)
   - 查看uploads目录权限

### 系统模式说明

**完整功能模式**: MongoDB连接成功
- ✅ 文件上传
- ✅ 分析处理  
- ✅ 数据存储
- ✅ 结果查看

**演示模式**: MongoDB未连接
- ❌ 文件上传 (显示配置提示)
- ❌ 分析处理
- ❌ 数据存储  
- ✅ 界面演示

## 🌟 使用流程

1. **启动系统**: `python quick_start.py`
2. **访问界面**: http://localhost:8000
3. **上传小说**: 选择`.txt`文件上传
4. **等待分析**: 后台自动进行三层分析
5. **查看结果**: 在分析详情页查看完整报告

## 📚 项目文件说明

```
novelpicks/
├── main.py                    # FastAPI主应用
├── database.py               # MongoDB数据库操作
├── novel_analyzer.py         # 小说分析核心逻辑
├── start_server.py          # 服务器启动脚本
├── quick_start.py           # 一键启动脚本
├── start_mongodb.py         # MongoDB管理脚本
├── check_environment.py     # 环境检查脚本
├── docker-compose.yml       # Docker配置
├── requirements.txt         # Python依赖
├── static/index.html       # 前端页面
├── README.md               # 项目说明
├── config_guide.md         # 配置指南
└── FINAL_SETUP.md          # 完整安装指南
```

## 🎯 下一步

系统已完全就绪! 现在你可以:

1. 配置你的大模型API
2. 启动系统: `python quick_start.py`
3. 上传小说文件进行分析
4. 查看详细的分析报告

如需帮助，请查看各个配置文件中的详细说明。

---
**🚀 享受AI驱动的小说分析体验！**
