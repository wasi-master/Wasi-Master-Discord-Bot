class ShopItem():
    def __init__(self, name: str, beautiful_name: str, buy: int, sell: int, is_usable: bool):
        self.name = name
        self.pretty_name = beautiful_name
        self.buy = buy
        self.sell = sell