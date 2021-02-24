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
async def kill(ctx):
    if ctx.author.id not in [378887088524886016, 731836288147259432]:
        await ctx.send("권한없음")
        return
    await bot.close()
    
@bot.command()
async def 주식(ctx,stock_name="테스트"):
    if stock_name=="테스트":
        serchStock=stock.stock_info()
    embed_title = serchStock.name
    embed_title_url = serchStock.naverUrl
    embed= discord.Embed(title=embed_title,url=embed_title_url)
    
    
    embed_discription_1=f"{serchStock.price:<10}{serchStock.comparedPrice:<10}{serchStock.rate:<10}\n"
    embed_discription_2="**거래량(천주)     거래대금(백만)**\n"
    embed_discription_3=f"{serchStock.volume:<17}{serchStock.transactionPrice:<17}\n"
    embed_discription_4="**장중최고         장중최저**\n"
    embed_discription_5=f"{serchStock.highPrice:<17}{serchStock.lowPrice:<17}"
    
    embed_discription_total=embed_discription_1+embed_discription_2+embed_discription_3+embed_discription_4+embed_discription_5
    
    embed.description = embed_discription_total
    embed.set_image(url=serchStock.chartUrl)
    
    await ctx.send("테스트")
    

bot.run("ODE0MTE1MjI2OTMxNjkxNTIw.YDZJ4w.mocMn2S2OQyS3WOwiVRRlwu8wOI")