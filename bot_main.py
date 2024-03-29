import discord
from discord.ext import commands, tasks
import pandas
from datetime import date, datetime
from datetime import time
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import multiprocessing
import json
import sys

from res.Class import parser
from res.Class.embed_form import embed_factory as ef
from res.Class import triggers
from res.DB import db

from res.DB.market_data import Login

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="-", intents=intents)

extensions = [
    "res.Cogs.bot_function",
    "res.Cogs.mock"
]

@bot.event
async def on_ready():
    print("--- 연결 성공 ---")
    print(f"봇 이름: {bot.user.name}")
    print(f"ID: {bot.user.id}")


    Login().login_mock()

    # print('로그인 완료') → 이거 어차피 api에서 메세지 띄워주는거라 걍 주석처리해놈.
    if datetime.now().hour >= 8 and datetime.now().hour < 17:
        await triggers.bot_action(bot).api_start()
        print('실시간 데이터 시작')
    else:
        await bot.get_channel(833299968987103242).send('실시간 데이터 시작 안함')
    
    sched = AsyncIOScheduler(timezone="Asia/Seoul")
    sched.add_job(triggers.bot_action(bot).api_start, 'cron', hour=8, day_of_week="0-4")
    # 봇 끄는거 확실히 완성하고 주석표시 지울 것
    sched.add_job(triggers.bot_action(bot).api_stop, 'cron', hour=16, day_of_week="0-4")
    sched.add_job(triggers.bot_action(bot).update_stock_info, 'cron', hour=7, day_of_week="0-4")
    
    sched.start()
    
    print('스케쥴러 시작')
    if bot.user.name == 'StonkBot_test':
        await bot.get_channel(833299968987103242).send('봇 켜짐')
    elif bot.user.name == 'StonkBot':
        await bot.get_channel(833299968987103242).send('봇 켜짐')
    
# 관리 코드
@bot.command()
async def 킬(ctx):
    if ctx.author.id not in [378887088524886016, 731836288147259432, 797492145980047361]:
        await ctx.send("권한없음")
        return
    
    if bot.user.name == 'StonkBot_test':
        await bot.get_channel(833299968987103242).send('봇 꺼짐')
    elif bot.user.name == 'StonkBot':
        await bot.get_channel(833299968987103242).send('봇 꺼짐')
        
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

        await triggers.bot_action(bot).api_stop()

    # 주식목록 업데이트
    elif action_type == '업데이트':
        await triggers.bot_action(bot).update_stock_info()
        

@bot.command()
async def 테스트(ctx):
    if ctx.author.id not in [378887088524886016, 731836288147259432, 797492145980047361]:
        await ctx.send("권한없음")
        return
    await ctx.send(ctx.author)
    await ctx.send(ctx.author.id)
    await ctx.send(bot.get_user(ctx.author.id))
    # await ctx.send(embed=ef("testembed").get)

@bot.command(aliases=('도움',))
async def help_all(ctx, help_input=None):
    help_type_dic = {None:'help_all', '주식':'help_serch', '검색':'help_serch',
                     '모의':'help_mock', '코스피':'help_kos', '코스닥':'help_kos',
                     '가즈아':'help_gazua', '계산':'help_calculate', '매매동향':'help_trend'
                     ,'지수':'help_index', '순위':'help_ranking'}
    
    help_type = help_type_dic.get(help_input)
    if not help_type:
        help_type = 'help_all'
    
    await ctx.send(embed=ef(help_type).get)


@bot.command()
async def 지수(ctx, index_name='도움', chart_type='일'):
    if index_name == "도움":
        await ctx.send(embed=ef('help_index').get)
        return
    elif index_name in ('코스피', 'kospi', 'KOSPI', '코스닥', 'kosdaq', 'KOSDAQ'):
        if index_name in ('코스피', 'kospi', 'KOSPI'):
            index_real_name = 'KOSPI'
            index_code = '001'
        elif index_name in ('코스닥', 'kosdaq', 'KOSDAQ'):
            index_real_name = 'KOSDAQ'
            index_code = '301'

        result = db.KRXIndexData().read(index_code)

        if result is None:
            print("지수 오류")
            return

        #이름,
        input_variable = {'name': index_real_name, 'compared_sign': result[2],
                          'compared_price': result[3], 'rate': result[4],
                          'price': result[5], 'start_price': result[6],
                          'high_price': result[7], 'low_price': result[8],
                          'frgsvalue': result[12], 'orgsvalue': result[13],
                          'chart_type': chart_type}

        await ctx.send(embed=ef("serch_result_index", **input_variable).get)
        return
    else:
        index_parser = parser.IndexInfo()
        index_parser.get(index_name)
        
        if index_parser.name is None:
            await ctx.send('결과 없음')
            return
        
        await ctx.send(embed=ef("serch_result_world", **index_parser.to_dict(), chart_type=chart_type).get)


# 주식 검색 기능
@bot.command(aliases=('검색', 'ㄱㅅ', 'ㅈㅅ', 'ㄳ'))
async def 주식(ctx, stock_name="도움", chart_type='일'):
    if stock_name == "도움":
        await ctx.send(embed=ef('help_serch').get)
        return
    
    # 나중에 코스피, 코스닥 함수로 빼기

    # 주식 검색
    serch_stock = bot.get_cog('serch_stock')
    serch_result = await serch_stock.serch_stock_by_bot(ctx, stock_name)
    stock_code = serch_result.stock_code
    stock_name = serch_result.stock_name
    stock_market = serch_result.stock_market
    alert_info = serch_result.alert_info
    uplimit = serch_result.uplimit
    downlimit = serch_result.downlimit
    
    if stock_code is None:
        return
    
    result = db.KRXRealData().read(stock_code)
    
    if result is None:
        stock_parser = parser.StockInfo()
        price = stock_parser.get(stock_code).price
        
        input_variable = {'name' : stock_name, 'stock_market' : stock_market, 'code' : stock_code,
                          'price' : price, 'chart_type' : chart_type, 'alert_info' : alert_info}

        await ctx.send(embed=ef("serch_result2",**input_variable).get)
        return
    
    # 종목코드, 체결시간, 전일대비구분, 전일대비, 등락율, 현재가, 시가, 고가, 저가, 누적거래량, 누적거래대금
    input_variable = {'name' : stock_name, 'stock_market' : stock_market,
                      'code' : result[0], 'compared_sign' : result[2],
                      'compared_price' : result[3], 'rate' : result[4],
                      'price' : result[5], 'start_price' : result[6],
                      'high_price' : result[7], 'low_price' : result[8],
                      'uplimit' : uplimit, 'downlimit' : downlimit,
                      'volume' : result[9], 'transaction_price' : result[10],
                      'chart_type' : chart_type, 'alert_info' : alert_info}
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
    
    # 주식 검색
    serch_stock = bot.get_cog('serch_stock')
    serch_result = await serch_stock.serch_stock_by_bot(ctx, stock_name)
    stock_code = serch_result.stock_code
    stock_name = serch_result.stock_name
    
    if stock_code is None:
        await ctx.send('주식명 오류?')
        return
    
    stock_price = db.KRXRealData().read_price(stock_code)
    
    if stock_price is None:
        await ctx.send("거래 정지 종목입니다.")
        return
    
    await ctx.send(embed=ef("calculate", stock_count=stock_count, name=stock_name, price=stock_price).get)
    # 나중에 수수료 계산도 넣어주자

@bot.command(aliases=("매매현황", '동향', '현황', '매매', 'ㅁㅁ'))
async def 매매동향(ctx, stock_name='도움', input_type=None, chart_type="월"):
    if stock_name == "도움":
        # await ctx.send(embed=ef('help_gazua').get)
        return
    if input_type not in ['외국인', '기관']:
        await ctx.send('외국인, 기관 입력해주세요')
        return
    
    # 주식
    serch_stock = bot.get_cog('serch_stock')
    serch_result = await serch_stock.serch_stock_by_bot(ctx, stock_name)
    stock_code = serch_result.stock_code
    stock_name = serch_result.stock_name
    
    if stock_code == None:
        return
    
    await ctx.send(embed=ef('trading_trend', name=stock_name, code=stock_code, input_type=input_type, chart_type=chart_type).get)
    
               
# 가즈아 기능
# 나중에 가격도 검색해서 로그에 넣게 바꾸기?
@bot.command(aliases=('ㄱㅈㅇ',))
async def 가즈아(ctx, stock_name="도움", stock_price=None):
    if stock_name == "도움":
        await ctx.send(embed=ef('help_gazua').get)
        return
    
    # 주식 검색
    serch_stock = bot.get_cog('serch_stock')
    serch_result = await serch_stock.serch_stock_by_bot(ctx, stock_name)
    stock_code = serch_result.stock_code
    stock_name = serch_result.stock_name
    
    if stock_code is None:
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
    
    # 주식코드를 기본키로 해서 추가?
    await ctx.send(embed=ef("gazua", stock_name, gazua_count, stock_price).get)
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
    
    # 처음일경우 지원금 500만
    if fund_get_result is None:
        db.SupportFundTable().insert(user_id)
        db.AccountTable().insert(user_id, "KRW", 3000000, 3000000)
        await ctx.send(embed=ef("mock_support_first").get)
        return
    # 아닐경우 매일마다 3만
    else:
        last_get_time, get_count = fund_get_result
        if date.today() != last_get_time:
            db.SupportFundTable().update(user_id)
            db.AccountTable().update(user_id, "KRW", 30000, 30000)
            await ctx.send(embed=ef("mock_support_second", get_count).get)
            # 후원하면 지원금 묵혀서 얻는 것은 어떨까
        else:
            await ctx.send(embed=ef("mock_support_no").get)

@bot.command(name="매수", aliases=('ㅁㅅ',))
async def mock_buy(ctx, stock_name=None, stock_count='1'):
     mock = bot.get_cog('mock_trans')
     await mock.mock_buy(ctx, stock_name, stock_count)

@bot.command(name="풀매수", aliases=('ㅍㅁㅅ',))
async def mock_buy_full(ctx, stock_name=None):
     mock = bot.get_cog('mock_trans')
     await mock.mock_buy(ctx, stock_name, '풀')
    
@bot.command(name="매도", aliases=('ㅁㄷ',))
async def mock_sell(ctx, stock_name=None, stock_count='1'):
    mock = bot.get_cog('mock_trans')
    await mock.mock_sell(ctx, stock_name, stock_count)
    
@bot.command(name="풀매도", aliases=('ㅍㅁㄷ',))
async def mock_sell_full(ctx, stock_name=None, stock_count='1'):
    mock = bot.get_cog('mock_trans')
    await mock.mock_sell(ctx, stock_name, '풀')

@bot.command(name="전량매도")
async def mock_sell_all(ctx):
    mock = bot.get_cog('mock_trans')
    await mock.mock_sell_all(ctx)


@bot.command(name="보유")
async def mock_have(ctx, stock_name=None):
    user_id = ctx.author.id
    fund_list = db.AccountTable().read_all(user_id)
    
    if fund_list is None:
        await ctx.send("보유 자산이 없습니다. 지원금을 받아주세요.")
        return
    
    await ctx.send(embed=ef("mock_have", ctx.author, fund_list).get)

@bot.command(name="파산")
async def mock_bankrupt(ctx):
    user_id = ctx.author.id
    total_account = db.AccountTable().read_all_sum(user_id)

    read_support = db.SupportFundTable().read(user_id)
    if not read_support:
        await ctx.send('지원금을 받은적이 없습니다')
        return
    else:
        support_count = read_support[1]

    if not total_account:
        await ctx.send('계좌가 없습니다')
        return

    if support_count >= 30 and total_account <= 100000:
        serch_stock = bot.get_cog('serch_stock')
        warn_result = await serch_stock.warn_send(ctx, '파산')

        if warn_result:
            db.SupportFundTable.delete(user_id)

        return

    else:
        await ctx.send('파산은 지원금 횟수 30회 이상, 계좌 가치 십만 이하만 가능합니다.')
        return


#순위 관련 기능
@bot.command()
async def 순위(ctx, stock_name = 'all'):
    if stock_name in ('all', '전체', '자산'):
        df = db.AccountTable().read_rank_all()
        stock_name = '전체 자산 가치(매수기준)' 
    elif stock_name in ('돈', '한화', 'KRW', '원', '현금'):
        df = db.AccountTable().read_rank_by_code('KRW')
        stock_name = '원화'
    else:
        serch_stock = bot.get_cog('serch_stock')
        
        serch_result = await serch_stock.serch_stock_by_bot(ctx, stock_name)
        stock_code = serch_result.stock_code
        stock_name = serch_result.stock_name
        
        df = db.AccountTable().read_rank_by_code(stock_code)
        
        if stock_code is None:
            await ctx.send("올바르지 않는 주식명")
            return
    
    def get_user_name(user_id):
        user = bot.get_user(user_id)
        # get_user는 그 서버에 있는 사람만 얻어줄 수 있나봄 결국에는 fetch_user(id)를 해야하는데
        # 그러면 지금 같이 한줄로는 못 줄이고 반복문 써서 해야할 듯 
        # 어차피 많은 수도 아니고 걍 순차적으로 해도 될듯
        if user is None:
            return None
        return bot.get_user(user_id).name
    
    df['author_id'] = df['author_id'].map(get_user_name)

    await ctx.send(embed=ef("ranking", stock_name, df).get)
        

def main():
    if __name__ == "__main__":
        # 봇 실행
        
        # if is_64bits := sys.maxsize > 2**32:
        #     print('it must be run on 32bit!')
        #     return
        
        for extension in extensions:
            try:
                bot.load_extension(extension)
            except Exception as error:
                print('fail to load %s: %s' % (extension, error))
            else:
                print('loaded %s' % extension)
                
        '''   
        bot_token.json 구조
        {"r" : "봇토큰",
         "t" : "봇토큰"}
        '''
        file_path = "./bot_token.json"
        with open(file_path, "r") as json_file:
            token_dic = json.load(json_file)
            
        bot_token = token_dic.get(input("r/t 입력 : "))
                    
        bot.run(bot_token)

        """
        뉴스데이터는 아직 어떻게 처리할지 안정해서 일단 냅둠. 이건 실행시키지 말것
        """
        # process_news = multiprocessing.Process(target=market_data.news)
        # process_news.start()

main()