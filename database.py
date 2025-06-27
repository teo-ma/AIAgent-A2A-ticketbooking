from sqlalchemy import create_engine, Column, Integer, String, Date, Time, DECIMAL, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库连接字符串，使用postgresql+asyncpg驱动
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password123@localhost:5433/smart_flight_booking")
# 如果URL不包含驱动信息，则使用同步驱动
if "postgresql://" in DATABASE_URL and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

# 创建数据库引擎
try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    # 如果psycopg2失败，尝试使用SQLite作为fallback
    print(f"⚠️  PostgreSQL连接失败: {e}")
    print("🔄 使用SQLite作为备用数据库...")
    DATABASE_URL = "sqlite:///./smart_flight_booking.db"
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    passenger_name = Column(String(100), nullable=False)
    flight_number = Column(String(20), nullable=False)
    departure_date = Column(Date, nullable=False)
    departure_time = Column(Time, nullable=False)
    arrival_date = Column(Date, nullable=False)
    arrival_time = Column(Time, nullable=False)
    departure_airport = Column(String(10), nullable=False)
    arrival_airport = Column(String(10), nullable=False)
    seat_number = Column(String(10), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(20), unique=True, nullable=False)
    airline = Column(String(50), nullable=False)
    departure_airport = Column(String(10), nullable=False)
    arrival_airport = Column(String(10), nullable=False)
    departure_time = Column(Time, nullable=False)
    arrival_time = Column(Time, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    available_seats = Column(Integer, default=0)
    aircraft_type = Column(String(50), nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)
