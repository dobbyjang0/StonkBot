# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 21:51:25 2021

@author: dobbyjang0
"""

import nest_asyncio
import discord
from discord.ext import commands, tasks
import pandas
import stock
import save_log_yesalchemy

nest_asyncio.apply()

bot = commands.Bot(command_prefix="--")

@bot.event
async def on_ready():
    print("--- 연결 성공 ---")
    print(f"봇 이름: {bot.user.name}")
    print(f"ID: {bot.user.id}")
    
    
@bot.command()
async def 킬(ctx):
    if ctx.author.id not in [378887088524886016, 731836288147259432]:
        await ctx.send("권한없음")
        return
    await ctx.send("봇 꺼짐")
    await bot.close()
    
@bot.command()
async def 주식(ctx,stock_name="삼성전자"):
    #코드가 아닐시 검색해본다
    if stock_name.isdigit() is not True:
        stock_list_pd = save_log_yesalchemy.get_stock_code(stock_name)
        
        stock_list_len = len(stock_list_pd)
        
        if stock_list_len == 0:
            await ctx.send("데이터가 없음")
            return
        elif stock_list_len == 1:
            stock_code = int(stock_list_pd.iat[0, 0])
        else:
            await ctx.send(str(stock_list_pd))
            def check(message: discord.Message):
                return message.channel == ctx.channel and message.author == ctx.author
            try:
                check_number_msg = await bot.wait_for('message', timeout=10, check=check)
            except:
                await ctx.send("시간초과")
                return
            else:
                check_number = str(check_number_msg.content)
                if check_number.isdigit() is not True and int(check_number) >= stock_list_len and int(check_number) < 0:
                    await ctx.send("잘못된 입력")
                    return
                else:
                    stock_index = int(check_number)
                    stock_code = int(stock_list_pd.iat[stock_index, 0])
    else:
        stock_code = stock_name
            
    
    #코드로 주식 검색
    serching_stock=stock.StockInfo()
    
    try:
        serching_stock.get_stock(stock_code)
    except:
        await ctx.send("잘못된 코드명")
        return
    
    # 출력할 embed 만들기
    embed_title = serching_stock.name
    embed_title_url = serching_stock.naver_url
    embed= discord.Embed(title=embed_title,url=embed_title_url)
    embed_discription_1=f"{serching_stock.price}\t{serching_stock.compared_price}\t{serching_stock.rate}\n"
    embed.description = embed_discription_1
    
    embed.add_field(name="거래량(천주)", value=serching_stock.volume)
    embed.add_field(name="거래대금(백만)", value=serching_stock.transaction_price)
    embed.add_field(name=".", value=".")
    embed.add_field(name="장중최고", value=serching_stock.high_price)
    embed.add_field(name="장중최저", value=serching_stock.low_price)
    
    embed.set_image(url=serching_stock.chart_url)
    
    await ctx.send(embed=embed)
    
#깃허브에 올릴시에는 봇 토큰 지우기
bot_token = input("봇 토큰 입력 : ")
bot.run(bot_token)
