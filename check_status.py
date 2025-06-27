#!/usr/bin/env python3
"""
系统状态检查脚本
检查各个组件的运行状态
"""

import requests
import sqlite3
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class SystemStatusChecker:
    def __init__(self):
        self.mcp_server_url = "http://localhost:8000"
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./smart_flight_booking.db")
    
    def check_mcp_server(self):
        """检查MCP服务器状态"""
        print("🌐 检查MCP服务器状态...")
        
        try:
            response = requests.get(f"{self.mcp_server_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ MCP服务器运行正常")
                print(f"   - 状态: {health_data.get('status', 'unknown')}")
                print(f"   - 时间: {health_data.get('timestamp', 'unknown')}")
                return True
            else:
                print(f"❌ MCP服务器响应异常: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ MCP服务器连接失败: {e}")
            return False
    
    def check_database(self):
        """检查数据库状态"""
        print("\n🗄️  检查数据库状态...")
        
        try:
            # 检查SQLite数据库文件
            if self.database_url.startswith('sqlite:///'):
                db_path = self.database_url.replace('sqlite:///', '')
                if not os.path.exists(db_path):
                    print(f"❌ 数据库文件不存在: {db_path}")
                    return False
                
                # 连接SQLite数据库
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 检查数据库连接
                cursor.execute("SELECT sqlite_version()")
                version = cursor.fetchone()[0]
                print(f"✅ 数据库连接正常")
                print(f"   - SQLite版本: {version}")
                
                # 检查表是否存在
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                tables = cursor.fetchall()
                table_names = [table[0] for table in tables]
                
                if 'bookings' in table_names and 'flights' in table_names:
                    print(f"✅ 数据表存在: {', '.join(table_names)}")
                    
                    # 检查数据量
                    cursor.execute("SELECT COUNT(*) FROM flights")
                    flight_count = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM bookings")
                    booking_count = cursor.fetchone()[0]
                    
                    print(f"   - 航班数: {flight_count}")
                    print(f"   - 预订数: {booking_count}")
                else:
                    print(f"⚠️  数据表不完整: {', '.join(table_names)}")
                
                cursor.close()
                conn.close()
                return True
            else:
                print(f"❌ 不支持的数据库类型: {self.database_url}")
                return False
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def check_docker_containers(self):
        """检查Docker容器状态"""
        print("\n🐳 检查Docker容器状态...")
        
        try:
            # 检查数据库容器
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=smart_flight_booking_db", "--format", "table {{.Names}}\t{{.Status}}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                lines = output.split('\n')
                if len(lines) > 1:  # 有标题行
                    print("✅ Docker容器运行状态:")
                    for line in lines:
                        print(f"   {line}")
                else:
                    print("⚠️  未找到相关Docker容器")
            else:
                print(f"❌ Docker命令执行失败: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ Docker未安装或不在PATH中")
            return False
        except Exception as e:
            print(f"❌ 检查Docker容器失败: {e}")
            return False
        
        return True
    
    def check_python_environment(self):
        """检查Python环境"""
        print("\n🐍 检查Python环境...")
        
        # 检查虚拟环境
        venv_path = os.path.join(os.getcwd(), 'venv')
        if os.path.exists(venv_path):
            print("✅ 虚拟环境存在")
        else:
            print("⚠️  虚拟环境不存在")
        
        # 检查关键依赖
        required_packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'requests', 'openai']
        
        try:
            import pkg_resources
            installed_packages = [pkg.project_name for pkg in pkg_resources.working_set]
            
            missing_packages = []
            for package in required_packages:
                if package not in installed_packages:
                    missing_packages.append(package)
            
            if not missing_packages:
                print("✅ 所有必需的Python包已安装")
            else:
                print(f"⚠️  缺少以下包: {', '.join(missing_packages)}")
                
        except Exception as e:
            print(f"❌ 检查Python包失败: {e}")
    
    def check_configuration(self):
        """检查配置文件"""
        print("\n⚙️  检查配置文件...")
        
        # 检查.env文件
        if os.path.exists('.env'):
            print("✅ .env文件存在")
            
            # 检查关键配置
            azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            azure_key = os.getenv('AZURE_OPENAI_API_KEY')
            
            if azure_endpoint and azure_endpoint != 'your-endpoint.openai.azure.com':
                print("✅ Azure OpenAI端点已配置")
            else:
                print("⚠️  Azure OpenAI端点未配置")
            
            if azure_key and azure_key != 'your-api-key-here':
                print("✅ Azure OpenAI API密钥已配置")
            else:
                print("⚠️  Azure OpenAI API密钥未配置")
        else:
            print("❌ .env文件不存在")
        
        # 检查其他配置文件
        config_files = ['requirements.txt', 'docker-compose.yml']
        for file in config_files:
            if os.path.exists(file):
                print(f"✅ {file} 存在")
            else:
                print(f"❌ {file} 不存在")
    
    def check_api_endpoints(self):
        """检查API端点"""
        print("\n🔗 检查API端点...")
        
        endpoints = [
            "/health",
            "/flights",
            "/bookings",
            "/stats"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.mcp_server_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - 正常")
                else:
                    print(f"⚠️  {endpoint} - 状态码: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - 失败: {e}")
    
    def check_processes(self):
        """检查相关进程"""
        print("\n🔄 检查相关进程...")
        
        # 检查MCP服务器进程
        if os.path.exists('mcp_server.pid'):
            with open('mcp_server.pid', 'r') as f:
                pid = f.read().strip()
            
            try:
                os.kill(int(pid), 0)  # 检查进程是否存在
                print(f"✅ MCP服务器进程运行中 (PID: {pid})")
            except (OSError, ValueError):
                print(f"❌ MCP服务器进程不存在 (PID文件: {pid})")
        else:
            print("⚠️  未找到MCP服务器PID文件")
    
    def run_full_check(self):
        """运行完整的系统检查"""
        print("🔍 智能机票预订系统状态检查")
        print("=" * 50)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        checks = [
            self.check_configuration,
            self.check_python_environment,
            self.check_docker_containers,
            self.check_database,
            self.check_processes,
            self.check_mcp_server,
            self.check_api_endpoints
        ]
        
        success_count = 0
        for check in checks:
            try:
                result = check()
                if result is not False:
                    success_count += 1
            except Exception as e:
                print(f"❌ 检查失败: {e}")
        
        print(f"\n📊 检查总结")
        print("=" * 30)
        print(f"完成检查: {len(checks)} 项")
        print(f"成功检查: {success_count} 项")
        
        if success_count == len(checks):
            print("🎉 系统状态良好！")
        else:
            print("⚠️  系统存在一些问题，请检查上述输出")

def main():
    checker = SystemStatusChecker()
    checker.run_full_check()

if __name__ == "__main__":
    main()
