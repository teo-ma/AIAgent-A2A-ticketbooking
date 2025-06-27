#!/usr/bin/env python3
"""
MCP服务器测试脚本
用于测试MCP服务器的所有API端点
"""

import requests
import json
import unittest
from datetime import datetime, date, time
from decimal import Decimal

class TestMCPServer(unittest.TestCase):
    def setUp(self):
        """测试初始化"""
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.test_booking_id = None
        self.test_flight_id = None
    
    def test_01_health_check(self):
        """测试健康检查端点"""
        response = self.session.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        print("✅ 健康检查通过")
    
    def test_02_get_flights(self):
        """测试获取航班列表"""
        response = self.session.get(f"{self.base_url}/flights")
        self.assertEqual(response.status_code, 200)
        
        flights = response.json()
        self.assertIsInstance(flights, list)
        
        if flights:
            flight = flights[0]
            required_fields = ['id', 'flight_number', 'airline', 'departure_airport', 
                             'arrival_airport', 'departure_time', 'arrival_time', 'price']
            for field in required_fields:
                self.assertIn(field, flight)
        
        print(f"✅ 获取航班列表通过 ({len(flights)} 个航班)")
    
    def test_03_search_flights(self):
        """测试搜索航班"""
        response = self.session.get(f"{self.base_url}/flights/search/PEK/SHA")
        self.assertEqual(response.status_code, 200)
        
        flights = response.json()
        self.assertIsInstance(flights, list)
        
        # 验证搜索结果
        for flight in flights:
            self.assertIn('PEK', flight['departure_airport'])
            self.assertIn('SHA', flight['arrival_airport'])
        
        print(f"✅ 搜索航班通过 (找到 {len(flights)} 个航班)")
    
    def test_04_create_flight(self):
        """测试创建航班"""
        flight_data = {
            "flight_number": "TEST001",
            "airline": "测试航空",
            "departure_airport": "PEK",
            "arrival_airport": "SHA",
            "departure_time": "08:00:00",
            "arrival_time": "10:30:00",
            "price": "599.00",
            "available_seats": 100,
            "aircraft_type": "Boeing 737",
            "status": "active"
        }
        
        response = self.session.post(f"{self.base_url}/flights", json=flight_data)
        self.assertEqual(response.status_code, 200)
        
        flight = response.json()
        self.assertEqual(flight['flight_number'], 'TEST001')
        self.test_flight_id = flight['id']
        
        print(f"✅ 创建航班通过 (ID: {self.test_flight_id})")
    
    def test_05_get_flight_by_number(self):
        """测试根据航班号获取航班"""
        response = self.session.get(f"{self.base_url}/flights/number/TEST001")
        self.assertEqual(response.status_code, 200)
        
        flight = response.json()
        self.assertEqual(flight['flight_number'], 'TEST001')
        
        print("✅ 根据航班号获取航班通过")
    
    def test_06_create_booking(self):
        """测试创建预订"""
        booking_data = {
            "title": "测试预订",
            "passenger_name": "测试用户",
            "flight_number": "TEST001",
            "departure_date": "2024-08-15",
            "departure_time": "08:00:00",
            "arrival_date": "2024-08-15",
            "arrival_time": "10:30:00",
            "departure_airport": "PEK",
            "arrival_airport": "SHA",
            "seat_number": "12A",
            "price": "599.00"
        }
        
        response = self.session.post(f"{self.base_url}/bookings", json=booking_data)
        self.assertEqual(response.status_code, 200)
        
        booking = response.json()
        self.assertEqual(booking['passenger_name'], '测试用户')
        self.test_booking_id = booking['id']
        
        print(f"✅ 创建预订通过 (ID: {self.test_booking_id})")
    
    def test_07_get_bookings(self):
        """测试获取预订列表"""
        response = self.session.get(f"{self.base_url}/bookings")
        self.assertEqual(response.status_code, 200)
        
        bookings = response.json()
        self.assertIsInstance(bookings, list)
        
        print(f"✅ 获取预订列表通过 ({len(bookings)} 个预订)")
    
    def test_08_get_booking_by_id(self):
        """测试根据ID获取预订"""
        if self.test_booking_id:
            response = self.session.get(f"{self.base_url}/bookings/{self.test_booking_id}")
            self.assertEqual(response.status_code, 200)
            
            booking = response.json()
            self.assertEqual(booking['id'], self.test_booking_id)
            
            print("✅ 根据ID获取预订通过")
    
    def test_09_search_bookings_by_passenger(self):
        """测试根据乘客姓名搜索预订"""
        response = self.session.get(f"{self.base_url}/bookings/search/测试用户")
        self.assertEqual(response.status_code, 200)
        
        bookings = response.json()
        self.assertIsInstance(bookings, list)
        
        # 验证搜索结果
        for booking in bookings:
            self.assertIn('测试用户', booking['passenger_name'])
        
        print(f"✅ 搜索预订通过 (找到 {len(bookings)} 个预订)")
    
    def test_10_update_booking(self):
        """测试更新预订"""
        if self.test_booking_id:
            update_data = {
                "seat_number": "15B",
                "status": "confirmed"
            }
            
            response = self.session.put(f"{self.base_url}/bookings/{self.test_booking_id}", 
                                      json=update_data)
            self.assertEqual(response.status_code, 200)
            
            booking = response.json()
            self.assertEqual(booking['seat_number'], '15B')
            
            print("✅ 更新预订通过")
    
    def test_11_get_stats(self):
        """测试获取统计信息"""
        response = self.session.get(f"{self.base_url}/stats")
        self.assertEqual(response.status_code, 200)
        
        stats = response.json()
        required_fields = ['total_bookings', 'total_flights', 'confirmed_bookings', 'timestamp']
        for field in required_fields:
            self.assertIn(field, stats)
        
        print(f"✅ 获取统计信息通过 (预订: {stats['total_bookings']}, 航班: {stats['total_flights']})")
    
    def test_99_cleanup(self):
        """清理测试数据"""
        # 删除测试预订
        if self.test_booking_id:
            response = self.session.delete(f"{self.base_url}/bookings/{self.test_booking_id}")
            if response.status_code == 200:
                print(f"✅ 清理测试预订 (ID: {self.test_booking_id})")
        
        # 删除测试航班
        if self.test_flight_id:
            response = self.session.delete(f"{self.base_url}/flights/{self.test_flight_id}")
            if response.status_code == 200:
                print(f"✅ 清理测试航班 (ID: {self.test_flight_id})")

def run_manual_tests():
    """手动运行测试（不使用unittest框架）"""
    print("🧪 MCP服务器手动测试")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    try:
        # 健康检查
        print("\n1. 测试健康检查...")
        response = session.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return
        
        # 获取航班
        print("\n2. 测试获取航班...")
        response = session.get(f"{base_url}/flights", timeout=5)
        if response.status_code == 200:
            flights = response.json()
            print(f"✅ 获取到 {len(flights)} 个航班")
        else:
            print(f"❌ 获取航班失败: {response.status_code}")
        
        # 搜索航班
        print("\n3. 测试搜索航班...")
        response = session.get(f"{base_url}/flights/search/PEK/SHA", timeout=5)
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ 搜索到 {len(search_results)} 个航班")
        else:
            print(f"❌ 搜索航班失败: {response.status_code}")
        
        # 创建预订
        print("\n4. 测试创建预订...")
        booking_data = {
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
        }
        
        response = session.post(f"{base_url}/bookings", json=booking_data, timeout=5)
        if response.status_code == 200:
            booking = response.json()
            booking_id = booking['id']
            print(f"✅ 创建预订成功 (ID: {booking_id})")
            
            # 获取预订
            print("\n5. 测试获取预订...")
            response = session.get(f"{base_url}/bookings/{booking_id}", timeout=5)
            if response.status_code == 200:
                print("✅ 获取预订成功")
            else:
                print(f"❌ 获取预订失败: {response.status_code}")
            
        else:
            print(f"❌ 创建预订失败: {response.status_code}")
        
        # 获取统计
        print("\n6. 测试获取统计...")
        response = session.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 统计信息: {stats['total_bookings']} 预订, {stats['total_flights']} 航班")
        else:
            print(f"❌ 获取统计失败: {response.status_code}")
        
        print("\n🎉 所有测试完成！")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接错误: {e}")
        print("请确保MCP服务器已启动 (python mcp_server.py)")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--unittest":
        # 运行unittest测试
        unittest.main(argv=[''], exit=False, verbosity=2)
    else:
        # 运行手动测试
        run_manual_tests()

if __name__ == "__main__":
    main()
