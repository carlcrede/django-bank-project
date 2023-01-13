from uuid import uuid4
from django.db import models, transaction
from ..errors import InsufficientStocks
from django.core.validators import MinValueValidator, MaxValueValidator
from bank_app.models import Stock_Symbols, Ledger

class Stocks_Ledger(models.Model):
    transaction_id = models.UUIDField()
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE)
    stock_volume = models.IntegerField(validators=[MinValueValidator(1, message="Minimum value is 1")])
    created_at = models.DateTimeField(auto_now_add=True)
    # "Chosen stock is not in the list of available stocks"

    @classmethod
    def transfer_stock(cls, price_at_purchase, stock_volume_to_buy, 
                        stock_of_seller, stock_seller_account,  stock_seller_text, 
                        stock_of_buyer, stock_buyer_account, stock_buyer_text, bank_stocks=False):
        uuid = uuid4()
        # f"selling {stock_symbol} stocks"
        with transaction.atomic():
            if  bank_stocks or (stock_of_seller.stock_volume >= stock_volume_to_buy):
                amount_to_transfer_for_stock_purchase = stock_volume_to_buy * price_at_purchase
                Ledger.transfer(amount_to_transfer_for_stock_purchase, stock_buyer_account, stock_buyer_text, stock_seller_account, stock_seller_text)
                cls(transaction_id=uuid, stock_volume=-stock_volume_to_buy,stock=stock_of_seller).save()
                cls(transaction_id=uuid, stock_volume=stock_volume_to_buy, stock=stock_of_buyer).save()
            else: 
                raise InsufficientStocks(f"Not enough {stock_of_seller.stock_symbol} stocks to perform the operation")
        return uuid


    def __str__(self) -> str:
        return f'({self.stock}) {self.stock_volume}'

# @classmethod
# def get_available_stocks(cls, user):
#     available_stocks = []
#     for stock_symbol in Stock_Symbols.values:
#         stock = cls.get_available_stock(stock_symbol)
#         available_stocks.append(stock)
#     return available_stocks

# @classmethod
# def get_available_stock(cls, stock_symbol):
#     ticker = yf.Ticker(stock_symbol)
#     available_stock = cls(ticker["longName"], ticker["symbol"], ticker["currentPrice"], ticker["currency"])
#     return available_stock

