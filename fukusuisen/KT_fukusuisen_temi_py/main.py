import socket
import datetime
import common
import commonGPT
import predict
import threading
import time
from queue import Queue
import random
import requests
from flask import Flask, request, jsonify, render_template
import logging
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

global_id = None

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)

q = Queue()


@app.route('/')
def index():
    return render_template('speech_recognition.html')


@app.route('/start_main', methods=['POST'])
def start_main():
    # `main` 関数を無限ループで実行するスレッドを開始
    thread = threading.Thread(target=run_main)
    thread.start()
    return jsonify({"message": "main loop has started!"})


@app.route('/set_id', methods=['POST'])
def set_id_route():
    global global_id
    try:
        data = request.get_json()
        app.logger.debug(f"Received data: {data}")
        id = data.get('id')
        if id is not None:
            global_id = id
            app.logger.debug(f"ID set to: {id}")
            return jsonify({"message": "ID set successfully"}), 200
        else:
            app.logger.debug("No ID provided")
            return jsonify({"error": "No ID provided"}), 400
    except Exception as e:
        app.logger.debug(f"Error: {e}")
        return jsonify({"error": "Bad Request"}), 400


@app.route('/process_id', methods=['GET'])
def process_id():
    global global_id
    if global_id is None:
        app.logger.debug("ID not set")
        return jsonify({"error": "ID not set"}), 400

    id = global_id

    # if id == 70:
    #     app.logger.debug("70です")
    # elif id == 71:
    #     app.logger.debug("71です")
    # if 1 <= id <= 33:
    #     server_url = 'http://localhost:5001/update_image'
    #     app.logger.debug("1から33です")
    # elif 34 <= id <= 67:
    #     server_url = 'http://localhost:5002/update_image'
    #     app.logger.debug("33から67です")
    # else:
    #     server_url = 'http://localhost:5003/update_image'
    #     app.logger.debug("67から100です")

    # テクノモール用
    if id == 70:
        app.logger.debug("70です")
    else:
        server_url = 'http://localhost:5001/update_image'
        app.logger.debug("70以外です")

    image_src = f'static/images/{id}.jpg'
    response = requests.post(server_url, json={'image_src': image_src})
    if response.status_code == 200:
        app.logger.debug(f"Image updated on server: {server_url}")
        return jsonify({"message": f"Image updated on server: {server_url}"})
    else:
        app.logger.debug(f"Failed to update image on server: {server_url}")
        return jsonify({"message": f"Failed to update image on server: {server_url}"}), 500


@socketio.on('user_message')
def handle_user_message(message):
    q.put(message['data'])


def set_id(id):
    server_url = "http://192.168.1.103:4999/set_id"
    requests.post(server_url, json={"id": int(id)})
    # if response.status_code == 200:
    #     print("ID set successfully")
    # else:
    #     print(f"Failed to set ID: {response.status_code}, {response.text}")

def process_id():
    server_url = "http://192.168.1.103:4999/process_id"
    requests.get(server_url)

# メイン
def main(mode, f):
    global turn

    def generating_text():
        global turn
        global ask_id
        global recommend
        global good
        global bad
        
        generated_text = ""
        score = -1
        result = -1
        
        if turn == 1: # user「こんにちは」 temi「こんにちは、10点で評価してください」
            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt) # gptの返答を生成
            generated_text = generated_text + ":none"
            q_internal.put(generated_text)
            turn += 1


        elif turn == 2: # user「おけい」 temi「これ何点？（1個目）」 # NMF_ASK
            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            ask_id = predict.show_image(predict.candidate[0])
            generated_text = generated_text + ":picture:" + str(ask_id)
            q_internal.put(generated_text)
            turn += 1


        elif turn == 3: # user「n点（1個目に対して）」 temi「これ何点？（2個目）」 # NMF_ASK
            score = commonGPT.GPT_score_judge(input_prompt)
            print("score: " + str(score))
            f.write("score: " + str(score) + '\n')

            # スコアが上手く判定されなかった時の処理
            if score == -1 or score > 10:
                print("<greet_and_question>")
                generated_text = commonGPT.GPT_greet_and_question(input_prompt)
                generated_text = generated_text + ":picture:" + str(ask_id)
                q_internal.put(generated_text)
                return # スコアが上手く判定されなければ抜ける（turnは増えないのでもう一回聞かれる）
        
            predict.user_pref.append(score)

            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            ask_id = predict.predict_pref_pre()
            generated_text = generated_text + ":picture:" + str(ask_id)
            q_internal.put(generated_text)
            turn += 1


        elif turn == 4: # user「n点（2個目に対して）」 temi「これ何点？（3個目）」 # PREF_ASK
            score = commonGPT.GPT_score_judge(input_prompt)
            print("score: " + str(score))
            f.write("score: " + str(score) + '\n')

            # スコアが上手く判定されなかった時の処理
            if score == -1 or score > 10:
                print("<greet_and_question>")
                generated_text = commonGPT.GPT_greet_and_question(input_prompt)
                generated_text = generated_text + ":picture:" + str(ask_id)
                q_internal.put(generated_text)
                return # スコアが上手く判定されなければ抜ける（turnは増えないのでもう一回聞かれる）
        
            predict.user_pref.append(score)

            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            ask_id = predict.predict_pref_pre()
            generated_text = generated_text + ":picture:" + str(ask_id)
            q_internal.put(generated_text)
            turn += 1


        elif turn == 5: # user「n点（3個目に対して）」 temi「これ何点？（4個目）」 # PREF_ASK
            score = commonGPT.GPT_score_judge(input_prompt)
            print("score: " + str(score))
            f.write("score: " + str(score) + '\n')

            # スコアが上手く判定されなかった時の処理
            if score == -1 or score > 10:
                print("<greet_and_question>")
                generated_text = commonGPT.GPT_greet_and_question(input_prompt)
                generated_text = generated_text + ":picture:" + str(ask_id)
                q_internal.put(generated_text)
                return # スコアが上手く判定されなければ抜ける（turnは増えないのでもう一回聞かれる）
        
            predict.user_pref.append(score)

            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            ask_id = predict.predict_pref_pre()
            generated_text = generated_text + ":picture:" + str(ask_id)
            q_internal.put(generated_text)
            turn += 1


        elif turn == 6: # user「n点（4個目に対して）」 temi「おけ、案内するわ（1個目）; これどう？」
            score = commonGPT.GPT_score_judge(input_prompt)
            print("score: " + str(score))
            f.write("score: " + str(score) + '\n')

            # スコアが上手く判定されなかった時の処理
            if score == -1 or score > 10:
                print("<greet_and_question>")
                generated_text = commonGPT.GPT_greet_and_question(input_prompt)
                generated_text = generated_text + ":picture:" + str(ask_id)
                q_internal.put(generated_text)
                return # スコアが上手く判定されなければ抜ける（turnは増えないのでもう一回聞かれる）
            
            predict.user_pref.append(score)
            recommend = predict.predict_finalpref()
            print(recommend)
            f.write("recommend: " + str(recommend) + '\n')
            
            commonGPT.conversation_history_tmp_reset() # 会話履歴を一旦消す
            print("<introduce_clothes>")
            generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
            print(1)
            generated_text = generated_text + ":move:" + str(recommend[0])
            print(2)
            q_internal.put(generated_text)
            print(3)
            turn += 1
            # webに画像を表示
            set_id(recommend[0])
            print(4)
            process_id()
            print(5)


        elif turn == 7: # user「適当な感想（1個目の案内に対して）」 temi「つぎ案内するわ（2個目）; これどう？」
            print("<introduce_clothes>")
            generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
            generated_text = generated_text + ":move:" + str(recommend[1])
            q_internal.put(generated_text)
            turn += 1
            # webに画像を表示
            set_id(recommend[1])
            process_id()


        elif turn == 8: # user「適当な感想（3個目の案内に対して）」 temi「つぎ案内するわ（3個目）; これどう？」
            print("<introduce_clothes>")
            generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
            generated_text = generated_text + ":move:" + str(recommend[2])
            q_internal.put(generated_text)
            turn += 1
            # webに画像を表示
            set_id(recommend[2])
            process_id()


        elif turn == 9: # user「適当な感想（3個目の案内に対して）」 temi「全体通してどうだった？」
            commonGPT.conversation_history_tmp_reset()

            print("<result>")
            generated_text = commonGPT.GPT_result(input_prompt)
            generated_text = generated_text + ":none"
            q_internal.put(generated_text)
            turn += 1


        elif turn == 10: # user「プラスの意見」 temi「よかったです」 OR  user「マイナスの意見」 temi「もう一個だけ案内するわ（4個目）; これどう？」
            result = commonGPT.GPT_reaction_judge(input_prompt)
            print("result: " + str(result))
            f.write("result: " + str(result) + '\n')
            
            commonGPT.conversation_history_tmp_reset()
            
            if result == 1: # 満足
                good = True # goodend
                print("<goodend>")
                generated_text = commonGPT.GPT_goodend(input_prompt)
                generated_text = generated_text + ":none"
                q_internal.put(generated_text)
                turn += 1
            if result == 0: # 不満
                print("<introduce_clothes_more>")
                generated_text = commonGPT.GPT_introduce_clothes_more(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
                generated_text = generated_text + ":move:" + str(recommend[3])
                q_internal.put(generated_text)
                turn += 1
                # webに画像を表示
                set_id(recommend[3])
                process_id()


        elif turn == 11 and good == False: # user「プラスの意見」 temi「よかったです」 OR  user「マイナスの意見」 temi「力になれんくて申し訳ない」
            result = commonGPT.GPT_reaction_judge(input_prompt)
            print("result: " + str(result))
            f.write("result: " + str(result) + '\n')

            commonGPT.conversation_history_tmp_reset()

            if result == 1: # 満足
                good = True # goodend
                print("<goodend>")
                generated_text = commonGPT.GPT_goodend(input_prompt)
                generated_text = generated_text + ":none"
                q_internal.put(generated_text)
                turn += 1
            if result == 0: # 不満
                bad = True
                print("<badend>")
                generated_text = commonGPT.GPT_badend(input_prompt)
                generated_text = generated_text + ":none"
                q_internal.put(generated_text)
                turn += 1


        else: # 終わった後
            print("<talk>")
            generated_text = commonGPT.GPT_talk(input_prompt)
            generated_text = generated_text + ":none"
            q_internal.put(generated_text)
            turn += 1

    #ここから
    print("[TURN: " + str(turn) + "]")

    if mode == True:
        socketio.emit('start_recognition')
    else:
        input_prompt = input("[YOU] ")

    if mode == True:
        input_prompt = q.get()  # データが入るまでブロックする

    if input_prompt: # input_prompt が取得できた場合のみ処理を続行
        input_prompt = common.text_modify(input_prompt) # 認識結果をreplace
        f.write("[YOU] " + input_prompt + '\n')
        q_internal = Queue()

        generating_text()
        
        # thread1 = threading.Thread(target=generating_text)
        # thread1.start() # スレッドの実行

        # backchannel = ['うーんと^', 'えーと']
        
        # y = random.uniform(1.5, 2)
        # while(thread1.is_alive()): # スレッドの実行が終わるまでループ
            # x = random.randint(0, 1)
            # y = 4
            # if mode == True:
            #     servermessege = ""
            #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #         # サーバを指定
            #         s.connect((common.ip, common.port))
            #         # 回答をpepperに送信
            #         s.sendall((backchannel[x]+':none'+'\r\n').encode())
            #         servermessege = s.recv(1024).decode()
            #     time.sleep(y)

        generated_text = q_internal.get()
        print("[GPT]", generated_text)
        f.write("[GPT] " + generated_text + '\n')

        if mode == True: # temiと通信を行う
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # サーバを指定
                s.connect((common.ip, common.port))
                # 回答をpepperに送信
                s.sendall((generated_text+'\r\n').encode())
                s.recv(1024).decode() # temiからOKサインが来るまで次の音声認識をはじめないようにしてる


# メインループを実行する関数
def run_main():
    global turn
    turn = 1
    with open('./log/log_'+ datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '_main.txt', mode='w') as f:
        while True:
            main(True, f)


#__main__内はグローバル変数
if __name__ == "__main__":

    turn = 1 # 会話ターン
    ask_id = -1 # 質問で使用
    recommend = [] # 好み推定結果を保存
    good = False # goodend
    bad = False # badend

    socketio.run(app, host='0.0.0.0', port=4999, allow_unsafe_werkzeug=True)
