import discord
from discord.ext import commands

from ..DB import db
from ..Class.embed_form import embed_factory as ef

class mock_trans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mock_buy(self, ctx, stock_name, stock_count):
        user_id = ctx.author.id
        #입력 오류
        if stock_name is None:
            await ctx.send("거래할 주식을 입력해주세요.")
            return
        if not (stock_count.isdigit() or stock_count in ['최대', '풀', '올인','반'] or stock_count[-1] in ['%', '퍼', '원']):
            await ctx.send("수량에 숫자를 입력해주세요.")
            return

        serch_stock = self.bot.get_cog('serch_stock')
        
        stock_code, stock_name, __, __, alert_info = await serch_stock.serch_stock_by_bot(ctx, stock_name)
        
   
        if stock_code is None:
            await ctx.send("올바르지 않는 주식명")
            return
        
        stock_price = db.KRXRealData().read_price(stock_code)
        
        if stock_price is None or alert_info == '매매정지':
            await ctx.send("거래 정지 종목입니다.")
            return
    
        
        # 계좌의 돈을 불러온다
        krw_account = db.AccountTable().read(user_id,"KRW")
        if krw_account is None:
            await ctx.send("지원금을 받아주세요.")
            return
        krw_money = int(krw_account[1])

        # stock_count 계산
        if stock_count.isdigit():
            stock_count = int(stock_count)
        elif stock_count in ['최대', '풀', '올인']:
            stock_count = krw_money//stock_price
        elif stock_count in ['반']:
            stock_count = krw_money//2//stock_price
        elif stock_count[-1] in ['%', '퍼', '원']:
            input_int = stock_count[:-1]
            if not input_int.isdigit():
                await ctx.send("수 입력 오류")
                return
            real_input_int = int(input_int)
            
            if stock_count[-1] in ['%', '퍼']:
                base_price = krw_money * real_input_int // 100
            elif stock_count[-1] == '원':
                base_price = real_input_int
            
            if base_price < stock_price:
                await ctx.send("돈 부족")
                return
            
            stock_count = base_price // stock_price
            
        total_stock_price = stock_price * stock_count
        
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
                    
            await ctx.send(embed=ef("mock_buy", ctx.author, stock_name, stock_count, stock_price, total_stock_price).get)
        else:
            await ctx.send('오류 : 거래실패')

    async def mock_sell(self, ctx, stock_name, stock_count):
        user_id = ctx.author.id
        #입력 오류
        if stock_name is None:
            await ctx.send("거래할 주식을 입력해주세요.")
            return
        if not (stock_count.isdigit() or stock_count in ['최대', '풀', '올인', '반'] or stock_count[-1] in ['%', '퍼', '원']):
            await ctx.send("수량에 숫자를 입력해주세요.")
            return
        
        serch_stock = self.bot.get_cog('serch_stock')
        stock_code, stock_name, __, __, alert_info = await serch_stock.serch_stock_by_bot(ctx, stock_name)

        if stock_code is None:
            await ctx.send("올바르지 않는 주식명")
            return

        stock_price = db.KRXRealData().read_price(stock_code)

        if stock_price is None or alert_info == '매매정지':
            await ctx.send("거래 정지 종목입니다.")
            return
    
        # 계좌에 주식이 있는지 확인
        stock_account = db.AccountTable().read(user_id, stock_code)
        if stock_account is None:
            await ctx.send("팔고자 하는 주식이 없습니다.")
            return
        
        balance = int(stock_account[0])
        
        # stock_count 계산
        if stock_count.isdigit():
            stock_count = int(stock_count)
        elif stock_count in ['최대', '풀', '올인']:
            stock_count = balance
        elif stock_count in ['반']:
            stock_count = balance//2
        elif stock_count[-1] in ['%', '퍼', '원']:
            input_int = stock_count[:-1]
            if not input_int.isdigit():
                await ctx.send("수 입력 오류")
                return
            real_input_int = int(input_int)
            
            if stock_count[-1] in ['%', '퍼']:
                stock_count = balance*real_input_int//100
            elif stock_count[-1] == '원':
                stock_count = real_input_int//stock_price
                
                if stock_count>balance:
                    await ctx.send("수량 부족")
                    return
        
        total_stock_price = stock_price * stock_count
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
            
            await ctx.send(embed=ef("mock_sell", ctx.author, stock_name, stock_count, stock_price, total_stock_price, profit).get)
        else:
            await ctx.send('오류 : 거래실패, 거래가 취소되었습니다.')

def setup(bot):
    bot.add_cog(mock_trans(bot))
                            
    
    
