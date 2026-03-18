from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional
from uuid import UUID

from models.order import OrderStatus

class OrderResponse(BaseModel):
    id: UUID
    total_amount: Decimal
    status: OrderStatus

    model_config = ConfigDict(from_attributes=True)