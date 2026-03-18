from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.order import Order, OrderStatus
from app.models.payment import PaymentStatus, PaymentType, Payment
from app.integrations.bank import BankClient, BankAPIError

class PaymentServiceError(Exception):
    pass

class PaymentService:
    def __init__(self, session: AsyncSession, bank_client: BankClient):
        self.session = session
        self.bank_client = bank_client

    async def _recalculate_order_status(self, order: Order):
        """Внутренний метод для согласования статуса заказа на основе успешных платежей."""
        result = await self.session.execute(
            select(func.sum(Payment.amount))
            .where(Payment.order_id == order.id, Payment.status == PaymentStatus.SUCCESS)
        )
        total_paid = result.scalar() or Decimal('0.00')

        if total_paid == Decimal('0.00'):
            order.status = OrderStatus.NEW
        elif total_paid >= order.total_amount:
            order.status = OrderStatus.PAID
        else:
            order.status = OrderStatus.PARTIAL

    async def process_deposit(self, order_id: str, amount: Decimal, payment_type: PaymentType) -> Payment:
        # 1. Блокируем заказ для конкурентных транзакций
        result = await self.session.execute(
            select(Order).where(Order.id == order_id).with_for_update()
        )
        order = result.scalars().first()
        if not order:
            raise PaymentServiceError("Order not found")

        # 2. Проверяем лимиты
        paid_res = await self.session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.order_id == order.id, 
                Payment.status.in_([PaymentStatus.SUCCESS, PaymentStatus.PENDING])
            )
        )
        already_paid_or_pending = paid_res.scalar() or Decimal('0.00')
        
        if already_paid_or_pending + amount > order.total_amount:
            raise PaymentServiceError("Payment amount exceeds order total")

        # 3. Создаем платеж (Полиморфизм поведения)
        payment = Payment(order_id=order.id, amount=amount, type=payment_type)
        self.session.add(payment)

        if payment_type == PaymentType.CASH:
            # Наличные проводим сразу
            payment.status = PaymentStatus.SUCCESS
            await self._recalculate_order_status(order)
        elif payment_type == PaymentType.ACQUIRING:
            # Эквайринг требует похода в банк
            try:
                bank_id = await self.bank_client.acquiring_start(str(order.id), amount)
                payment.bank_payment_id = bank_id
                payment.status = PaymentStatus.PENDING
                # Статус заказа пока не меняем, ждем check
            except BankAPIError as e:
                payment.status = PaymentStatus.FAILED
                raise PaymentServiceError(str(e))

        await self.session.commit()
        return payment

    async def process_refund(self, payment_id: str) -> Payment:
        # Сначала блокируем платеж, потом его заказ
        result = await self.session.execute(
            select(Payment).where(Payment.id == payment_id).with_for_update()
        )
        payment = result.scalars().first()
        if not payment:
            raise PaymentServiceError("Payment not found")
            
        if payment.status != PaymentStatus.SUCCESS:
            raise PaymentServiceError("Can only refund successful payments")

        order_res = await self.session.execute(
            select(Order).where(Order.id == payment.order_id).with_for_update()
        )
        order = order_res.scalars().first()

        # Логика возврата (для банка тут был бы вызов bank API refund, если бы требовалось)
        payment.status = PaymentStatus.REFUNDED
        await self._recalculate_order_status(order)
        
        await self.session.commit()
        return payment

    async def sync_bank_payment(self, payment_id: str):
        """Метод для вызова из фоновых джобов (Celery) или вебхуков."""
        result = await self.session.execute(select(Payment).where(Payment.id == payment_id))
        payment = result.scalars().first()
        
        if not payment or payment.type != PaymentType.ACQUIRING or payment.status != PaymentStatus.PENDING:
            return

        try:
            bank_status_data = await self.bank_client.acquiring_check(payment.bank_payment_id)
            # В реальном мире тут маппинг статусов банка на наши
            if bank_status_data.get("status") == "SUCCESS":
                # Блокируем заказ и обновляем
                order_res = await self.session.execute(
                    select(Order).where(Order.id == payment.order_id).with_for_update()
                )
                order = order_res.scalars().first()
                payment.status = PaymentStatus.SUCCESS
                await self._recalculate_order_status(order)
                await self.session.commit()
        except BankAPIError:
            pass # Оставляем pending до следующего поллинга