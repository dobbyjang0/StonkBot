import nest_asyncio
import asyncio
import discord
from discord.ext import commands, tasks
import pandas
import stock
import save_log_yesalchemy as bot_table
from datetime import date
from embed_form import embed_factory as ef
import market_data
import multiprocessing

nest_asyncio.apply()

bot = commands.Bot(command_prefix="-")


@bot.event
async def on_ready():
    print("--- 연결 성공 ---")
    print(f"봇 이름: {bot.user.name}")
    print(f"ID: {bot.user.id}")
    return
    
    
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


#코스피, 코스닥
#로그 저장 추가하기
@bot.command(aliases=["kospi"])
async def 코스피(ctx, chart_type=None):
    serching_index = stock.KOSInfo()
    serching_index.get("KOSPI")
    
    if chart_type:
        serching_index.change_graph_interval(chart_type)
    
    await ctx.send(embed=ef("serch_result",**serching_index.to_dict()).get)
    
@bot.command(aliases=["kosdaq"])
async def 코스닥(ctx, chart_type=None):
    serching_index = stock.KOSInfo()
    serching_index.get("KOSDAQ")
    
    if chart_type:
        serching_index.change_graph_interval(chart_type)
    
    await ctx.send(embed=ef("serch_result",**serching_index.to_dict()).get)

# 주식 검색 기능
@bot.command(aliases=["검색"])
async def 주식(ctx,stock_name="도움",chart_type="일"):
    if stock_name == "도움":
        await ctx.send("도움말 출력")
        return
    
    serching_stock = await get_stock_info(ctx, stock_name)
    
    if serching_stock is None:
        return

    #그래프의 url을 바꿈
    if chart_type != "일":
        serching_stock.change_graph_interval(chart_type)
    
    # 로그에 저장
    input_variable={"guild_id" : ctx.guild.id, "channel_id" : ctx.channel.id,
                        "author_id" : ctx.author.id, "stock_code" : serching_stock.code,
                        "stock_value" : int(serching_stock.price.replace(",",""))
                        }
    try:
        bot_table.LogTable().insert_serch_log(**input_variable)
    except:
        print("로그 저장 에러")
        
    # embed 출력
    await ctx.send(embed=ef("serch_result",**serching_stock.to_dict()).get)
    return

#가즈아 기능
@bot.command()
async def 가즈아(ctx, stock_name="삼성전자", stock_price=None):
    #주식 검색
    stock_code, stock_real_name, __ = await serch_stock_by_bot(ctx, stock_name)
    
    if stock_code == None:
        return
    
    if stock_price is not None:
        if stock_price.isdigit() or stock_price[-1] != "층":
            await ctx.send("주식 가격이나 층수를 입력해주세요")
            return
    
    #주식코드를 기본키로 해서 추가?
    await ctx.send(embed=ef("gazua", stock_real_name, stock_price).get)
    return
    
# 모의 주식 관련 커맨드
@bot.group(name="모의")
async def mock(ctx):
    pass

@mock.command(name="도움")
async def mock_help(ctx):
    await ctx.send("도움 메세지 출력")
    return

@mock.command(name="지원금")
async def mock_support_fund(ctx):
    user_id = ctx.author.id
    try:
        fund_get_result = bot_table.SupportFundTable().read(user_id)
        print(fund_get_result)
    except:
        print("에러")
        return
    
    #처음일경우 지원금 500만
    if fund_get_result is None:
        bot_table.SupportFundTable().insert(user_id)
        bot_table.AccountTable().insert(user_id, "KRW", 3000000, None)
        await ctx.send(embed=ef("mock_support_first").get)
        return
    #아닐경우 매일마다 3만
    else:
        last_get_time, get_count = fund_get_result
        if date.today() != last_get_time:
            bot_table.SupportFundTable().update(user_id)
            bot_table.AccountTable().update(user_id, "KRW", 30000, None)
            await ctx.send(embed=ef("mock_support_second", get_count).get)
            #후원하면 지원금 묵혀서 얻는 것은 어떨까
        else:
            await ctx.send(embed=ef("mock_support_no").get)


@mock.command(name="매수")
async def mock_buy(ctx, stock_name=None, stock_count=1):
    user_id = ctx.author.id
    #입력 오류
    if stock_name is None:
        await ctx.send("거래할 주식을 입력해주세요.")
        return
    if type(stock_count) != int:
        await ctx.send("수량에 숫자를 입력해주세요.")
        return
        
    #주식을 검색한다
    serching_stock = await get_stock_info(ctx, stock_name)

    if serching_stock is None:
        await ctx.send("거래가 취소되었습니다.")
        return
    stock_code= serching_stock.code
    stock_name= serching_stock.name
    stock_price = int(serching_stock.price.replace(",",""))
    total_stock_price = stock_price * stock_count
    
    # 계좌의 돈을 불러온다
    krw_account = bot_table.AccountTable().read(user_id,"KRW")
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
    else:
        if bot_table.AccountTable().read(user_id, stock_code) is None:
            bot_table.AccountTable().insert(user_id, stock_code, stock_count, total_stock_price)
        else:
            bot_table.AccountTable().update(user_id, stock_code, stock_count, total_stock_price)
        bot_table.AccountTable().update(user_id, "KRW", -total_stock_price, None)
        
        # 로그에 저장
        input_variable={"guild_id" : ctx.guild.id, "channel_id" : ctx.channel.id,
                        "author_id" : ctx.author.id, "stock_code" : stock_code,
                        "stock_value" : stock_price
                        }
        
        try:
            bot_table.LogTable().insert_mock_log(mock_type="매수",stock_count=stock_count,**input_variable)
        except:
            print("로그 저장 에러")
        
        await ctx.send(embed=ef("mock_buy", stock_name, stock_count, stock_price, total_stock_price).get)
        return

@mock.command(name="매도")
async def mock_sell(ctx, stock_name=None, stock_count=1):
    user_id = ctx.author.id
    #입력 오류
    if stock_name is None:
        await ctx.send("거래할 주식을 입력해주세요.")
        return
    if type(stock_count) != int:
        await ctx.send("수량을 입력해주세요.")
        return
    
    #주식 검색
    serching_stock = await get_stock_info(ctx, stock_name)

    if serching_stock is None:
        await ctx.send("거래가 취소되었습니다.")
        return
    stock_code = serching_stock.code
    stock_name = serching_stock.name
    stock_price = int(serching_stock.price.replace(",",""))
    total_stock_price = stock_price * stock_count
    
    # 계좌에 주식이 있는지 확인
    stock_account = bot_table.AccountTable().read(user_id, stock_code)
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
    elif balance == stock_count:
        bot_table.AccountTable().delete(user_id, stock_code)
        bot_table.AccountTable().update(user_id, "KRW", total_stock_price, None)
        
        # 로그에 저장
        input_variable={"guild_id" : ctx.guild.id, "channel_id" : ctx.channel.id,
                        "author_id" : ctx.author.id, "stock_code" : stock_code,
                        "stock_value" : stock_price
                        }
        try:
            bot_table.LogTable().insert_mock_log(mock_type="매도",stock_count=stock_count,**input_variable)
        except:
            print("로그 저장 에러")
            
        await ctx.send(embed=ef("mock_sell", stock_name, stock_count, stock_price, total_stock_price, profit).get)
        
        return
    else:
        bot_table.AccountTable().update(user_id, stock_code, -stock_count, -sell_sum_value)
        bot_table.AccountTable().update(user_id, "KRW", total_stock_price, None)
        
        # 로그에 저장
        input_variable={"guild_id" : ctx.guild.id, "channel_id" : ctx.channel.id,
                        "author_id" : ctx.author.id, "stock_code" : stock_code,
                        "stock_value" : stock_price
                        }
        try:
            bot_table.LogTable().insert_mock_log(mock_type="매도",stock_count=stock_count,**input_variable)
        except:
            print("로그 저장 에러")
        
        await ctx.send(embed=ef("mock_sell", stock_name, stock_count, stock_price, total_stock_price, profit).get)
        
        return

@mock.command(name="보유")
async def mock_have(ctx, stock_name=None, stock_count=1):
    user_id = ctx.author.id
    try:
        fund_list = bot_table.AccountTable().read_all(user_id)
        await ctx.send(embed=ef("mock_have", ctx.author, fund_list).get)
        return
    except:
        await ctx.send("보유 자산이 없습니다")
        return

# 애매한 주식명이 입력되었을 시
async def serch_stock_by_bot(ctx, stock_name):
    print("검색")
    # 이름을 sql에 검색해봄
    stock_list_pd = bot_table.StockInfoTable().read_stock_name(stock_name)
    
    # 데이터의 갯수에 따라
    stock_list_len = len(stock_list_pd)
    # 0개일 경우
    if stock_list_len == 0:
        await ctx.send("데이터가 없음")
        return None, None, None
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
            check_number_msg = await bot.wait_for('message', timeout=10, check=check)
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
    stock_name = bot_table.StockInfoTable().read_stock_code(stock_code)
    
    return (stock_name is not None)

# 주식의 정보를 불러온다.
async def get_stock_info(ctx, stock_name):
    #코드가 아닐시 검색해본다
    if is_stock_code(stock_name):
        stock_code = stock_name
    else:
        stock_code, stock_real_name, stock_market, is_ETF = await serch_stock_by_bot(ctx, stock_name)
        if stock_code == None:
            return None
    
    #코드로 주식 검색
    serching_stock=stock.StockInfo()
    
    try:
        serching_stock.get(stock_code)
        serching_stock.market = stock_market
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
        실시간 시세, 뉴스 데이터 받는 부분
        api 세팅 완료하면 이거 주석 해제하고 사용할것
        사용전에 save_log_yesalchemy.KRXRealData 클래스의 create_table 꼭 실행할것
        """
        # market_data.login()
        # process_kospi = multiprocessing.Process(target=market_data.kospi_tickdata)
        # process_kosdaq = multiprocessing.Process(target=market_data.kosdaq_tickdata)
        # process_kospi.start()
        # process_kosdaq.start()

        """
        뉴스데이터는 아직 어떻게 처리할지 안정해서 일단 냅둠. 이건 실행시키지 말것
        """
        # process_news = multiprocessing.Process(target=market_data.news)
        # process_news.start()

main()