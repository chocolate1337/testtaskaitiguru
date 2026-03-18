from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.models.payment import PaymentType, PaymentStatus

class PaymentBase(BaseModel):
    
    amount: Decimal = Field(
        gt=0, 
        max_digits=10, 
        decimal_places=2, 
        description="Сумма платежа (строго больше нуля)"
    )
    type: PaymentType

class PaymentCreateRequest(PaymentBase):
    order_id: UUID

class PaymentResponse(PaymentBase):
    id: UUID
    order_id: UUID
    status: PaymentStatus
    # bank_payment_id можно скрыть из внешнего API, если клиент не должен его знать,
    # либо оставить для дебага
    bank_payment_id: Optional[str] = None

    
    model_config = ConfigDict(from_attributes=True)