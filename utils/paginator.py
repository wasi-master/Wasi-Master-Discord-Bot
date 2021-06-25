import asyncio

import discord
from discord.ext import menus


class Paginator(menus.Menu):
    def __init__(self, embeds):
        self.embeds = embeds
        self.current_page = 0
        self.channel = None
        super().__init__()

    async def send_initial_message(self, ctx, channel):
        self.channel = channel
        emb = self.embeds[self.current_page].set_footer(
            text=f"page {self.current_page+1}/{len(self.embeds)}"
        )
        self.message = await channel.send(embed=emb)
        return self.message

    def check_skip(self):
        return len(self.embeds) < 2

    @menus.button("\u23ee\ufe0f", skip_if=check_skip)
    async def on_first_page(self, payload):
        if self.current_page == 0:
            return
        self.current_page = 0
        await self.message.edit(
            embed=self.embeds[self.current_page].set_footer(
                text=f"page {self.current_page+1}/{len(self.embeds)}"
            )
        )

    @menus.button("\u2b05\ufe0f")
    async def on_previous_page(self, payload):
        if self.current_page == 0:
            return
        self.current_page -= 1
        await self.message.edit(
            embed=self.embeds[self.current_page].set_footer(
                text=f"page {self.current_page+1}/{len(self.embeds)}"
            )
        )

    @menus.button("\u23f8\ufe0f")
    async def on_pause(self, payload):
        self.stop()
        await self.message.clear_reactions()

    @menus.button("\u23f9\ufe0f")
    async def on_stop(self, payload):
        self.stop()
        await self.message.delete()

    @menus.button("\u27a1\ufe0f")
    async def on_next_page(self, payload):
        if self.current_page == len(self.embeds):
            return
        self.current_page += 1
        await self.message.edit(
            embed=self.embeds[self.current_page].set_footer(
                text=f"page {self.current_page+1}/{len(self.embeds)}"
            )
        )

    @menus.button("\u23ed\ufe0f", skip_if=check_skip)
    async def on_last_page(self, payload):
        if self.current_page == len(self.embeds) - 1:
            return
        self.current_page = len(self.embeds) - 1
        await self.message.edit(
            embed=self.embeds[self.current_page].set_footer(
                text=f"page {self.current_page+1}/{len(self.embeds)}"
            )
        )

    @menus.button("\U0001f522")
    async def numbered_page(self, payload):
        channel = self.message.channel
        to_delete = []
        to_delete.append(
            await channel.send(
                f"{self.ctx.author.mention}, What page do you want to go to?"
            )
        )

        def message_check(msg):
            return (
                msg.author.id == payload.user_id
                and channel == msg.channel
                and msg.content.isdigit()
            )

        try:
            msg = await self.bot.wait_for("message", check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(
                await channel.send("{self.ctx.author.mention}, You took too long.")
            )
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            if page in range(0, len(self.embeds - 1)):
                self.current_page = page - 1
                await self.message.edit(
                    embed=self.embeds[self.current_page].set_footer(
                        text=f"page {self.current_page+1}/{len(self.embeds)}"
                    )
                )
            else:
                try:
                    await channel.delete_messages(to_delete)
                    return
                except discord.Forbidden:
                    pass

        try:
            await channel.delete_messages(to_delete)
        except discord.Forbidden:
            pass


# @bot.command()
# async def menu_example(ctx):
#     m = MyMenu()
#     await m.start(ctx)
