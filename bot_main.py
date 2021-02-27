# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 21:51:25 2021

@author: dobbyjang0
"""

import nest_asyncio
import discord
from discord.ext import commands, tasks
import stock

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
    await bot.close()
    
@bot.command()
async def 주식(ctx,stock_name="005930"):
    serching_stock=stock.StockInfo()
    
    try:
        serching_stock.get_stock(stock_name)
    except:
        await ctx.send("잘못된 코드명")
        return
    
    print(ctx.guild.id, ctx.channel.id, ctx.author.id, stock_name)
    #서버 id, 채널 id, 내용 id, 보낸이 id, 검색내용
    
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
bot.run("ODE0MTE1MjI2OTMxNjkxNTIw.YDZJ4w.ra6IgSsnn0Uh9chN65o7PVxWrDg")
