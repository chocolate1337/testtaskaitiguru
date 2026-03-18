import httpx
from decimal import Decimal
from typing import Optional, Dict, Any

class BankAPIError(Exception):
    pass

class BankClient:
    def __init__(self, base_url: str = "https://bank.api"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=5.0)

    async def acquiring_start(self, order_id: str, amount: Decimal) -> str:
        """Возвращает ID платежа в банке или бросает ошибку."""
        try:
            response = await self.client.post(
                "/acquiring_start", 
                json={"order_id": order_id, "amount": str(amount)}
            )
            response.raise_for_status()
            data = response.json()
            return data["bank_payment_id"]
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            
            raise BankAPIError(f"Bank start error: {str(e)}")

    async def acquiring_check(self, bank_payment_id: str) -> Dict[str, Any]:
        """Возвращает состояние платежа."""
        try:
            response = await self.client.get(f"/acquiring_check?id={bank_payment_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise BankAPIError("Payment not found")
            raise BankAPIError(f"Bank check error: {str(e)}")
        except httpx.RequestError as e:
            raise BankAPIError(f"Bank connection error: {str(e)}")