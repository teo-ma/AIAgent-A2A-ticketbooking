#!/usr/bin/env python3
"""
数据库初始化脚本
创建表结构并插入示例数据
"""

from database import create_tables, SessionLocal, Flight, Booking
from datetime import datetime, date, time
from decimal import Decimal

def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    # 创建表
    create_tables()
    print("✅ 数据库表创建成功")
    
    # 插入示例数据
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing_flights = db.query(Flight).count()
        if existing_flights > 0:
            print("ℹ️  数据库中已有数据，跳过初始化")
            return
        
        # 插入示例航班数据
        sample_flights = [
            Flight(
                flight_number="CA1001",
                airline="中国国际航空",
                departure_airport="PEK",
                arrival_airport="SHA",
                departure_time=time(8, 30),
                arrival_time=time(10, 45),
                price=Decimal("680.00"),
                available_seats=120,
                aircraft_type="Boeing 737",
                status="active"
            ),
            Flight(
                flight_number="MU2001",
                airline="中国东方航空",
                departure_airport="SHA",
                arrival_airport="CAN",
                departure_time=time(14, 20),
                arrival_time=time(17, 10),
                price=Decimal("860.00"),
                available_seats=180,
                aircraft_type="Airbus A320",
                status="active"
            ),
            Flight(
                flight_number="CZ3001",
                airline="中国南方航空",
                departure_airport="CAN",
                arrival_airport="CTU",
                departure_time=time(19, 45),
                arrival_time=time(22, 30),
                price=Decimal("720.00"),
                available_seats=160,
                aircraft_type="Boeing 787",
                status="active"
            ),
            Flight(
                flight_number="3U4001",
                airline="四川航空",
                departure_airport="CTU",
                arrival_airport="KMG",
                departure_time=time(9, 15),
                arrival_time=time(11, 50),
                price=Decimal("580.00"),
                available_seats=140,
                aircraft_type="Airbus A319",
                status="active"
            ),
            Flight(
                flight_number="MF5001",
                airline="厦门航空",
                departure_airport="XIY",
                arrival_airport="HGH",
                departure_time=time(16, 30),
                arrival_time=time(19, 15),
                price=Decimal("920.00"),
                available_seats=100,
                aircraft_type="Boeing 737 MAX",
                status="active"
            )
        ]
        
        for flight in sample_flights:
            db.add(flight)
        
        # 插入示例预订数据
        sample_bookings = [
            Booking(
                title="张三的商务出差",
                passenger_name="张三",
                flight_number="CA1001",
                departure_date=date(2024, 7, 15),
                departure_time=time(8, 30),
                arrival_date=date(2024, 7, 15),
                arrival_time=time(10, 45),
                departure_airport="PEK",
                arrival_airport="SHA",
                seat_number="12A",
                price=Decimal("680.00"),
                status="confirmed"
            ),
            Booking(
                title="李四的度假旅行",
                passenger_name="李四",
                flight_number="MU2001",
                departure_date=date(2024, 7, 20),
                departure_time=time(14, 20),
                arrival_date=date(2024, 7, 20),
                arrival_time=time(17, 10),
                departure_airport="SHA",
                arrival_airport="CAN",
                seat_number="8C",
                price=Decimal("860.00"),
                status="confirmed"
            )
        ]
        
        for booking in sample_bookings:
            db.add(booking)
        
        db.commit()
        print(f"✅ 成功插入 {len(sample_flights)} 个航班和 {len(sample_bookings)} 个预订")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("🎉 数据库初始化完成！")

if __name__ == "__main__":
    init_database()
