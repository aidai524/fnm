# 项目配置说明

## 环境配置

项目使用环境变量来管理不同环境的配置。主要包含以下环境：

- development: 开发环境（默认）
- production: 生产环境

### 配置文件

项目包含以下配置文件：

- `.env.example`: 环境变量示例文件，展示所有可用的配置项
- `.env`: 本地环境配置文件（不应提交到版本控制）

### 数据库配置

所有环境的数据库配置都通过环境变量进行管理。你需要在 `.env` 文件中配置以下环境变量：

```bash
# 环境设置
ENV=development  # 或 production

# 数据库配置
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=your_db_name
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=50
DB_POOL_RECYCLE=3600
```

## 项目设置

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境：
   - 复制 `.env.example` 为 `.env`
   - 修改 `.env` 中的配置，填入正确的数据库连接信息

3. 数据库工具使用：
```bash
# 查看数据库结构和数据
python utils/db_tools.py
```

## API 文档

### 项目权重排序 API

获取按权重排序的项目列表，优先展示特定平台（如"pump"）的项目，并按时间倒序排列。

#### 接口信息

- 路径: `/projects/weighted`
- 方法: GET
- 参数:
  - `page`: 页码（从1开始）
  - `per_page`: 每页记录数（默认5）

#### 请求示例

```bash
# 获取第一页，每页5条记录
curl -X GET "http://localhost:8000/projects/weighted?page=1&per_page=5" -H "accept: application/json"

# 获取第二页，每页10条记录
curl -X GET "http://localhost:8000/projects/weighted?page=2&per_page=10" -H "accept: application/json"
```

#### 响应格式

```json
[
  {
    "id": 16765,
    "dapp": "pump",
    "time": 1740378176000,
    "share_num": 0,
    "like": 4,
    "launched_like": 0,
    "comment": 0,
    "status": 1,
    "created_at": "2025-02-24T06:23:01",
    "updated_at": "2025-02-24T06:23:04"
  }
  // ... 更多记录
]
```

#### 权重计算说明

项目权重基于以下因素计算：
1. 平台优先级：特定平台（如"pump"）的项目获得更高权重
2. 时间因素：最新的项目优先展示
3. 互动指标：考虑点赞数、评论数等用户互动数据

#### 注意事项

- API 使用分页机制，建议合理设置 per_page 参数避免返回数据过大
- 时间戳使用毫秒级 Unix 时间戳
- 所有时间相关字段均为 UTC 时间

## 注意事项

- 不要将包含敏感信息的 `.env` 文件提交到版本控制系统
- 所有环境的数据库配置都应该使用环境变量管理
- 建议定期更新数据库连接池配置以优化性能
- 确保 `.env` 文件中的敏感信息安全存储，不要泄露给未授权的人员 