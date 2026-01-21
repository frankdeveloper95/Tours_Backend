import stripe
from app.core.config import settings

stripe.api_key = str(settings.STRIPE_SECRET_KEY)


class StripeService:
    @staticmethod
    def create_payment_intent(amount: int, reserva_id: int):
        return stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={"reserva_id": reserva_id},
        )

    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str):
        return stripe.PaymentIntent.retrieve(payment_intent_id)
