import discord

class ShopItem():
    def __init__(self, name: str, beautiful_name: str, description: str, buy: int, sell: int, is_usable: bool):
        self.name = name
        self.pretty_name = beautiful_name
        self.buy = buy
        self.sell = sell

class Embed(discord.Embed):
  def __init__(self, **kwargs):
    self.colour = kwargs.get(color) or 0x36393E
    super().__init__(kwargs)