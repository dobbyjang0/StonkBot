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

# 첫 로그인시 사용
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
    
    return

def create_log_table():
    global connection

    sql = sql_text("""
        CREATE TABLE input_log (
        `index` int unsigned PRIMARY KEY AUTO_INCREMENT,
        `guild_id` bigint unsigned,
        `channel_id` bigint unsigned,
        `author_id` bigint unsigned,
        `stock_code` int unsigned
        );
        """)
    try:
        connection.execute(sql)
    except:
        error_message = "Already exist"
        print(error_message)
        
#검색 로그를 db에 넣는다
def insert_serch_log(guild_id, channel_id, author_id, stock_code):
    global connection
    
    #에러 처리
    if type(connection) != sqlalchemy.engine.base.Engine:
        raise TypeError("curs_obj should be cursor object")
    for i in [guild_id, channel_id, author_id, stock_code]:
        if type(i) != int:
            raise TypeError("guild_id, channel_id, author_id, stock_code should be 'int' type")
            
    #실행
    sql = sql_text("""
        INSERT INTO input_log (
            guild_id, channel_id, author_id, stock_code
        )
        VALUES (guild_id, :channel_id, :author_id, :stock_code)
        """)

    result = connection.execute(sql, guild_id=guild_id, channel_id=channel_id, author_id=author_id, stock_code=stock_code)
    
    return result

# 이름을 입력하면 코드를 pandas 형식으로 찾아온다
def get_stock_code(stock_name):
    global connection

    #에러처리
    if type(connection) != sqlalchemy.engine.base.Engine:
        raise TypeError("curs_obj should be cursor object")
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
    df = pandas.read_sql_query(sql = sql, con = connection, params={"stock_name":stock_name+"%"})
    
    return df


#main 함수
def main():
    #체크용
    if __name__ == "__main__":
        print("메인으로 실행")
        # 로그인
        admin_login()

        create_log_table()
        print(get_stock_code("L"))
        
        # 입력y
        #insert_serch_log(1,2,3,"000000")
        
        #print(get_stock_code("L"))
        

main()

    

