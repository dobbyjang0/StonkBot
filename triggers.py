import save_log_yesalchemy as db

class db_update:
    def __init__(self, bot):
        self.bot = bot

    async def process(self):
        channel = self.bot.get_channel(812895047862452254)
        if channel:
            await channel.send(f"주식 목록 업데이트 테스트")
        pass
    