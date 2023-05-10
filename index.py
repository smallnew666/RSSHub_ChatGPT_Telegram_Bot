# -*- coding: utf-8 -*-
import time
import feedparser
import requests
from telegram import Bot
from datetime import datetime
from bs4 import BeautifulSoup
from translate import Translator
from dotenv import load_dotenv
import os
import asyncio
import json
import openai
from datetime import datetime

# Set the source and target languages
source_language = "en"
target_language = "zh"
translator = Translator(from_lang=source_language, to_lang=target_language)

load_dotenv()  # Load environment variables from .env file

TOKEN = os.getenv("TOKEN")
target_chat_id = os.getenv("target_chat_id")

bot = Bot(token=TOKEN)

rss_list = []
# 读取文本文件
with open("twitter_list.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# 遍历文本里的每一行
for line in lines:
    info = line.strip().split(',')

    # 获取 Twitter ID 和昵称
    twitter_id = info[0].strip()
    nickname = info[1].strip() if len(info) > 1 else twitter_id

    # 构造 URL
    url = f"http://127.0.0.1:1200/twitter/user/{twitter_id}"

    # 添加到 rss_list
    rss_list.append({
        "name": nickname,
        "url": url
    })

def get_latest_twitter_updates(rss_url, last_item_link):
    response = requests.get(rss_url)
    rss_content = response.content
    feed = feedparser.parse(rss_content)
    
    latest_items = []
    for entry in feed["entries"]:
        if entry["link"] == last_item_link:
            break
        latest_items.append(entry)
        
    return latest_items

async def send_update_to_telegram(items):
    for item in items:
        author = item["author"]
        title = item["title"]

        description_html = item["description"]
        soup = BeautifulSoup(description_html, 'html.parser')

        # Convert div with class rsshub-quote
        rsshub_quotes = soup.find_all('div', class_='rsshub-quote')
        for rsshub_quote in rsshub_quotes:
            rsshub_quote.string = f"\n&gt; {rsshub_quote.get_text(separator=' ', strip=True)}\n\n"
        
        for br in soup.find_all('br'):
            br.replace_with('\n')
        
        description = "\n".join(soup.stripped_strings)
        #description_zh = translator.translate(description)
        pub_date_parsed = datetime.strptime(item["published"], "%a, %d %b %Y %H:%M:%S %Z")
        pub_date = pub_date_parsed.strftime("%Y-%m-%d %H:%M:%S")
        link = item["link"]
        #比较当前时间
        time_str = item["published"]
        time_obj = datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S %Z')
        # 将datetime对象转换为时间戳
        timestamp = int(time_obj.timestamp())

        # 获取当前时间的时间戳
        now_timestamp = int(datetime.now().timestamp())
        if now_timestamp-timestamp>24*3600:
            continue
        openai.api_key = "" #修改这里为自己申请的api_key
        messages = [
            {"role": "system", "content": '你是一个著名的自媒体编辑，你可以对收到的资讯进行分析评级，等级分为1-10，根据发布时间，与AI内容的关联性，AI资讯的重要性等各个维度进行评级，评级方向着重于AI信息，下面我给你来自twitter的内容，请你对内容进行分析,用中文回答，回答格式为json格式，{"grade":得分,"analysis":"分析"}：'},
        ]
        
        messages.append({"role": "user", "content": "发布时间: "+pub_date+"内容："+description})
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=messages,
                temperature=0,
                stream=False  # again, we set stream=True
            )
            generated_text = response["choices"][0]["message"].content
            time.sleep(20)
            res = json.loads(generated_text)
            if res['grade']<5:
                continue
        except Exception as e:
            print(e)
            res['grade']=0
            res['analysis']=""
        message = (
            f"From {author}:\n\n"
            f"发布时间: {pub_date}\n\n"
            f"{description}\n\n"  
            f"评分等级：{res['grade']}\n\n"
            f"分析：{res['analysis']}\n\n"
            f"链接: {link}"
        )
        #print(message)
        await asyncio.to_thread(bot.send_message, chat_id=target_chat_id, text=message)  # Do not use parse_mode="HTML"

last_links = [None] * len(rss_list)
interval = 10  # 以秒为单位，根据需要调整RSS检查的频率

async def main():
    while True:
        for index, rss_source in enumerate(rss_list):
            latest_items = get_latest_twitter_updates(rss_source["url"], last_links[index])

            if latest_items:
                last_links[index] = latest_items[0]["link"]
                await send_update_to_telegram(latest_items[::-1]) # Send tweets from oldest to newest
            
            await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(main())
