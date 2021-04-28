from ..DB import db
from ..DB import market_data
import multiprocessing
import discord
import time

'''
class RealDataMediator:
    """
    실시간 데이터 start, terminate 전용 mediator

    Attributes:
        process_list: market_data.py 의 실시간데이터 감시용 클래스의 인스턴스를 요소로 하는 리스트.
    """
    def __init__(self):
        self.process_list = []

    def add_process(self, target):
        """
        실시간 감시를 실행할 인스턴스를 등록한다

        Args:
            target: 등록할 실시간데이터 감시용 클래스 인스턴스
        """
        self.process_list.append(target)

    def on_start(self):
        """
        multiprocess.Process 의 start() 메소드를 실행시켜 process_list 에 등록된 프로세스 시작
        """
        for process in self.process_list:
            time.sleep(4)
            process.start()

    def on_terminate(self):
        """
        multiprocess.Process 의 terminate() 메소드를 실행시켜 process_list 에 등록된 프로세스 종료
        """
        for process in self.process_list:
            time.sleep(4)
            process.terminate()

class LoadReal:
    """
    실시간데이터 수신 on, off 여부를 전달하는 클래스
    """
    def __init__(self):
        self.mediator = None

    def set_mediator(self, mediator):
        self.mediator = mediator

    def real_start(self):
        self.mediator.on_start()

    def real_terminate(self):
        self.mediator.on_terminate()
'''

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

        # self.real = LoadReal()
        # self.mediator = RealDataMediator()
        # self.real.set_mediator(self.mediator)

        # self.mediator.add_process(Kospi())
        # self.mediator.add_process(Kosdaq())
        # self.mediator.add_process(KrIndex())

        self.is_real_time_on = False

        print('bot_action 생성')
        
        
    async def api_start(self):
        if not self.is_real_time_on:
            # self.real.real_start()
            
            self.is_real_time_on = True
            
            process_kospi = market_data.Kospi()
            process_kosdaq = market_data.Kosdaq()
            # process_index = KrIndex()
            # process_news = multiprocessing.Process(target = news)
            time.sleep(3)
            process_kospi.start()
            print('코스피 시작')
            time.sleep(3)
            print(2)
            process_kosdaq.start()
            print('코스닥 시작')
            #time.sleep(3)
            #process_index.start()
            
            
            print('실시간 데이터 시작 완료')
            await self.channel.send('실시간 데이터 시작 완료')
        else:
            print('실시간 데이터 이미 켜짐')
            await self.channel.send('실시간 데이터 이미 켜짐')
        
        return
    

    async def api_stop(self):
        if self.is_real_time_on:
            self.real.real_terminate()

            self.is_real_time_on = False
            
            print('실시간 데이터 종료')
            await self.channel.send('실시간 데이터 종료')
        else:
            print('실시간 데이터 이미 꺼짐')
            await self.channel.send('실시간 데이터 이미 꺼짐')

        return

    
    async def update_stock_info(self):
        db.StockInfoTable().drop_table()
        db.StockInfoTable().create_table()
        db.StockInfoTable().update_table()
        
        await self.channel.send('주식테이블 업데이트 완료')
        
        return

def main():
    if __name__ == '__main__':
        # trigger 시도하기
        pass
    
