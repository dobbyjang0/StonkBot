import discord
from discord.ext import commands, tasks
import pandas
import stock
import save_log_yesalchemy as db
from datetime import date
from embed_form import embed_factory as ef
import market_data
import multiprocessing

import nest_asyncio
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import triggers

nest_asyncio.apply()

bot = commands.Bot(command_prefix="-")


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
    
    market_data.login()
    process_kospi = multiprocessing.Process(target=market_data.kospi_tickdata)
    process_kosdaq = multiprocessing.Process(target=market_data.kosdaq_tickdata)
    process_index = multiprocessing.Process(target=market_data.index_tickdata)
    process_kospi.start()
    process_kosdaq.start()
    process_index.start()
    
    print('실시간 데이터 시작')
    
    sched = AsyncIOScheduler(timezone="Asia/Seoul")
    sched.add_job(triggers.db_update(bot).process, 'cron', hour=4)
    sched.start()
    
    print('스케쥴러 시작')
    
    
@bot.command()
async def 킬(ctx):
    if ctx.author.id not in [378887088524886016, 731836288147259432]:
        await ctx.send("권한없음")
        return
    await ctx.send("봇 꺼짐")
    await bot.close()
    
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
    
    stock_code, stock_real_name, stock_market, is_ETF = await serch_stock_by_bot(ctx, stock_name)
    
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
    
    stock_code, stock_name, __, __ = await serch_stock_by_bot(ctx, stock_name)
    
    if stock_code is None:
        await ctx.send('주식명 오류?')
        return
    
    stock_price = db.KRXRealData().read_price(stock_code)
    
    if stock_price is None:
        await ctx.send("거래 정지 종목입니다.")
        return
    
    await ctx.send(embed=ef("calculate", stock_count=stock_count, name=stock_name, price=stock_price).get)
    # 나중에 수수료 계산도 넣어주자

@bot.command()
async def 매매동향(ctx, stock_name='도움', input_type=None, chart_type=None):
    if stock_name == "도움":
        #await ctx.send(embed=ef('help_gazua').get)
        return
    if input_type not in ['외국인', '기관']:
        await ctx.send('외국인, 기관 입력해주세요')
        return
    
    #주식 검색
    stock_code, stock_name, __, __ = await serch_stock_by_bot(ctx, stock_name)
    
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
    stock_code, stock_real_name, __, __ = await serch_stock_by_bot(ctx, stock_name)
    
    if stock_code == None:
        return
    
    if stock_price and type(stock_price) != int:
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
        db.AccountTable().insert(user_id, "KRW", 3000000, None)
        await ctx.send(embed=ef("mock_support_first").get)
        return
    #아닐경우 매일마다 3만
    else:
        last_get_time, get_count = fund_get_result
        if date.today() != last_get_time:
            db.SupportFundTable().update(user_id)
            db.AccountTable().update(user_id, "KRW", 30000, None)
            await ctx.send(embed=ef("mock_support_second", get_count).get)
            #후원하면 지원금 묵혀서 얻는 것은 어떨까
        else:
            await ctx.send(embed=ef("mock_support_no").get)

@bot.command(name="매수")
async def mock_buy(ctx, stock_name=None, stock_count=1):
    user_id = ctx.author.id
    #입력 오류
    if stock_name is None:
        await ctx.send("거래할 주식을 입력해주세요.")
        return
    if type(stock_count) != int:
        await ctx.send("수량에 숫자를 입력해주세요.")
        return
    stock_code, stock_name, __, __ = await serch_stock_by_bot(ctx, stock_name)
    
    if stock_code is None:
        await ctx.send("올바르지 않는 주식명")
        return
    
    stock_price = db.KRXRealData().read_price(stock_code)
    
    if stock_price is None:
        await ctx.send("거래 정지 종목입니다.")
        return
    
    print(stock_price)
    total_stock_price = stock_price * stock_count
    
    # 계좌의 돈을 불러온다
    krw_account = db.AccountTable().read(user_id,"KRW")
    if krw_account is None:
        await ctx.send("지원금을 받아주세요.")
        return
    krw_money = int(krw_account[0])
        
    # 돈이 없으면 취소
    if krw_money < total_stock_price:
        await ctx.send("돈 없음")
        await ctx.send(f"최대 {krw_money//stock_price}주 가능")
        return
    # 돈이 있으면 계좌 돈 감소, 주식 갯수 증가
    trade_result = db.MockTransection().buy(user_id, stock_code, stock_count, total_stock_price)
    
    if trade_result:
        input_variable={"guild_id" : ctx.guild.id, "channel_id" : ctx.channel.id,
                        "author_id" : ctx.author.id, "stock_code" : stock_code,
                        "stock_value" : stock_price
                        }
        
        try:
            db.LogTable().insert_mock_log(mock_type="매수",stock_count=stock_count,**input_variable)
        except:
            print("로그 저장 에러")
            
        await ctx.send(embed=ef("mock_buy", stock_name, stock_count, stock_price, total_stock_price).get)
    else:
        await ctx.send('오류 : 거래실패')

@bot.command(name="매도")
async def mock_sell(ctx, stock_name=None, stock_count=1):
    user_id = ctx.author.id
    #입력 오류
    if stock_name is None:
        await ctx.send("거래할 주식을 입력해주세요.")
        return
    if type(stock_count) != int:
        await ctx.send("수량을 입력해주세요.")
        return
    
    stock_code, stock_name, __, __ = await serch_stock_by_bot(ctx, stock_name)

    if stock_code is None:
        await ctx.send("올바르지 않는 주식명")
        return

    stock_price = db.KRXRealData().read_price(stock_code)

    if stock_price is None:
        await ctx.send("거래 정지 종목입니다.")
        return
    
    total_stock_price = stock_price * stock_count
    
    # 계좌에 주식이 있는지 확인
    stock_account = db.AccountTable().read(user_id, stock_code)
    if stock_account is None:
        await ctx.send("팔고자 하는 주식이 없습니다.")
        return
    
    balance = int(stock_account[0])
    sum_value = stock_account[1]
    sell_sum_value = sum_value*stock_count/balance
    profit = total_stock_price - sell_sum_value
    
    # 보유 주식이 팔려는 갯수보다 적으면 취소
    if balance < stock_count:
        await ctx.send("팔고자 하는 주식이 적습니다")
        await ctx.send(f"최대 {balance}주 가능")
        return
    
    # 갯수가 충분하면 주식 갯수 감소, 계좌 돈 증가 
    trade_result = db.MockTransection().sell(user_id, stock_code, stock_count, total_stock_price)
    
    if trade_result:
        input_variable={"guild_id" : ctx.guild.id, "channel_id" : ctx.channel.id,
                        "author_id" : ctx.author.id, "stock_code" : stock_code,
                        "stock_value" : stock_price
                        }
        
        try:
            db.LogTable().insert_mock_log(mock_type="매도",stock_count=stock_count,**input_variable)
        except:
            print("로그 저장 에러")
            
        await ctx.send(embed=ef("mock_sell", stock_name, stock_count, stock_price, total_stock_price, profit).get)
    else:
        await ctx.send('오류 : 거래실패, 거래가 취소되었습니다.')


@bot.command(name="보유")
async def mock_have(ctx, stock_name=None, stock_count=1):
    user_id = ctx.author.id
    fund_list = db.AccountTable().read_all(user_id)
    
    if fund_list is None:
        await ctx.send("보유 자산이 없습니다. 지원금을 받아주세요.")
        return
    
    await ctx.send(embed=ef("mock_have", ctx.author, fund_list).get)

# 애매한 주식명이 입력되었을 시
async def serch_stock_by_bot(ctx, stock_name):
    #코드일 경우 단순히 검색해본다.
    if is_stock_code(stock_name):
        stock_code = stock_name
        stock_code, stock_real_name, stock_market, is_ETF = db.StockInfoTable().read_stock_by_code(stock_code)
        return stock_code, stock_real_name, stock_market, is_ETF
    
    # 이름일 경우 sql에 검색해봄
    stock_list_pd = db.StockInfoTable().read_stock_name(stock_name)
    
    # 데이터의 갯수에 따라
    stock_list_len = len(stock_list_pd)
    # 0개일 경우
    if stock_list_len == 0:
        await ctx.send("데이터가 없음")
        return None, None, None, None
    # 1개일 경우
    elif stock_list_len == 1:
        stock_code = stock_list_pd.iat[0, 0]
        stock_real_name = stock_list_pd.iat[0, 1]
        stock_market = stock_list_pd.iat[0, 2]
        is_ETF = stock_list_pd.iat[0, 3]
        
        return stock_code, stock_real_name, stock_market, is_ETF
    
    # 1개 이상일 경우
    else:
        # 목록을 보여준다
        list_msg = await ctx.send(embed=ef("serch_list", stock_list_pd).get)
        
        def check(message: discord.Message):
            return message.channel == ctx.channel and message.author == ctx.author
        
        stock_code, stock_real_name, stock_market, is_ETF = None, None, None, None
        
        try:
            # 숫자 입력을 받는다
            check_number_msg = await bot.wait_for('message', timeout=60, check=check)
        except:
            # 시간 초과시
            await ctx.send("시간초과")            
        else:
            # 내용을 읽는다
            check_number = str(check_number_msg.content)
            if check_number.isdigit() is not True:
                await ctx.send("잘못된 입력")
                
            elif int(check_number) >= stock_list_len or int(check_number) < 0:
                await ctx.send("범위내 숫자를 입력해주세요")
                
            else:
                stock_index = int(check_number)
                stock_code = stock_list_pd.iat[stock_index, 0]
                stock_real_name = stock_list_pd.iat[stock_index, 1]
                stock_market = stock_list_pd.iat[stock_index, 2]
                is_ETF = stock_list_pd.iat[stock_index, 3]
                
            await check_number_msg.delete()
            
        finally:
            # 목록 지우고 출력
            await list_msg.delete()
            return stock_code, stock_real_name, stock_market, is_ETF

#주식 코드인지 아닌지 확인
def is_stock_code(stock_code):
    stock_name = db.StockInfoTable().read_stock_code(stock_code)
    
    return (stock_name is not None)

# 주식의 정보를 불러온다.
async def get_stock_info(ctx, stock_name):
    #코드가 아닐시 검색해본다
    if is_stock_code(stock_name):
        stock_code = stock_name
        stock_code, stock_real_name, stock_market, is_ETF = db.StockInfoTable().read_stock_by_code(stock_code)
    else:
        stock_code, stock_real_name, stock_market, is_ETF = await serch_stock_by_bot(ctx, stock_name)
        
    if stock_code == None:
        return None
    
    #코드로 주식 검색
    serching_stock=stock.StockInfo()
    
    print(stock_code)
    
    serching_stock.get(stock_code)
    serching_stock.stock_market = stock_market
    
    try:
        serching_stock.get(stock_code)
        serching_stock.stock_market = stock_market
        #stock과의 연관성이 너무 많다. 증권사 api 쓸줄 알게되면 갈아치울것
    except:
        await ctx.send("잘못된 코드명")
        return None
    
    return serching_stock

            
def main():
    if __name__ == "__main__":
        #봇 실행
        with open("bot_token.txt", mode='r', encoding='utf-8') as txt:
            bot_token = txt.read()
        bot.run(bot_token)

        """
        뉴스데이터는 아직 어떻게 처리할지 안정해서 일단 냅둠. 이건 실행시키지 말것
        """
        # process_news = multiprocessing.Process(target=market_data.news)
        # process_news.start()

main()