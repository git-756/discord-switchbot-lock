import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
# SwitchBot APIを利用するためのライブラリ（requestsなどでも代用可）
# 今回は公式APIの認証処理を考慮し、requestsを使うか、API認証をラップしたライブラリを使います。
# ここではAPI v1.1に対応するため、requestsを使った基本的な関数を用意します。
import time
import hashlib
import hmac
import base64
import uuid
import json
import requests

# .envファイルを読み込む
load_dotenv()

# --- 環境変数の設定 ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TRIGGER_WORD = os.getenv("TRIGGER_WORD", "温湿度は？") 
SWITCHBOT_TOKEN = os.getenv("SWITCHBOT_TOKEN")
SWITCHBOT_SECRET = os.getenv("SWITCHBOT_SECRET")
SWITCHBOT_DEVICE_ID = os.getenv("SWITCHBOT_DEVICE_ID")

# --- SwitchBot API クライアント関数 ---
def get_switchbot_data():
    """
    SwitchBot API v1.1 を使用して温湿度データを取得する
    """
    # 必要な情報が揃っているか確認
    if not (SWITCHBOT_TOKEN and SWITCHBOT_SECRET and SWITCHBOT_DEVICE_ID):
        print("SwitchBot APIの設定情報が不足しています。")
        return None, None

    # API v1.1 認証情報の生成
    token = SWITCHBOT_TOKEN
    secret = bytes(SWITCHBOT_SECRET.encode('utf-8'))
    t = int(round(time.time() * 1000))
    nonce = str(uuid.uuid4())
    string_to_sign = '{}{}{}'.format(token, t, nonce)
    string_to_sign_bytes = bytes(string_to_sign.encode('utf-8'))
    
    # 署名生成
    sign = base64.b64encode(
        hmac.new(secret, msg=string_to_sign_bytes, digestmod=hashlib.sha256).digest()
    )

    # リクエストヘッダー
    headers = {
        'Authorization': token,
        't': str(t),
        'sign': sign.decode('utf-8'),
        'nonce': nonce,
        'Content-Type': 'application/json'
    }

    # デバイスの状態を取得するAPIエンドポイント
    url = f"https://api.switch-bot.com/v1.1/devices/{SWITCHBOT_DEVICE_ID}/status"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 200以外の場合は例外を発生
        data = response.json()
        
        # APIレスポンスのチェック
        if data.get('statusCode') == 100 and 'body' in data:
            body = data['body']
            # 温湿度計のデータは 'temperature' と 'humidity' キーに含まれる
            temperature = body.get('temperature')
            humidity = body.get('humidity')
            battery = body.get('battery')
            
            return temperature, humidity, battery
        else:
            print(f"SwitchBot APIエラー: {data.get('message', '不明なエラー')}")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"SwitchBot APIリクエスト失敗: {e}")
        return None, None, None

# --- Discord Botの設定 ---
# Intenstを有効にする (Message Content Intent が必要)
intents = discord.Intents.default()
intents.message_content = True 

# Botクライアントの作成
bot = commands.Bot(command_prefix='!', intents=intents) # コマンドは使用しないが、clientの代わりにcommands.Botを使用

@bot.event
async def on_ready():
    """
    BotがDiscordに接続したときに実行される
    """
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_message(message):
    """
    メッセージが送信されるたびに実行される
    """
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return

    # 指定のワードが含まれているかチェック
    # 大文字・小文字、全角・半角の違いを無視する場合は message.content.lower() などを使用
    if TRIGGER_WORD in message.content:
        # データの取得
        await message.channel.send("SwitchBotの温湿度データを取得中です... 📡")
        
        # API呼び出しはI/O操作なので非同期(await)対応
        # requestsは同期処理なので、run_in_executorで非同期化
        loop = asyncio.get_event_loop()
        temperature, humidity, battery = await loop.run_in_executor(
            None, get_switchbot_data
        )

        if temperature is not None and humidity is not None:
            response_message = (
                f"🌡️ **現在の温湿度データ** 🌡️\n"
                f"温度: **{temperature:.1f} °C**\n"
                f"湿度: **{humidity:.1f} %**\n"
                f"バッテリー残量: {battery} %"
            )
        else:
            response_message = (
                "データの取得に失敗しました。SwitchBot Hubの接続、APIキー、デバイスIDを再確認してください。:interrobang:"
            )

        # 結果をテキストチャンネルに送信
        await message.channel.send(response_message)
    
    # commands.Botを使用しているため、他のコマンド処理のために以下を呼び出す
    await bot.process_commands(message)

# Botの実行
if DISCORD_TOKEN:
    try:
        # Intentの設定に問題がないか確認
        if not bot.intents.message_content:
            print("エラー: intents.message_contentが有効になっていません。Discord Developer Portalで有効化が必要です。")
        
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("致命的なエラー: Discordトークンが無効です。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
else:
    print("致命的なエラー: DISCORD_TOKENが設定されていません。")