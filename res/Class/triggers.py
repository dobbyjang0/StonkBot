from ..DB import db

class db_update:
    def __init__(self, bot):
        self.bot = bot
        self.channel = self.bot.get_channel(812895047862452254)

    async def process(self):
        if self.channel:
            await self.channel.send(f"주식 목록 업데이트 테스트")
        pass
