#!/usr/bin/env python3
"""
智能Agent 1: 预订管理助手
处理所有预订相关操作，提供智能对话接口
"""

import requests
import json
from datetime import datetime, date, time
from decimal import Decimal
from typing import Dict, Any, Optional
import os
from azure_openai_client import azure_client

class BookingAgent:
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
    
    def create_booking(self, booking_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建新预订"""
        return self._make_request("POST", "/bookings", json=booking_data)
    
    def get_all_bookings(self, skip: int = 0, limit: int = 100) -> Optional[list]:
        """获取所有预订"""
        params = {"skip": skip, "limit": limit}
        return self._make_request("GET", "/bookings", params=params)
    
    def get_booking_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取预订"""
        return self._make_request("GET", f"/bookings/{booking_id}")
    
    def search_bookings_by_passenger(self, passenger_name: str) -> Optional[list]:
        """根据乘客姓名搜索预订"""
        return self._make_request("GET", f"/bookings/search/{passenger_name}")
    
    def update_booking(self, booking_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新预订"""
        return self._make_request("PUT", f"/bookings/{booking_id}", json=update_data)
    
    def delete_booking(self, booking_id: int) -> bool:
        """删除预订"""
        result = self._make_request("DELETE", f"/bookings/{booking_id}")
        return result is not None
    
    def interactive_create_booking(self) -> None:
        """交互式创建预订"""
        print("📝 创建新预订")
        print("-" * 30)
        
        try:
            title = input("预订标题: ").strip()
            passenger_name = input("乘客姓名: ").strip()
            flight_number = input("航班号: ").strip()
            
            # 日期时间输入
            departure_date_str = input("出发日期 (YYYY-MM-DD): ").strip()
            departure_time_str = input("出发时间 (HH:MM): ").strip()
            arrival_date_str = input("到达日期 (YYYY-MM-DD): ").strip()
            arrival_time_str = input("到达时间 (HH:MM): ").strip()
            
            departure_airport = input("出发机场代码: ").strip().upper()
            arrival_airport = input("到达机场代码: ").strip().upper()
            seat_number = input("座位号 (可选): ").strip() or None
            price_str = input("票价: ").strip()
            
            # 数据验证和转换
            departure_date = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
            departure_time = datetime.strptime(departure_time_str, "%H:%M").time()
            arrival_date = datetime.strptime(arrival_date_str, "%Y-%m-%d").date()
            arrival_time = datetime.strptime(arrival_time_str, "%H:%M").time()
            price = Decimal(price_str)
            
            booking_data = {
                "title": title,
                "passenger_name": passenger_name,
                "flight_number": flight_number,
                "departure_date": departure_date.isoformat(),
                "departure_time": departure_time.isoformat(),
                "arrival_date": arrival_date.isoformat(),
                "arrival_time": arrival_time.isoformat(),
                "departure_airport": departure_airport,
                "arrival_airport": arrival_airport,
                "seat_number": seat_number,
                "price": str(price)
            }
            
            result = self.create_booking(booking_data)
            if result:
                print(f"✅ 预订创建成功！预订ID: {result['id']}")
            else:
                print("❌ 预订创建失败")
                
        except ValueError as e:
            print(f"❌ 输入格式错误: {e}")
        except Exception as e:
            print(f"❌ 创建预订时发生错误: {e}")
    
    def interactive_search_bookings(self) -> None:
        """交互式搜索预订"""
        print("🔍 搜索预订")
        print("-" * 30)
        
        search_type = input("搜索类型 (1=按ID, 2=按乘客姓名, 3=显示所有): ").strip()
        
        if search_type == "1":
            try:
                booking_id = int(input("请输入预订ID: ").strip())
                result = self.get_booking_by_id(booking_id)
                if result:
                    self._display_booking(result)
                else:
                    print("❌ 未找到该预订")
            except ValueError:
                print("❌ 请输入有效的预订ID")
        
        elif search_type == "2":
            passenger_name = input("请输入乘客姓名: ").strip()
            results = self.search_bookings_by_passenger(passenger_name)
            if results:
                print(f"✅ 找到 {len(results)} 个预订:")
                for booking in results:
                    self._display_booking(booking, brief=True)
            else:
                print("❌ 未找到相关预订")
        
        elif search_type == "3":
            results = self.get_all_bookings()
            if results:
                print(f"✅ 共有 {len(results)} 个预订:")
                for booking in results:
                    self._display_booking(booking, brief=True)
            else:
                print("❌ 暂无预订记录")
        
        else:
            print("❌ 无效的搜索类型")
    
    def interactive_update_booking(self) -> None:
        """交互式更新预订"""
        print("✏️ 更新预订")
        print("-" * 30)
        
        try:
            booking_id = int(input("请输入要更新的预订ID: ").strip())
            
            # 先获取当前预订信息
            current_booking = self.get_booking_by_id(booking_id)
            if not current_booking:
                print("❌ 预订不存在")
                return
            
            print("当前预订信息:")
            self._display_booking(current_booking)
            
            print("\n请输入要更新的字段 (留空表示不更改):")
            
            update_data = {}
            
            new_seat = input(f"座位号 (当前: {current_booking.get('seat_number', '无')}): ").strip()
            if new_seat:
                update_data["seat_number"] = new_seat
            
            new_status = input(f"状态 (当前: {current_booking['status']}): ").strip()
            if new_status:
                update_data["status"] = new_status
            
            if update_data:
                result = self.update_booking(booking_id, update_data)
                if result:
                    print("✅ 预订更新成功!")
                    self._display_booking(result)
                else:
                    print("❌ 预订更新失败")
            else:
                print("ℹ️  未进行任何更改")
                
        except ValueError:
            print("❌ 请输入有效的预订ID")
        except Exception as e:
            print(f"❌ 更新预订时发生错误: {e}")
    
    def interactive_delete_booking(self) -> None:
        """交互式删除预订"""
        print("🗑️ 删除预订")
        print("-" * 30)
        
        try:
            booking_id = int(input("请输入要删除的预订ID: ").strip())
            
            # 先显示预订信息确认
            booking = self.get_booking_by_id(booking_id)
            if not booking:
                print("❌ 预订不存在")
                return
            
            print("将要删除的预订:")
            self._display_booking(booking)
            
            confirm = input("\n确认删除? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                if self.delete_booking(booking_id):
                    print("✅ 预订删除成功!")
                else:
                    print("❌ 预订删除失败")
            else:
                print("ℹ️  取消删除操作")
                
        except ValueError:
            print("❌ 请输入有效的预订ID")
        except Exception as e:
            print(f"❌ 删除预订时发生错误: {e}")
    
    def _display_booking(self, booking: Dict[str, Any], brief: bool = False) -> None:
        """显示预订信息"""
        if brief:
            print(f"  ID: {booking['id']} | {booking['passenger_name']} | {booking['flight_number']} | {booking['status']}")
        else:
            print(f"""
📋 预订详情:
   ID: {booking['id']}
   标题: {booking['title']}
   乘客: {booking['passenger_name']}
   航班: {booking['flight_number']}
   日期: {booking['departure_date']} {booking['departure_time']} → {booking['arrival_date']} {booking['arrival_time']}
   航线: {booking['departure_airport']} → {booking['arrival_airport']}
   座位: {booking.get('seat_number', '未指定')}
   价格: ¥{booking['price']}
   状态: {booking['status']}
   创建时间: {booking['created_at'][:19]}
""")
    
    def ai_chat(self, user_input: str) -> str:
        """AI智能对话"""
        # 使用Azure OpenAI分析用户输入
        analysis = azure_client.analyze_booking_request(user_input)
        
        intent = analysis.get("intent", "general_question")
        entities = analysis.get("entities", {})
        response = analysis.get("response", "")
        
        # 根据意图执行相应操作
        if intent == "search_booking":
            passenger_name = entities.get("passenger_name")
            if passenger_name:
                results = self.search_bookings_by_passenger(passenger_name)
                if results:
                    result_text = f"找到 {len(results)} 个预订:\n"
                    for booking in results:
                        result_text += f"- ID: {booking['id']}, 航班: {booking['flight_number']}, 状态: {booking['status']}\n"
                    return result_text
                else:
                    return f"未找到 {passenger_name} 的预订记录。"
        
        elif intent == "general_question":
            return response
        
        return response or "我理解您的需求，请告诉我更多详细信息，或者使用命令菜单进行操作。"
    
    def run_interactive_mode(self) -> None:
        """运行交互模式"""
        print("🎫 智能预订管理助手")
        print("=" * 60)
        
        while True:
            print("\n可用命令:")
            print("1. create - 创建预订")
            print("2. search - 搜索预订") 
            print("3. update - 更新预订")
            print("4. delete - 删除预订")
            print("5. quit - 退出")
            print("或直接输入问题进行AI对话")
            
            user_input = input("\n请输入命令或询问: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见!")
                break
            elif user_input.lower() == 'create':
                self.interactive_create_booking()
            elif user_input.lower() == 'search':
                self.interactive_search_bookings()
            elif user_input.lower() == 'update':
                self.interactive_update_booking()
            elif user_input.lower() == 'delete':
                self.interactive_delete_booking()
            else:
                # AI对话模式
                print("🤖 AI助手:", self.ai_chat(user_input))

def main():
    # 检查MCP服务器连接
    agent = BookingAgent()
    
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
