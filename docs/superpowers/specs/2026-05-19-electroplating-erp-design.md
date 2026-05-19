# 电镀工厂 ERP 财务系统 - 设计文档

## 1. 项目概述

为电镀工厂构建一套 Web 端 ERP 财务管理系统，解决当前纯手工/Excel 管理的效率和准确性问题。系统聚焦 **应收应付管理** 和 **成本核算** 两大核心功能，支持多角色多权限访问。

### 1.1 核心目标

- 实现订单全生命周期管理（来料 → 加工 → 出货 → 对账 → 回款）
- 自动化月度对账单生成，减少人工对账工作量
- 按订单/批次和按客户/月度两个维度进行成本核算
- 提供经营概览看板，让管理层实时了解经营状况

### 1.2 用户角色

| 角色 | 使用场景 | 权限范围 |
|------|---------|---------|
| 老板/管理层 | 查看经营数据、审批 | 全模块只读 + 审批权限 |
| 财务人员 | 日常财务操作 | 应收应付、收付款、对账单、成本、报表 |
| 车间主管 | 生产过程管理 | 订单查看、来料/出货登记、报工 |

### 1.3 业务特点

- **计费模式**：混合计费（按面积/重量/件数，不同产品工艺使用不同方式）
- **镀种范围**：几种常见镀种（镀锌、镀镍、镀铬等）
- **客户模式**：少量大客户，长期合作，月结对账
- **数据规模**：10-20 人使用，月订单几百到上千单

## 2. 技术架构

### 2.1 技术选型

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 后端框架 | Django + DRF | Django 4.2 LTS | 稳定、权限系统完善 |
| 数据库 | MySQL | 8.0+ | 运维成熟 |
| 前端框架 | Vue 3 | 3.x | 组合式 API，响应式 |
| UI 组件库 | Element Plus | 最新稳定版 | 表格/表单组件丰富 |
| 构建工具 | Vite | 5.x | 快速热更新 |
| 图表库 | ECharts | 5.x | 功能强大，中文友好 |
| HTTP 客户端 | Axios | 最新 | 拦截器、Token 管理 |
| 状态管理 | Pinia | 最新 | Vue 3 官方推荐 |
| 认证方式 | JWT | djangorestframework-simplejwt | 无状态、前后端分离友好 |
| Excel 导出 | openpyxl | 最新 | 对账单/报表导出 |
| PDF 导出 | WeasyPrint | 最新 | 对账单打印 |
| Python | 3.11+ | — | 类型提示、性能提升 |

### 2.2 系统架构

```
┌─────────────────────────────────────────────────┐
│           浏览器 (Vue 3 + Element Plus)           │
│      老板看板 │ 财务操作台 │ 车间终端             │
└────────────────────────┬────────────────────────┘
                         │ HTTP / REST API (JWT)
┌────────────────────────▼────────────────────────┐
│             Django + DRF 后端                     │
│   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │
│   │ 认证 & │ │ 订单   │ │ 应收   │ │ 成本   │  │
│   │ 权限   │ │ 管理   │ │ 应付   │ │ 核算   │  │
│   └────────┘ └────────┘ └────────┘ └────────┘  │
└────────────────────────┬────────────────────────┘
                         │ ORM
┌────────────────────────▼────────────────────────┐
│                MySQL 数据库                       │
│     客户 │ 订单 │ 财务凭证 │ 对账 │ 成本        │
└─────────────────────────────────────────────────┘
```

### 2.3 项目目录结构

```
electroplating-erp/
├── backend/
│   ├── manage.py
│   ├── config/                  # Django 项目配置
│   │   ├── settings/
│   │   │   ├── base.py          # 基础配置
│   │   │   ├── dev.py           # 开发环境
│   │   │   └── prod.py         # 生产环境
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/               # 用户 & 权限
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── permissions.py
│   │   ├── customers/           # 客户档案
│   │   ├── orders/              # 订单管理
│   │   ├── finance/             # 应收应付 & 收付款
│   │   ├── costing/             # 成本核算
│   │   └── reports/             # 报表统计
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/               # 页面组件
│   │   │   ├── dashboard/       # 经营看板
│   │   │   ├── orders/          # 订单管理
│   │   │   ├── finance/         # 财务管理
│   │   │   ├── reports/         # 报表中心
│   │   │   └── settings/        # 系统设置
│   │   ├── components/          # 公共组件
│   │   ├── api/                 # API 请求封装
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── router/              # 路由 & 权限守卫
│   │   └── utils/               # 工具函数
│   ├── package.json
│   └── vite.config.js
└── docs/                        # 文档
```

## 3. 数据模型

### 3.1 用户与权限

```
User (用户)
├── id: int (PK)
├── username: varchar(50)
├── password: varchar(128) (哈希)
├── real_name: varchar(20)
├── role: enum('boss', 'finance', 'workshop')
├── phone: varchar(11)
├── is_active: boolean
├── created_at: datetime
└── updated_at: datetime
```

### 3.2 客户档案

```
Customer (客户)
├── id: int (PK)
├── name: varchar(100)
├── short_name: varchar(20) (简称)
├── contact_person: varchar(20)
├── phone: varchar(20)
├── address: varchar(200)
├── payment_terms: int (月结天数，如 30/60/90)
├── default_billing_type: enum('area', 'weight', 'piece')
├── remark: text
├── is_active: boolean
├── created_at: datetime
└── updated_at: datetime
```

### 3.3 工艺与计费

```
PlatingProcess (镀种工艺)
├── id: int (PK)
├── name: varchar(50) (如"镀锌"、"镀镍"、"镀铬")
├── code: varchar(20) (编码)
├── unit: enum('area', 'weight', 'piece')
├── base_price: decimal(10,2) (基础单价)
├── description: text
└── is_active: boolean

PricingRule (计费规则)
├── id: int (PK)
├── customer_id: int (FK → Customer，可为空表示通用)
├── plating_process_id: int (FK → PlatingProcess)
├── unit_price: decimal(10,4) (该客户该工艺的单价)
├── min_charge: decimal(10,2) (最低收费)
├── effective_date: date
└── remark: text
```

### 3.4 订单管理

```
Order (订单)
├── id: int (PK)
├── order_no: varchar(20) (单号，自动生成)
├── customer_id: int (FK → Customer)
├── plating_process_id: int (FK → PlatingProcess)
├── product_name: varchar(100) (产品名称)
├── product_spec: varchar(100) (规格型号)
├── quantity: decimal(12,2) (数量)
├── unit: varchar(10) (单位：dm²/kg/件)
├── unit_price: decimal(10,4) (单价)
├── total_amount: decimal(12,2) (订单金额)
├── status: enum('pending','processing','completed','shipped')
├── received_at: date (来料日期)
├── completed_at: date (完工日期)
├── shipped_at: date (出货日期)
├── remark: text
├── created_by: int (FK → User)
├── created_at: datetime
└── updated_at: datetime
```

### 3.5 成本核算

```
OrderCost (订单成本)
├── id: int (PK)
├── order_id: int (FK → Order, unique)
├── material_cost: decimal(10,2) (材料费)
├── electricity_cost: decimal(10,2) (电费)
├── labor_cost: decimal(10,2) (人工费)
├── other_cost: decimal(10,2) (其他费用)
├── total_cost: decimal(10,2) (总成本)
├── profit: decimal(10,2) (利润 = 订单金额 - 总成本)
├── profit_rate: decimal(5,2) (利润率 %)
├── remark: text
├── created_at: datetime
└── updated_at: datetime
```

### 3.6 应收应付

```
Receivable (应收账款)
├── id: int (PK)
├── receivable_no: varchar(20) (应收单号)
├── customer_id: int (FK → Customer)
├── year: int
├── month: int
├── total_amount: decimal(12,2) (应收总额)
├── received_amount: decimal(12,2) (已收金额)
├── balance: decimal(12,2) (余额)
├── status: enum('open', 'partial', 'settled')
├── due_date: date (到期日)
├── created_at: datetime
└── updated_at: datetime

Payable (应付账款)
├── id: int (PK)
├── payable_no: varchar(20)
├── supplier_name: varchar(100) (供应商)
├── category: varchar(50) (类别：原料/电费/设备/其他)
├── total_amount: decimal(12,2)
├── paid_amount: decimal(12,2)
├── balance: decimal(12,2)
├── status: enum('open', 'partial', 'settled')
├── due_date: date
├── created_at: datetime
└── updated_at: datetime
```

### 3.7 收付款记录

```
Payment (收付款记录)
├── id: int (PK)
├── payment_no: varchar(20) (流水号)
├── type: enum('receive', 'pay') (收款/付款)
├── customer_id: int (FK → Customer, nullable)
├── receivable_id: int (FK → Receivable, nullable)
├── payable_id: int (FK → Payable, nullable)
├── amount: decimal(12,2)
├── payment_method: enum('transfer', 'cash', 'acceptance') (转账/现金/承兑)
├── payment_date: date
├── remark: text
├── created_by: int (FK → User)
├── created_at: datetime
└── updated_at: datetime
```

### 3.8 月度对账单

```
MonthlyStatement (月度对账单)
├── id: int (PK)
├── statement_no: varchar(20) (对账单号)
├── customer_id: int (FK → Customer)
├── year: int
├── month: int
├── total_amount: decimal(12,2) (合计金额)
├── adjustment: decimal(10,2) (调整金额：退货/折让)
├── final_amount: decimal(12,2) (最终金额)
├── status: enum('draft', 'confirmed', 'sent')
├── confirmed_by: int (FK → User, nullable)
├── confirmed_at: datetime
├── created_at: datetime
└── updated_at: datetime

StatementOrder (对账单-订单关联)
├── id: int (PK)
├── statement_id: int (FK → MonthlyStatement)
└── order_id: int (FK → Order)
```

### 3.9 表关系总结

```
Customer 1──N Order
Customer 1──N Receivable
Customer 1──N MonthlyStatement
PlatingProcess 1──N Order
Order 1──1 OrderCost
Order N──N MonthlyStatement (通过 StatementOrder)
Receivable 1──N Payment (收款)
Payable 1──N Payment (付款)
User 1──N Order (created_by)
User 1──N Payment (created_by)
```

## 4. 核心业务流程

### 4.1 订单到回款主线

```
来料登记 → 创建订单(pending) → 加工生产(processing) → 报工完成(completed) → 出货登记(shipped)
                                                                                    │
                                                                                    ▼
                                                          月底汇总当月已出货订单 → 生成对账单(draft)
                                                                                    │
                                                                                    ▼
                                                          财务审核 → 确认(confirmed) → 发送客户(sent)
                                                                                    │
                                                                                    ▼
                                                          生成应收账款(open) → 客户回款 → 核销(settled)
```

### 4.2 成本核算流程

1. 订单状态变为"已完工"时，触发成本录入
2. 成本项：
   - **材料费**：根据镀种 + 数量 × 单位成本系数（可手动调整）
   - **电费**：按比例分摊或手动录入
   - **人工费**：按比例分摊或手动录入
   - **其他费用**：手动录入
3. 系统自动计算：总成本 = 各项之和，利润 = 订单金额 - 总成本
4. 支持按客户/月度汇总查看

### 4.3 月度对账流程

1. 每月初，系统自动汇总上月各客户已出货订单
2. 财务人员审核金额，可添加调整项（退货、折让等）
3. 确认后生成正式对账单，支持导出 Excel/PDF
4. 对账单确认后，自动生成对应的应收账款记录
5. 应收账款开始计算账龄，到期提醒

### 4.4 收款核销流程

1. 收到客户回款，登记收款记录
2. 选择关联的应收单进行核销
3. 部分回款：应收状态变为"部分回款"，更新余额
4. 全额回款：应收状态变为"已结清"

## 5. 前端页面设计

### 5.1 页面导航结构

```
侧边栏导航
├── 经营看板（首页）
├── 订单管理
│   ├── 订单列表
│   └── 新建订单
├── 财务管理
│   ├── 应收账款
│   ├── 应付账款
│   ├── 收付款登记
│   └── 月度对账单
├── 报表中心
│   ├── 经营概览
│   ├── 客户分析
│   └── 成本分析
└── 系统设置
    ├── 客户管理
    ├── 镀种/工艺配置
    ├── 计费规则
    └── 用户与权限
```

### 5.2 经营看板（首页）

**顶部统计卡片**：本月收入、本月支出、本月利润、应收余额（含环比变化）

**中部图表**：近 6 个月收入/利润趋势折线图（ECharts）

**底部双栏**：
- 左侧：最近订单动态（最新 10 条）
- 右侧：客户应收 TOP5 排名

### 5.3 核心页面说明

**订单列表页**：
- 筛选条件：客户、状态、镀种、日期范围
- 表格列：单号、客户、产品、镀种、数量、金额、状态、日期
- 操作：查看详情、编辑、状态变更、录入成本

**应收账款页**：
- 筛选条件：客户、状态、账期月份
- 表格列：应收单号、客户、账期、应收金额、已收、余额、状态、到期日
- 操作：查看明细、登记收款、标记结清

**月度对账单页**：
- 操作流程：选择客户+月份 → 自动拉取订单 → 审核调整 → 确认 → 导出
- 导出格式：Excel、PDF（含公司抬头、明细、合计）

## 6. 权限设计

### 6.1 权限矩阵

| 功能 | 老板 | 财务 | 车间主管 |
|------|------|------|---------|
| 经营看板 | ✅ 查看 | ✅ 查看 | ❌ |
| 订单列表 | ✅ 查看 | ✅ 查看 | ✅ 查看+操作 |
| 新建订单 | ❌ | ❌ | ✅ |
| 来料/出货 | ❌ | ❌ | ✅ |
| 应收应付 | ✅ 查看 | ✅ 查看+操作 | ❌ |
| 收付款 | ✅ 查看 | ✅ 操作 | ❌ |
| 对账单 | ✅ 查看+审批 | ✅ 操作 | ❌ |
| 成本核算 | ✅ 查看 | ✅ 录入 | ❌ |
| 报表 | ✅ 全部 | ✅ 全部 | ❌ |
| 系统设置 | ✅ 全部 | ✅ 客户/计费 | ❌ |
| 用户管理 | ✅ | ❌ | ❌ |

### 6.2 实现方式

使用 Django 内置的 Group + Permission 机制：
- 创建 3 个用户组：boss、finance、workshop
- 每个 API 接口通过 DRF permission_classes 控制访问
- 前端路由守卫根据角色动态生成菜单

## 7. API 设计概要

### 7.1 认证

```
POST /api/auth/login/          # 登录，返回 JWT
POST /api/auth/refresh/        # 刷新 Token
GET  /api/auth/me/             # 当前用户信息
```

### 7.2 客户

```
GET    /api/customers/          # 客户列表（分页、搜索）
POST   /api/customers/          # 创建客户
GET    /api/customers/{id}/     # 客户详情
PUT    /api/customers/{id}/     # 更新客户
DELETE /api/customers/{id}/     # 删除客户（软删除）
```

### 7.3 订单

```
GET    /api/orders/             # 订单列表（筛选、分页）
POST   /api/orders/             # 创建订单
GET    /api/orders/{id}/        # 订单详情
PUT    /api/orders/{id}/        # 更新订单
PATCH  /api/orders/{id}/status/ # 变更订单状态
```

### 7.4 成本

```
GET    /api/orders/{id}/cost/   # 获取订单成本
POST   /api/orders/{id}/cost/   # 录入/更新订单成本
GET    /api/costing/summary/    # 成本汇总（按客户/月份筛选）
```

### 7.5 财务

```
GET    /api/receivables/            # 应收列表
GET    /api/receivables/{id}/       # 应收详情
POST   /api/payments/               # 登记收付款
GET    /api/payments/               # 收付款记录列表

GET    /api/statements/             # 对账单列表
POST   /api/statements/generate/    # 生成对账单
PUT    /api/statements/{id}/        # 编辑对账单
PATCH  /api/statements/{id}/confirm/ # 确认对账单
GET    /api/statements/{id}/export/ # 导出对账单(Excel/PDF)

GET    /api/payables/               # 应付列表
POST   /api/payables/               # 创建应付
```

### 7.6 报表

```
GET /api/reports/dashboard/         # 看板数据
GET /api/reports/revenue-trend/     # 收入趋势
GET /api/reports/customer-analysis/ # 客户分析
GET /api/reports/cost-analysis/     # 成本分析
```

## 8. 非功能性需求

### 8.1 安全性

- JWT Token 有效期 2 小时，Refresh Token 7 天
- 密码使用 Django 默认的 PBKDF2 哈希
- API 接口全部需要认证（登录接口除外）
- 敏感操作（删除、审批）记录操作日志

### 8.2 性能

- 列表接口分页，默认每页 20 条
- 报表数据做缓存（Redis 可选，初期可不加）
- 数据库关键字段加索引（customer_id, status, created_at 等）

### 8.3 可扩展性

- Django App 模块化，后续可独立新增模块（如药水管理、质检管理）
- API 版本化（/api/v1/）预留升级空间
- 前端路由和菜单配置化，新增模块无需改动框架代码

## 9. 开发计划概要

| 阶段 | 内容 | 预计时间 |
|------|------|---------|
| 第一阶段 | 项目搭建 + 用户认证 + 客户管理 | — |
| 第二阶段 | 工艺配置 + 订单管理 | — |
| 第三阶段 | 应收应付 + 收付款 | — |
| 第四阶段 | 月度对账单 | — |
| 第五阶段 | 成本核算 | — |
| 第六阶段 | 报表看板 | — |
| 第七阶段 | 权限完善 + 测试 + 优化 | — |
