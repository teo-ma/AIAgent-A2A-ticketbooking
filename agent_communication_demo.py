#!/usr/bin/env python3
"""
多Agent协作演示
展示智能预订管理助手和航班查询助手之间的协作流程
"""

import requests
import json
from datetime import datetime, date, time
from decimal import Decimal
from typing import Dict, Any, Optional, List
import random

from booking_agent import BookingAgent
from airline_agent import AirlineAgent

class MultiAgentDemo:
    def __init__(self):
        self.booking_agent = BookingAgent()
        self.airline_agent = AirlineAgent()
    
    def check_mcp_server(self) -> bool:
        """检查MCP服务器状态"""
        try:
            response = requests.get(f"{self.booking_agent.mcp_server_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def automated_booking_flow(self, passenger_name: str, departure: str, arrival: str) -> Dict[str, Any]:
        """
        自动化预订流程演示
        1. 航班查询助手搜索航班
        2. 选择合适的航班
        3. 预订管理助手创建预订
        """
        print(f"\n🔄 多Agent协作流程")
        print(f"乘客: {passenger_name}")
        print(f"航线: {departure} → {arrival}")
        print("=" * 50)
        
        # 步骤1: 航班查询助手搜索航班
        print(f"\n📡 步骤1: 航班查询助手搜索航班...")
        flights = self.airline_agent.search_flights(departure, arrival)
        
        if not flights:
            return {"success": False, "message": "未找到航班"}
        
        print(f"✅ 找到 {len(flights)} 个航班")
        for i, flight in enumerate(flights, 1):
            print(f"  {i}. {flight['flight_number']} ({flight['airline']}) - ¥{flight['price']}")
        
        # 步骤2: 选择航班（这里选择第一个）
        selected_flight = flights[0]
        print(f"\n📡 步骤2: 选择航班 {selected_flight['flight_number']}")
        
        # 步骤3: 预订管理助手创建预订
        print(f"\n📡 步骤3: 预订管理助手创建预订...")
        
        # 构造预订数据
        booking_data = {
            "title": f"{passenger_name}的航班预订",
            "passenger_name": passenger_name,
            "flight_number": selected_flight['flight_number'],
            "departure_date": "2024-08-15",  # 示例日期
            "departure_time": selected_flight['departure_time'],
            "arrival_date": "2024-08-15",
            "arrival_time": selected_flight['arrival_time'],
            "departure_airport": selected_flight['departure_airport'],
            "arrival_airport": selected_flight['arrival_airport'],
            "seat_number": f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
            "price": str(selected_flight['price'])
        }
        
        booking_result = self.booking_agent.create_booking(booking_data)
        
        if booking_result:
            print(f"✅ 预订创建成功，预订ID: {booking_result['id']}")
            return {
                "success": True,
                "flight": selected_flight,
                "booking": booking_result,
                "message": "预订流程完成"
            }
        else:
            return {"success": False, "message": "预订创建失败"}
    
    def interactive_collaboration_demo(self):
        """交互式协作演示"""
        print("\n🎭 多Agent交互式协作演示")
        print("=" * 50)
        
        passenger_name = input("请输入乘客姓名: ").strip()
        departure = input("请输入出发机场代码: ").strip().upper()
        arrival = input("请输入到达机场代码: ").strip().upper()
        
        result = self.automated_booking_flow(passenger_name, departure, arrival)
        
        if result["success"]:
            print(f"\n🎉 协作演示成功!")
            print(f"航班: {result['flight']['flight_number']}")
            print(f"预订ID: {result['booking']['id']}")
            
            # 演示后续操作
            print(f"\n🔄 演示后续操作...")
            
            # 查询刚创建的预订
            print(f"📡 预订管理助手查询预订...")
            booking_details = self.booking_agent.get_booking_by_id(result['booking']['id'])
            if booking_details:
                print(f"✅ 预订查询成功: {booking_details['passenger_name']} - {booking_details['flight_number']}")
            
            # 获取系统统计
            print(f"📡 航班查询助手获取统计...")
            stats = self.airline_agent.get_stats()
            if stats:
                print(f"✅ 系统统计: {stats['total_bookings']} 个预订, {stats['total_flights']} 个航班")
            
        else:
            print(f"\n❌ 协作演示失败: {result['message']}")
    
    def batch_demo(self):
        """批量演示多个预订流程"""
        print("\n🎯 批量预订演示")
        print("=" * 50)
        
        # 预定义的演示数据
        demo_data = [
            {"passenger": "张三", "departure": "PEK", "arrival": "SHA"},
            {"passenger": "李四", "departure": "SHA", "arrival": "CAN"},
            {"passenger": "王五", "departure": "CAN", "arrival": "CTU"},
        ]
        
        successful_bookings = []
        
        for i, data in enumerate(demo_data, 1):
            print(f"\n📋 演示 {i}/{len(demo_data)}")
            result = self.automated_booking_flow(
                data["passenger"], 
                data["departure"], 
                data["arrival"]
            )
            
            if result["success"]:
                successful_bookings.append(result)
            
            # 添加一些延迟，模拟真实场景
            import time
            time.sleep(1)
        
        # 总结演示结果
        print(f"\n📊 批量演示总结")
        print("=" * 30)
        print(f"总演示数: {len(demo_data)}")
        print(f"成功预订: {len(successful_bookings)}")
        print(f"成功率: {len(successful_bookings)/len(demo_data)*100:.1f}%")
        
        if successful_bookings:
            print(f"\n✅ 成功的预订:")
            for booking in successful_bookings:
                print(f"  - {booking['booking']['passenger_name']}: {booking['flight']['flight_number']} (ID: {booking['booking']['id']})")
    
    def agent_communication_test(self):
        """Agent间通信测试"""
        print("\n🔗 Agent间通信测试")
        print("=" * 50)
        
        # 测试1: 航班查询助手获取航班信息
        print("\n📡 测试1: 航班查询助手获取航班信息")
        flights = self.airline_agent.get_all_flights(limit=3)
        if flights:
            print(f"✅ 获取到 {len(flights)} 个航班")
            for flight in flights:
                print(f"  - {flight['flight_number']}: {flight['departure_airport']} → {flight['arrival_airport']}")
        else:
            print("❌ 获取航班信息失败")
        
        # 测试2: 预订管理助手获取预订信息
        print("\n📡 测试2: 预订管理助手获取预订信息")
        bookings = self.booking_agent.get_all_bookings(limit=3)
        if bookings:
            print(f"✅ 获取到 {len(bookings)} 个预订")
            for booking in bookings:
                print(f"  - {booking['passenger_name']}: {booking['flight_number']} (状态: {booking['status']})")
        else:
            print("❌ 获取预订信息失败")
        
        # 测试3: 跨Agent数据关联
        print("\n📡 测试3: 跨Agent数据关联测试")
        if flights and bookings:
            # 查找使用了现有航班的预订
            flight_numbers = {f['flight_number'] for f in flights}
            booking_flights = {b['flight_number'] for b in bookings}
            common_flights = flight_numbers.intersection(booking_flights)
            
            if common_flights:
                print(f"✅ 发现 {len(common_flights)} 个共同航班:")
                for flight_num in common_flights:
                    print(f"  - {flight_num}")
            else:
                print("ℹ️  暂无共同航班数据")
    
    def run_demo(self):
        """运行演示"""
        print("🎮 智能机票预订系统 - 多Agent协作演示")
        print("=" * 60)
        
        # 检查MCP服务器状态
        if not self.check_mcp_server():
            print("❌ MCP服务器未启动，请先启动服务器")
            print("启动命令: python mcp_server.py")
            return
        
        print("✅ MCP服务器连接正常")
        
        while True:
            print("\n选择演示模式:")
            print("1. 自动演示")
            print("2. 交互模式")
            print("3. 批量演示")
            print("4. 通信测试")
            print("5. 退出")
            
            choice = input("\n请选择 (1-5): ").strip()
            
            if choice == "1":
                # 自动演示
                result = self.automated_booking_flow("张三", "PEK", "SHA")
                if result["success"]:
                    print("\n🎉 演示完成！")
                else:
                    print(f"\n❌ 演示失败: {result['message']}")
            
            elif choice == "2":
                self.interactive_collaboration_demo()
            
            elif choice == "3":
                self.batch_demo()
            
            elif choice == "4":
                self.agent_communication_test()
            
            elif choice == "5":
                print("👋 再见!")
                break
            
            else:
                print("❌ 无效选择")

def main():
    demo = MultiAgentDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
