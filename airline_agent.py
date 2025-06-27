#!/usr/bin/env python3
"""
智能Agent 2: 航班查询助手
管理航班信息，提供查询和推荐服务
"""

import requests
import json
from datetime import datetime, time
from decimal import Decimal
from typing import Dict, Any, Optional, List
from azure_openai_client import azure_client

class AirlineAgent:
    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        self.mcp_server_url = mcp_server_url
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """发送HTTP请求到MCP服务器"""
        url = f"{self.mcp_server_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return None
    
    def get_all_flights(self, skip: int = 0, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """获取所有航班"""
        params = {"skip": skip, "limit": limit}
        return self._make_request("GET", "/flights", params=params)
    
    def get_flight_by_id(self, flight_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取航班"""
        return self._make_request("GET", f"/flights/{flight_id}")
    
    def get_flight_by_number(self, flight_number: str) -> Optional[Dict[str, Any]]:
        """根据航班号获取航班"""
        return self._make_request("GET", f"/flights/number/{flight_number}")
    
    def search_flights(self, departure: str, arrival: str) -> Optional[List[Dict[str, Any]]]:
        """搜索航班"""
        return self._make_request("GET", f"/flights/search/{departure}/{arrival}")
    
    def create_flight(self, flight_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建新航班"""
        return self._make_request("POST", "/flights", json=flight_data)
    
    def delete_flight(self, flight_id: int) -> bool:
        """删除航班"""
        result = self._make_request("DELETE", f"/flights/{flight_id}")
        return result is not None
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """获取系统统计信息"""
        return self._make_request("GET", "/stats")
    
    def interactive_search_flights(self) -> None:
        """交互式搜索航班"""
        print("🔍 航班搜索")
        print("-" * 30)
        
        search_type = input("搜索类型 (1=按航线, 2=按航班号, 3=显示所有): ").strip()
        
        if search_type == "1":
            departure = input("出发机场代码: ").strip().upper()
            arrival = input("到达机场代码: ").strip().upper()
            
            print(f"\n🔍 搜索航班: {departure} → {arrival}")
            results = self.search_flights(departure, arrival)
            
            if results:
                print("-" * 60)
                print(f"{'航班号':<10} {'航空公司':<15} {'出发时间':<10} {'到达时间':<10} {'价格':<8} {'余票':<6}")
                print("-" * 60)
                for flight in results:
                    print(f"{flight['flight_number']:<10} {flight['airline']:<15} {flight['departure_time']:<10} {flight['arrival_time']:<10} ¥{flight['price']:<7} {flight['available_seats']:<6}")
                
                # AI推荐
                recommendation = azure_client.generate_flight_recommendation(departure, arrival, results)
                print(f"\n🤖 AI推荐:\n{recommendation}")
            else:
                print("❌ 未找到相关航班")
        
        elif search_type == "2":
            flight_number = input("请输入航班号: ").strip().upper()
            result = self.get_flight_by_number(flight_number)
            if result:
                self._display_flight(result)
            else:
                print("❌ 未找到该航班")
        
        elif search_type == "3":
            results = self.get_all_flights()
            if results:
                print(f"✅ 共有 {len(results)} 个航班:")
                print("-" * 80)
                print(f"{'ID':<4} {'航班号':<8} {'航空公司':<15} {'航线':<10} {'价格':<8} {'余票':<6} {'状态':<8}")
                print("-" * 80)
                for flight in results:
                    route = f"{flight['departure_airport']}-{flight['arrival_airport']}"
                    print(f"{flight['id']:<4} {flight['flight_number']:<8} {flight['airline']:<15} {route:<10} ¥{flight['price']:<7} {flight['available_seats']:<6} {flight['status']:<8}")
            else:
                print("❌ 暂无航班记录")
        
        else:
            print("❌ 无效的搜索类型")
    
    def interactive_create_flight(self) -> None:
        """交互式创建航班"""
        print("✈️ 创建新航班")
        print("-" * 30)
        
        try:
            flight_number = input("航班号: ").strip().upper()
            airline = input("航空公司: ").strip()
            departure_airport = input("出发机场代码: ").strip().upper()
            arrival_airport = input("到达机场代码: ").strip().upper()
            
            departure_time_str = input("出发时间 (HH:MM): ").strip()
            arrival_time_str = input("到达时间 (HH:MM): ").strip()
            
            price_str = input("票价: ").strip()
            available_seats_str = input("可用座位数: ").strip()
            aircraft_type = input("机型 (可选): ").strip() or None
            
            # 数据验证和转换
            departure_time = datetime.strptime(departure_time_str, "%H:%M").time()
            arrival_time = datetime.strptime(arrival_time_str, "%H:%M").time()
            price = Decimal(price_str)
            available_seats = int(available_seats_str)
            
            flight_data = {
                "flight_number": flight_number,
                "airline": airline,
                "departure_airport": departure_airport,
                "arrival_airport": arrival_airport,
                "departure_time": departure_time.isoformat(),
                "arrival_time": arrival_time.isoformat(),
                "price": str(price),
                "available_seats": available_seats,
                "aircraft_type": aircraft_type,
                "status": "active"
            }
            
            result = self.create_flight(flight_data)
            if result:
                print(f"✅ 航班创建成功！航班ID: {result['id']}")
                self._display_flight(result)
            else:
                print("❌ 航班创建失败")
                
        except ValueError as e:
            print(f"❌ 输入格式错误: {e}")
        except Exception as e:
            print(f"❌ 创建航班时发生错误: {e}")
    
    def interactive_delete_flight(self) -> None:
        """交互式删除航班"""
        print("🗑️ 删除航班")
        print("-" * 30)
        
        try:
            flight_id = int(input("请输入要删除的航班ID: ").strip())
            
            # 先显示航班信息确认
            flight = self.get_flight_by_id(flight_id)
            if not flight:
                print("❌ 航班不存在")
                return
            
            print("将要删除的航班:")
            self._display_flight(flight)
            
            confirm = input("\n确认删除? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                if self.delete_flight(flight_id):
                    print("✅ 航班删除成功!")
                else:
                    print("❌ 航班删除失败")
            else:
                print("ℹ️  取消删除操作")
                
        except ValueError:
            print("❌ 请输入有效的航班ID")
        except Exception as e:
            print(f"❌ 删除航班时发生错误: {e}")
    
    def show_stats(self) -> None:
        """显示系统统计"""
        print("📊 系统统计")
        print("-" * 30)
        
        stats = self.get_stats()
        if stats:
            print(f"总航班数: {stats['total_flights']}")
            print(f"总预订数: {stats['total_bookings']}")
            print(f"已确认预订: {stats['confirmed_bookings']}")
            print(f"统计时间: {stats['timestamp'][:19]}")
        else:
            print("❌ 无法获取统计信息")
    
    def _display_flight(self, flight: Dict[str, Any]) -> None:
        """显示航班详细信息"""
        print(f"""
✈️ 航班详情:
   ID: {flight['id']}
   航班号: {flight['flight_number']}
   航空公司: {flight['airline']}
   航线: {flight['departure_airport']} → {flight['arrival_airport']}
   时间: {flight['departure_time']} → {flight['arrival_time']}
   机型: {flight.get('aircraft_type', '未指定')}
   价格: ¥{flight['price']}
   余票: {flight['available_seats']}
   状态: {flight['status']}
   创建时间: {flight['created_at'][:19]}
""")
    
    def ai_chat(self, user_input: str) -> str:
        """AI智能对话"""
        # 分析用户输入，提取航班查询意图
        user_input_lower = user_input.lower()
        
        # 简单的意图识别
        if any(keyword in user_input_lower for keyword in ['搜索', '查找', '航班', '查询']):
            # 尝试提取机场代码
            airports = ["pek", "sha", "pvg", "can", "ctu", "kmg", "xiy", "hgh"]
            found_airports = [airport.upper() for airport in airports if airport in user_input_lower]
            
            if len(found_airports) >= 2:
                departure, arrival = found_airports[0], found_airports[1]
                results = self.search_flights(departure, arrival)
                if results:
                    response = f"为您找到 {len(results)} 个从 {departure} 到 {arrival} 的航班:\n"
                    for flight in results:
                        response += f"- {flight['flight_number']} ({flight['airline']}) - ¥{flight['price']}\n"
                    
                    # 添加AI推荐
                    recommendation = azure_client.generate_flight_recommendation(departure, arrival, results)
                    response += f"\n🤖 AI推荐: {recommendation}"
                    return response
                else:
                    return f"抱歉，未找到从 {departure} 到 {arrival} 的航班。"
        
        elif any(keyword in user_input_lower for keyword in ['推荐', '建议', '便宜', '划算']):
            # 获取一些热门航班进行推荐
            all_flights = self.get_all_flights(limit=5)
            if all_flights:
                flights_text = "以下是一些推荐航班:\n"
                for flight in all_flights:
                    flights_text += f"- {flight['flight_number']} ({flight['airline']}) {flight['departure_airport']}→{flight['arrival_airport']} ¥{flight['price']}\n"
                
                # 使用AI生成个性化推荐
                recommendation = azure_client.generate_flight_recommendation("热门", "推荐", all_flights)
                return f"{flights_text}\n🤖 {recommendation}"
        
        elif any(keyword in user_input_lower for keyword in ['统计', '数据', '信息']):
            stats = self.get_stats()
            if stats:
                return f"📊 系统统计:\n- 总航班数: {stats['total_flights']}\n- 总预订数: {stats['total_bookings']}\n- 已确认预订: {stats['confirmed_bookings']}"
        
        # 默认AI回复
        messages = [
            {"role": "system", "content": "你是一个专业的航班查询助手。帮助用户查询航班信息、提供出行建议。"},
            {"role": "user", "content": user_input}
        ]
        
        response = azure_client.chat_completion(messages, max_tokens=300, temperature=0.7)
        return response or "我可以帮您查询航班信息、搜索航线或提供出行建议。请告诉我您的具体需求。"
    
    def run_interactive_mode(self) -> None:
        """运行交互模式"""
        print("✈️ 智能航班查询助手")
        print("=" * 60)
        
        while True:
            print("\n可用命令:")
            print("1. search - 搜索航班")
            print("2. create - 创建航班")
            print("3. delete - 删除航班")
            print("4. stats - 系统统计")
            print("5. quit - 退出")
            print("或直接输入问题进行AI对话")
            
            user_input = input("\n请输入命令或询问: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见!")
                break
            elif user_input.lower() == 'search':
                self.interactive_search_flights()
            elif user_input.lower() == 'create':
                self.interactive_create_flight()
            elif user_input.lower() == 'delete':
                self.interactive_delete_flight()
            elif user_input.lower() == 'stats':
                self.show_stats()
            else:
                # AI对话模式
                print("🤖 AI助手:", self.ai_chat(user_input))

def main():
    # 检查MCP服务器连接
    agent = AirlineAgent()
    
    # 测试连接
    try:
        response = requests.get(f"{agent.mcp_server_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP服务器连接正常")
        else:
            print("⚠️  MCP服务器连接异常，请确保服务器已启动")
    except requests.exceptions.RequestException:
        print("❌ 无法连接到MCP服务器，请确保服务器已启动")
        print("启动命令: python mcp_server.py")
        return
    
    # 启动交互模式
    agent.run_interactive_mode()

if __name__ == "__main__":
    main()
