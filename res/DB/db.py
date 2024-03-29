from .xing_api import XASession
from .xing_api import XAQuery
from .xing_api import XAReal
from .xing_api import EventHandler
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import text as sql_text
from sqlalchemy import and_
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
import time
import datetime
import pymysql
import pandas
import json


#싱글톤 커낵션, 아니 이거 걍 이래놔도 되나? 시발?
class Connection():
    def __new__(cls):
        if not hasattr(cls, 'cursor'):
            
            def conn(user, password, host, port, db, charset):
                db_connection_str = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
                engine = create_engine(db_connection_str, encoding = charset, echo = True)

                return engine
            
            def quick_admin_login():
                
                '''
                admin_loging_info.json 구조
                {"user" : "dobbyjang0",
                 "password" : "1234",
                 "host" : "127.0.0.1",
                 "port" : "3306",
                 "db" : "stonk_bot",
                 "charset" : "utf8"}
                '''
                
                file_path = "./admin_login_info.json"
                with open(file_path, "r") as json_file:
                    user = json.load(json_file)

                connection = conn(**user)
                print(connection)
    
                return connection
            
            cls.cursor = quick_admin_login()
            
        return cls.cursor

#부모 테이블 클래스, 여기다가 각 테이블마다 추가되는거 추가하기
class Table:
    def __init__(self):
        self.connection = Connection()
        #self.name 필요하려나?
        
# 트렌잭션 클래스, 나중에 수정 쉬우라고 만들어둠
class Transection:
    def __init__(self):
        self.connection = Connection()
        #self.name 필요하려나?

#로그 테이블
class LogTable(Table):
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
        for i in [guild_id, channel_id, author_id]:
            if type(i) != int:
                raise TypeError("guild_id, channel_id, author_id should be 'int' type")
            
        #실행
        sql = sql_text("""
                       INSERT INTO input_log (
                           time, type, guild_id, channel_id, author_id, stock_code, stock_value
                       )
                       VALUES (default, "검색", :guild_id, :channel_id, :author_id, :stock_code, :stock_value)
                       """)

        result = self.connection.execute(sql, **input_variable)
    
        return result
    
    #매수, 매도 로그를 db에 넣는다.
    def insert_mock_log(self, mock_type, stock_count, guild_id, channel_id, author_id, stock_code, stock_value):
        input_variable={"guild_id" : guild_id, "channel_id" : channel_id,
                        "author_id" : author_id, "stock_code" : stock_code,
                        "stock_value" : stock_value, "mock_type" : mock_type,
                        "stock_count" : stock_count
                        }
        
        #에러 처리
        for i in [guild_id, channel_id, author_id]:
            if type(i) != int:
                raise TypeError("guild_id, channel_id, author_id should be 'int' type")
            
        #실행
        sql = sql_text("""
                       INSERT INTO input_log (
                           time, type, guild_id, channel_id, author_id, stock_code, stock_value, stock_count
                       )
                       VALUES (default, :mock_type, :guild_id, :channel_id, :author_id, :stock_code, :stock_value, :stock_count)
                       """)

        result = self.connection.execute(sql, **input_variable)
    
        return result

    #가즈아 로그를 db에 넣는다.
    def insert_gazua_log(self, guild_id, channel_id, author_id, stock_code, stock_value_want):
        input_variable={"guild_id" : guild_id, "channel_id" : channel_id,
                        "author_id" : author_id, "stock_code" : stock_code,
                        "stock_value_want" : stock_value_want
                        }
        
        #에러 처리
        for i in [guild_id, channel_id, author_id]:
            if type(i) != int:
                raise TypeError("guild_id, channel_id, author_id should be 'int' type")
            
        #실행
        sql = sql_text("""
                       INSERT INTO input_log (
                           time, type, guild_id, channel_id, author_id, stock_code, stock_value_sub
                       )
                       VALUES (default, '가즈아', :guild_id, :channel_id, :author_id, :stock_code, :stock_value_want)
                       """)

        result = self.connection.execute(sql, **input_variable)
    
        return result
# 걍 가즈아 갯수 세는 용도
class GazuaCountTable(Table):
    #테이블을 만든다
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE gazua_count (
                           `stock_code` varchar(15) PRIMARY KEY,
                           `count` int unsigned
                           );
                       """)
        
        print(self.connection)
        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)
    
    def insert_update(self, stock_code):
        sql = sql_text("""
                       INSERT INTO gazua_count (stock_code, count)
                       VALUES (:stock_code, 1)
                       ON DUPLICATE KEY UPDATE count=count+1
                       """)
                       
        result = self.connection.execute(sql, stock_code=stock_code)
    
        return result
    
    def read(self, stock_code):
        
        sql = sql_text("""
                       SELECT count
                       FROM `gazua_count`
                       WHERE stock_code = :stock_code;
                       """)
        result = self.connection.execute(sql, stock_code=stock_code).fetchone()
        return result
        

class StockInfoTable(Table):
    """
    경고:
        이 클래스를 사용하여 종목정보 업데이트 시 반드시 api 에 로그인 한 상태여야 함
    """
    # 모든종목 정보
    # 데이터프레임으로
    # market 열이 0이면 코스피 1이면 코스닥
    # ETF 열이 0이면 일반종목, 1이면 ETF
    def _stock_name(self):
        """
        kospi, kosdaq에 존재하는 모든 종목에 대한 정보를 pandas 데이터프레임 객체로 반환

        Returns:
            pandas dataframe object

                   code            name    market   ETF    uplimit    downlimit    beforeclose
            0     000020          동화약품   KOSPI   주식
            1     000040         KR모터스   KOSPI   주식
            2     000050            경방   KOSPI   주식
            3     000060         메리츠화재   KOSPI   주식
            ...      ...           ...    ...  ..

            Columns:
                code: 종목코드
                name: 종목명
                market: 시장구분
                ETF: ETF 구분
                uplimit: 상한가
                downlimit: 하한가
                beforeclose: 전일종가
        """
        query = XAQuery()
        in_field = {"gubun": '0'}
        query.set_inblock('t8430', in_field)
        query.request()
        out_count = query.get_count('t8430OutBlock')

        shcode = [query.get_outblock('t8430OutBlock', "shcode", i)["shcode"] for i in range(out_count)]
        hname = [query.get_outblock('t8430OutBlock', "hname", i)["hname"] for i in range(out_count)]
        gubun = ["KOSPI" if query.get_outblock('t8430OutBlock', "gubun", i)["gubun"] == '1' else "KOSDAQ" for i in
                 range(out_count)]
        etfgubun = ["주식" if query.get_outblock('t8430OutBlock', "etfgubun", i)["etfgubun"] == '0' else "ETF" for i in
                    range(out_count)]
        uplmtprice = [query.get_outblock('t8430OutBlock', "uplmtprice", i)["uplmtprice"] for i in range(out_count)]
        dnlmtprice = [query.get_outblock('t8430OutBlock', "dnlmtprice", i)["dnlmtprice"] for i in range(out_count)]
        jnilclose = [query.get_outblock('t8430OutBlock', "jnilclose", i)["jnilclose"] for i in range(out_count)]

        data = {
            "code": shcode,
            "name": hname,
            "market": gubun,
            "ETF": etfgubun,
            "uplimit": uplmtprice,
            "downlimit": dnlmtprice,
            "beforeclose": jnilclose
        }

        df = pandas.DataFrame(data, columns=["code", "name", "market", "ETF", "uplimit", "downlimit", "beforeclose"])
        return df

    def _stock_alert(self):
        """
        관리/불성실/투자유의 조회

        Returns:
            pandas dataframe object

            code    type
        0    000220    투자경고
        1    000225    투자경고
        2    002025    투자경고
        3    003530    투자경고
        """
        mapping = {
            '1': '관리',
            '2': '불성실공시',
            '3': '투자유의',
            '4': '투자환기'
        }
        shcode = []
        alert_type = []
        today = datetime.datetime.today()
        day = datetime.timedelta(days=1)
        for chk in range(1, 5):
            chk = str(chk)
            query = XAQuery()
            cts_shcode = ''
            is_next = 0
            in_field = {"gubun": '0', "jongchk": chk}
            query.set_inblock('t1404', in_field)
            while True:
                query.com_obj.SetFieldData('t1404InBlock', 'cts_shcode', 0, cts_shcode)
                query.request(is_next=is_next)
                cts_shcode = query.get_outblock('t1404OutBlock', 'cts_shcode', 0)['cts_shcode']
                out_count = query.get_count('t1404OutBlock1')
                for i in range(out_count):
                    s_date = query.get_outblock('t1404OutBlock1', "date", i)["date"]
                    if s_date == '':
                        s_date = today
                    else:
                        s_date = datetime.datetime.strptime(s_date, '%Y%m%d')
                    e_date = query.get_outblock('t1404OutBlock1', "edate", i)["edate"]
                    if e_date == '':
                        e_date = '40001231'
                    e_date = datetime.datetime.strptime(e_date, '%Y%m%d') + day
                    if s_date <= today < e_date:
                        shcode.append(query.get_outblock('t1404OutBlock1', "shcode", i)["shcode"])
                        alert_type.append(mapping[chk])
                    else:
                        continue
                if cts_shcode == '':
                    break
                else:
                    is_next = 1
            time.sleep(3)
        data = {
            "code": shcode,
            "type": alert_type
        }
        df = pandas.DataFrame(data, columns=["code", "type"])
        return df

    def _stock_danger(self):
        """
        투자경고/매매정지/정리매매조회

        Returns:
            pandas dataframe object

             code    type
        0    000220    투자경고
        1    000225    투자경고
        2    002025    투자경고
        3    003530    투자경고
        """
        mapping = {
            '1': '투자경고',
            '2': '매매정지',
            '3': '정리매매',
            '4': '투자주의',
            '5': '투자위험',
            '6': '위험예고',
            '7': '단기과열지정',
            '8': '상장주식수 부족'
        }
        shcode = []
        alert_type = []
        today = datetime.datetime.today()
        day = datetime.timedelta(days=1)
        for chk in range(1, 9):
            chk = str(chk)
            query = XAQuery()
            cts_shcode = ''
            is_next = 0
            in_field = {"gubun": '0', "jongchk": chk}
            query.set_inblock('t1405', in_field)
            while True:
                query.com_obj.SetFieldData('t1405InBlock', 'cts_shcode', 0, cts_shcode)
                query.request(is_next=is_next)
                cts_shcode = query.get_outblock('t1405OutBlock', 'cts_shcode', 0)['cts_shcode']
                out_count = query.get_count('t1405OutBlock1')
                for i in range(out_count):
                    s_date = query.get_outblock('t1405OutBlock1', "date", i)["date"]
                    if s_date == '':
                        s_date = today
                    else:
                        s_date = datetime.datetime.strptime(s_date, '%Y%m%d')
                    e_date = query.get_outblock('t1405OutBlock1', "edate", i)["edate"]
                    if e_date == '':
                        e_date = '40001231'
                    e_date = datetime.datetime.strptime(e_date, '%Y%m%d') + day
                    if s_date <= today < e_date:
                        shcode.append(query.get_outblock('t1405OutBlock1', "shcode", i)["shcode"])
                        alert_type.append(mapping[chk])
                    else:
                        continue
                if cts_shcode == '':
                    break
                else:
                    is_next = 1
            time.sleep(3)
        data = {
            "code": shcode,
            "type": alert_type
        }
        df = pandas.DataFrame(data, columns=["code", "type"])
        return df

    # 종목정보 업데이트
    # 일단 3월 28일자 기준 파일 사용, 자동화 필요
    # └-> 2021.04.10 api 로 대체함
    def update_table(self):
        """
        종목정보 업데이트

        !todo 하루 한번 08:20 에 실행되도록 할것
        returns:
            Bool type
            api 서버와 연결되어 있으면 True 리턴
            api 서버와 연결되어 있지 않으면 False 리턴
        """

        # 이베스트 증권 서버 연결상태가 True 이면 테이블 업데이트 실시하고 True반환
        # 그렇지 않으면 업데이트 미실시 후 False반환
        if XASession().is_connected():
            # 이전 데이터 모두 삭제
            sql = sql_text("""
                           DELETE FROM stock_code;
                           """)
            self.connection.execute(sql)


            # api 사용하여 종목이름, 종목코드 read
            df_name = self._stock_name()

            # 투자유의/관리 정보 read
            df_alert = self._stock_alert()
            df_danger = self._stock_danger()
            df_alertdanger = pandas.concat([df_alert, df_danger])
            df_alertdanger['type'] = df_alertdanger['type'].astype('category')

            custom_order = ['매매정지', '정리매매', '투자경고', '투자위험', '위험예고', '단기과열지정', '단기과열지정예고', '관리', '불성실공시', '투자유의', '투자환기', '상장주식수 부족']
            df_alertdanger['type'] = df_alertdanger['type'].cat.set_categories(custom_order, ordered=True)
            df_alertdanger.sort_values(by=['type'], inplace=True)
            df_alertdanger = df_alertdanger.drop_duplicates(['code'], keep = 'first')

            # 병합후 데이터베이스에 저장
            df = pandas.merge(df_name, df_alertdanger, on='code', how='left')

            df['uplimit'] = df['uplimit'].map(int)
            df['downlimit'] = df['downlimit'].map(int)
            df['beforeclose'] = df['beforeclose'].map(int)

            df.to_sql(name='stock_code', con=self.connection, if_exists='append', index=False, method='multi')
            print("저장완료")
            return True

        else:
            print("EBEST disconnected")
            return False

    
    def drop_table(self):
        sql = sql_text("""
                       DROP TABLE stock_code;
                       """)
        self.connection.execute(sql)

    # 최초 테이블 생성
    # 처음 테이블 만들 때 이것으로 만드는거 추천
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE stock_code (
                           `code` varchar(15) PRIMARY KEY,
                           `name` varchar(100),
                           `market` varchar(15),
                           `ETF` varchar(10),
                           `uplimit` int unsigned,
                           `downlimit` int unsigned,
                           `beforeclose` int unsigned,
                           `type` varchar(20)
                           );
                       """)
        
        print(self.connection)
        try:
            self.connection.execute(sql)
        except:
            error_message = "Already exist"
            print(error_message)
        pass
    
    # 이름을 입력하면 코드를 pandas 형식으로 찾아온다
    def read_stock_name(self,stock_name):
        #에러처리
        if type(stock_name) != str:
            raise TypeError("stock_name should be 'str' type")
    
        #실행
        sql = sql_text("""
                       SELECT code, name, market, ETF, `uplimit`, `downlimit`, `beforeclose`, `type`
                       FROM `stock_code`
                       WHERE name LIKE :stock_name
                       ORDER BY name ASC
                       LIMIT 10
                       """)
        df = pandas.read_sql_query(sql = sql, con = self.connection, params={"stock_name":"%"+stock_name+"%"})

        return df
    
    def read_stock_by_code(self,stock_code):
        #에러처리
        if type(stock_code) != str:
            raise TypeError("stock_code should be 'str' type")
        
        #실행
        sql = sql_text("""
                       SELECT code, name, market, ETF, `uplimit`, `downlimit`, `beforeclose`, `type`
                       FROM `stock_code`
                       WHERE code = :stock_code
                       """)
                       
        result = self.connection.execute(sql, stock_code=stock_code).fetchone()
        
        return result
    
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
    
class AccountTable(Table):
    # 외화, 가상화폐 등의 확장을 고려하여 종목코드는 VARCHAR로 하였음
    # 원화도 자산개념으로 이 테이블에 전부 넣음
    # !TODO BTC등의 가상화폐는 가장 영향력 높은 거래소 하나만 거래가능하게 할것
    # balance 속성에 주식, 원화는 int 로 들어가게 필터링, 가상화폐는 소수점 8자리까지만
    # 여기서는 CRUD 만 조작하고 매수, 매도 조건확인 등의 작업은 bot_main.py 에서 컨트롤할것
    
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

    # 계좌 자산을 이름과 같이 읽는다.
    def read_all(self, author_id):
        sql = sql_text("""
                       SELECT ua.stock_code, ua.balance, ua.sum_value, sc.name, 
                           CASE WHEN rd.price IS NULL 
                           THEN ua.sum_value
                           ELSE rd.price*ua.balance END 
                           AS now_price
                       FROM (
                           SELECT stock_code, balance, sum_value
                           FROM `account`
                           WHERE author_id = :author_id) AS ua
                       LEFT JOIN `stock_code` AS sc ON ua.stock_code = sc.code
                       LEFT JOIN `krx_real_data` AS rd ON ua.stock_code = rd.shcode
                       ORDER BY FIELD(stock_code, 'KRW') DESC, balance DESC;
                       """)
        df = pandas.read_sql_query(sql = sql, con = self.connection, params={"author_id": author_id})
        return df

    def read_only_tradealbe_stock(self, author_id):
        sql = sql_text("""
                       SELECT ua.stock_code, ua.balance, ua.sum_value, sc.name, 
                           CASE WHEN rd.price IS NULL 
                           THEN ua.sum_value
                           ELSE rd.price*ua.balance END 
                           AS now_price
                       FROM (
                           SELECT stock_code, balance, sum_value
                           FROM `account`
                           WHERE author_id = :author_id) AS ua
                       LEFT JOIN `stock_code` AS sc ON ua.stock_code = sc.code
                       LEFT JOIN `krx_real_data` AS rd ON ua.stock_code = rd.shcode
                       WHERE sc.type != '매매정지' and ua.stock_code != 'KRW';
                       """)

        df = pandas.read_sql_query(sql = sql, con = self.connection, params={"author_id": author_id})
        return df

    # 가격만 생각한다
    def read_all_sum(self, author_id):
        sql = sql_text("""
                       SELECT SUM(
                           CASE WHEN rd.price IS NULL 
                           THEN ua.sum_value
                           ELSE rd.price*ua.balance END)
                           AS sum_value
                       FROM (
                           SELECT stock_code, balance, sum_value
                           FROM `account`
                           WHERE author_id = :author_id) AS ua
                       LEFT JOIN `krx_real_data` AS rd ON ua.stock_code = rd.shcode;
                       """)

        price = self.connection.execute(sql, author_id=author_id).fetchone()

        if price:
            result = price[0]
        else:
            result = None

        return result

    def read_rank_all(self):
        sql = sql_text("""
                       SELECT author_id, MAX(sum_value) AS all_value
                       FROM `account`
                       GROUP BY author_id
                       ORDER BY all_value DESC
                       LIMIT 10;
                       """)
                       
        df = pandas.read_sql_query(sql = sql, con = self.connection)
        return df
        
    def read_rank_by_code(self, stock_code):
        sql = sql_text("""
                       SELECT author_id, sum_value, balance
                       FROM `account`
                       WHERE stock_code = :stock_code
                       ORDER BY balance DESC
                       LIMIT 10;
                       """)
                       
        df = pandas.read_sql_query(sql = sql, con = self.connection, params={"stock_code": stock_code})
        return df

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

class SupportFundTable(Table):
    # 유저 id, 시간,            
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

# 실시간 시세가 저장되는 테이블
class KRXRealData(Table):
    """
    실시간 시세를 저장하는 테이블
    """
    def create_table(self):
        """
        테이블 생성
        """
        sql = sql_text("""
                       CREATE TABLE krx_real_data(
                           `shcode` varchar(8) PRIMARY KEY,
                           `chetime` varchar(8),
                           `sign` tinyint,
                           `change` int,
                           `drate` decimal(5, 2),
                           `price` int,
                           `open` int,
                           `high` int,
                           `low` int,
                           `volume` int,
                           `value` bigint
                           );
                       """)

        try:
            self.connection.execute(sql)
        except:
            error_message = "refu"
            print(error_message)

    def update(self, context):
        """
        테이블 업데이트,
        값이 존재하면 업데이트하고 존재하지 않는다면 insert into실행

        Args:
            context: 테이블에 업데이트 할 실시간 시세 데이터
            {'shcode': '035720', 'chetime': '134330', 'sign': '2', 'change': '1000', 'drate': '0.18', 'price': '543000', 'open': '539000', 'high': '561000', 'low': '534000', 'volume': '687611', 'value': '377637'}
        """

        # ms sql query
        #
        # sql = sql_text("""
        #                UPDATE KRX_real_data
        #                SET
        #                chetime = :chetime,
        #                sign = :sign,
        #                change = :change,
        #                drate = :drate,
        #                price = :price,
        #                open = :open,
        #                high = :high,
        #                low = :low,
        #                volume = :volume,
        #                value = :value
        #                WHERE shcode = :shcode
        #                IF @@ROWCOUNT=0
        #                INSERT INTO KRX_real_data(shcode, chetime, sign, change, drate, price, open, high, low, volume, value)
        #                VALUES(:shcode, :chetime, :sign, :change, :drate, :price, :open, :high, :low, :volume, :value);
        #                """)

        sql = sql_text("""
                       INSERT INTO krx_real_data VALUES(:shcode, :chetime, :sign, :change, :drate, :price, :open, :high, :low, :volume, :value)
                       ON DUPLICATE KEY UPDATE `chetime` = :chetime, `sign` = :sign, `change` = :change, `drate` = :drate, `price` = :price, `open` = :open, `high` = :high, `low` = :low, `volume` = :volume, `value` = :value;
                       """)


        self.connection.execute(sql, **context)

    def read(self, shcode):
        """
        종목코드를 기준으로 실시간 데이터를 가져온다

        Args:
            shcode: 6자리 단축코드(str)
            
        Returns:
            종목코드에 해당하는 실시간 시세데이터
        """
        sql = sql_text("""
                       SELECT *
                       FROM `krx_real_data`
                       WHERE shcode = :shcode;
                       """)
        result = self.connection.execute(sql, shcode = shcode).fetchone()
        return result
    
    # 가격만 스캔한다
    def read_price(self, shcode):
        sql = sql_text("""
                       SELECT `price`
                       FROM `krx_real_data`
                       WHERE shcode = :shcode;
                       """)
        price = self.connection.execute(sql, shcode = shcode).fetchone()
        
        if price:
            result = price[0]
        else:
            result = None
        
        return result
    
class MockTransection(Transection):
    def buy(self, author_id, stock_code, balance, stock_value, stock_fee):
        sql_inset_stock = sql_text("""
                       INSERT INTO `account`
                       VALUES(:author_id, :stock_code, :balance, :stock_value)
                       ON DUPLICATE KEY UPDATE balance = balance + (:balance), sum_value= sum_value + (:stock_value);
                       """)
                       
        sql_update_won = sql_text("""
                       UPDATE `account`
                       SET balance = balance - (:stock_value) - (:stock_fee), sum_value = sum_value - (:stock_value)- (:stock_fee)
                       WHERE author_id = :author_id and stock_code = 'KRW';
                       """)

        Session = sessionmaker(autocommit=False, autoflush=False, bind=self.connection)
        session = Session()

        try:
            session.execute(sql_inset_stock, {'author_id':author_id, 'stock_code':stock_code, 'balance':balance, 'stock_value':stock_value})
            session.execute(sql_update_won, {'author_id':author_id, 'stock_code':stock_code, 'balance':balance, 'stock_value':stock_value, 'stock_fee': stock_fee})
            session.commit()
            result = True
        except:
            session.rollback()
            result = False
        finally:
            session.close()
        
        return result
    
    def sell(self, author_id, stock_code, balance, stock_value, stock_fee):
        sql_update_stock = sql_text("""
                       UPDATE `account`
                       SET balance = balance - (:balance), sum_value= sum_value - (:stock_value)
                       WHERE author_id = :author_id and stock_code = :stock_code;
                       """)
                       
        sql_update_won = sql_text("""
                       UPDATE `account`
                       SET balance = balance + (:stock_value) - (:stock_fee), sum_value = sum_value + (:stock_value) - (:stock_fee)
                       WHERE author_id = :author_id and stock_code = 'KRW';
                       """)

        sql_delete = sql_text("""
                       DELETE FROM `account`
                       WHERE author_id = :author_id and stock_code = :stock_code and balance = 0;
                       """)
                       
        Session = sessionmaker(autocommit=False, autoflush=False, bind=self.connection)
        session = Session()

        try:
            session.execute(sql_update_stock, {'author_id':author_id, 'stock_code':stock_code, 'balance':balance, 'stock_value':stock_value})
            session.execute(sql_update_won, {'author_id':author_id, 'stock_code':stock_code, 'balance':balance, 'stock_value':stock_value, 'stock_fee': stock_fee})
            session.execute(sql_delete, {'author_id':author_id, 'stock_code':stock_code, 'balance':balance, 'stock_value':stock_value})
            session.commit()
            result = True
        except:
            session.rollback()
            result = False
        finally:
            session.close()
        
        return result


class KRXNewsData(Table):
    """
    뉴스정보를 저장할 테이블
    """
    def create_table(self):
        """
        테이블 생성
        """
        sql = sql_text("""
                       CREATE TABLE krx_news_data(
                           `index` int AUTO_INCREMENT PRIMARY KEY,
                           `datetime` datetime,
                           `id` varchar(3),
                           `title` text,
                           `code` varchar(250)                           
                           );
                       """)
        self.connection.execute(sql)



    def insert(self, context):
        """
        데이터를 krx_news_data 에 삽입
        """
        sql = sql_text("""
                       INSERT INTO krx_news_data 
                       (`datetime`, `id`, `title`, `code`)
                       VALUES(:datetime, :id, :title, :code)
                       """)

        self.connection.execute(sql, **context)

class KRXIndexData(Table):
    """
    지수 실시간 데이터를 저장할 테이블
    """
    def create_table(self):
        """
        테이블 생성
        """
        sql = sql_text("""
                       CREATE TABLE krx_index_data(
                           `upcode` varchar(5) PRIMARY KEY,
                           `time` varchar(8) ,
                           `sign` tinyint,
                           `change` decimal(10,2),
                           `drate` decimal(5,2),
                           `jisu` decimal(10,2),
                           `openjisu` decimal(10,2),
                           `highjisu` decimal(10,2),
                           `lowjisu` decimal(10,2),
                           `upjo` int,
                           `downjo` int,
                           `upjrate` decimal(5,2),
                           `frgsvalue` bigint,
                           `orgsvalue` bigint                                                      
                           );
                       """)
        self.connection.execute(sql)

    def update(self, context):
        sql = sql_text("""
                       INSERT INTO krx_index_data VALUES(:upcode, :time, :sign, :change, :drate, :jisu, :openjisu, :highjisu, :lowjisu, :upjo, :downjo, :upjrate, :frgsvalue, :orgsvalue)
                       ON DUPLICATE KEY UPDATE 
                           `time` = :time,
                           `sign` = :sign,
                           `change` = :change,
                           `drate` = drate,
                           `jisu` = :jisu,
                           `openjisu` = :openjisu,
                           `highjisu` = :highjisu,
                           `lowjisu` = :lowjisu,
                           `upjo` = :upjo,
                           `downjo` = :downjo,
                           `upjrate` = :upjrate,
                           `frgsvalue` = :frgsvalue,
                           `orgsvalue` = :orgsvalue  
                       """)

        self.connection.execute(sql, **context)

    def read(self, upcode):
        sql = sql_text("""
                        SELECT *
                        FROM `krx_index_data`
                        WHERE upcode = :upcode;
                        """)

        result = self.connection.execute(sql, upcode=upcode).fetchone()
        return result

class TodaySoaring(Table):
    def create_table(self):
        sql = sql_text("""
                       CREATE TABLE `today_soaring`(
                           `stock_code` varchar(8) PRIMARY KEY,
                           `datetime` datetime DEFAULT NOW(),
                           `increase_rate` int unsigned                       
                           );
                       """)
        self.connection.execute(sql)

    def check_5per(self):
        sql = sql_text("""
                        SELECT nh.author_id, nh.open, nh.price
                        FROM(
                            SELECT shcode AS stock_code, open, price
                            FROM `krx_real_data`
                            WHERE price > open * 1.05) AS nh
                        LEFT JOIN `today_soaring` AS ts ON nh.stock_code = ts.stock_code
                        WHERE ts.stock_code is NULL
                        """)

        df = pandas.read_sql_query(sql=sql, con=self.connection)
        return df

    def check_10per(self):
        sql = sql_text("""
                        SELECT nh.author_id, nh.open, nh.price
                        FROM(
                            SELECT shcode AS stock_code, open, price
                            FROM `krx_real_data`
                            WHERE price > open * 1.1) AS nh
                        LEFT JOIN `today_soaring` AS ts ON nh.stock_code = ts.stock_code
                        WHERE ts.increase_rate != 10
                        """)

        df = pandas.read_sql_query(sql=sql, con=self.connection)
        return df

    def insert(self, stock_code, increase_rate):
        sql = sql_text("""
                        INSERT INTO `today_soaring`
                        VALUES(:stock_code, DEFAULT, :increase_rate)
                        ON DUPLICATE KEY UPDATE datetime=DEFAULT, increase_rate=:increase_rate
                        """)

        self.connection.execute(sql, stock_code=stock_code, increase_rate=increase_rate)

#main 함수
def main():
    import market_data
    market_data.login()
    a = KRXIndexData()
    a.create_table()
    a.update_table()
    #KRXIndexData().update()
    #a = KRXIndexData()
    #a.create_table()
    pass

if __name__ == "__main__":
    main()
    

