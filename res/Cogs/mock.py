import discord
from discord.ext import commands

from ..DB import db
from ..Class.embed_form import embed_factory as ef

class mock_trans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="매수2")
    async def mock_buy2(self, ctx, stock_name=None, stock_count=1):
        print(ctx, stock_name)
        user_id = ctx.author.id
        #입력 오류
        if stock_name is None:
            await ctx.send("거래할 주식을 입력해주세요.")
            return
        if type(stock_count) != int:
            await ctx.send("수량에 숫자를 입력해주세요.")
            return
        
        serch_stock = self.bot.get_cog('serch_stock')
        
        stock_code, stock_name, __, __ = await serch_stock.serch_stock_by_bot(ctx, stock_name)
        
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
        krw_money = int(krw_account[1])
            
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
                        
def setup(bot):
    bot.add_cog(mock_trans(bot))
                            
    
    
