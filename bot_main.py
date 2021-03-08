import nest_asyncio
import asyncio
import discord
from discord.ext import commands, tasks
import pandas
import stock
import save_log_yesalchemy

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
async def 주식(ctx,stock_name="삼성전자",chart_type="일"):
    #코드가 아닐시 검색해본다
    if stock_name.isdigit() is not True:
        stock_code , stock_real_name = await serch_stock_by_bot(ctx, stock_name)
        if stock_code == None:
            return
    else:
        stock_code = stock_name
    
    #코드로 주식 검색
    serching_stock=stock.StockInfo()
    
    try:
        serching_stock.get_stock(stock_code)
    except:
        await ctx.send("잘못된 코드명")
        return
    
    #그래프의 url을 바꿈
    if chart_type != "일":
        serching_stock.change_graph_interval(chart_type)
    
    # 로그에 저장
    try:
        save_log_yesalchemy.insert_serch_log(ctx.guild.id, ctx.channel.id, ctx.author.id, stock_code, serching_stock.price)
    except:
        print("로그 저장 에러")
    
    # 출력할 embed 만들기
    embed_title = serching_stock.name
    embed_title_url = serching_stock.naver_url
    embed= discord.Embed(title=embed_title,url=embed_title_url)
    embed_discription_1=f"{serching_stock.price}\t{serching_stock.compared_price}\t{serching_stock.rate}\n"
    embed.description = embed_discription_1
    
    embed.add_field(name="거래량(천주)", value=serching_stock.volume)
    embed.add_field(name="거래대금(백만)", value=serching_stock.transaction_price, inline=False)
    embed.add_field(name="장중최고", value=serching_stock.high_price)
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
async def 모의(ctx, service_type="도움", stock_name="삼성전자", stock_count=None):
    if service_type == "도움":
        await ctx.send("도움 메세지 출력")
        return
    elif service_type == "지원금":
        # 지원금이 없는 경우 초기 지원금을 준다
        # 24시간이 지나면 지원금을 준다
        return
    elif service_type == "매도":
        # 계좌의 돈을 불러온다
            # 돈이 없으면 취소
        # 돈이 있으면 계좌 돈 감소, 주식 갯수 증가
        return
    elif service_type == "매수":
        # 보유주식 목록을 불러온다
            # 보유 주식이 팔려는 갯수보다 적으면 취소
        # 갯수가 충분하면 주식 갯수 감소, 계좌 돈 증가 
        return
    elif service_type == "순위":
        # 계좌를 돈 순으로 정렬 후 10개 불러오면 될듯
        return
    elif service_type == "서버순위":
        # 유저당 접속 서버도 저장해야되나??
        return
    elif service_type == "보유":
        # 보유 주식에서 유저랑 똑같은 것 불러오면 될듯
        # 자금도 추가
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
    stock_list_pd = save_log_yesalchemy.read_stock_code(stock_name)
    
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
            
            
def main():
    if __name__ == "__main__":
        #커낵션 불러옴
        save_log_yesalchemy.admin_login()
        
        #봇 실행
        bot_token = input("봇 토큰 입력 : ")
        bot.run(bot_token)
        
main()
