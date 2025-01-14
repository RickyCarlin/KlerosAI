import pandas as pd

class PriceDataModel:

    # timestamp is always in milliseconds
    def __init__(self,
                    symbol: str,
                    price: float,
                    exchange: str,
                    timestamp: str,
                    volume: float = None):
        self.symbol = symbol
        self.price = float(price)
        self.exchange = exchange
        self.timestamp = timestamp
        self.volume = float(volume)
        return
    
    def setVolume(self, volume):
        self.volume = volume
        return
    
    def pretty_timestamp(self):
        return pd.to_datetime(int(self.timestamp), unit='ms')
    
    def __str__(self):
        return f"{self.symbol} price at {self.pretty_timestamp()}: {self.price} with a volume of ({self.volume}) in ({self.exchange})"
    
    def volume_in_quote_currency(self):
        return self.price * self.volume