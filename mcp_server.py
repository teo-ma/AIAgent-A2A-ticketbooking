#!/usr/bin/env python3
"""
MCP HTTP服务器
提供标准化的RESTful API接口，支持多Agent通信
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, date, time
from decimal import Decimal
import uvicorn
import os

from database import get_db, Booking, Flight
from sqlalchemy.orm import Session

# 创建FastAPI实例
app = FastAPI(
    title="智能机票预订系统 MCP Server",
    description="基于MCP协议的多Agent智能机票预订服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic模型定义
class BookingCreate(BaseModel):
    title: str
    passenger_name: str
    flight_number: str
    departure_date: date
    departure_time: time
    arrival_date: date
    arrival_time: time
    departure_airport: str
    arrival_airport: str
    seat_number: Optional[str] = None
    price: Decimal

class BookingUpdate(BaseModel):
    title: Optional[str] = None
    passenger_name: Optional[str] = None
    flight_number: Optional[str] = None
    departure_date: Optional[date] = None
    departure_time: Optional[time] = None
    arrival_date: Optional[date] = None
    arrival_time: Optional[time] = None
    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None
    seat_number: Optional[str] = None
    price: Optional[Decimal] = None
    status: Optional[str] = None

class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    passenger_name: str
    flight_number: str
    departure_date: date
    departure_time: time
    arrival_date: date
    arrival_time: time
    departure_airport: str
    arrival_airport: str
    seat_number: Optional[str]
    price: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

class FlightCreate(BaseModel):
    flight_number: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: time
    arrival_time: time
    price: Decimal
    available_seats: int = 0
    aircraft_type: Optional[str] = None
    status: str = "active"

class FlightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    flight_number: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: time
    arrival_time: time
    price: Decimal
    available_seats: int
    aircraft_type: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "message": "MCP Server is running",
        "timestamp": datetime.utcnow().isoformat()
    }

# 预订管理API端点

@app.post("/bookings", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    """创建新预订"""
    try:
        db_booking = Booking(**booking.model_dump())
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建预订失败: {str(e)}")

@app.get("/bookings", response_model=List[BookingResponse])
async def get_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取所有预订"""
    bookings = db.query(Booking).offset(skip).limit(limit).all()
    return bookings

@app.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """根据ID获取预订"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="预订不存在")
    return booking

@app.get("/bookings/search/{passenger_name}", response_model=List[BookingResponse])
async def search_bookings_by_passenger(passenger_name: str, db: Session = Depends(get_db)):
    """根据乘客姓名搜索预订"""
    bookings = db.query(Booking).filter(
        Booking.passenger_name.ilike(f"%{passenger_name}%")
    ).all()
    return bookings

@app.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int, 
    booking_update: BookingUpdate, 
    db: Session = Depends(get_db)
):
    """更新预订"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="预订不存在")
    
    try:
        update_data = booking_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(booking, field, value)
        
        booking.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新预订失败: {str(e)}")

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    """删除预订"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="预订不存在")
    
    try:
        db.delete(booking)
        db.commit()
        return {"message": f"预订 {booking_id} 已成功删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除预订失败: {str(e)}")

# 航班管理API端点

@app.post("/flights", response_model=FlightResponse)
async def create_flight(flight: FlightCreate, db: Session = Depends(get_db)):
    """创建新航班"""
    try:
        db_flight = Flight(**flight.model_dump())
        db.add(db_flight)
        db.commit()
        db.refresh(db_flight)
        return db_flight
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建航班失败: {str(e)}")

@app.get("/flights", response_model=List[FlightResponse])
async def get_flights(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取所有航班"""
    flights = db.query(Flight).filter(Flight.status == "active").offset(skip).limit(limit).all()
    return flights

@app.get("/flights/{flight_id}", response_model=FlightResponse)
async def get_flight(flight_id: int, db: Session = Depends(get_db)):
    """根据ID获取航班"""
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="航班不存在")
    return flight

@app.get("/flights/search/{departure}/{arrival}", response_model=List[FlightResponse])
async def search_flights(departure: str, arrival: str, db: Session = Depends(get_db)):
    """搜索航班"""
    flights = db.query(Flight).filter(
        Flight.departure_airport.ilike(f"%{departure}%"),
        Flight.arrival_airport.ilike(f"%{arrival}%"),
        Flight.status == "active"
    ).all()
    return flights

@app.get("/flights/number/{flight_number}", response_model=FlightResponse)
async def get_flight_by_number(flight_number: str, db: Session = Depends(get_db)):
    """根据航班号获取航班"""
    flight = db.query(Flight).filter(Flight.flight_number == flight_number).first()
    if not flight:
        raise HTTPException(status_code=404, detail="航班不存在")
    return flight

@app.delete("/flights/{flight_id}")
async def delete_flight(flight_id: int, db: Session = Depends(get_db)):
    """删除航班"""
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="航班不存在")
    
    try:
        db.delete(flight)
        db.commit()
        return {"message": f"航班 {flight_id} 已成功删除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除航班失败: {str(e)}")

# 统计信息端点
@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """获取系统统计信息"""
    total_bookings = db.query(Booking).count()
    total_flights = db.query(Flight).filter(Flight.status == "active").count()
    confirmed_bookings = db.query(Booking).filter(Booking.status == "confirmed").count()
    
    return {
        "total_bookings": total_bookings,
        "total_flights": total_flights,
        "confirmed_bookings": confirmed_bookings,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    # 获取配置
    host = os.getenv("MCP_SERVER_HOST", "localhost")
    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    
    print(f"🚀 启动MCP服务器...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"📖 API文档: http://{host}:{port}/docs")
    print(f"🔄 交互式文档: http://{host}:{port}/redoc")
    
    uvicorn.run(
        "mcp_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
