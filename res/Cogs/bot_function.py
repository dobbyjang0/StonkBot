import discord
from discord.ext import commands

from ..DB import db
from ..Class.embed_form import embed_factory as ef
from ..Class import stock


class serch_stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 애매한 주식명이 입력되었을 시
    async def serch_stock_by_bot(self, ctx, stock_name):
    #코드일 경우 단순히 검색해본다.
        if self.is_stock_code(stock_name):
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
                check_number_msg = await self.bot.wait_for('message', timeout=60, check=check)
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
            
            
    # 주식의 정보를 불러온다.
    async def get_stock_info(self, ctx, stock_name):
        #코드가 아닐시 검색해본다
        if self.is_stock_code(stock_name):
            stock_code = stock_name
            stock_code, stock_real_name, stock_market, is_ETF = db.StockInfoTable().read_stock_by_code(stock_code)
        else:
            stock_code, stock_real_name, stock_market, is_ETF = await self.serch_stock_by_bot(ctx, stock_name)
        
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
    #주식 코드인지 아닌지 확인
    def is_stock_code(stock_code):
        stock_name = db.StockInfoTable().read_stock_code(stock_code)
    
        return (stock_name is not None)
    
def setup(bot):
    bot.add_cog(serch_stock(bot))