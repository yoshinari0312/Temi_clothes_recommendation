import os
import socket
from openai import OpenAI
import speech_recognition as sr
from colorama import Fore, Back, Style
import threading
from queue import Queue
import random

# GPTとのやりとり
def GPT_talk(prompt):

    # ユーザーの質問を会話履歴に追加
    conversation_history.append({"role": "user", "content": prompt})
    
    # GPT-4モデルを使用してテキストを生成
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {
            "role": "system",
            "content": "・あなたはロボットのtemiです。\n\
                        ・ユーザと雑談を行ってください。\n"
        }] + conversation_history,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = response.choices[0].message.content.strip()
    
    # アシスタントの回答を会話履歴に追加
    conversation_history.append({"role": "assistant", "content": message})
    
    return message


# 音声認識
def record():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 500
    try:
        with sr.Microphone() as source:
            print(Fore.YELLOW + "[発言してください]" + Style.RESET_ALL)

            ## 録音開始
            audio = recognizer.listen(source, timeout = 30)

            # 入力があった場合以下が実行，なければExceptionへ　入力があっても認識できなかった，ノイズを入力と勘違いしてしまった場合もExceptionへ？
            ## 文字起こし
            text = recognizer.recognize_google(audio, language="ja-JP")

            print("[YOU] " + text)
            return text
            
    except Exception as e:
        print(e)



# メイン
def main(mode):

    def generating_text():
        generated_text = GPT_talk(input_prompt)
        q.put(generated_text)


    input_prompt = None

    if mode == True:
        input_prompt = record()
    else:
        input_prompt = input("[YOU] ")

    if input_prompt != None: # 入力があった場合

        q = Queue()
        thread1 = threading.Thread(target=generating_text)
        thread1.start() # スレッドの実行

        backchannel = ['うーんと', 'えーと']
        
        while(thread1.is_alive()): # スレッドの実行が終わるまでループ
            x = random.randint(0, 1)
            y = 4
            # if mode == True:
            #     servermessege = ""
            #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #         # サーバを指定
            #         s.connect((ip, port))
            #         # 回答をpepperに送信
            #         s.sendall((backchannel[x]+'\r\n').encode())
            #         servermessege = s.recv(1024).decode()
            #     time.sleep(y)

        generated_text = q.get()
        print("[GPT]", generated_text)

        if mode == True: # temiと通信を行う
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # サーバを指定
                s.connect((ip, port))
                # 回答をpepperに送信
                s.sendall((generated_text+'\r\n').encode())

                servermessege = s.recv(1024).decode()



#__main__内はグローバル変数
if __name__ == "__main__":

    openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY']) # OpenAI key
    conversation_history = [] # 会話履歴を格納するためのリストを初期化

    # IPアドレスを変更する必要アリ
    ip = "192.168.1.64"
    port = 5530

    while True:
        main(True) # mainの引数によって、音声でtemiとやりとりするか（本番用）、temiに接続せずテキストでやりとりするか（GPTの動作確認）を選べる