from django.db import models

available_stocks = {
                    "NOVOb": {"info": {"longName": "Novo", "symbol": "NOVOb","currency": "DKK", "currentPrice": 100}},
                    "GN": {"info": {"longName": "GN Store Nord A/S", "symbol": "GN","currency": "DKK", "currentPrice": 170}},
                    "DANSKE": {"info": {"longName": "Danske Bank", "symbol": "DANSKE","currency": "DKK", "currentPrice": 50}},
                    "GMAB": {"info": {"longName": "Genmab A/S", "symbol": "GMAB","currency": "DKK", "currentPrice": 300}},
                    "DSV": {"info": {"longName": "Dsv A/S", "symbol": "DSV","currency": "DKK", "currentPrice": 1000}},
                   }

# ticker.info["currentPrice"]
# stock_name= ticker.info["longName"], stock_symbol=ticker.info["symbol"], price_currency=ticker.info["currency"]

class Stock_Symbols(models.TextChoices):
    NOVOb = "NOVOb",
    GN = "GN",
    DANSKE = "DANSKE",
    GMAB = "GMAB",
    DSV = "DSV",
    # MAERSKb = "MAERSKb",
    # VWS = "VWS",
    # ORSTED = "ORSTED",
    # NZYMb = "NZYMb",
    # AMBUb = "AMBUb",
    # CHRH = "CHRH",
    # CARLb = "CARLb",
    # PNDORA = "PNDORA",
    # JYSK = "JYSK",
    # NDADK = "NDADK",
    # SYDB = "SYDB"


    @classmethod
    def get_ticker(cls, stock_symbol):
        return available_stocks[stock_symbol]