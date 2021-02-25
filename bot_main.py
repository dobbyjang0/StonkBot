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
    serchStock=stock.stock_info()
    
    try:
        serchStock.getstock(stock_name)
    except:
        await ctx.send("잘못된 코드명")
        return
    
    print(ctx.guild.id, ctx.channel.id, ctx.author.id, stock_name)
    #서버 id, 채널 id, 내용 id, 보낸이 id, 검색내용
    
    embed_title = serchStock.name
    embed_title_url = serchStock.naverUrl
    embed= discord.Embed(title=embed_title,url=embed_title_url)
    
    embed_discription_1=f"{serchStock.price}\t{serchStock.comparedPrice}\t{serchStock.rate}\n"
    embed.description = embed_discription_1
    
    embed.add_field(name="거래량(천주)", value=serchStock.volume)
    embed.add_field(name="거래대금(백만)", value=serchStock.transactionPrice)
    embed.add_field(name=".", value=".")
    embed.add_field(name="장중최고", value=serchStock.highPrice)
    embed.add_field(name="장중최저", value=serchStock.lowPrice)
    
    embed.set_image(url=serchStock.chartUrl)
    
    await ctx.send(embed=embed)
    
#깃허브에 올릴시에는 봇 토큰 지우기
bot.run("")
