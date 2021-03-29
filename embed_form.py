import discord

def embed_factory(form_name, *arg, **kwarg):
    
        #이 부분 조심하기
    output = eval(form_name)(*arg, **kwarg)
    return output

    
#아래의 form들은 모두 이 클래스를 상속할 것
class formbase:
    def __init__(self, *arg, **kwarg):
        self.embed = discord.Embed()
        self.init_make()
        if arg is not None or kwarg is not None:
            self.insert(*arg, **kwarg)
    def init_make(self):
        pass
    def insert(self, *arg, **kwarg):
        pass
    @property
    def get(self):
        return self.embed
        
# 처음에 안바뀌는건 init_make, 처음에 값을 넣어줘야 되는건 insert에서 해줘야함
# 더 좋은 구조 있으면 추천받음

#이모지 변형
def set_market_to_emoji(market):
    if market is None:
        return ""
    elif market == "KOSPI":
        return "<:KOS:825783079229980674><:PI:825783079590297600>"
    elif market == "KOSDAQ":
        return "<:KOS:825783079229980674><:DAQ:825783079570243594>"
    elif market == 'KONEX':
        return '<:KON:825783079481901067><:EX:825783079754661888>'

def number_to_emoji(number):
    emoji = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    return emoji[number]

#검색 관련
class serch_result(formbase):
    def insert(self, name, naver_url, price, compared_price, rate, volume, transaction_price, high_price, low_price, chart_url, market = None, *arg, **kwarg):

        self.embed.title = name + ' ' + set_market_to_emoji(market)
        self.embed.url = naver_url
        self.embed.description = f"{price}\t{compared_price}\t{rate}\n"
        
        self.embed.add_field(name="거래량(천주)", value=volume)
        self.embed.add_field(name="거래대금(백만)", value=transaction_price)
        self.embed.add_field(name=".", value=".")
        self.embed.add_field(name="장중최고", value=high_price)
        self.embed.add_field(name="장중최저", value=low_price)
        self.embed.set_image(url=chart_url)
        
class serch_list(formbase):
    def init_make(self):
        self.embed.title = "검색하고자 하는 주식 번호를 입력해주세요"
    def insert(self, pd, *arg, **kwarg):
        self.embed.description = "\n".join(f"{number_to_emoji(idx)} {pd.iat[idx, 1]} {set_market_to_emoji(pd.iat[idx, 2])}" for idx in range(len(pd))) 

#모의주식 관련


#가즈아 관련     
class gazua(formbase):
    def insert(self, stock_name, stock_price=None, *arg, **kwarg):
        if stock_price is None:
            embed_message_price = ""
        else:
            embed_message_price = f"{stock_price}까지"
        self.embed.title = f"{stock_name}, {embed_message_price}가즈아!!"
        self.embed.set_author(name="총 n명의 사용자가 가즈아를 외쳤습니다")
        
class testembed(formbase):
    def init_make(self):
        self.embed.title = "빈칸테스트 : %10s" % "내용"
        self.embed.description = "빈칸테스트 : %10s" % "내용"

if __name__ == "__main__":
    print(embed_factory("gazua",3).embed.title)
    pass