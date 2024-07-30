import speech_recognition as sr
from colorama import Fore, Back, Style
import re
import random
import requests
import playsound
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
            playsound.playsound("startrecognition.mp3")
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


# 認識結果を改変
def text_modify(text):
    text = text.replace('qoo 10','9点').replace('Qoo 10','9点')
    text = text.replace('発展','8点')
    text = text.replace('一転','1点')
    text = text.replace('一','1').replace('二','2').replace('三','3').replace('四','4').replace('五','5').replace('六','6').replace('七','7').replace('八','8').replace('九','9').replace('十','10')
    
    return text


def set_id(id):
    server_url = 'http://192.168.1.59:4999/set_id'
    response = requests.post(server_url, json={'id': int(id)})
    # if response.status_code == 200:
    #     print("ID set successfully")
    # else:
    #     print(f"Failed to set ID: {response.status_code}, {response.text}")

def process_id():
    server_url = 'http://192.168.1.59:4999/process_id'
    response = requests.get(server_url)