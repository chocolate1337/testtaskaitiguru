import enum
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base
import uuid

class OrderStatus(enum.Enum):
    NEW = "NEW"
    PARTIAL = "PARTIAL"
    PAID = "PAID"

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.NEW)
    
    payments = relationship("Payment", back_populates="order")