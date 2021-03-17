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

class serch_result(formbase):
    def insert(self, name, naver_url, price, compared_price, rate, volume, transaction_price, high_price, low_price, chart_url, *arg, **kwarg):
        self.embed.title = name
        self.embed.url = naver_url
        self.embed.description = f"{price}\t{compared_price}\t{rate}\n"
        
        self.embed.add_field(name="거래량(천주)", value=volume)
        self.embed.add_field(name="거래대금(백만)", value=transaction_price)
        self.embed.add_field(name=".", value=".")
        self.embed.add_field(name="장중최고", value=high_price)
        self.embed.add_field(name="장중최저", value=low_price)
        self.embed.set_image(url=chart_url)
        
class gazua(formbase):
    def insert(self, stock_name, stock_price=None, *arg, **kwarg):
        if stock_price is None:
            embed_message_price = ""
        else:
            embed_message_price = f"{stock_price}까지"
        self.embed.title = f"{stock_name}, {embed_message_price}가즈아!!"
        self.embed.set_author(name="총 n명의 사용자가 가즈아를 외쳤습니다")

if __name__ == "__main__":
    print(embed_factory("gazua",3).embed.title)
    pass