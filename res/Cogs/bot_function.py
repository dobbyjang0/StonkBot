import discord
from discord.ext import commands

from ..DB import db
from ..Class.embed_form import embed_factory as ef

class serch_stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 애매한 주식명이 입력되었을 시
    async def serch_stock_by_bot(self, ctx, stock_name):
        capsule = stock_info_capsule()
        #아직도 의존도가 높아서 db하고 동시에 바꿔줘야한다. db에서 열이름(columns)까지 가져와야 의존도가 0이 될 듯
        #아님 pd로 가져오면 자동으로 df.columns 하면 되니 편할지도 모르겠다.
        #아님 db에서 건너오는걸 캡슐로 중간에서 만든다던가? 아직은 지금이 나은듯
        element_name_tuple = ('stock_code', 'stock_name', 'stock_market', 'is_ETF', 'uplimit', 'downlimit', 'beforeclose', 'alert_info')
        element_count = 8
        
        #코드일 경우 단순히 검색해본다.
        if self.is_stock_code(stock_name):
            stock_code = stock_name
            read_result = db.StockInfoTable().read_stock_by_code(stock_code)
            for idx in range(element_count):
                capsule.add_stuff(element_name_tuple[idx], read_result[idx])
            
            return capsule
    
        # 이름일 경우 sql에 검색해봄
        stock_list_df = db.StockInfoTable().read_stock_name(stock_name)
        
        # 데이터의 갯수에 따라
        stock_list_len = len(stock_list_df)
        # 0개일 경우
        if stock_list_len == 0:
            await ctx.send("데이터가 없음")
            return capsule
        
        # 1개일 경우
        elif stock_list_len == 1:
            for idx in range(element_count):
                capsule.add_stuff(element_name_tuple[idx], stock_list_df.iat[0,idx])

            return capsule
        
        # 1개 이상일 경우
        else:
            # 목록을 보여준다
            list_msg = await ctx.send(embed=ef("serch_list", stock_list_df).get)
            
            def check(message: discord.Message):
                return message.channel == ctx.channel and message.author == ctx.author
        
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
                    
                    for idx in range(element_count):
                        capsule.add_stuff(element_name_tuple[idx], stock_list_df.iat[stock_index,idx])

                await check_number_msg.delete()
            
            finally:
                # 목록 지우고 출력
                await list_msg.delete()
                return capsule
            
    #주식 코드인지 아닌지 확인
    def is_stock_code(self, stock_code):
        stock_name = db.StockInfoTable().read_stock_code(stock_code)
    
        return (stock_name is not None)

class stock_info_capsule():
    def __init__(self):
        self.stock_code = None
        self.stock_name = None
        self.stock_market = None
        self.is_ETF = None
        self.uplimit = None
        self.downlimit = None
        self.beforeclose = None
        self.alert_info = None
    
    def add_stuff(self, element_name, content):
        self.__dict__[element_name] = content
    
    def to_dict(self):
        return self.__dict__

def setup(bot):
    bot.add_cog(serch_stock(bot))
    
def main():
    if __name__ == "__main__":
        a = stock_info_capsule()
        b = stock_info_capsule()
        a.add_stuff('hh', 'jj')
        b.add_stuff('hh', 'kk')
        print(a.hh)
        print(b.hh)
        pass
    
main()