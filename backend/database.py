import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pikrakshak.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================
# MODELS
# ============================================================

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    district = Column(String, nullable=False, index=True)
    crop = Column(String, nullable=False)
    telegram_chat_id = Column(String, nullable=True)  # Store Telegram Chat ID

    cases = relationship("Case", back_populates="farmer")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    farmer_name = Column(String, nullable=False)
    district = Column(String, nullable=False, index=True)
    crop = Column(String, nullable=False)
    disease = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String, default="High")  # High, Medium, Low
    status = Column(String, default="Pending Expert")  # Pending Expert, Resolved
    gps_lat = Column(Float, default=20.3888)
    gps_long = Column(Float, default=78.1204)
    image_url = Column(String, nullable=True)
    expert_diagnosis = Column(String, nullable=True)
    prescription = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    farmer = relationship("Farmer", back_populates="cases")


class AlertDispatch(Base):
    __tablename__ = "alert_dispatches"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String, nullable=False)
    crop = Column(String, nullable=False)
    disease = Column(String, nullable=False)
    message_en = Column(Text, nullable=False)
    message_mr = Column(Text, nullable=True)
    farmers_notified = Column(Integer, default=0)
    status = Column(String, default="Delivered")  # Delivered, Failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# INITIAL SEED DATA (Creates demo records for Member D's tests)
# ============================================================

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(Farmer).count() == 0:
        # Seed test farmers across Maharashtra districts
        f1 = Farmer(name="Ramesh Patil", phone="9876543210", district="Yavatmal", crop="Cotton", telegram_chat_id="")
        f2 = Farmer(name="Suresh Deshmukh", phone="9876543211", district="Yavatmal", crop="Cotton", telegram_chat_id="")
        f3 = Farmer(name="Anil Jadhav", phone="9876543212", district="Yavatmal", crop="Cotton", telegram_chat_id="")
        f4 = Farmer(name="Vikas Shinde", phone="9876543213", district="Nagpur", crop="Rice", telegram_chat_id="")
        f5 = Farmer(name="Prakash Gaikwad", phone="9876543214", district="Amravati", crop="Groundnut", telegram_chat_id="")
        
        db.add_all([f1, f2, f3, f4, f5])
        db.commit()

        # Seed 6 Yavatmal Cotton Pink Bollworm cases to trigger the >= 5 outbreak threshold
        for i in range(1, 7):
            db.add(Case(
                farmer_name=f"Farmer {i} (Yavatmal)",
                district="Yavatmal",
                crop="Cotton",
                disease="cotton_pink_bollworm",
                confidence=0.92,
                severity="High",
                status="Pending Expert",
                gps_lat=20.3888 + (i * 0.005),
                gps_long=78.1204 + (i * 0.005),
                image_url="/uploads/sample_leaf.jpg"
            ))

        # Seed other district cases for the Analytics and Map views
        db.add(Case(farmer_name="Nagpur Rice Farmer", district="Nagpur", crop="Rice", disease="rice_leaf_blast", confidence=0.88, severity="Medium", status="Pending Expert", gps_lat=21.1458, gps_long=79.0882))
        db.add(Case(farmer_name="Amravati Farmer", district="Amravati", crop="Groundnut", disease="groundnut_early_rust", confidence=0.85, severity="Low", status="Resolved", expert_diagnosis="Early Rust", prescription="Apply Mancozeb 2g/L", resolved_at=datetime.datetime.utcnow(), gps_lat=20.9374, gps_long=77.7796))
        
        db.commit()
    db.close()