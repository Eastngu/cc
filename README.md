# 电镀工厂 ERP 财务系统

一套面向电镀加工厂的 Web 端 ERP 财务管理系统，聚焦**应收应付管理**和**成本核算**，支持多角色多权限访问。

## 功能模块

| 模块 | 功能 |
|------|------|
| 经营看板 | 本月收入/支出/利润、趋势图、客户应收TOP5 |
| 订单管理 | 订单录入、状态跟踪（待加工→加工中→已完工→已出货） |
| 财务管理 | 应收账款、应付账款、收付款登记、月度对账单 |
| 成本核算 | 按订单录入成本（材料/电费/人工/其他），自动计算利润率 |
| 系统设置 | 客户管理、镀种工艺配置、计费规则、用户权限 |

## 技术栈

- **后端**：Python 3.8+ / Django 4.2 / Django REST Framework / JWT 认证
- **前端**：Vue 3 / Element Plus / Pinia / Axios / Vite
- **数据库**：MySQL 8.0（生产） / SQLite（开发）

## 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- Git

### 1. 拉取代码

```bash
git clone https://github.com/Eastngu/cc.git
cd cc
```

### 2. 后端部署

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 填充演示数据
python manage.py seed_demo

# 启动后端服务
python manage.py runserver 0.0.0.0:8000
```

### 3. 前端构建

```bash
cd ../frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

构建完成后，Django 会自动从 `frontend/dist/` 提供前端页面服务。

### 4. 访问系统

浏览器打开：**http://localhost:8000**

### 演示账号

| 用户名 | 密码 | 角色 | 权限说明 |
|--------|------|------|---------|
| admin | admin123 | 老板 | 全部模块查看 + 审批 |
| caiwu | caiwu123 | 财务 | 应收应付、收付款、对账单、成本、报表 |
| chejian | chejian123 | 车间主管 | 订单查看、来料/出货登记 |

## 生产环境部署

### 使用 MySQL

```bash
# 安装 MySQL 客户端
pip install mysqlclient

# 设置环境变量
export DJANGO_SECRET_KEY='your-random-secret-key'
export DB_NAME='electroplating_erp'
export DB_USER='your_db_user'
export DB_PASSWORD='your_db_password'
export DB_HOST='127.0.0.1'
export DB_PORT='3306'
```

### 创建生产配置

创建 `backend/config/settings/prod.py`：

```python
from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'your-server-ip']
CORS_ALLOWED_ORIGINS = ['https://your-domain.com']

# 使用 MySQL（环境变量已在 base.py 中配置）
```

### 使用 Gunicorn 启动

```bash
pip install gunicorn

# 启动服务
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --env DJANGO_SETTINGS_MODULE=config.settings.prod
```

### Nginx 反向代理（推荐）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /assets/ {
        alias /path/to/cc/frontend/dist/assets/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 项目结构

```
cc/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/              # Django 配置
│   │   ├── settings/
│   │   │   ├── base.py      # 基础配置
│   │   │   └── dev.py       # 开发环境
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       ├── users/           # 用户 & 权限
│       ├── customers/       # 客户管理
│       ├── processes/       # 工艺 & 计费配置
│       ├── orders/          # 订单管理
│       ├── finance/         # 应收应付 & 对账单
│       ├── costing/         # 成本核算
│       └── reports/         # 报表统计
├── frontend/
│   ├── src/
│   │   ├── api/             # API 请求封装
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── router/          # 路由 & 权限守卫
│   │   ├── views/           # 页面组件
│   │   └── utils/           # 工具函数
│   ├── package.json
│   └── vite.config.js
└── docs/                    # 设计文档 & 实施计划
```

## API 文档

所有 API 以 `/api/v1/` 为前缀，使用 JWT Bearer Token 认证。

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | POST /api/v1/auth/login/ | 登录获取 Token |
| 认证 | POST /api/v1/auth/refresh/ | 刷新 Token |
| 认证 | GET /api/v1/auth/me/ | 当前用户信息 |
| 客户 | /api/v1/customers/ | 客户 CRUD |
| 工艺 | /api/v1/processes/ | 镀种工艺 CRUD |
| 计费 | /api/v1/pricing-rules/ | 计费规则 CRUD |
| 订单 | /api/v1/orders/ | 订单 CRUD |
| 订单 | PATCH /api/v1/orders/{id}/status/ | 变更订单状态 |
| 应收 | /api/v1/receivables/ | 应收账款管理 |
| 应付 | /api/v1/payables/ | 应付账款管理 |
| 收付款 | /api/v1/payments/ | 收付款记录 |
| 对账单 | /api/v1/statements/ | 月度对账单 |
| 对账单 | POST /api/v1/statements/generate/ | 生成对账单 |
| 对账单 | PATCH /api/v1/statements/{id}/confirm/ | 确认对账单 |
| 成本 | /api/v1/costing/ | 订单成本 CRUD |
| 成本 | GET /api/v1/costing/summary/ | 成本汇总 |
| 报表 | GET /api/v1/reports/dashboard/ | 经营看板数据 |
| 报表 | GET /api/v1/reports/revenue-trend/ | 收入趋势 |
| 报表 | GET /api/v1/reports/customer-analysis/ | 客户分析 |
| 报表 | GET /api/v1/reports/cost-analysis/ | 成本分析 |

## 开发

### 运行测试

```bash
cd backend
pip install pytest pytest-django
python -m pytest -v
```

### 前端开发模式

```bash
cd frontend
npm run dev
```

开发模式下前端运行在 3000 端口，API 请求自动代理到后端 8000 端口。

## License

MIT
