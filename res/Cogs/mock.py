import discord
from discord.ext import commands
from decimal import *

from ..DB import db
from ..Class.embed_form import embed_factory as ef

class mock_trans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mock_buy(self, ctx, stock_name, stock_count):
        BUY_FEE = Decimal('0.001') # 0.5%

        user_id = ctx.author.id
        #입력 오류
        if stock_name is None:
            await ctx.send("거래할 주식을 입력해주세요.")
            return
        if not (stock_count.isdigit() or stock_count in ('최대', '풀', '올인','반') or stock_count[-1] in ('%', '퍼', '원')):
            await ctx.send("수량에 숫자를 입력해주세요.")
            return

        serch_stock = self.bot.get_cog('serch_stock')
        
        serch_result = await serch_stock.serch_stock_by_bot(ctx, stock_name)
        
        stock_code = serch_result.stock_code
        stock_name = serch_result.stock_name
        alert_info = serch_result.alert_info
        
   
        if stock_code is None:
            await ctx.send("올바르지 않는 주식명")
            return
        
        stock_price = db.KRXRealData().read_price(stock_code)
        stock_price_include_fee = stock_price * (1+BUY_FEE)

        
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
        elif stock_count in ('최대', '풀', '올인'):
            stock_count = int(krw_money/stock_price_include_fee)
        elif stock_count in ('반',):
            stock_count = int(krw_money/2/stock_price_include_fee)
        elif stock_count[-1] in ('%', '퍼', '원'):
            input_int = stock_count[:-1]
            if not input_int.isdigit():
                await ctx.send("수 입력 오류")
                return
            real_input_int = int(input_int)
            
            if stock_count[-1] in ('%', '퍼'):
                base_price = krw_money * real_input_int // 100
            elif stock_count[-1] == '원':
                base_price = real_input_int
            
            if base_price < stock_price:
                await ctx.send("돈 부족")
                return
            
            stock_count = int(base_price/stock_price_include_fee)
            
        total_stock_price = stock_price * stock_count
        total_stock_fee = int(total_stock_price * BUY_FEE)
        
        # 돈이 없으면 취소
        if krw_money < total_stock_price or stock_count == 0:
            await ctx.send("돈 없음")
            await ctx.send(f"최대 {int(krw_money/stock_price_include_fee)}주 가능")
            return
       
        # 돈이 있으면 계좌 돈 감소, 주식 갯수 증가
        trade_result = db.MockTransection().buy(user_id, stock_code, stock_count, total_stock_price, total_stock_fee)
        
        if trade_result:
            input_variable={"guild_id" : ctx.guild.id, "channel_id" : ctx.channel.id,
                            "author_id" : ctx.author.id, "stock_code" : stock_code,
                            "stock_value" : stock_price
                            }
            
            try:
                db.LogTable().insert_mock_log(mock_type="매수",stock_count=stock_count,**input_variable)
            except:
                print("로그 저장 에러")
                    
            await ctx.send(embed=ef("mock_buy", ctx.author, stock_name, stock_count, stock_price, total_stock_price, total_stock_fee).get)
        else:
            await ctx.send('오류 : 거래실패')

    async def mock_sell(self, ctx, stock_name, stock_count):
        SELL_FEE = Decimal('0.001')

        user_id = ctx.author.id
        #입력 오류
        if stock_name is None:
            await ctx.send("거래할 주식을 입력해주세요.")
            return
        if not (stock_count.isdigit() or stock_count in ('최대', '풀', '올인', '반') or stock_count[-1] in ('%', '퍼', '원')):
            await ctx.send("수량에 숫자를 입력해주세요.")
            return
        
        serch_stock = self.bot.get_cog('serch_stock')
        serch_result = await serch_stock.serch_stock_by_bot(ctx, stock_name)
        
        stock_code = serch_result.stock_code
        stock_name = serch_result.stock_name
        alert_info = serch_result.alert_info

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
        elif stock_count in ('최대', '풀', '올인'):
            stock_count = balance
        elif stock_count in ('반',):
            stock_count = balance//2
        elif stock_count[-1] in ('%', '퍼', '원'):
            input_int = stock_count[:-1]
            if not input_int.isdigit():
                await ctx.send("수 입력 오류")
                return
            real_input_int = int(input_int)
            
            if stock_count[-1] in ('%', '퍼'):
                stock_count = balance*real_input_int//100
            elif stock_count[-1] == '원':
                stock_count = real_input_int//stock_price
                
                if stock_count>balance:
                    await ctx.send("수량 부족")
                    return
        
        total_stock_price = stock_price * stock_count
        total_stock_fee = int(total_stock_price * SELL_FEE)

        sum_value = stock_account[1]
        sell_sum_value = sum_value*stock_count/balance
        profit = total_stock_price - sell_sum_value - total_stock_fee
        
        # 보유 주식이 팔려는 갯수보다 적으면 취소
        if balance < stock_count:
            await ctx.send("팔고자 하는 주식이 적습니다")
            await ctx.send(f"최대 {balance}주 가능")
            return
        
        # 갯수가 충분하면 주식 갯수 감소, 계좌 돈 증가
        trade_result = db.MockTransection().sell(user_id, stock_code, stock_count, total_stock_price, total_stock_fee)
        
        if trade_result:
            input_variable={"guild_id" : ctx.guild.id, "channel_id" : ctx.channel.id,
                            "author_id" : ctx.author.id, "stock_code" : stock_code,
                            "stock_value" : stock_price
                            }

            try:
                db.LogTable().insert_mock_log(mock_type="매도",stock_count=stock_count,**input_variable)
            except:
                print("로그 저장 에러")
            
            await ctx.send(embed=ef("mock_sell", ctx.author, stock_name, stock_count, stock_price, total_stock_price, total_stock_fee, profit).get)
        else:
            await ctx.send('오류 : 거래실패, 거래가 취소되었습니다.')

    async def mock_sell_all(self, ctx):
        serch_stock = self.bot.get_cog('serch_stock')
        warn_result = await serch_stock.warn_send(ctx, '전량매도')

        if warn_result:
            SELL_FEE = Decimal('0.001')
            user_id = ctx.author.id

            stock_account = db.AccountTable().read_only_tradealbe_stock(self, user_id)

            if stock_account is None:
                await ctx.send("팔고자 하는 주식이 없습니다.")
                return

            trade_list = ['주식명 0주 : 판매금액(이익금)']

            for idx in stock_account.index:
                stock_name = stock_account.iat[idx, 3]
                stock_code = stock_account.iat[idx, 0]
                stock_count = int(stock_account.iat[idx, 1])
                all_buy_price = stock_account.iat[idx, 2]
                all_present_price = stock_account.iat[idx, 4]
                total_stock_fee = int(all_present_price * SELL_FEE)

                profit = all_present_price - all_buy_price - total_stock_fee

                trade_result = db.MockTransection().sell(user_id, stock_code, stock_count, all_present_price, total_stock_fee)

                if trade_result:
                    trade_list.append(f'{stock_name} {stock_count}주 : {all_present_price}({int(profit)})')
                else:
                    trade_list.append(f'{stock_name} {stock_count}주 : 거래실패')

            await ctx.send(embed=ef("mock_sell_all", ctx.author, trade_list).get)


def setup(bot):
    bot.add_cog(mock_trans(bot))
                            
    
    
