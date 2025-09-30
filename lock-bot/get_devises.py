import time
import hashlib
import hmac
import base64
import uuid
import requests
import json
from dotenv import load_dotenv
import os

# .envファイルを読み込む (事前にTokenとSecretを.envに設定している場合)
load_dotenv()

# Step 1 で取得した情報を設定
# .envから読み込む場合は以下のように設定
TOKEN = os.getenv("SWITCHBOT_TOKEN", "YOUR_API_TOKEN_HERE")
SECRET = os.getenv("SWITCHBOT_SECRET", "YOUR_API_SECRET_HERE").encode('utf-8')

def get_device_list(token, secret):
    """SwitchBot API v1.1 を使用して全デバイスのリストを取得する"""

    # API v1.1 認証情報の生成 (前回と同じロジック)
    t = int(round(time.time() * 1000))
    nonce = str(uuid.uuid4())
    string_to_sign = '{}{}{}'.format(token, t, nonce)
    string_to_sign_bytes = bytes(string_to_sign.encode('utf-8'))
    
    # 署名生成
    sign = base64.b64encode(
        hmac.new(secret, msg=string_to_sign_bytes, digestmod=hashlib.sha256).digest()
    ).decode('utf-8') # バイト列を文字列にデコード

    # リクエストヘッダー
    headers = {
        'Authorization': token,
        't': str(t),
        'sign': sign,
        'nonce': nonce,
        'Content-Type': 'application/json'
    }

    # デバイス一覧を取得するAPIエンドポイント
    url = "https://api.switch-bot.com/v1.1/devices"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 200以外の場合は例外を発生
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"APIリクエスト失敗: {e}")
        return None

if __name__ == "__main__":
    device_data = get_device_list(TOKEN, SECRET)
    
    if device_data and device_data.get('statusCode') == 100:
        print("--- デバイス一覧 ---")
        # 温湿度計を含む物理デバイスリストを表示
        for device in device_data.get('body', {}).get('deviceList', []):
            if device['deviceType'] in ['Meter', 'Meter Plus', 'Outdoor Meter', 'Meter Pro']:
                 print(f"デバイス名: {device['deviceName']}")
                 print(f"デバイスタイプ: {device['deviceType']}")
                 print(f"**デバイスID: {device['deviceId']}**\n")
            else:
                 print(f"デバイス名: {device['deviceName']} (タイプ: {device['deviceType']})")
                 print(f"ID: {device['deviceId']}\n")
    else:
        print("デバイス一覧の取得に失敗しました。トークン/シークレットキー、またはインターネット接続を確認してください。")