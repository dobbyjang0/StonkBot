import discord
from discord.ext import commands, tasks
import pandas
from datetime import date, datetime
from datetime import time
import nest_asyncio
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import multiprocessing
import json

from res.Class import stock
from res.Class.embed_form import embed_factory as ef
from res.Class import triggers
from res.DB import db

from res.DB.market_data import login


nest_asyncio.apply()

bot = commands.Bot(command_prefix="-")

extensions = [
    "res.Cogs.bot_function",
    "res.Cogs.mock"
]

@bot.event
async def on_ready():
    
    
    print("--- 연결 성공 ---")
    print(f"봇 이름: {bot.user.name}")
    print(f"ID: {bot.user.id}")
    
    """
    실시간 시세, 뉴스 데이터 받는 부분
    api 세팅 완료하면 이거 주석 해제하고 사용할것
    사용전에 save_log_yesalchemy.KRXRealData 클래스의 create_table 꼭 실행할것
    """
    
    '''
    market_data.login()
    process_kospi = multiprocessing.Process(target=market_data.kospi_tickdata)
    process_kosdaq = multiprocessing.Process(target=market_data.kosdaq_tickdata)
    process_index = multiprocessing.Process(target=market_data.index_tickdata)
    process_kospi.start()
    process_kosdaq.start()
    process_index.start()
    
    print('실시간 데이터 시작')
    '''
    login()
    print('로그인 완료')
    if datetime.now().hour > 7 and datetime.now().hour < 15:
        await triggers.bot_action(bot).api_start()
        print('실시간 데이터 시작')
    else:
        await bot.get_channel(833299968987103242).send('실시간 데이터 시작 안함')
    
    sched = AsyncIOScheduler(timezone="Asia/Seoul")
    sched.add_job(triggers.bot_action(bot).api_start, 'cron', hour=7)
    # 봇 끄는거 확실히 완성하고 주석표시 지울 것
    # sched.add_job(triggers.bot_action(bot).api_stop, 'cron', hour=15)
    sched.add_job(triggers.bot_action(bot).update_stock_info, 'cron', hour=4)
    
    sched.start()
    
    print('스케쥴러 시작')
    if bot.user.name == 'StonkBot_test':
        await bot.get_channel(833299968987103242).send('봇 켜짐')
    elif bot.user.name == 'StonkBot':
        await bot.get_channel(817874717921902703).send('봇 켜짐')
    
#관리 코드
@bot.command()
async def 킬(ctx):
    if ctx.author.id not in [378887088524886016, 731836288147259432, 797492145980047361]:
        await ctx.send("권한없음")
        return
    
    if bot.user.name == 'StonkBot_test':
        await bot.get_channel(833299968987103242).send('봇 꺼짐')
    elif bot.user.name == 'StonkBot':
        await bot.get_channel(817874717921902703).send('봇 꺼짐')
        
    await bot.close()
    
@bot.command()
async def 관리(ctx, action_type=None):
    if ctx.author.id not in [378887088524886016, 731836288147259432, 797492145980047361]:
        await ctx.send("권한없음")
        return
    
    # 실시간 시작
    if action_type == '시작':
        await triggers.bot_action(bot).api_start()
    # 실시간 끝, 하지 말것
    elif action_type == '끝':
        pass
        #await triggers.bot_action(bot).api_stop()
    # 주식목록 업데이트
    elif action_type == '업데이트':
        await triggers.bot_action(bot).update_stock_info()
        

@bot.command()
async def 테스트(ctx):
    if ctx.author.id not in [378887088524886016, 731836288147259432]:
        await ctx.send("권한없음")
        return
    await ctx.send(embed=ef("testembed").get)

@bot.command(aliases=['도움'])
async def help_all(ctx, help_input=None):
    help_type_dic = {None:'help_all', '주식':'help_serch', '검색':'help_serch',
                     '모의':'help_mock', '코스피':'help_kos', '코스닥':'help_kos',
                     '가즈아':'help_gazua', '계산':'help_calculate', '매매동향':'help_trend'}
    
    help_type = help_type_dic.get(help_input)
    if not help_type:
        help_type = 'help_all'
    
    await ctx.send(embed=ef(help_type).get)

#코스피, 코스닥
#로그 저장 추가하기
@bot.command(aliases=["kospi", 'KOSPI'])
async def 코스피(ctx, chart_type=None):
    serching_index = stock.KOSInfo()
    serching_index.get("KOSPI")
    
    if chart_type:
        serching_index.change_graph_interval(chart_type)
    
    await ctx.send(embed=ef("serch_result",**serching_index.to_dict()).get)
    
@bot.command(aliases=["kosdaq", 'KOSDAQ'])
async def 코스닥(ctx, chart_type=None):
    serching_index = stock.KOSInfo()
    serching_index.get("KOSDAQ")
    
    if chart_type:
        serching_index.change_graph_interval(chart_type)
    
    await ctx.send(embed=ef("serch_result",**serching_index.to_dict()).get)

# 주식 검색 기능
@bot.command(aliases=['검색'])
async def 주식(ctx, stock_name="도움", chart_type='일'):
    if stock_name == "도움":
        await ctx.send(embed=ef('help_serch').get)
        return
    
    #나중에 코스피, 코스닥 함수로 빼기
    elif stock_name == "코스피":
        serching_index = stock.KOSInfo()
        serching_index.get("KOSPI")
    
        if chart_type:
            serching_index.change_graph_interval(chart_type)
    
        await ctx.send(embed=ef("serch_result",**serching_index.to_dict()).get)
        return
    
    elif stock_name == '코스닥':
        serching_index = stock.KOSInfo()
        serching_index.get("KOSDAQ")
    
        if chart_type:
            serching_index.change_graph_interval(chart_type)
    
        await ctx.send(embed=ef("serch_result",**serching_index.to_dict()).get)
        return
    
    
    #주식 검색
    serch_stock = bot.get_cog('serch_stock')
    stock_code, stock_real_name, stock_market, is_ETF, alert_info = await serch_stock.serch_stock_by_bot(ctx, stock_name)
    
    if stock_code is None:
        return
    
    result = db.KRXRealData().read(stock_code)
    # 종목코드, 체결시간, 전일대비구분, 전일대비, 등락율, 현재가, 시가, 고가, 저가, 누적거래량, 누적거래대금
    input_variable = {'name' : stock_real_name, 'stock_market' : stock_market,
                      'code' : result[0], 'compared_sign' : result[2],
                      'compared_price' : result[3], 'rate' : result[4],
                      'price' : result[5], 'start_price' : result[6],
                      'high_price' : result[7], 'low_price' : result[8],
                      'volume' : result[9], 'transaction_price' : result[10],
                      'chart_type' : chart_type}
    #이름, 시장구분, 코드, 전일대비구분, 전일대비, 등락율, 현재가, 시가, 조가, 저가, 누적거래량, 누적거래대금, 차트타입

    await ctx.send(embed=ef("serch_result2",**input_variable).get)

@bot.command()
async def 계산(ctx, stock_name="도움", stock_count=1):
    if stock_name == "도움":
        await ctx.send(embed=ef('help_calculate').get)
        return
    
    if type(stock_count) != int:
        await ctx.send('주식 갯수는 숫자를 입력해 주세요')
        return
    
    #주식 검색
    serch_stock = bot.get_cog('serch_stock')
    stock_code, stock_real_name, *__= await serch_stock.serch_stock_by_bot(ctx, stock_name)
    
    if stock_code is None:
        await ctx.send('주식명 오류?')
        return
    
    stock_price = db.KRXRealData().read_price(stock_code)
    
    if stock_price is None:
        await ctx.send("거래 정지 종목입니다.")
        return
    
    await ctx.send(embed=ef("calculate", stock_count=stock_count, name=stock_name, price=stock_price).get)
    # 나중에 수수료 계산도 넣어주자

@bot.command(aliases=["매매현황", '동향', '현황', '매매'])
async def 매매동향(ctx, stock_name='도움', input_type=None, chart_type="월"):
    if stock_name == "도움":
        #await ctx.send(embed=ef('help_gazua').get)
        return
    if input_type not in ['외국인', '기관']:
        await ctx.send('외국인, 기관 입력해주세요')
        return
    
    #주식 
    serch_stock = bot.get_cog('serch_stock')
    stock_code, stock_real_name, *__ = await serch_stock.serch_stock_by_bot(ctx, stock_name)
    
    if stock_code == None:
        return
    
    await ctx.send(embed=ef('trading_trend', name=stock_name, code=stock_code, input_type=input_type, chart_type=chart_type).get)
    
               
#가즈아 기능
#나중에 가격도 검색해서 로그에 넣게 바꾸기?
@bot.command()
async def 가즈아(ctx, stock_name="도움", stock_price=None):
    if stock_name == "도움":
        await ctx.send(embed=ef('help_gazua').get)
        return
    
    #주식 검색
    serch_stock = bot.get_cog('serch_stock')
    stock_code, stock_real_name, *__ = await serch_stock.serch_stock_by_bot(ctx, stock_name)
    
    if stock_code == None:
        return
    
    if stock_price and stock_price.isdigit():
        await ctx.send('숫자를 입력해주세요')
        return
    
    
    #로그에 넣는다
    input_variable={"guild_id" : ctx.guild.id, "channel_id" : ctx.channel.id,
                    "author_id" : ctx.author.id, "stock_code" : stock_code,
                    "stock_value_want" : stock_price
                    }
    
    db.LogTable().insert_gazua_log(**input_variable)
    
    gazua_count = db.GazuaCountTable().read(stock_code)    
    db.GazuaCountTable().insert_update(stock_code)
    
    #주식코드를 기본키로 해서 추가?
    await ctx.send(embed=ef("gazua", stock_real_name, gazua_count, stock_price).get)
    return
    
# 모의 주식 관련 커맨드
@bot.command(name="지원금")
async def mock_support_fund(ctx):
    user_id = ctx.author.id
    try:
        fund_get_result = db.SupportFundTable().read(user_id)
        print(fund_get_result)
    except:
        print("에러")
        return
    
    #처음일경우 지원금 500만
    if fund_get_result is None:
        db.SupportFundTable().insert(user_id)
        db.AccountTable().insert(user_id, "KRW", 3000000, 3000000)
        await ctx.send(embed=ef("mock_support_first").get)
        return
    #아닐경우 매일마다 3만
    else:
        last_get_time, get_count = fund_get_result
        if date.today() != last_get_time:
            db.SupportFundTable().update(user_id)
            db.AccountTable().update(user_id, "KRW", 30000, 30000)
            await ctx.send(embed=ef("mock_support_second", get_count).get)
            #후원하면 지원금 묵혀서 얻는 것은 어떨까
        else:
            await ctx.send(embed=ef("mock_support_no").get)

@bot.command(name="매수")
async def mock_buy(ctx, stock_name=None, stock_count='1'):
     mock = bot.get_cog('mock_trans')
     await mock.mock_buy(ctx, stock_name, stock_count)

@bot.command(name="풀매수")
async def mock_buy_full(ctx, stock_name=None):
     mock = bot.get_cog('mock_trans')
     await mock.mock_buy(ctx, stock_name, '풀')
    
@bot.command(name="매도")
async def mock_sell(ctx, stock_name=None, stock_count='1'):
    mock = bot.get_cog('mock_trans')
    await mock.mock_sell(ctx, stock_name, stock_count)
    
@bot.command(name="풀매도")
async def mock_sell_full(ctx, stock_name=None, stock_count='1'):
    mock = bot.get_cog('mock_trans')
    await mock.mock_sell(ctx, stock_name, '풀')


@bot.command(name="보유")
async def mock_have(ctx, stock_name=None, stock_count=1):
    user_id = ctx.author.id
    fund_list = db.AccountTable().read_all(user_id)
    
    if fund_list is None:
        await ctx.send("보유 자산이 없습니다. 지원금을 받아주세요.")
        return
    
    await ctx.send(embed=ef("mock_have", ctx.author, fund_list).get)

            
def main():
    if __name__ == "__main__":
        #봇 실행
        
        for extension in extensions:
            try:
                bot.load_extension(extension)
            except Exception as error:
                print('fail to load %s: %s' % (extension, error))
            else:
                print('loaded %s' % extension)
                
        '''   
        bot_token.json 구조
        {"real" : "봇토큰",
         "test" : "봇토큰"}
        '''
        file_path = "./bot_token.json"
        with open(file_path, "r") as json_file:
            token_dic = json.load(json_file)
            
        bot_token = token_dic.get(input("real/test 입력 : "))
                    
        bot.run(bot_token)

        """
        뉴스데이터는 아직 어떻게 처리할지 안정해서 일단 냅둠. 이건 실행시키지 말것
        """
        # process_news = multiprocessing.Process(target=market_data.news)
        # process_news.start()

main()