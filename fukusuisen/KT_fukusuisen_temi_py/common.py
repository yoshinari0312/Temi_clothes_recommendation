import speech_recognition as sr
from colorama import Fore, Back, Style
import re
import random
import requests
import commonGPT

# IPアドレスを変更する必要アリ
ip = "192.168.1.64"
port = 5531


# 音声認識
def record():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 500
    try:
        with sr.Microphone() as source:
            print(Fore.YELLOW + "[発言してください]" + Style.RESET_ALL)
            #input() #これがないと，pepperが喋ってる最中に録音が始まり，pepperが喋ってる内容を文字起こししちゃう
            ## 録音開始
            audio = recognizer.listen(source, timeout = 30)

            # 入力があった場合以下が実行，なければExceptionへ　入力があっても認識できなかった，ノイズを入力と勘違いしてしまった場合もExceptionへ？
            ## 文字起こし
            text = recognizer.recognize_google(audio, language="ja-JP")

            print("[YOU] " + text)
            return text
            
    except Exception as e:
        print(e)


# generate_textを一文単位に分割
def split_text(text):
    splited_text = re.split("(?<=[。？、！，．])(?<=[.,])", text)
    #print(splited_text)
    return splited_text


# 文に方向を示す語があるかチェック（ジェスチャーラベル）
def text_judge(text):
    #最初に見つけた方向を採用(多分)
    if "左" in text:
        text = text + ":left"
        return text
    elif "右" in text:
        text = text + ":right"
        return text
    elif "上" in text:
        text = text + ":up"
        return text
    elif "下" in text:
        text = text + ":down"
        return text
    elif "建物" in text:
        text = text + ":building"
        return text
    elif "進" in text:
        text = text + ":straight"
        return text

    #方向を示す語がなかった場合
    text = text + ":none"
    return text


def set_id(id):
    server_url = 'http://192.168.1.80:4999/set_id'
    response = requests.post(server_url, json={'id': int(id)})
    # if response.status_code == 200:
    #     print("ID set successfully")
    # else:
    #     print(f"Failed to set ID: {response.status_code}, {response.text}")

def process_id():
    server_url = 'http://192.168.1.80:4999/process_id'
    response = requests.get(server_url)