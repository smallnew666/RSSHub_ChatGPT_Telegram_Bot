# RSSHub_ChatGPT_Telegram_Bot

通过ChatGPT分析处理RSSHub抓取的twitter数据，分析AI相关资讯等级并推送给自己的Telegram bot

## 前置条件
安装RSSHub
https://docs.rsshub.app/install/#shou-dong-bu-shu-an-zhuang

运行RSSHub
yarn start

测试是否安装成功
http://127.0.0.1:1200

## 使用方法
1 创建Telegram机器人，获取Token
打开 https://t.me/botfather 输入 /start
按引导流程，先输入机器人名字，然后输入想要ID（必须以bot结尾），比如telegram_rss_bot
创建后会给Token，类似这种结构：5987500169:AAEBqLx7OWmK6ne9pIfHhrgMktDmq_VcsSQ

2 获取自己的Telegram ID
打开 https://t.me/userinfobot 输入 \/start，拿到自己的ID，类似结构：1293676963


3 设置Token和Telegram ID

把Token和Telegram ID 填入env.txt文件，然后把env.txt改名为".env"

4 安装依赖程序
```
pip3 install -r requirements.txt
```
5 设置openai api_key
添加api_key到index.py
openai.api_key = "sk-xxxx" 

6 运行程序
python3 index.py

## 修改twitter源
修改 twitter_list.txt ，一行一个name

## 更多
可以根据你想要处理的数据类型可以手动替换ChatGPT的系统提示词，也可以分析其他平台的信息源，reddit、facebook、youtube等等

### 参考
https://github.com/DIYgod/RSSHub

https://github.com/joeseesun/AIGC_Telegram_Bot





