# Telegram hotel-bot 
Bot for searching hotels on airbnb

## Start usage

To start, you need to get a token from Telegram and also get a key at:
https://rapidapi.com/3b-data-3b-data-default/api/airbnb13/,
after, you need to create .env file and input values:
```
BOT_TOKEN = "your bot token"
RAPID_API_KEY = "your api key"
```
For run app:
```
% pip install -r requirements.txt
% python main.py
```
## Bot commands
/start - start bot
/help - list of bot commands  
/lowprice - command for search low price hotels  
/highprice - command for search high price hotels  
/bestdeals - command for search best rate hotels  
/custom - command for search hotels by advanced criteria  
/history - command for see your requests  
/cancel - cancel current command  