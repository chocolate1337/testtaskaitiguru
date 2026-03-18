import pytest
from decimal import Decimal
import uuid
from app.models.order import Order, OrderStatus
from app.models.payment import PaymentStatus, PaymentType
from app.services.payment_service import PaymentService, PaymentServiceError

@pytest.mark.asyncio
async def test_deposit_cash_updates_order_status(db_session, mock_bank_client):
    
    order = Order(id=uuid.uuid4(), total_amount=Decimal("100.00"), status=OrderStatus.NEW)
    db_session.add(order)
    await db_session.commit()

    service = PaymentService(db_session, mock_bank_client)

    
    payment = await service.process_deposit(
        order_id=order.id, 
        amount=Decimal("50.00"), 
        payment_type=PaymentType.CASH
    )

    
    assert payment.status == PaymentStatus.SUCCESS
    
    await db_session.refresh(order)
    assert order.status == OrderStatus.PARTIAL

@pytest.mark.asyncio
async def test_deposit_exceeds_total_amount_raises_error(db_session, mock_bank_client):
    order = Order(id=uuid.uuid4(), total_amount=Decimal("100.00"), status=OrderStatus.NEW)
    db_session.add(order)
    await db_session.commit()

    service = PaymentService(db_session, mock_bank_client)

    
    with pytest.raises(PaymentServiceError) as excinfo:
        await service.process_deposit(
            order_id=order.id, 
            amount=Decimal("150.00"), 
            payment_type=PaymentType.CASH
        )
    assert "exceeds order total" in str(excinfo.value)

@pytest.mark.asyncio
async def test_acquiring_payment_creates_pending_status(db_session, mock_bank_client):
    order = Order(id=uuid.uuid4(), total_amount=Decimal("100.00"))
    db_session.add(order)
    await db_session.commit()

    
    mock_bank_client.acquiring_start.return_value = "bank_123"
    service = PaymentService(db_session, mock_bank_client)

    payment = await service.process_deposit(
        order_id=order.id, 
        amount=Decimal("100.00"), 
        payment_type=PaymentType.ACQUIRING
    )

    assert payment.status == PaymentStatus.PENDING
    assert payment.bank_payment_id == "bank_123"
    
    await db_session.refresh(order)
    
    assert order.status == OrderStatus.NEW