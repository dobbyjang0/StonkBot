# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 21:51:51 2021

@author: dobbyjang0
"""
class stock_info:
    def __init__(self):
        self.name = "테스트" #주식명
        self.code = 0 #주식코드
        self.price = 0 #현재가
        self.comparedPrice= 0 #전일대비
        self.rate="+0.00%" #등락률
        self.volume = 0 #거래량(천주)
        self.transactionPrice = 0 #거래대금(백만)
        self.highPrice= 0 #장중고가
        self.lowPrice= 0 #장중저가
        self.chartUrl="https://cdn.discordapp.com/attachments/804815694717911080/805011065950830592/error-image-generic.png"
        #차트 이미지 url
        self.naverUrl="https://finance.naver.com/"
        #네이버 증권 url