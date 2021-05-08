import discord
import time

def embed_factory(form_name, *arg, **kwarg):
    
    #이 부분 조심하기
    output = eval(form_name)(*arg, **kwarg)
    return output

# 아래의 form들은 모두 이 클래스를 상속할 것
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
        
#싱글톤 봇 (아직 고민중, 시작하기전에 bot_main에서 불러올 것)


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
    emoji = ("0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟")
    return emoji[number]

def compared_sign_to_emoji(number):
    emoji = (None, '<:toptop:832329922634448896>',
             '<:upup:832329922622128198>',
             '<:samesame:832329922604302356>',
             '<:downdown:832329922571141150>',
             '<:bottbott:832329922747564062>')
    return emoji[number]

def rate_plus_sign(rate):
    if rate>0:
        return '+'
    else:
        return ''

def alert_info_to_emoji(alert_info):
    if not alert_info:
        return ''
    alert_emoji ={"투자경고":"⚠️",
                   "매매정지":"⛔",
                   '단기과열지정':'🔥',
                   '관리':'🔧'
        }
    
    output = alert_emoji.get(alert_info)
    
    if not output:
        output = f'‼️{alert_info}'
        
    return output
        
def make_arrow_sign(number):
    if number > 0:
        sign = compared_sign_to_emoji(2)
    elif number < 0:
        sign = compared_sign_to_emoji(4)
    else:
        sign = compared_sign_to_emoji(3)
        
    return sign

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
    def insert(self, name, code, compared_sign=0, compared_price=0, rate=0, price=0, start_price=0, high_price=0, low_price=0, uplimit=0, downlimit=0,volume=0, transaction_price=0, chart_type=None, alert_info=None, stock_market = None, *arg, **kwarg):
        
        IMG_URL_BASE = "https://ssl.pstatic.net/imgfinance/chart/item/%s/%s.png?sidcode=%d"
        MAIN_URL_BASE = "https://finance.naver.com/item/main.nhn?code="
        
        def chart_type_change(chart_type):
            chart_type_dic = {"일":"area/day", "주":"area/week", "월":"area/month3", "년":"area/year",
                              "3년":"area/year3", "5년":"area/year5", "10년":"area/year10",
                              "일봉":"candle/day", "주봉":"candle/week", "월봉":"candle/month"
                              }
            
            result = chart_type_dic.get(chart_type)
            
            if not result:
                result = "area/day"
            
            return result
        
        self.embed.title = f'{name} {set_market_to_emoji(stock_market)} {alert_info_to_emoji(alert_info)}'
        self.embed.url = MAIN_URL_BASE + code
        
        if alert_info != '매매정지':
            self.embed.description = f'현재가 : **{price}**\t{compared_sign_to_emoji(compared_sign)}{compared_price}\t{rate_plus_sign(rate)}{rate}%\n'
            self.embed.add_field(name="시가", value=start_price)
            self.embed.add_field(name="고가(상한)", value=f'{high_price}({uplimit})')
            self.embed.add_field(name="저가(하한)", value=f'{low_price}({downlimit})')
            self.embed.add_field(name="거래량(천주)", value=volume)
            self.embed.add_field(name="거래대금(백만)", value=transaction_price)
        else:
            self.embed.description = f'현재가 : **{price}**'
        self.embed.set_image(url=IMG_URL_BASE % (chart_type_change(chart_type), code, int(time.time()*1000//1)))


class serch_result_index(formbase):
    def insert(self, name, price, compared_sign, compared_price, rate, start_price, high_price, low_price, frgsvalue, orgsvalue, chart_type, *arg, **kwarg):
        MAIN_URL_BASE = 'https://finance.naver.com/sise/sise_index.nhn?code=%s'

        def get_chart_url(name, chart_type):
            chart_type_dic = {"월": "area/month3", "년": "area/year",
                              "3년": "area/year3", "10년": "area/year10",
                              "일봉": "candle/day", "주봉": "candle/week", "월봉": "candle/month"
                              }

            result = chart_type_dic.get(chart_type)
            if result:
                url = 'https://ssl.pstatic.net/imgfinance/chart/mobile/%s/%s_end.png?%s' % (result, name, int(time.time()*1000//1))
            else:
                url = 'https://ssl.pstatic.net/imgfinance/chart/sise/siseMain%s.png?sid=%s' % (name, int(time.time()*1000//1))
            return url

        self.embed.title = f'**{name}**'
        self.embed.url = MAIN_URL_BASE % name
        self.embed.description = f'현재가 : **{price}**\t{compared_sign_to_emoji(compared_sign)}{compared_price}\t{rate_plus_sign(rate)}{rate}%\n'
        self.embed.add_field(name="시가", value=start_price)
        self.embed.add_field(name="고가", value=high_price)
        self.embed.add_field(name="저가", value=low_price)
        self.embed.add_field(name="외인순매수량", value=frgsvalue)
        self.embed.add_field(name="기관순매수량", value=orgsvalue)
        self.embed.set_image(url=get_chart_url(name, chart_type))
        if chart_type == '일':
            self.embed.set_footer(text='🟣개인 🔴외국인 🔵기관')


class serch_result_world(formbase):
    def insert(self, name, code, price, compared_sign, compared_price, rate, start_price, high_price, low_price, naver_url, chart_type, *arg, **kwarg):
        
        IMG_URL_BASE = 'https://ssl.pstatic.net/imgfinance/chart/mobile/world/%s/.%s_end.png?%s'
        
        def chart_type_change(chart_type):
            chart_type_dic = {"일":"day", "월":"area/month3", "년":"area/year",
                              "3년":"area/year3", "10년":"area/year10",
                              "일봉":"candle/day", "주봉":"candle/week", "월봉":"candle/month"
                              }
            
            result = chart_type_dic.get(chart_type)
            if not result:
                result = "day"
            return result
        
        self.embed.title = f'**{name}** ({code})'
        self.embed.url = naver_url
        self.embed.description = f'현재가 : **{price}**\t{compared_sign_to_emoji(compared_sign)}{compared_price}\t{rate_plus_sign(rate)}{rate}%\n'
        self.embed.add_field(name="시가", value=start_price)
        self.embed.add_field(name="고가", value=high_price)
        self.embed.add_field(name="저가", value=low_price)
        self.embed.set_image(url=IMG_URL_BASE % (chart_type_change(chart_type), code, int(time.time()*1000//1)))
        
class serch_list(formbase):
    def init_make(self):
        self.embed.title = "검색하고자 하는 주식 번호를 입력해주세요"
    def insert(self, pd, *arg, **kwarg):
        self.embed.description = "\n".join(f"{number_to_emoji(idx)} {pd.iat[idx, 1]} {set_market_to_emoji(pd.iat[idx, 2])}" for idx in pd.index) 
        
class calculate(formbase):
    def insert(self, stock_count, name, price, *arg, **kwarg):
        total_stock_price = price * stock_count
        self.embed.title = f'{total_stock_price}원'
        self.embed.set_footer(text=f'{name} {price} * {stock_count}주의 가격')
        
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
    def insert(self, author, name, count, price, total_price, total_fee, *arg, **kwarg):
        self.embed.set_author(name=f'{author.name}', icon_url=str(author.avatar_url))
        self.embed.title= f"🔴 {name} {count}주 매수 완료되었습니다."
        self.embed.add_field(name='단가', value=price)
        self.embed.add_field(name='총 금액', value=total_price)
        self.embed.add_field(name='수수료', value=total_fee)

class mock_sell(formbase):
    def insert(self, author, name, count, price, total_price, total_fee, profit, *arg, **kwarg):
        self.embed.set_author(name=f'{author.name}', icon_url=str(author.avatar_url))
        self.embed.title= f"🔵 {name} {count}주 매도 완료되었습니다."
        self.embed.add_field(name='단가', value=price)
        self.embed.add_field(name='총 금액', value=total_price)
        self.embed.add_field(name='수수료', value=total_fee)
        self.embed.add_field(name='차익', value=int(profit))
        
class mock_have(formbase):
    def insert(self, author, pd, *arg, **kwarg):
        self.embed.set_author(name=f'{author.name}님의 계좌입니다.', icon_url=str(author.avatar_url))
        
        if pd.empty:
            self.embed.title = '지원금을 받아주세요!'
            return
        
        for idx in range(1,len(pd)):
            stock_name = pd.iat[idx,3] 
            stock_count = int(pd.iat[idx,1])
            all_buy_price = pd.iat[idx,2]
            all_present_price = pd.iat[idx,4]
            
            profit = all_present_price - all_buy_price
            profit_rate = round(profit/all_buy_price * 100, 2)
            
            field_title = f'{stock_name} {stock_count}주'
            field_content = f'{int(all_present_price)}원 {make_arrow_sign(profit)}{int(profit)} {rate_plus_sign(profit_rate)}{profit_rate}%'
            
            self.embed.add_field(name=field_title, value=field_content, inline=False)
        #self.embed.description = "\n".join(f'{pd.iat[idx,3]} : {int(pd.iat[idx,1])}주 {int(pd.iat[idx,2])}원' for idx in range(1,len(pd)))
        
        print(pd.columns)
        sum_buy = sum(pd.loc[:, 'sum_value'])
        sum_present = sum(pd.loc[:, 'now_price'])
        won = int(pd.iat[0, 2])
        
        sum_profit = sum_present - sum_buy
        sum_rate = round(sum_profit/sum_buy * 100, 2)
        
        # 현금도 계산에 합칠지 말지 고민좀 해봐야 될 듯
        self.embed.title = f'총 자산 가치 : {int(sum_present)}원 {make_arrow_sign(sum_profit)}{int(sum_profit)} {rate_plus_sign(sum_rate)}{sum_rate}%'
        self.embed.set_footer(text=f'원화 : {won}원')
        
        
#가즈아 관련
class gazua(formbase):
    def insert(self, stock_name, gazua_count, stock_price=None, *arg, **kwarg):
        if stock_price is None:
            embed_message_price = ""
        else:
            embed_message_price = f"{stock_price}까지"
            
        if gazua_count:
                gazua_count = gazua_count[0]
        else:
            gazua_count = 0
        
        self.embed.title = f"{stock_name}, {embed_message_price}가즈아!!"
        self.embed.set_author(name=f"총 {gazua_count}명의 사용자가 가즈아를 외쳤습니다")
        
        GAZUA_IMG_URL = 'https://media.discordapp.net/attachments/804815694717911080/827234484112982086/gazua.png?width=676&height=676'
        self.embed.set_thumbnail(url=GAZUA_IMG_URL)

#매매동향 관련
class trading_trend(formbase):
    def init_make(self):
        self.embed.description = "🔵매도 🔴매수 🟣주가"
    def insert(self, name, code, input_type, chart_type, *arg, **kwarg):
        IMG_URL_BASE = 'https://ssl.pstatic.net/imgfinance/chart/trader/%s/%s_%s.png'
        
        def chart_type_change(chart_type):
            chart_type_dic = {"월":"month1", "3월":"month3", "6월":"month6", "년":"year1"}
            result = chart_type_dic.get(chart_type)
            
            if not result:
                chart_type = "월"
                result = "month1"
            
            return result
        
        def input_type_change(input_type):
            input_type_dic = {"외국인":"F", "기관":"I"}
            
            result = input_type_dic.get(input_type)
            return result
        
        self.embed.title = f"{name} {input_type} 매매동향 {chart_type}"
        url = IMG_URL_BASE % (chart_type_change(chart_type), input_type_change(input_type), code)
        self.embed.set_image(url=url)

#순위, 랭킹 관련
#코드가 존나 못생겼다 시발, 나중에 바꾸기
class ranking(formbase):
    def insert(self, stock_name, df, *arg, **kwarg):
        self.embed.set_author(name=f'{stock_name} 순위')
        
        print(df)
        if df.empty:
            self.embed.title = '✨ 해당 주식을 가진 사람이 아직 없습니다!'
            self.embed.description = '📈 이 주식의 첫 주주가 되어보는 것은 어떤가요?'
            return
        
        description_list =[]  
        columns_count = len(df.columns)
        for idx in df.index:
            if columns_count == 3 and stock_name != '원화':
                balance_description = f'`{int(df.iat[idx, 2])}주`'
            else:
                balance_description = ''
                
            if idx==0:
                title = f'👑　**{df.iat[0, 0]}** : `{int(df.iat[0, 1])}원` {balance_description}'
            else:
                description_list.append(f'{number_to_emoji(idx+1)}　**{df.iat[idx, 0]}** : `{int(df.iat[idx, 1])}원` {balance_description}')
    
        self.embed.title = title
        self.embed.description = "\n".join(x for x in description_list)

#
class warning_message(formbase):
    def init_make(self):
        self.embed.description = "동의하시면 ✔, 아니라면 ✖를 클릭해주세요."
    def insert(self, message):
        self.embed.title = f"{message}를(을) 하시겠습니까?"

class testembed(formbase):
    def init_make(self):
        self.embed.title = "빈칸테스트 : %10s" % "내용"
        self.embed.description = "빈칸테스트 : %10s" % "내용"

#도움 관련
class help_all(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='StonkBot의 명령어 모음입니다.', icon_url = IMG_URL)
        
        description_list = ['`주식` : -주식 `<주식 이름/코드>` `<차트 형태>`',
                            '`계산` : -계산 `<주식 이름/코드>` `<주식 갯수>`',
                            '`모의` : `지원금` `매수` `매도` `보유` `도움` `순위`',
                            '`가즈아` : -가즈아 `<주식 이름/코드>` `<예상하는 가격>`',
                            '`매매동향` : -매매동향 `<주식 이름/코드>` `<외국인/기관>` `<차트 형태>`',
                            '`지수` : -지수 `<지수 이름>` `<차트 형태>`',
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
        self.embed.title = '`지원금` `매수` `매도` `보유` `도움` `풀매수` `풀매도`'
        description_list = ['`지원금` : 매일마다 지원금을 받습니다',
                            '`보유` : 보유하고 있는 주식 목록 및 원화를 보여줍니다',
                            '`매수` : -매수 `<주식 이름/코드>` `<주식 갯수/가격>`',
                            '`매도` : -매도 `<주식 이름/코드>` `<주식 갯수/가격>`',
                            '`풀매수` `풀매도` : 최대한 매수/매도합니다',
                            '`도움` : 도움말을 보여줍니다',
                            '',
                            '`<주식 갯수/가격>` 입력시 실행방식',
                            ' `숫자` : 해당 갯수만큼의 주식을 사고 팝니다.',
                            ' `최대`, `풀`, `반` : 최대 또는 반만큼의 주식을 사고 팝니다.',                            
                            ' `원` : 해당 돈에서 최대한 할 수 있는 만큼의 주식을 사고 팝니다 ex) 100원',
                            ' `%` : 해당 퍼센트 만큼의 주식을 사고 팝니다 ex) 42%'
                             ]
        self.embed.description = "\n".join(x for x in description_list)

class help_kos(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='코스피 코스닥 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-코스피 또는 코스닥 (`<차트 형태>`)'
        self.embed.description = '`<차트 형태>` : 일, 월, 년, 3년'

class help_gazua(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='가즈아 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-가즈아 `<주식 이름/코드>` (`<주식 가격>`)'

class help_calculate(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='계산 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-계산 `<주식 이름/코드>` (`<주식 갯수>`)'

class help_trend(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='매매동향 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-매매동향 `<주식 이름/코드>` `<외국인/기관>` (`<차트 형태>`)'
        self.embed.description = '`<차트 형태>` : 월, 3월, 6월, 년'

class help_index(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='지수 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-지수 `<지수 이름>` (`<차트 형태>`)'
        description_list = ['`<지수 이름>` : 코스피, 코스닥, 해외 지수 이름, 국가명',
                            '`<차트 형태>` : 일, 월, 년, 3년, 10년, 일봉, 주봉, 월봉'
                             ]
        self.embed.description = "\n".join(x for x in description_list)
        
class help_ranking(formbase):
    def init_make(self):
        IMG_URL = 'https://media.discordapp.net/attachments/813006733881376778/814116320123551744/1.png?width=672&height=676'
        self.embed.set_author(name='순위 관련 설명', icon_url = IMG_URL)
        self.embed.title = '-순위 `<순위 대상>`'
        self.embed.description = '`<순위 대상>` : 전체, 돈, 주식 이름'



if __name__ == "__main__":
    print(embed_factory("gazua",3).embed.title)
    pass