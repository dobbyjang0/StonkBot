from ..DB import db
from ..DB import market_data
import multiprocessing
import discord

class MetaSingleton(type):
    
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class bot_action(metaclass=MetaSingleton):
    def __init__(self, bot):
        self.bot = bot
        self.channel = self.bot.get_channel(833299968987103242)
        self.process_kospi = multiprocessing.Process(target=market_data.kospi_tickdata)
        self.process_kosdaq = multiprocessing.Process(target=market_data.kosdaq_tickdata)
        self.process_index = multiprocessing.Process(target=market_data.index_tickdata)

        print('bot_action 생성')
        
    async def api_start(self):
        self.process_kospi.start()
        self.process_kosdaq.start()
        self.process_index.start()
        
        
        # await self.channel.send('실시간 데이터 시작 완료')
        # RuntimeWarning: Enable tracemalloc to get the object allocation traceback
        # 해결하기
        
        print('실시간 데이터 시작 완료')
        
        
    async def api_stop(self):
        self.process_kospi.close()
        self.process_kosdaq.start()
        self.process_index.start()
        
        # await self.channel.send('실시간 데이터 종료')
        
        print('실시간 데이터 종료')


    async def update_stock_info(self):
        db.StockInfoTable().update_table()
        
        # await self.channel.send('주식정보 업데이트')
        
        print('주식정보 업데이트')