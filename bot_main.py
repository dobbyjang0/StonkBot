import nest_asyncio
import asyncio
import discord
from discord.ext import commands, tasks
import pandas
import stock
import save_log_yesalchemy as bot_table

nest_asyncio.apply()

bot = commands.Bot(command_prefix="--")

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
                        "author_id" : ctx.author.id, "stock_code" : int(serching_stock.code),
                        "stock_value" : int(serching_stock.price.replace(",",""))
                        }
    try:
        bot_table.LogTable().insert_serch_log(**input_variable)
    except:
        print("로그 저장 에러")
    
    # 출력할 embed 만들기
    embed_title = serching_stock.name
    embed_title_url = serching_stock.naver_url
    embed= discord.Embed(title=embed_title,url=embed_title_url)
    embed_discription_1=f"{serching_stock.price}\t{serching_stock.compared_price}\t{serching_stock.rate}\n"
    embed.description = embed_discription_1
    
    embed.add_field(name="거래량(천주)", value=serching_stock.volume)
    embed.add_field(name="거래대금(백만)", value=serching_stock.transaction_price)
    embed.add_field(name=".", value=".")
    embed.add_field(name="장중최고", value=serching_stock.high_price, inline=False)
    embed.add_field(name="장중최저", value=serching_stock.low_price)
    
    embed.set_image(url=serching_stock.chart_url)
    
    await ctx.send(embed=embed)
    return
    
@bot.command()
async def 가즈아(ctx,stock_name="삼성전자", stock_price=None):
    #주식 검색
    stock_code , stock_real_name = await serch_stock_by_bot(ctx, stock_name)
    
    if stock_code == None:
        return
    
    if stock_price is None:
        embed_message_price = ""
    else:
        if stock_price.isdigit() is not True or stock_price[-1] != "층":
            await ctx.send("주식 가격이나 층수를 입력해주세요")
            return
        embed_message_price = f"{stock_price}까지"
    
    embed = discord.Embed(title= f"{stock_real_name}, {embed_message_price}가즈아!!" )
    embed.set_author(name="총 n명의 사용자가 가즈아를 외쳤습니다")
    #주식코드를 기본키로 해서 추가?

    await ctx.send(embed=embed)
    return
    
@bot.command()
async def 모의(ctx, service_type="도움", stock_name=None, stock_count=1):
    # 자주 쓰이는 변수 미리 지정
    user_id = ctx.author.id   
    
    if service_type == "도움":
        await ctx.send("도움 메세지 출력")
        return
    elif service_type == "지원금":
        try:
            fund_get_result = bot_table.SupportFundTable().read(user_id)
            print(fund_get_result)
        except:
            print("에러")
            return
            
        #처음일경우 지원금 500만
        if fund_get_result is None:
            bot_table.SupportFundTable().insert(user_id)
            bot_table.AccountTable().insert(user_id, "KRW", 5000000, None)
            await ctx.send("초기 지원금 500만")
            return
        #아닐경우 매일마다 3만
        else:
            bot_table.SupportFundTable().update(user_id)
            bot_table.AccountTable().update(user_id, "KRW", 30000, None)
            await ctx.send("일일 지원금 3만")
            return
    elif service_type == "매수":
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
            await ctx.send(f"{stock_code},{stock_price},{stock_count}거래완료")
            return
    elif service_type == "매도":
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
        stock_code= serching_stock.code
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
        
        # 보유 주식이 팔려는 갯수보다 적으면 취소
        if balance < stock_count:
            await ctx.send("팔고자 하는 주식이 적습니다")
            await ctx.send(f"최대 {balance}주 가능")
            return
        # 갯수가 충분하면 주식 갯수 감소, 계좌 돈 증가 
        elif balance == stock_count:
            bot_table.AccountTable().delete(user_id, stock_code)
            bot_table.AccountTable().update(user_id, "KRW", total_stock_price, None)
            await ctx.send(f"{stock_code},{stock_price},{stock_count}거래완료")
            return
        else:
            bot_table.AccountTable().update(user_id, stock_code, -stock_count, -sell_sum_value)
            bot_table.AccountTable().update(user_id, "KRW", total_stock_price, None)
            await ctx.send(f"{stock_code},{stock_price},{stock_count}거래완료")
            return


    elif service_type == "순위":
        # 계좌를 돈 순으로 정렬 후 10개 불러오면 될듯
        return
    elif service_type == "서버순위":
        # 유저당 접속 서버도 저장해야되나??
        return
    elif service_type == "보유":
        try:
            fund_list = bot_table.AccountTable().read(user_id)
            await ctx.send(str(fund_list))
            return
        except:
            await ctx.send("보유 자산이 없습니다")
            return
    elif service_type == "분석":
        # 자신이 이득을 봤는지 손해를 봤는지 기록해주는 기능
        # 구현 힘들라나?
        return
    else: #최근 거래, 파산, 
        await ctx.send("알맞은 명령어 없음. 도움을 눌러 명령어 목록을 확인해주세요")
        return
    

async def serch_stock_by_bot(ctx, stock_name):
    print("검색")
    # 이름을 sql에 검색해봄
    stock_list_pd = bot_table.StockInfoTable().read_stock_name(stock_name)
    
    # 데이터의 갯수에 따라
    stock_list_len = len(stock_list_pd)
    # 0개일 경우
    if stock_list_len == 0:
        await ctx.send("데이터가 없음")
        return None , None
    # 1개일 경우
    elif stock_list_len == 1:
        stock_code = int(stock_list_pd.iat[0, 0])
        stock_real_name = stock_list_pd.iat[0, 1]
        
        return stock_code , stock_real_name
    
    # 1개 이상일 경우
    else:
        # 목록을 보여준다
        list_msg = await ctx.send(str(stock_list_pd))
        
        def check(message: discord.Message):
            return message.channel == ctx.channel and message.author == ctx.author
        
        stock_code , stock_real_name = None , None
        
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
                stock_code = int(stock_list_pd.iat[stock_index, 0])
                stock_real_name = stock_list_pd.iat[stock_index, 1]
                
            await check_number_msg.delete()
            
        finally:
            # 목록 지우고 출력
            await list_msg.delete()
            return stock_code , stock_real_name
        
def is_stock_code(stock_code):
    stock_name = bot_table.StockInfoTable().read_stock_code(stock_code)
    
    return (stock_name is not None)

async def get_stock_info(ctx, stock_name):
    #코드가 아닐시 검색해본다
    if is_stock_code(stock_name):
        stock_code = stock_name
    else:
        stock_code , stock_real_name = await serch_stock_by_bot(ctx, stock_name)
        if stock_code == None:
            return None
    
    #코드로 주식 검색
    serching_stock=stock.StockInfo()
    
    try:
        serching_stock.get_stock(stock_code)
    except:
        await ctx.send("잘못된 코드명")
        return None
    
    return serching_stock
            
def main():
    if __name__ == "__main__":
        #커낵션 불러옴
        
        #봇 실행
        with open("bot_token.txt", mode='r', encoding='utf-8') as txt:
            bot_token = txt.read()
        bot.run(bot_token)
        
main()