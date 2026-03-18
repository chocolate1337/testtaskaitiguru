from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session 
from app.services.payment_service import PaymentService, PaymentServiceError
from app.integrations.bank import BankClient
from app.schemas.payment import PaymentCreateRequest, PaymentResponse

router = APIRouter(prefix="/payments", tags=["Payments"])

def get_payment_service(session: AsyncSession = Depends(get_session)) -> PaymentService:
    bank_client = BankClient() 
    return PaymentService(session=session, bank_client=bank_client)

@router.post("/deposit", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    payload: PaymentCreateRequest, 
    service: PaymentService = Depends(get_payment_service)
):
    """
    Создание нового платежа (депозит).
    """
    try:
        # Pydantic проверилUUID валиден amount > 0
        payment = await service.process_deposit(
            order_id=str(payload.order_id), 
            amount=payload.amount, 
            payment_type=payload.type
        )
        return payment
    except PaymentServiceError as e:
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: UUID4,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Оформление возврата по успешному платежу.
    """
    try:
        payment = await service.process_refund(payment_id=str(payment_id))
        return payment
    except PaymentServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))