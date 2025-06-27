#!/usr/bin/env python3
"""
快速演示脚本
快速测试系统的核心功能
"""

import requests
import json
from datetime import datetime, date, time
from decimal import Decimal

def test_mcp_server():
    """测试MCP服务器"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试MCP服务器...")
    
    try:
        # 健康检查
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 健康检查: {health_data}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
        
        # 获取航班
        response = requests.get(f"{base_url}/flights", timeout=5)
        if response.status_code == 200:
            flights = response.json()
            print(f"✅ 获取到 {len(flights)} 个航班")
            
            if flights:
                print("前3个航班:")
                for flight in flights[:3]:
                    print(f"  - {flight['flight_number']}: {flight['departure_airport']} → {flight['arrival_airport']} ¥{flight['price']}")
        else:
            print(f"❌ 获取航班失败: {response.status_code}")
            return False
        
        # 搜索航班
        response = requests.get(f"{base_url}/flights/search/PEK/SHA", timeout=5)
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ 搜索PEK到SHA: 找到 {len(search_results)} 个航班")
        else:
            print(f"❌ 搜索航班失败: {response.status_code}")
        
        # 创建测试预订
        booking_data = {
            "title": "快速演示预订",
            "passenger_name": "测试用户",
            "flight_number": "CA1001",
            "departure_date": "2024-08-15",
            "departure_time": "08:30:00",
            "arrival_date": "2024-08-15", 
            "arrival_time": "10:45:00",
            "departure_airport": "PEK",
            "arrival_airport": "SHA",
            "seat_number": "12A",
            "price": "680.00"
        }
        
        response = requests.post(f"{base_url}/bookings", json=booking_data, timeout=5)
        if response.status_code == 200:
            booking = response.json()
            booking_id = booking['id']
            print(f"✅ 创建预订成功! ID: {booking_id}")
            
            # 更新预订
            update_data = {"seat_number": "12A"}
            response = requests.put(f"{base_url}/bookings/{booking_id}", json=update_data, timeout=5)
            if response.status_code == 200:
                updated_booking = response.json()
                print(f"✅ 更新预订成功: 座位号 {updated_booking['seat_number']}")
            else:
                print(f"❌ 更新预订失败: {response.status_code}")
        else:
            print(f"❌ 创建预订失败: {response.status_code}")
            return False
        
        # 获取统计信息
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 系统统计: {stats['total_bookings']} 个预订, {stats['total_flights']} 个航班")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_ai_features():
    """测试AI功能"""
    print("\n🤖 测试AI功能...")
    
    try:
        from azure_openai_client import azure_client
        
        if not azure_client.available:
            print("⚠️  Azure OpenAI未配置，跳过AI测试")
            return
        
        # 测试分析预订请求
        test_input = "我要预订明天北京到上海的航班"
        analysis = azure_client.analyze_booking_request(test_input)
        print(f"✅ AI分析结果: 意图={analysis.get('intent', 'unknown')}")
        
        # 测试航班推荐
        mock_flights = [
            {"flight_number": "CA1001", "airline": "中国国际航空", "price": "680.00"},
            {"flight_number": "MU2001", "airline": "中国东方航空", "price": "720.00"}
        ]
        recommendation = azure_client.generate_flight_recommendation("PEK", "SHA", mock_flights)
        if recommendation:
            print(f"✅ AI推荐: {recommendation[:100]}...")
        
    except ImportError:
        print("⚠️  Azure OpenAI模块未安装")
    except Exception as e:
        print(f"❌ AI测试失败: {e}")

def test_agents():
    """测试Agent功能"""
    print("\n🤖 测试Agent功能...")
    
    try:
        from booking_agent import BookingAgent
        from airline_agent import AirlineAgent
        
        # 测试航班查询助手
        airline_agent = AirlineAgent()
        flights = airline_agent.get_all_flights(limit=3)
        if flights:
            print(f"✅ 航班查询助手: 获取到 {len(flights)} 个航班")
        else:
            print("❌ 航班查询助手测试失败")
        
        # 测试预订管理助手
        booking_agent = BookingAgent()
        bookings = booking_agent.get_all_bookings(limit=3)
        if bookings is not None:
            print(f"✅ 预订管理助手: 获取到 {len(bookings)} 个预订")
        else:
            print("❌ 预订管理助手测试失败")
        
        # 测试AI对话
        if flights:
            ai_response = airline_agent.ai_chat("推荐一些便宜的航班")
            if ai_response:
                print(f"✅ AI对话测试: {ai_response[:50]}...")
        
    except ImportError as e:
        print(f"⚠️  Agent模块导入失败: {e}")
    except Exception as e:
        print(f"❌ Agent测试失败: {e}")

def main():
    print("🚀 智能机票预订系统 - 快速演示")
    print("=" * 50)
    
    # 测试MCP服务器
    if not test_mcp_server():
        print("\n❌ MCP服务器测试失败，请确保服务器已启动")
        print("启动命令: python mcp_server.py")
        return
    
    # 测试AI功能
    test_ai_features()
    
    # 测试Agent功能
    test_agents()
    
    print("\n🎉 演示完成！")
    print("\n可用的操作:")
    print("1. 运行预订管理助手: python booking_agent.py")
    print("2. 运行航班查询助手: python airline_agent.py")
    print("3. 运行多Agent协作演示: python agent_communication_demo.py")
    print("4. 查看API文档: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
