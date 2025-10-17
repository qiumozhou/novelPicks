# 📋 系统配置指南

## 🚀 快速配置步骤

### 1. 安装Python依赖
```bash
pip install -r requirements.txt
```

### 2. 配置MongoDB数据库

#### 选项A: 使用Docker Compose (推荐)
```bash
# 使用项目提供的docker-compose.yml
docker compose up -d mongodb

# 或使用管理脚本
python start_mongodb.py start
```

#### 选项B: 使用Docker直接运行
```bash
# 启动MongoDB容器 (无认证)
docker run -d \
  --name novel_mongodb \
  -p 27017:27017 \
  mongo:latest
```

#### 选项C: 本地安装MongoDB
1. 下载并安装MongoDB
2. 启动MongoDB服务 (无认证模式)
```bash
mongod --noauth
```

### 3. 配置大模型API

编辑 `novel_analyzer.py` 文件第22-27行:

```python
self.model_config = {
    "base_url": "http://你的API地址:端口/v1",    # 替换为实际API地址
    "api_key": "你的API密钥",                    # 替换为实际API密钥
    "model_name": "模型名称",                    # 如 gpt-4, gpt-3.5-turbo等
    "timeout": 120,                             # 请求超时时间(秒)
    "max_retries": 3                           # 最大重试次数
}
```

### 4. 环境检查
```bash
# 运行环境检查脚本
python check_environment.py
```

### 5. 启动系统
```bash
# 启动服务器
python start_server.py
```

## 🔧 高级配置

### 自定义MongoDB连接
编辑 `database.py` 文件第18行:
```python
# 无认证连接
self.mongodb_url = "mongodb://主机:端口"

# 认证连接 (如需要)
self.mongodb_url = "mongodb://用户名:密码@主机:端口/?authSource=admin"
```

### 自定义服务器端口
编辑 `start_server.py` 文件第26行:
```python
port=你的端口号,  # 默认8000
```

### 文件上传大小限制
在 `main.py` 中添加:
```python
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]
)
```

## 🌍 环境变量配置

创建 `.env` 文件:
```bash
# MongoDB配置
MONGODB_URL=mongodb://admin:admin@localhost:27017

# 模型API配置  
MODEL_BASE_URL=http://your-api-url:3100/v1
MODEL_API_KEY=your-api-key
MODEL_NAME=gpt-5-chat

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## 🐛 常见问题解决

### MongoDB连接失败
```bash
# 检查MongoDB服务状态
sudo systemctl status mongod

# 重启MongoDB服务
sudo systemctl restart mongod
```

### API调用失败
1. 检查网络连接
2. 验证API密钥有效性
3. 确认API配额未超限
4. 查看防火墙设置

### 端口被占用
```bash
# 查看端口占用
netstat -tulpn | grep :8000

# 杀死占用进程
sudo kill -9 进程ID
```

## 📊 性能优化

### 1. 数据库索引
系统会自动创建必要的索引，但可以手动优化:
```javascript
// 在MongoDB中执行
db.novels.createIndex({title: "text"})
db.chapter_analysis.createIndex({novel_id: 1, segment_number: 1})
```

### 2. 文件处理
- 建议小说文件大小不超过50MB
- 使用UTF-8编码保存文件
- 定期清理uploads目录

### 3. 内存管理
```python
# 在novel_analyzer.py中调整段落大小
segment_size = 30000  # 减少内存占用
```

## 🔒 安全配置

### 1. 数据库安全
```javascript
// 创建专用数据库用户
use novel_analysis
db.createUser({
  user: "novel_user",
  pwd: "secure_password",
  roles: ["readWrite"]
})
```

### 2. API安全
在生产环境中添加认证:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.middleware("http")
async def authenticate(request: Request, call_next):
    # 添加认证逻辑
    response = await call_next(request)
    return response
```

## 📈 监控配置

### 1. 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('novel_analysis.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 健康检查
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

---

完成配置后，运行 `python check_environment.py` 验证所有设置是否正确！
