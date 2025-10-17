# 🔧 调试指南 - 解决上传后pending状态问题

## 问题诊断

如果上传后小说一直显示pending状态，请按以下步骤排查：

### 1. 检查系统状态
访问: http://localhost:8000/api/system/status

应该返回：
```json
{
  "database_connected": true,
  "system_mode": "完整功能"
}
```

### 2. 检查调试信息
访问: http://localhost:8000/api/debug/logs

查看：
- uploads_directory: 应该是 "uploads"
- uploads_files: 应该包含上传的文件
- database_connected: 应该是 true

### 3. 检查控制台日志

启动服务器时应该看到：
```
[START] 启动小说分析系统...
[SETUP] 目录检查完成
[SERVER] 服务器启动中...
[URL] 访问地址: http://localhost:8000
```

上传文件时应该看到：
```
✅ 小说记录已创建: novel-id-123
🚀 启动后台分析任务: novel-id-123
📋 分析任务已添加到后台队列
```

### 4. 手动测试分析

如果后台任务没有启动，可以手动测试：

#### 方法A: 使用测试API
```bash
curl -X POST http://localhost:8000/api/test/analyze
```

#### 方法B: 使用测试脚本
```bash
python test_analysis.py
```

#### 方法C: 手动触发分析
在前端点击"重新分析"按钮

## 常见问题解决

### 问题1: 数据库未连接
**症状**: 上传时提示"数据库未连接"
**解决**: 
```bash
# 启动MongoDB
docker compose up -d mongodb
# 或
python start_mongodb.py start
```

### 问题2: 后台任务没有启动
**症状**: 上传成功但没有分析日志
**解决**: 
1. 检查控制台是否有错误
2. 重启服务器
3. 使用测试脚本验证

### 问题3: 文件上传失败
**症状**: 上传时出现错误
**解决**:
1. 检查文件格式(.txt)
2. 检查文件大小(不要太大)
3. 检查uploads目录权限

### 问题4: 模型API调用失败
**症状**: 分析过程中断
**解决**:
1. 检查novel_analyzer.py中的API配置
2. 验证网络连接
3. 检查API密钥和配额

## 调试步骤

### 步骤1: 环境检查
```bash
python check_environment.py
```

### 步骤2: 启动MongoDB
```bash
python start_mongodb.py start
```

### 步骤3: 启动系统
```bash
python start_server.py
```

### 步骤4: 测试上传
1. 访问 http://localhost:8000
2. 上传一个小的.txt文件
3. 观察控制台日志

### 步骤5: 手动测试
```bash
python test_analysis.py
```

## 日志说明

### 正常的上传日志
```
✅ 小说记录已创建: novel-id-123
🚀 启动后台分析任务: novel-id-123
📋 分析任务已添加到后台队列
```

### 正常的分析日志
```
============================================================
🚀 后台任务启动: 分析小说
📚 小说ID: novel-id-123
📁 文件路径: uploads/novel-id-123_小说.txt
⏰ 开始时间: 2024-10-17 15:30:00
🔧 数据库状态: 已连接
============================================================
✅ 小说状态已更新为: processing
```

## 联系支持

如果问题仍然存在，请提供：
1. 控制台完整日志
2. 系统状态API返回结果
3. 调试信息API返回结果
4. 使用的操作系统和Python版本
