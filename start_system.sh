#!/bin/bash
# 智能机票预订系统一键启动脚本

set -e  # 出错时退出

echo "🚀 智能机票预订系统启动脚本"
echo "===================================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Python版本
check_python() {
    echo -e "${BLUE}📋 检查Python环境...${NC}"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo -e "${GREEN}✅ Python版本: $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}❌ Python3未安装，请先安装Python 3.13+${NC}"
        exit 1
    fi
}

# 检查Docker
check_docker() {
    echo -e "${BLUE}🐳 检查Docker环境...${NC}"
    
    if command -v docker &> /dev/null; then
        if docker info &> /dev/null; then
            echo -e "${GREEN}✅ Docker运行正常${NC}"
        else
            echo -e "${RED}❌ Docker未运行，请启动Docker${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
        exit 1
    fi
}

# 创建虚拟环境
setup_venv() {
    echo -e "${BLUE}🔧 设置Python虚拟环境...${NC}"
    
    if [ ! -d "venv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    echo "激活虚拟环境..."
    source venv/bin/activate
    
    echo "升级pip..."
    pip install --upgrade pip
    
    echo -e "${GREEN}✅ 虚拟环境准备完成${NC}"
}

# 安装依赖
install_dependencies() {
    echo -e "${BLUE}📦 安装Python依赖...${NC}"
    
    source venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo -e "${GREEN}✅ 依赖安装完成${NC}"
    else
        echo -e "${YELLOW}⚠️  requirements.txt不存在，手动安装依赖...${NC}"
        pip install fastapi uvicorn psycopg2-binary pydantic openai requests python-dotenv sqlalchemy alembic
        echo -e "${GREEN}✅ 核心依赖安装完成${NC}"
    fi
}

# 启动数据库
start_database() {
    echo -e "${BLUE}🗄️  启动PostgreSQL数据库...${NC}"
    
    # 检查是否已有运行的容器
    if docker ps | grep -q "smart_flight_booking_db"; then
        echo -e "${YELLOW}⚠️  数据库容器已在运行${NC}"
    else
        if docker ps -a | grep -q "smart_flight_booking_db"; then
            echo "启动现有数据库容器..."
            docker start smart_flight_booking_db
        else
            echo "创建并启动新的数据库容器..."
            docker compose up -d
        fi
        
        # 等待数据库启动
        echo "等待数据库启动..."
        sleep 5
        
        # 检查数据库连接
        for i in {1..30}; do
            if docker exec smart_flight_booking_db pg_isready -U admin -d smart_flight_booking &> /dev/null; then
                break
            fi
            if [ $i -eq 30 ]; then
                echo -e "${RED}❌ 数据库启动超时${NC}"
                exit 1
            fi
            sleep 1
        done
    fi
    
    echo -e "${GREEN}✅ 数据库启动成功${NC}"
}

# 初始化数据库
init_database() {
    echo -e "${BLUE}🔄 初始化数据库...${NC}"
    
    source venv/bin/activate
    
    if [ -f "init_db.py" ]; then
        python init_db.py
        echo -e "${GREEN}✅ 数据库初始化完成${NC}"
    else
        echo -e "${YELLOW}⚠️  init_db.py不存在，跳过数据库初始化${NC}"
    fi
}

# 检查环境配置
check_env() {
    echo -e "${BLUE}⚙️  检查环境配置...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env文件不存在，创建默认配置...${NC}"
        cat > .env << EOF
# Azure OpenAI 配置
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview
AZURE_OPENAI_API_KEY=your-api-key-here

# 数据库配置
DATABASE_URL=postgresql://admin:password123@localhost:5433/smart_flight_booking

# MCP Server 配置
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
EOF
        echo -e "${YELLOW}⚠️  请编辑.env文件设置Azure OpenAI配置${NC}"
    fi
    
    echo -e "${GREEN}✅ 环境配置检查完成${NC}"
}

# 启动MCP服务器
start_mcp_server() {
    echo -e "${BLUE}🌐 启动MCP服务器...${NC}"
    
    source venv/bin/activate
    
    if [ -f "mcp_server.py" ]; then
        echo "在后台启动MCP服务器..."
        nohup python mcp_server.py > mcp_server.log 2>&1 &
        MCP_PID=$!
        echo $MCP_PID > mcp_server.pid
        
        # 等待服务器启动
        echo "等待MCP服务器启动..."
        sleep 3
        
        # 检查服务器是否运行
        if curl -s http://localhost:8000/health > /dev/null; then
            echo -e "${GREEN}✅ MCP服务器启动成功 (PID: $MCP_PID)${NC}"
        else
            echo -e "${RED}❌ MCP服务器启动失败${NC}"
            if [ -f "mcp_server.pid" ]; then
                kill $(cat mcp_server.pid) 2>/dev/null || true
                rm mcp_server.pid
            fi
            exit 1
        fi
    else
        echo -e "${RED}❌ mcp_server.py不存在${NC}"
        exit 1
    fi
}

# 运行快速测试
run_quick_test() {
    echo -e "${BLUE}🧪 运行快速测试...${NC}"
    
    source venv/bin/activate
    
    if [ -f "quick_demo.py" ]; then
        python quick_demo.py
    else
        # 简单的API测试
        echo "测试API端点..."
        if curl -s http://localhost:8000/health | grep -q "healthy"; then
            echo -e "${GREEN}✅ API测试通过${NC}"
        else
            echo -e "${RED}❌ API测试失败${NC}"
        fi
    fi
}

# 显示启动信息
show_info() {
    echo ""
    echo -e "${GREEN}🎉 系统启动完成！${NC}"
    echo ""
    echo "可用的操作:"
    echo "1. 运行预订管理助手: source venv/bin/activate && python booking_agent.py"
    echo "2. 运行航班查询助手: source venv/bin/activate && python airline_agent.py"  
    echo "3. 运行多Agent协作演示: source venv/bin/activate && python agent_communication_demo.py"
    echo ""
    echo "服务信息:"
    echo "- MCP服务器: http://localhost:8000"
    echo "- API文档: http://localhost:8000/docs"
    echo "- 数据库: localhost:5433"
    echo ""
    echo "停止服务:"
    echo "- 停止MCP服务器: ./stop_system.sh"
    echo "- 停止数据库: docker compose down"
    echo ""
    echo -e "${YELLOW}注意: 请在.env文件中配置Azure OpenAI API密钥以启用AI功能${NC}"
}

# 创建停止脚本
create_stop_script() {
    cat > stop_system.sh << 'EOF'
#!/bin/bash
# 停止智能机票预订系统

echo "🛑 停止智能机票预订系统..."

# 停止MCP服务器
if [ -f "mcp_server.pid" ]; then
    PID=$(cat mcp_server.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "停止MCP服务器 (PID: $PID)..."
        kill $PID
        rm mcp_server.pid
        echo "✅ MCP服务器已停止"
    else
        echo "⚠️  MCP服务器进程不存在"
        rm mcp_server.pid
    fi
else
    echo "⚠️  未找到MCP服务器PID文件"
fi

# 停止数据库
echo "停止数据库容器..."
docker compose down

echo "🎉 系统已停止"
EOF
    chmod +x stop_system.sh
}

# 主函数
main() {
    echo -e "${BLUE}开始启动系统...${NC}"
    
    check_python
    check_docker
    setup_venv
    install_dependencies
    check_env
    start_database
    init_database
    start_mcp_server
    create_stop_script
    run_quick_test
    show_info
    
    echo -e "${GREEN}🚀 启动脚本执行完成！${NC}"
}

# 错误处理
cleanup() {
    echo -e "${RED}❌ 启动过程中发生错误${NC}"
    
    # 清理可能的后台进程
    if [ -f "mcp_server.pid" ]; then
        kill $(cat mcp_server.pid) 2>/dev/null || true
        rm mcp_server.pid
    fi
    
    exit 1
}

trap cleanup ERR

# 运行主函数
main
