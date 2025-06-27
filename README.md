# 🎫 智能机票预订系统 (Smart Flight Booking System)

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)](https://sqlite.org)
[![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-GPT--4.1-orange.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

这是一个基于**多智能体协作**架构和**MCP（Model Context Protocol）**的智能机票预订系统。系统通过两个协作的AI Agent实现完整的机票查询、预订和管理功能，展示了现代AI Agent间通信和协作的最佳实践。

## 📖 目录

- [🏗️ 系统架构](#️-系统架构)
- [✨ 核心功能](#-核心功能)
- [🛠️ 技术栈](#️-技术栈)
- [🚀 快速开始](#-快速开始)
- [⚙️ 配置说明](#️-配置说明)
- [🎮 使用指南](#-使用指南)
- [📚 API文档](#-api文档)
- [🔧 开发指南](#-开发指南)
- [🌟 项目亮点](#-项目亮点)
- [🔧 故障排除](#-故障排除)

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                智能机票预订系统架构图                              │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐              ┌─────────────────┐
    │  智能Agent 1    │◄────────────►│  智能Agent 2    │
    │ 预订管理助手     │   MCP协议通信  │ 航班查询助手     │
    │                 │              │                 │
    │ ✓ 创建预订       │              │ ✓ 查询航班       │
    │ ✓ 查询预订       │              │ ✓ 搜索航线       │
    │ ✓ 修改预订       │              │ ✓ 价格查询       │
    │ ✓ 删除预订       │              │ ✓ 座位查询       │
    │ ✓ AI对话        │              │ ✓ 智能推荐       │
    └─────────┬───────┘              └─────────┬───────┘
              │                                │
              │         MCP Protocol           │
              │                                │
        ┌─────▼────────────────────────────────▼─────┐
        │            MCP HTTP Server                │
        │                                           │
        │  FastAPI + RESTful APIs                   │
        │  ┌─────────────────────────────────────┐  │
        │  │ Booking APIs    │ Flight APIs       │  │
        │  │ POST /bookings  │ GET /flights      │  │
        │  │ GET /bookings   │ GET /flights/{id} │  │
        │  │ PUT /bookings   │ POST /flights     │  │
        │  │ DELETE /booking │ DELETE /flights   │  │
        │  └─────────────────────────────────────┘  │
        └─────────────────┬─────────────────────────┘
                          │
                    ┌─────▼─────┐      ┌─────────────┐
                    │  SQLite   │      │ Azure OpenAI│
                    │ Database  │      │   GPT-4.1   │
                    │           │      │             │
                    │📋 bookings│      │🤖 智能对话   │
                    │✈️ flights │      │💬 自然语言   │
                    └───────────┘      └─────────────┘
```

### 核心组件说明

| 组件 | 职责 | 技术实现 |
|------|------|----------|
| **预订管理Agent** | 处理所有预订相关操作，提供智能对话接口 | Python + Azure OpenAI |
| **航班查询Agent** | 管理航班信息，提供查询和推荐服务 | Python + 智能算法 |
| **MCP HTTP Server** | 提供标准化API接口，处理Agent间通信 | FastAPI + Pydantic |
| **SQLite数据库** | 轻量级数据持久化存储 | 本地文件数据库 |
| **Azure OpenAI** | 提供GPT-4.1智能对话能力 | Azure认知服务 |

## ✨ 核心功能

### 🎫 智能Agent 1: 预订管理助手
- **🆕 创建预订**: 完整的预订信息录入和验证
- **🔍 查询预订**: 按ID或乘客姓名搜索预订
- **✏️ 修改预订**: 更新座位、状态等信息
- **🗑️ 删除预订**: 安全的预订取消功能
- **🤖 智能对话**: 基于Azure OpenAI的自然语言理解

### ✈️ 智能Agent 2: 航班查询助手
- **🔍 航班查询**: 实时航班信息获取
- **🗺️ 航线搜索**: 出发地到目的地查询
- **🏢 航空公司筛选**: 按航空公司分类查询
- **💺 座位查询**: 实时座位可用性检查
- **🎯 智能推荐**: 基于AI的个性化推荐

### 🔄 多Agent协作功能
- **智能工作流编排**: 自动任务分配和结果聚合
- **数据一致性保证**: 跨Agent的事务管理
- **实时状态同步**: Agent间的状态信息共享
- **容错机制**: 失败重试和降级处理

## 🛠️ 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.13+ | 主要编程语言 |
| **FastAPI** | 0.115.14 | Web框架和API服务 |
| **SQLAlchemy** | 2.0.41 | ORM和数据库操作 |
| **Pydantic** | 2.11.7 | 数据验证和序列化 |
| **Uvicorn** | 0.34.3 | ASGI服务器 |

### 数据存储
| 技术 | 版本 | 用途 |
|------|------|------|
| **SQLite** | 3 | 轻量级本地数据库 |

### AI和外部服务
| 服务 | 模型 | 用途 |
|------|------|------|
| **Azure OpenAI** | GPT-4.1 | 智能对话和自然语言处理 |

## 🚀 快速开始

### 前置要求
- **Python 3.13+**: 运行应用程序
- **Azure OpenAI账户**: 获取API密钥

### 一键启动

```bash
# 克隆项目
git clone <your-repo-url>
cd A2A-ticketbooking

# 一键启动整个系统（推荐）
./start_system.sh
```

### 手动启动

如果一键启动失败，可以手动执行：

```bash
# 1. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install fastapi uvicorn pydantic openai requests python-dotenv sqlalchemy alembic

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置您的Azure OpenAI配置

# 4. 初始化数据库
python init_db.py

# 5. 启动MCP服务器
python mcp_server.py
```

系统启动成功后，您会看到：
```
🚀 启动MCP服务器...
📍 地址: http://localhost:8000
📖 API文档: http://localhost:8000/docs
```

## ⚙️ 配置说明

### 环境配置

编辑 `.env` 文件设置配置：

```env
# Azure OpenAI 配置
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview
AZURE_OPENAI_API_KEY=your-api-key-here

# 数据库配置
DATABASE_URL=sqlite:///./smart_flight_booking.db

# MCP Server 配置
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
```

### Azure OpenAI 配置步骤

1. 登录 [Azure Portal](https://portal.azure.com)
2. 创建或选择 Azure OpenAI 资源
3. 部署 GPT-4.1 模型
4. 获取 API 密钥和端点地址
5. 更新 `.env` 文件中的配置

## 🎮 使用指南

### 快速演示

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行快速演示脚本
python quick_demo.py
```

### 运行智能助手

#### 1. 预订管理助手
```bash
source venv/bin/activate
python booking_agent.py
```

**交互示例:**
```
🎫 智能预订管理助手
============================================================

请输入命令或询问: create
📝 创建新预订
------------------------------
预订标题: 张三的商务出差
乘客姓名: 张三
航班号: CA1001
...
✅ 预订创建成功！预订ID: 1

请输入命令或询问: 帮我查找张三的所有预订
🤖 AI助手: 我来帮您查找张三的所有预订记录...
```

#### 2. 航班查询助手
```bash
source venv/bin/activate
python airline_agent.py
```

**交互示例:**
```
✈️ 智能航班查询助手
============================================================

请输入命令或询问: search PEK SHA
🔍 搜索航班: PEK → SHA
------------------------------------------------------------
航班号      航空公司         出发时间    到达时间    价格      余票
------------------------------------------------------------
CA1001     中国国际航空      08:30:00   10:45:00   ¥680      120

请输入命令或询问: 推荐一些从北京到上海的便宜航班
🤖 AI助手: 根据您的需求，我为您推荐以下航班...
```

#### 3. 多Agent协作演示
```bash
source venv/bin/activate
python agent_communication_demo.py
```

### 系统状态检查
```bash
source venv/bin/activate
python check_status.py
```

## 📚 API文档

启动服务器后，可以通过以下地址访问API文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

#### 预订管理API
- `POST /bookings` - 创建预订
- `GET /bookings` - 获取所有预订
- `GET /bookings/{id}` - 获取单个预订
- `PUT /bookings/{id}` - 更新预订
- `DELETE /bookings/{id}` - 删除预订
- `GET /bookings/search/{passenger_name}` - 按乘客姓名搜索

#### 航班查询API
- `GET /flights` - 获取所有航班
- `GET /flights/{id}` - 获取单个航班
- `GET /flights/search/{from}/{to}` - 搜索航班
- `GET /flights/number/{flight_number}` - 按航班号查询

#### 系统API
- `GET /health` - 健康检查
- `GET /stats` - 系统统计

### API测试示例

```bash
# 健康检查
curl http://localhost:8000/health

# 获取所有航班
curl http://localhost:8000/flights

# 搜索航班
curl http://localhost:8000/flights/search/PEK/SHA

# 创建预订
curl -X POST "http://localhost:8000/bookings" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "测试预订",
       "passenger_name": "测试用户",
       "flight_number": "CA1001",
       "departure_date": "2024-08-15",
       "departure_time": "08:30:00",
       "arrival_date": "2024-08-15", 
       "arrival_time": "10:45:00",
       "departure_airport": "PEK",
       "arrival_airport": "SHA",
       "price": "680.00"
     }'
```

## 🔧 开发指南

### 项目结构

```
A2A-ticketbooking/
├── 📄 README.md                    # 项目文档
├── 📄 requirements.txt             # Python依赖
├── 📄 .env                        # 环境配置
├── 📄 .env.example                # 环境配置模板
├── 📄 .gitignore                  # Git忽略文件
├── 📄 start_system.sh             # 一键启动脚本
├── 🗄️ database.py                 # 数据库模型定义
├── 🔧 init_db.py                  # 数据库初始化脚本
├── 🌐 mcp_server.py               # MCP HTTP服务器
├── 🤖 booking_agent.py            # 预订管理助手
├── ✈️ airline_agent.py            # 航班查询助手
├── 🔄 agent_communication_demo.py # 多Agent协作演示
├── 🧠 azure_openai_client.py      # Azure OpenAI客户端
├── 🧪 test_mcp_server.py          # MCP服务器测试
├── ⚡ quick_demo.py               # 快速演示脚本
├── 🔍 check_status.py             # 系统状态检查
├── 🗃️ smart_flight_booking.db     # SQLite数据库文件
└── 📁 venv/                       # Python虚拟环境
```

### 数据库模式

系统使用SQLite数据库，包含两个主要表：

```sql
-- 航班表
CREATE TABLE flights (
    id INTEGER PRIMARY KEY,
    flight_number VARCHAR(20) UNIQUE NOT NULL,
    airline VARCHAR(50) NOT NULL,
    departure_airport VARCHAR(10) NOT NULL,
    arrival_airport VARCHAR(10) NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    available_seats INTEGER DEFAULT 0,
    aircraft_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预订表
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    passenger_name VARCHAR(100) NOT NULL,
    flight_number VARCHAR(20) NOT NULL,
    departure_date DATE NOT NULL,
    departure_time TIME NOT NULL,
    arrival_date DATE NOT NULL,
    arrival_time TIME NOT NULL,
    departure_airport VARCHAR(10) NOT NULL,
    arrival_airport VARCHAR(10) NOT NULL,
    seat_number VARCHAR(10),
    price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 机场代码参考

| 代码 | 机场名称 | 城市 |
|------|----------|------|
| PEK | 北京首都国际机场 | 北京 |
| SHA | 上海虹桥国际机场 | 上海 |
| PVG | 上海浦东国际机场 | 上海 |
| CAN | 广州白云国际机场 | 广州 |
| CTU | 成都双流国际机场 | 成都 |
| KMG | 昆明长水国际机场 | 昆明 |
| XIY | 西安咸阳国际机场 | 西安 |
| HGH | 杭州萧山国际机场 | 杭州 |

## 🌟 项目亮点

### 1. 🤝 真正的多Agent协作
- **智能任务分工**: 两个AI助手各司其职，通过MCP协议通信
- **动态工作流**: 根据业务需求自动编排工作流程
- **状态同步**: 实时保持Agent间的数据一致性

### 2. 🔗 MCP协议实现
- **标准化通信**: 遵循MCP协议规范进行Agent间通信
- **扩展性设计**: 易于添加新的Agent和功能模块
- **互操作性**: 支持不同技术栈的Agent无缝集成

### 3. 🧠 AI驱动交互
- **自然语言理解**: 支持中文自然语言查询和指令
- **上下文感知**: 保持多轮对话的上下文连续性
- **智能推荐**: 基于用户偏好和历史数据的个性化推荐

### 4. 🏗️ 轻量级架构
- **简单部署**: 使用SQLite，无需复杂的数据库配置
- **模块化设计**: 易于维护和扩展的代码结构
- **完善测试**: 覆盖主要功能的测试用例

### 5. 🚀 优秀的开发体验
- **一键部署**: 自动化的部署和配置脚本
- **详细文档**: 完善的使用和开发文档
- **丰富演示**: 多种演示场景和用例

## 🔧 故障排除

### 常见问题

#### Q: MCP服务器启动失败
**解决方案:**
```bash
# 检查端口占用
lsof -i :8000

# 检查虚拟环境
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt

# 手动启动服务器
python mcp_server.py
```

#### Q: Azure OpenAI API调用失败
**解决方案:**
1. 检查`.env`文件中的API密钥和端点
2. 验证Azure订阅状态
3. 检查API配额限制
4. 确认模型部署状态

#### Q: 数据库初始化失败
**解决方案:**
```bash
# 删除现有数据库文件
rm smart_flight_booking.db

# 重新初始化数据库
python init_db.py
```

#### Q: 依赖安装问题
**解决方案:**
```bash
# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 手动安装核心依赖
pip install fastapi uvicorn pydantic openai requests python-dotenv sqlalchemy
```

### 系统监控

使用系统状态检查工具：
```bash
python check_status.py
```

该工具会检查：
- Python环境和依赖
- 数据库状态
- MCP服务器运行状态
- Azure OpenAI配置
- API端点可用性

---

## 📞 支持与贡献

### 技术支持

如果您在使用过程中遇到问题：
1. 查看本README的故障排除部分
2. 运行 `python check_status.py` 检查系统状态
3. 查看服务器日志文件

### 贡献指南

欢迎贡献代码！请遵循以下步骤：
1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

---

## 📄 许可证

本项目使用 MIT 许可证

---

## 🎉 致谢

感谢以下技术和社区的支持：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能Web框架
- [SQLite](https://sqlite.org/) - 轻量级数据库
- [Azure OpenAI](https://azure.microsoft.com/products/ai-services/openai-service) - 企业级AI服务
- [Python](https://python.org/) - 优雅的编程语言

---

**🚀 恭喜！您已成功部署了一个完整的智能机票预订系统！**

*如果本项目对您有帮助，请给个 ⭐ Star 支持我们！*
