import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import time
import hashlib
import hmac
import base64
import uuid
import requests
import json

# .envファイルを読み込む
load_dotenv()

# --- 環境変数の設定 ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# SwitchBot APIのキーとスマートロックのID
TOKEN = os.getenv("SWITCHBOT_TOKEN")
SECRET = os.getenv("SWITCHBOT_SECRET")
SMARTLOCK_ID = os.getenv("SWITCHBOT_SMARTLOCK_ID")

# SECRETをバイト列に変換 (署名生成に使用)
SECRET_BYTES = SECRET.encode('utf-8') if SECRET else b''

# --- SwitchBot API 認証/署名生成 ヘルパー ---
def get_auth_headers():
    """SwitchBot API v1.1 認証に必要なヘッダーを生成する"""
    if not (TOKEN and SECRET):
        print("SwitchBot APIの設定情報が不足しています。")
        return None

    t = int(round(time.time() * 1000))
    nonce = str(uuid.uuid4())
    string_to_sign = '{}{}{}'.format(TOKEN, t, nonce)
    
    # 署名生成
    sign = base64.b64encode(
        hmac.new(SECRET_BYTES, msg=bytes(string_to_sign.encode('utf-8')), digestmod=hashlib.sha256).digest()
    ).decode('utf-8')

    return {
        'Authorization': TOKEN,
        't': str(t),
        'sign': sign,
        'nonce': nonce,
        'Content-Type': 'application/json'
    }

# --- SwitchBot API クライアント関数 ---

def get_lock_status(device_id):
    """スマートキーの現在の状態 (施錠/解錠) を取得する"""
    headers = get_auth_headers()
    if not headers:
        return None, "認証情報エラー"

    url = f"https://api.switch-bot.com/v1.1/devices/{device_id}/status"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('statusCode') == 100 and 'body' in data:
            # ロックの状態は 'lockState' キーに含まれる
            lock_state = data['body'].get('lockState')
            battery = data['body'].get('battery')

            # lockState の値に対応する日本語を返す
            if lock_state == "locked":
                status_text = f"施錠されています 🔒 (電池残量: {battery}%)"
            elif lock_state == "unlocked":
                status_text = f"解錠されています 🔓 (電池残量: {battery}%)"
            else:
                status_text = f"状態が不明です ({lock_state}) ❓ (電池残量: {battery}%)"
                
            return True, status_text
        else:
            return False, f"APIエラー: {data.get('message', '不明なエラー')}"

    except requests.exceptions.RequestException as e:
        return False, f"リクエスト失敗: {e}"


def control_smartlock(device_id, action):
    """スマートキーを操作する (lock/unlock)"""
    headers = get_auth_headers()
    if not headers:
        return False, "認証情報エラー"

    url = f"https://api.switch-bot.com/v1.1/devices/{device_id}/commands"

    command_body = {
        "command": action,  # "lock" または "unlock"
        "parameter": "default",
        "commandType": "command"
    }

    try:
        response = requests.post(url, headers=headers, json=command_body, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('statusCode') == 100:
            return True, "成功"
        else:
            return False, f"操作エラー: {data.get('message', '不明なエラー')}"

    except requests.exceptions.RequestException as e:
        return False, f"リクエスト失敗: {e}"


# --- Discord Botの設定 ---
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip()
    
    # ロック操作
    if content == "鍵開けて！":
        await message.channel.send("🔑 スマートキーを**ロック**中です...")
        
        # 非同期で操作を実行
        success, msg = await asyncio.get_event_loop().run_in_executor(
            None, control_smartlock, SMARTLOCK_ID, "unlock"
        )
        
        if success:
            await message.channel.send("✅ 開いたよ！")
        else:
            await message.channel.send(f"❌ ロック操作に失敗しました: {msg}")

    # アンロック操作
    elif content == "鍵閉めて！":
        await message.channel.send("🔓 今から閉めるよ...")
        
        # 非同期で操作を実行
        success, msg = await asyncio.get_event_loop().run_in_executor(
            None, control_smartlock, SMARTLOCK_ID, "lock"
        )

        if success:
            await message.channel.send("✅ 閉まったよ！")
        else:
            await message.channel.send(f"❌ アンロック操作に失敗しました: {msg}")
            
    # 状態取得
    elif content == "鍵閉まってる？":
        await message.channel.send("💬 確認するよ...")
        
        # 非同期で状態を取得
        success, status_msg = await asyncio.get_event_loop().run_in_executor(
            None, get_lock_status, SMARTLOCK_ID
        )

        if success:
            await message.channel.send(f"➡️ **現在の鍵の状態**: {status_msg}")
        else:
            await message.channel.send(f"❌ 状態取得に失敗しました: {status_msg}")


    await bot.process_commands(message)

# Botの実行
if DISCORD_TOKEN and TOKEN and SECRET and SMARTLOCK_ID:
    try:
        # SECRET_BYTESが空の場合はエラー
        if not SECRET_BYTES:
            print("致命的なエラー: SWITCHBOT_SECRETが.envに設定されていません。")
        else:
            bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("致命的なエラー: Discordトークンが無効です。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
else:
    print("致命的なエラー: 必要な環境変数 (DISCORD_TOKEN, SWITCHBOT_TOKEN, SWITCHBOT_SECRET, SWITCHBOT_SMARTLOCK_ID) が設定されていません。")