from ..DB import db
from ..DB.market_data import kospi_tickdata
from ..DB.market_data import kosdaq_tickdata
from ..DB.market_data import index_tickdata
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
        self.process_kospi = multiprocessing.Process(target=kospi_tickdata)
        self.process_kosdaq = multiprocessing.Process(target=kosdaq_tickdata)
        self.process_index = multiprocessing.Process(target=index_tickdata)
        self.is_real_time_on = False

        print('bot_action 생성')
        
        
    async def api_start(self):
        if not self.is_real_time_on:
            self.process_kospi.start()
            self.process_kosdaq.start()
            self.process_index.start()
            self.is_real_time_on = True
            
            print('실시간 데이터 시작 완료')
            await self.channel.send('실시간 데이터 시작 완료')
        else:
            print('실시간 데이터 이미 켜짐')
            await self.channel.send('실시간 데이터 이미 켜짐')
        
        return
    
    ''' 
    아직 어케하는지 잘 모르겠다. 하지말것.
    async def api_stop(self):
        if self.is_real_time_on:
            self.process_kospi.terminate()
            self.process_kospi.close()
            self.process_kosdaq.terminate()
            self.process_kosdaq.close()
            self.process_index.terminate()
            self.process_index.close()
            self.is_real_time_on = False
            
            print('실시간 데이터 종료')
            await self.channel.send('실시간 데이터 종료')
        else:
            print('실시간 데이터 이미 꺼짐')
            await self.channel.send('실시간 데이터 이미 꺼짐')

        return
    '''
    
    async def update_stock_info(self):
        db.StockInfoTable().update_table()
        
        await self.channel.send('주식테이블 업데이트 완료')
        
        return