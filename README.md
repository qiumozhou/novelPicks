# 小说分析系统

基于大模型的小说分层结构化分析平台，支持自动分析小说的章节、中层汇总和全书级别的详细分析。

## ✨ 功能特性

- 📚 **多层级分析**: 章节级、中层汇总、全书级三层递进分析
- 🧠 **AI驱动**: 基于大模型的智能内容分析和总结
- 💾 **MongoDB存储**: 完整的数据持久化和管理
- 🌐 **现代Web界面**: 响应式设计的原生JavaScript前端
- ⚡ **异步处理**: 后台异步分析，支持大文件处理
- 📊 **丰富指标**: 包含冲突密度、节奏分析、人物关系等多维度指标

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI**: 现代异步Web框架
- **MongoDB**: NoSQL数据库存储
- **Motor**: 异步MongoDB驱动
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI服务器

### 前端技术栈
- **原生JavaScript**: 无框架依赖
- **现代CSS**: 响应式设计和动画效果
- **RESTful API**: 前后端分离架构

## 🚀 快速开始

### 前置要求

1. **Python 3.8+**
2. **Docker** (用于运行MongoDB)
3. **大模型API接口** (需要配置API地址和密钥)

### 快速启动 (推荐)

```bash
# 1. 克隆项目
git clone <项目地址>
cd novelpicks

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 一键启动 (包含MongoDB和系统)
python quick_start.py
```

### 手动安装步骤

1. **克隆项目**
```bash
git clone <项目地址>
cd novelpicks
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动MongoDB (Docker)**
```bash
# 方式1: 使用Docker Compose
docker compose up -d mongodb

# 方式2: 使用管理脚本
python start_mongodb.py start
```

4. **配置大模型API**
编辑 `novel_analyzer.py` 中的模型配置:
```python
self.model_config = {
    "base_url": "http://your-api-url:3100/v1",
    "api_key": "your-api-key", 
    "model_name": "gpt-5-chat",
    "timeout": 120,
    "max_retries": 3
}
```

5. **启动系统**
```bash
python start_server.py
```

6. **访问应用**
- 主界面: http://localhost:8000
- API文档: http://localhost:8000/docs
- 系统状态: http://localhost:8000/api/system/status

## 📖 使用指南

### 1. 上传小说
- 支持 `.txt` 格式文件
- 可选择性设置小说标题
- 支持拖拽上传

### 2. 分析流程
系统会自动执行三层分析：

#### 第一层: 章节级分析
- 每5万字为一个分析段落
- 提取故事情节、人物关系、冲突事件
- 生成情感流向和标签体系

#### 第二层: 中层汇总
- 每10个章节为一组进行汇总
- 分析主线支线特征和冲突密度
- 评估节奏变化和人物成长

#### 第三层: 全书整合
- 综合所有中层数据
- 生成完整的作品评估指标
- 包含影视化潜力评估

### 3. 查看结果
- **全书分析**: 整体指标和核心标签
- **章组分析**: 中层汇总结果
- **章节分析**: 详细章节分解

## 🔧 API接口

### 小说管理
- `GET /api/novels` - 获取小说列表
- `POST /api/novels/upload` - 上传小说文件
- `GET /api/novels/{novel_id}` - 获取小说详情
- `DELETE /api/novels/{novel_id}` - 删除小说

### 分析功能
- `POST /api/novels/analyze/{novel_id}` - 重新分析小说
- `GET /api/novels/{novel_id}/analysis/{level}` - 获取分析结果
  - level: `chapter`、`group`、`book`

## 📊 数据结构

### 小说记录
```json
{
  "_id": "小说唯一ID",
  "title": "小说标题",
  "file_path": "文件路径",
  "status": "pending|processing|completed|failed",
  "word_count": 1000000,
  "created_at": "2023-10-17T10:00:00Z"
}
```

### 分析结果
```json
{
  "novel_id": "小说ID",
  "analysis": {
    "main_storylines": 3,
    "avg_conflict_density": 0.017,
    "total_climax_points": 21,
    "rhythm_pattern": "中快节奏",
    "character_count": 15,
    "core_tags": ["玄幻", "成长", "复仇"]
  }
}
```

## 🎯 分析指标说明

### 全书级指标
- **主线数量**: 主要故事线索统计
- **冲突密度**: 每万字冲突事件数量
- **高潮点数量**: 关键转折和高潮统计
- **节奏模式**: 平稳/起伏/快节奏/慢热
- **人物数量**: 主要角色统计
- **主角鲜明度**: 强/中/弱
- **场景适应性**: 影视化改编潜力
- **核心标签**: 作品主要标签分类

### 分析维度
- 📚 **内容分析**: 情节、人物、冲突
- 🎭 **情感分析**: 情绪氛围变化
- 🏷️ **标签提取**: 主题、类型、元素
- 📈 **指标评估**: 量化分析结果
- 🎬 **影视化评估**: 改编潜力分析

## 🔧 开发配置

### 环境变量
```bash
MONGODB_URL=mongodb://admin:admin@localhost:27017
```

### 目录结构
```
novelpicks/
├── main.py              # FastAPI主应用
├── database.py          # MongoDB数据库操作
├── novel_analyzer.py    # 小说分析核心逻辑
├── start_server.py      # 服务器启动脚本
├── requirements.txt     # Python依赖
├── static/
│   └── index.html      # 前端页面
└── uploads/            # 上传文件存储目录
```

## 🐛 故障排除

### 常见问题

1. **MongoDB连接失败**
   - 检查MongoDB服务是否启动
   - 验证用户名密码是否正确
   - 确认端口27017是否开放

2. **大模型API调用失败**
   - 检查API地址和密钥配置
   - 验证网络连接状况
   - 查看API配额和限制

3. **文件上传失败**
   - 确认文件格式为.txt
   - 检查文件编码（支持GBK/UTF-8等）
   - 验证uploads目录权限

4. **分析过程中断**
   - 检查API调用限制
   - 查看服务器日志信息
   - 验证文件内容完整性

## 📝 更新日志

### v1.0.0 (2024-10-17)
- ✅ 完成基础分析功能
- ✅ 实现MongoDB存储
- ✅ 创建Web界面
- ✅ 添加异步处理
- ✅ 支持多格式文件

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

[MIT License](LICENSE)

## 👥 联系我们

如有问题或建议，请通过以下方式联系：
- 创建Issue
- 发送邮件

---

**享受AI驱动的小说分析体验！** 📚✨
