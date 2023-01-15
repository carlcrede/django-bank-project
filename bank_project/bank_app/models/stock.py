from __future__ import annotations
from django.db import models, transaction
from django.db.models.query import QuerySet
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from bank_app.models import Stock_Symbols, Stocks_Ledger
from uuid import uuid4
import yfinance as yf
import time


class Stock(models.Model):
    stock_uuid = models.UUIDField()
    stock_company_name = models.CharField(max_length=30)
    stock_symbol = models.CharField(
        max_length=15, choices=Stock_Symbols.choices)
    price_currency = models.CharField(max_length=3)
    belongs_to = models.ForeignKey('Customer', on_delete=models.CASCADE)
    # created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = 'belongs_to', 'stock_symbol'

    def __str__(self) -> str:
        return f'({self.stock_symbol}) {self.stock_company_name}'

    @classmethod
    def stocks(cls, customer):
        customer_stocks = cls.objects.filter(belongs_to=customer)
        stocks_with_stock_volume_above_0 = []
        for stock in customer_stocks:
            if stock.stock_volume > 0:
                stocks_with_stock_volume_above_0.append(stock.pk)
        return cls.objects.filter(id__in=stocks_with_stock_volume_above_0)

    @classmethod
    def stock(cls, customer, stock_symbol):
        print("Stock > stock > customer: ", customer)
        print("Stock > stock > stock_symbol: ", stock_symbol)
        stock_of_buyer = cls.objects.filter(belongs_to=customer, stock_symbol=stock_symbol)
        if stock_of_buyer.count():
            stock_of_buyer = stock_of_buyer[0]
        print("Stock > stock > stock_of_buyer: ", stock_of_buyer)
        return stock_of_buyer
        # ticker = yf.Ticker(stock_symbol)
        # available_stock = cls(ticker.info["longName"], ticker.info["symbol"],
        #                       ticker.info["currentPrice"], ticker.info["currency"])
        # return available_stock

    @classmethod
    def stock_by_id(cls, stock_uuid):
        return cls.objects.filter(stock_uuid=stock_uuid)
        ticker = yf.Ticker(stock_symbol)
        available_stock = cls(ticker.info["longName"], ticker.info["symbol"],
                              ticker.info["currentPrice"], ticker.info["currency"])
        return available_stock

    @property
    def current_stock_price(self):
        ticker = yf.Ticker(self.stock_symbol)
        current_price = ticker.info["currentPrice"]
        return round(current_price, 2)
        # ticker = Stock_Symbols.get_ticker(self.stock_symbol)
        # return ticker["info"]["currentPrice"]

    @property
    def stock_volume(self):
        stock_volume = self.movements.aggregate(models.Sum('stock_volume'))[
            'stock_volume__sum'] or 0
        # print("Int Stock > stock_volume: ", stock_volume)
        return stock_volume

    @property
    def movements(self):
        movements = Stocks_Ledger.objects.filter(
            stock=self).order_by('-created_at')
        # print("Int Stock > movements: ", movements)
        return movements

    @classmethod
    def transfer_stock(cls, stock_volume_to_buy, stock_of_seller, stock_seller_account,  stock_buyer_account, stock_of_buyer=None):
        # create Stock object and save it to DB if it doesnt already exist

        if not stock_of_buyer:
            stock_of_buyer = cls.save_new_stock(
                stock_of_seller.stock_symbol, stock_buyer_account.customer)

        Stocks_Ledger.transfer_stock(price_at_purchase=stock_of_seller.current_stock_price, stock_volume_to_buy=stock_volume_to_buy,
                                        stock_of_seller=stock_of_seller, stock_seller_account=stock_seller_account, stock_seller_text="sold stock", 
                                        stock_of_buyer=stock_of_buyer, stock_buyer_account=stock_buyer_account, stock_buyer_text="bought stock"
                                    )
        # move stocks from seller to buyer

    @classmethod
    def save_new_stock(cls, stock_symbol, customer):
        uuid = uuid4()
        ticker = yf.Ticker(stock_symbol)
        # print(ticker.info)
        # print(ticker["info"]["longName"])
        return cls.objects.create(stock_uuid=uuid, stock_company_name= ticker.info["longName"], stock_symbol=ticker.info["symbol"], price_currency=ticker.info["currency"], belongs_to=customer)
        
        # ticker = Stock_Symbols.get_ticker(stock_symbol)
        # return cls.objects.create(stock_uuid=uuid, stock_company_name=ticker["info"]["longName"], stock_symbol=ticker["info"]["symbol"], price_currency=ticker["info"]["currency"], belongs_to=customer)
