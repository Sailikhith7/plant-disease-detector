import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Read the cloud or local database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/peekrakshak.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Database Models ---

class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String(100), primary_key=True, index=True)
    farmer_id = Column(String(100), nullable=True)
    farmer_name = Column(String(255), nullable=True)
    district = Column(String(100), nullable=True)
    crop = Column(String(100), nullable=True)
    disease_detected = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    severity = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(Text, nullable=True)
    status = Column(String(50), default="Pending Expert")
    created_at = Column(String(100), default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))


class ExpertResponse(Base):
    __tablename__ = "expert_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(100), index=True)
    expert_response = Column(Text)
    created_at = Column(String(100), default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))


class AlertDispatch(Base):
    __tablename__ = "alert_dispatches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    district = Column(String(100))
    crop = Column(String(100))
    disease = Column(String(255))
    target_phone = Column(String(50))
    officer_message = Column(Text)
    delivery_channel = Column(String(50))
    status = Column(String(50), default="DELIVERED")
    dispatched_at = Column(String(100), default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(String(100), unique=True, index=True)
    name = Column(String(255))
    phone = Column(String(50))
    district = Column(String(100))
    crop = Column(String(100))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()