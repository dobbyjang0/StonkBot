# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import text as sql_text
import pymysql
import pandas



# db와 연결, 'dict' 객체 context 를 인풋으로, 'sqlalchemy.engine.base.Engine' 객체 반환
# 오류처리는 안됨?
def conn(user, password, host, port, db, charset):
    
    db_connection_str = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
    engine = create_engine(db_connection_str, encoding = charset, echo = True)

    return engine

# 기존 로그인 함수
def admin_login():

    USER_DATA_KEY = ("user", "password", "host", "port", "db", "charset")
    USER_DATA_DEFAULT = ("dobbyjang0", "1234", "127.0.0.1", 3306, "stonk_bot", "utf8")
    context = { name:value for name, value in zip(USER_DATA_KEY, USER_DATA_DEFAULT) }
    
    """
    context = {"user": '설정한 db 유저명', 
    "password": '설정한 db 유저 비밀번호', 
    "host": '서버 주소, 로컬일 경우 127.0.0.1', 
    "port": '포트 주소'
    "db": 'db 이름', 
    "charset": 'utf8'}
    """

    # 어드민 인풋
    if input("sql 기본값 사용? (y/n)")!="y":
        for key in USER_DATA_KEY:
            user_input = input(f"{key} 입력 (기본값으로 하려면 y) : ")
            if user_input != "y":
                context[key] = user_input
    
    global connection
    connection = conn(**context)
    
    print(connection)
    return

# 로그인 함수
def quick_admin_login():
    context = pandas.read_csv('admin_login_info.csv', header=None, index_col=0, squeeze=True).to_dict()
    connection = conn(**context)
    print(connection)
    
    return connection

class LogTable:
    def __init__(self):
        self.connection = quick_admin_login()
        self.name = 'input_log'
        
    #어케 쓸지는 모르지만 일단 만들어둠
    def change_connection(self, conn):
        self.connection = conn
        
    #테이블을 만든다
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE input_log (
                           `index` int unsigned PRIMARY KEY AUTO_INCREMENT,
                           `time` datetime DEFAULT NOW(),
                           `type` varchar(15),
                           `type_sub` varchar(15),
                           `guild_id` bigint unsigned,
                           `channel_id` bigint unsigned,
                           `author_id` bigint unsigned,
                           `stock_code` varchar(15),
                           `stock_value` int unsigned,
                           `stock_value_sub` int unsigned,
                           `stock_count` int
                           );
                       """)
        
        print(self.connection)
        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)
    
    #검색 로그를 db에 넣는다
    def insert_serch_log(self, guild_id, channel_id, author_id, stock_code, stock_value):
        input_variable={"guild_id" : guild_id, "channel_id" : channel_id,
                        "author_id" : author_id, "stock_code" : stock_code,
                        "stock_value" : stock_value
                        }
        
        #에러 처리
        for i in [guild_id, channel_id, author_id, stock_code]:
            if type(i) != int:
                raise TypeError("guild_id, channel_id, author_id, stock_code should be 'int' type")
            
        #실행
        sql = sql_text("""
                       INSERT INTO input_log (
                           time, type, guild_id, channel_id, author_id, stock_code, stock_value
                       )
                       VALUES (default, "검색", :guild_id, :channel_id, :author_id, :stock_code, :stock_value)
                       """)

        result = self.connection.execute(sql, **input_variable)
    
        return result

class StockInfoTable:
    def __init__(self):
        self.connection = quick_admin_login()
        self.name = 'stock_code'
        
    # 어케 쓸지는 모르지만 일단 만들어둠
    def change_connection(self, conn):
        self.connection = conn
    
    # 테이블을 만든다
    # get_name_code.py에 있던거 긁어옴. 나중에 수정해야함
    def create_table(self):
        
        #특히 아직까지 주식정보 자동으로 뽑는법을 모르겠음. krx거기는 자바스크립트로 되어있어서 안퍼짐
        df = pandas.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)

        df = df[['회사명', '종목코드']]
        df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
        df = df.reindex(columns=['code','name'])
        
        df.to_sql(name='stock_code', con=self.connection, if_exists='append',index=False, method='multi')
        print("저장완료")
    
    # 이름을 입력하면 코드를 pandas 형식으로 찾아온다
    def read_stock_name(self,stock_name):
        #에러처리
        if type(stock_name) != str:
            raise TypeError("stock_name should be 'str' type")
    
        #실행
        sql = sql_text("""
                       SELECT code, name
                       FROM `stock_code`
                       WHERE name LIKE :stock_name
                       ORDER BY name ASC
                       LIMIT 10
                       """)
        df = pandas.read_sql_query(sql = sql, con = self.connection, params={"stock_name":stock_name+"%"})

        return df
    
    # 정확한 코드를 입력하면 이름을 찾는다
    def read_stock_code(self,stock_code):
        #실행
        sql = sql_text("""
                       SELECT name
                       FROM `stock_code`
                       WHERE code LIKE :stock_code
                       """)
                       
        result = self.connection.execute(sql, stock_code=stock_code).fetchone()
        
        return result
    
class AccountTable:
    # 외화, 가상화폐 등의 확장을 고려하여 종목코드는 VARCHAR로 하였음
    # 원화도 자산개념으로 이 테이블에 전부 넣음
    # !TODO BTC등의 가상화폐는 가장 영향력 높은 거래소 하나만 거래가능하게 할것
    # balance 속성에 주식, 원화는 int 로 들어가게 필터링, 가상화폐는 소수점 8자리까지만
    # 여기서는 CRUD 만 조작하고 매수, 매도 조건확인 등의 작업은 bot_main.py 에서 컨트롤할것
    
    def __init__(self):
        self.connection = quick_admin_login()
        self.name = 'account'
        
    #어케 쓸지는 모르지만 일단 만들어둠
    def change_connection(self, conn):
        self.connection = conn
    
    # 계좌 테이블 생성
    def create_table(self):
        
        sql = sql_text("""
                       CREATE TABLE account (
                           `author_id` bigint unsigned,
                           `stock_code` varchar(15),
                           `balance` decimal(21, 8),
                           `sum_value` decimal(21, 8),
                           PRIMARY KEY (author_id, stock_code)
                           );
                       """)
        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)


    # 계좌 자산 insert
    # 보유하지 않은 주식 매입할때
    # 원화 보유량 없을때 지원금 받은 경우 이걸 실행하면 됨
    def insert(self, author_id, stock_code, balance, stock_value):


        sql = sql_text("""
                       INSERT INTO account
                       VALUES (:author_id, :stock_code, :balance, :stock_value)
                       """)
    
        self.connection.execute(sql, author_id=author_id, stock_code=stock_code, balance=balance, stock_value=stock_value)

    # 계좌 자산 조회
    # 두번째 인자로 아무것도 입력하지 않으면 전체 조회
    # 두번째 인자에 조회하고자 하는 자산 입력(005930, 'KRW' 등)
    def read(self, author_id, stock_code = 'all'):
    
        # 계좌 전체 자산 보유량 조회
        # 원화가 최상단에 출력되게 하였음
        # 나머지는 자산 보유량에 따라 내림차순 정렬
        if stock_code == 'all':
            sql = sql_text("""
                           SELECT stock_code, balance, sum_value
                           FROM `account`
                           WHERE author_id = :author_id
                           ORDER BY FIELD(stock_code, 'KRW') DESC, balance DESC;
                           """)
            df = pandas.read_sql_query(sql = sql, con = self.connection, params={"author_id": author_id})
            
            return df
    
        # 특정 자산 보유량 조회
        else:
            sql = sql_text("""
                           SELECT balance, sum_value
                           FROM `account`
                           WHERE author_id = :author_id and stock_code = :stock_code;
                           """)
            result = self.connection.execute(sql, author_id=author_id, stock_code=stock_code).fetchone()
            return result

    # 계좌 자산 업데이트(유저, 자산종류, 수량)
    # balance는 가상화폐일경우 소수점 8자리까지, KRW나 현물 주식일 경우 정수로 입력
    def update(self, author_id, stock_code, balance, stock_value):

        sql = sql_text("""
                       UPDATE account
                       SET balance = balance + (:balance), sum_value= sum_value +(:stock_value)
                       WHERE author_id = :author_id and stock_code = :stock_code;
                       """)
    
        self.connection.execute(sql, author_id=author_id, stock_code=stock_code, balance=balance, stock_value=stock_value)

    # 계좌 자산 제거(유저, 자산종류)
    # 보유 수량 전부 매도하였을때 실행
    def delete(self, author_id, stock_code):

        sql = sql_text("""
                       DELETE FROM account
                       where author_id = :author_id and stock_code = :stock_code;
                       """)

        self.connection.execute(sql, author_id=author_id, stock_code=stock_code)

class SupportFundTable:
    # 유저 id, 시간,    
    def __init__(self):
        self.connection = quick_admin_login()
        self.name = 'account'
        
    #어케 쓸지는 모르지만 일단 만들어둠
    def change_connection(self, conn):
        self.connection = conn
        
    def create_table(self):
        
        sql = sql_text("""
                       CREATE TABLE support_fund (
                           `author_id` bigint unsigned PRIMARY KEY,
                           `last_get_time` date DEFAULT curdate(),
                           `get_count` int unsigned
                           );
                       """)
        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)
           
    #최초 지원금 지급
    def insert(self, author_id):

        sql = sql_text("""
                       INSERT INTO support_fund
                       VALUES (:author_id, default, 1)
                       """)
    
        self.connection.execute(sql, author_id=author_id)  
        
    def update(self, author_id):
        
        sql = sql_text("""
                       UPDATE support_fund
                       SET last_get_time = default, get_count = get_count + 1
                       WHERE author_id = :author_id;
                       """)
        
        self.connection.execute(sql, author_id=author_id)
    
    def read(self, author_id):
        
        sql = sql_text("""
                       SELECT last_get_time, get_count
                       FROM support_fund
                       WHERE author_id = :author_id
                       """)
        
        result = self.connection.execute(sql, author_id=author_id).fetchone()
        return result
    
    def delete(self, author_id):
        
        sql = sql_text("""
                       DELETE FROM support_fund
                       where author_id = :author_id
                       """)
                       
        self.connection.execute(sql, author_id=author_id) 

#main 함수
def main():
    #체크용
    if __name__ == "__main__":
        print("메인으로 실행")
        # 로그인
        SupportFundTable().create_table()
        LogTable().create_table()
        AccountTable().create_table()
        # 

main()

    

