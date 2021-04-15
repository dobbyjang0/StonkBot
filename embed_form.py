import discord
import time

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
    market_emoji ={"KOSPI":"<:KOS:825783079229980674><:PI:825783079590297600>",
                   "KOSDAQ":"<:KOS:825783079229980674><:DAQ:825783079570243594>",
                   'KONEX':'<:KON:825783079481901067><:EX:825783079754661888>'
        }
    output = market_emoji.get(market)
    if not output:
        output = ""
    return output

def number_to_emoji(number):
    emoji = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    return emoji[number]

def compared_sign_to_emoji(number):
    emoji = [None, '<:toptop:832329922634448896>',
             '<:upup:832329922622128198>',
             '<:samesame:832329922604302356>',
             '<:downdown:832329922571141150>',
             '<:bottbott:832329922747564062>']
    return emoji[number]

#검색 관련
#구식 파셔 디자인
class serch_result(formbase):
    def insert(self, name, naver_url, price, compared_sign, compared_price, rate, volume, transaction_price, start_price, high_price, low_price, chart_url, stock_market = None, *arg, **kwarg):

        self.embed.title = name + ' ' + set_market_to_emoji(stock_market)
        self.embed.url = naver_url
        self.embed.description = f"현재가 : **{price}**\t{compared_sign_to_emoji(compared_sign)}{compared_price}\t{rate}\n"
        
        self.embed.add_field(name="시가", value=start_price)
        self.embed.add_field(name="고가", value=high_price)
        self.embed.add_field(name="저가", value=low_price)
        self.embed.add_field(name="거래량(천주)", value=volume)
        self.embed.add_field(name="거래대금(백만)", value=transaction_price)
        self.embed.set_image(url=chart_url)

#신식 이베스트 
class serch_result2(formbase):
    def insert(self, name, code, compared_sign, compared_price, rate, price, start_price,  high_price, low_price, volume, transaction_price, stock_market = None, *arg, **kwarg):
        
        IMG_URL_BASE = "https://ssl.pstatic.net/imgfinance/chart/item/area/day/%s.png?sidcode=%d"
        MAIN_URL_BASE = "https://finance.naver.com/item/main.nhn?code="
        
        def rate_plus_sign(rate):
            if rate>0:
                return '+'
            else:
                return ''
        
        self.embed.title = name + ' ' + set_market_to_emoji(stock_market)
        self.embed.url = MAIN_URL_BASE + code
        self.embed.description = f"현재가 : **{price}**\t{compared_sign_to_emoji(compared_sign)}{compared_price}\t{rate_plus_sign(rate)}{rate}%\n"
        self.embed.add_field(name="시가", value=start_price)
        self.embed.add_field(name="고가", value=high_price)
        self.embed.add_field(name="저가", value=low_price)
        self.embed.add_field(name="거래량(천주)", value=volume)
        self.embed.add_field(name="거래대금(백만)", value=transaction_price)
        self.embed.set_image(url=IMG_URL_BASE % (code, int(time.time()*1000//1)))
        

class serch_list(formbase):
    def init_make(self):
        self.embed.title = "검색하고자 하는 주식 번호를 입력해주세요"
    def insert(self, pd, *arg, **kwarg):
        self.embed.description = "\n".join(f"{number_to_emoji(idx)} {pd.iat[idx, 1]} {set_market_to_emoji(pd.iat[idx, 2])}" for idx in range(len(pd))) 
        
class calculate(formbase):
    def insert(self, stock_count, name, price, *arg, **kwarg):
        price_int = int(price.replace(",",""))
        total_stock_price = price_int * stock_count
        self.embed.title = f'{total_stock_price}원'
        self.embed.set_footer(text=f'{name} {stock_count}주의 가격')
        
#모의주식 관련
#지원금 관련
class mock_support_first(formbase):
    def init_make(self):
        self.embed.title = '🎉 최초 지원금 300만원이 지급되었습니다!'
        
class mock_support_second(formbase):
    def init_make(self):
        self.embed.title = '💵 일일 지원금 3만원이 지급되었습니다.'
    def insert(self, count, *arg, **kwarg):
        self.embed.description = f'지원 받은 횟수 : {count}회'
        
class mock_support_no(formbase):
    def init_make(self):
        self.embed.title = '📅 오늘 이미 지원금을 받으셨어요.'
        self.embed.description = '하루 뒤에 다시 시도해 주세요.'
        
#매매 관련
class mock_buy(formbase):
    def insert(self, name, count, price, total_price, *arg, **kwarg):
        self.embed.title= f"🔴 {name} {count}주 매수 완료되었습니다."
        self.embed.add_field(name='단가', value=price)
        self.embed.add_field(name='총 금액', value=total_price)   

class mock_sell(formbase):
    def insert(self, name, count, price, total_price, profit, *arg, **kwarg):
        self.embed.title= f"🔵 {name} {count}주 매도 완료되었습니다."
        self.embed.add_field(name='단가', value=price)
        self.embed.add_field(name='총 금액', value=total_price)
        self.embed.add_field(name='차익', value=profit)
        
class mock_have(formbase):
    def insert(self, author, pd, *arg, **kwarg):
        self.embed.set_author(name=f'{author.name}님의 계좌입니다.', icon_url=str(author.avatar_url))
        self.embed.title = f'원화 : {int(pd.iat[0, 1])}원'
        #귀찮아서 이래놨는데 고치긴 해야할듯
        self.embed.description = "\n".join(f'{pd.iat[idx,3]} : {int(pd.iat[idx,1])}주 {int(pd.iat[idx,2])}원' for idx in range(1,len(pd)))

#가즈아 관련     
class gazua(formbase):
    def insert(self, stock_name, gazua_count, stock_price=None, *arg, **kwarg):
        if stock_price is None:
            embed_message_price = ""
        else:
            embed_message_price = f"{stock_price}까지"
        self.embed.title = f"{stock_name}, {embed_message_price}가즈아!!"
        self.embed.set_author(name=f"총 {gazua_count}명의 사용자가 가즈아를 외쳤습니다")
        
        GAZUA_IMG_URL = 'https://media.discordapp.net/attachments/804815694717911080/827234484112982086/gazua.png?width=676&height=676'
        self.embed.set_thumbnail(url=GAZUA_IMG_URL)
        
class testembed(formbase):
    def init_make(self):
        self.embed.title = "빈칸테스트 : %10s" % "내용"
        self.embed.description = "빈칸테스트 : %10s" % "내용"

#도움 관련
class help_all(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='StonkBot의 명령어 모음입니다.', icon_url = IMG_URL)
        
        description_list = ['`주식` : -주식 `<주식 이름 또는 코드>` `<차트 형태>`',
                            '`계산` : -계산 `<주식 이름 또는 코드>` `<주식 갯수>`',
                            '`모의` : `지원금` `매수` `매도` `보유` `도움`',
                            '`가즈아` : -가즈아 `<주식 이름 또는 코드>` `<예상하는 가격>`',
                            '`코스피` `코스닥`',
                            '-도움 `<명령어>`로 더 상세한 설명을 볼 수 있습니다.'
                             ]
        self.embed.description = "\n".join(x for x in description_list)

class help_serch(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='주식(또는 검색) 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-주식 `<주식 이름 또는 코드>` (`<차트 형태>`)'
        self.embed.description = '`<차트 형태>` : 일, 주, 월, 년, 3년, 5년, 10년, 일봉, 주봉, 월봉'
        
class help_mock(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='모의 관련 설명', icon_url = IMG_URL)
        self.embed.title = '`지원금` `매수` `매도` `보유` `도움`'
        description_list = ['`지원금` : 매일마다 지원금을 받습니다',
                            '`보유` : 보유하고 있는 주식 목록 및 원화를 보여줍니다',
                            '`매수` : -매수 `<주식 이름 또는 코드>` `<주식 갯수 또는 가격>`',
                            '`매도` : -매도 `<주식 이름 또는 코드>` `<주식 갯수 또는 가격>`',
                            '`도움` : 도움말을 보여줍니다',
                            '`<주식 갯수 또는 가격>` : 끝에 `주` 또는 아무것도 붙이지 않는다면 해당 갯수만큼의 주식을 사고 팝니다.',
                            '끝에 `원`이라고 입력시 해당 돈에서 최대한 살 수 있는 만큼의 주식을 삽니다'
                             ]
        self.embed.description = "\n".join(x for x in description_list)

class help_kos(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='코스피 코스닥 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-코스피 또는 크스닥 (`<차트 형태>`)'
        self.embed.description = '`<차트 형태>` : 일, 월, 년, 3년'

class help_gazua(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='가즈아 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-가즈아 `<주식 이름 또는 코드>` (`<주식 가격 또는 층수>`)'

class help_calculate(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='계산 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-계산 `<주식 이름 또는 코드>` (`<주식 갯수>`)'

if __name__ == "__main__":
    print(embed_factory("gazua",3).embed.title)
    pass