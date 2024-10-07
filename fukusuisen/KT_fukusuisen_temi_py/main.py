import socket
import datetime
import common
import commonGPT
import predict
import threading
import time
from queue import Queue
import random


# メイン
def main(mode):

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
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            generated_text = generated_text + ":none"
            q.put(generated_text)
            turn += 1


        elif turn == 2: # user「おけい」 temi「これ何点？（1個目）」 # NMF_ASK
            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            ask_id = predict.show_image(predict.candidate[0])
            generated_text = generated_text + ":picture:" + str(ask_id)
            q.put(generated_text)
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
                q.put(generated_text)
                return # スコアが上手く判定されなければ抜ける（turnは増えないのでもう一回聞かれる）
        
            predict.user_pref.append(score)

            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            ask_id = predict.predict_pref_pre()
            generated_text = generated_text + ":picture:" + str(ask_id)
            q.put(generated_text)
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
                q.put(generated_text)
                return # スコアが上手く判定されなければ抜ける（turnは増えないのでもう一回聞かれる）
        
            predict.user_pref.append(score)

            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            ask_id = predict.predict_pref_pre()
            generated_text = generated_text + ":picture:" + str(ask_id)
            q.put(generated_text)
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
                q.put(generated_text)
                return # スコアが上手く判定されなければ抜ける（turnは増えないのでもう一回聞かれる）
        
            predict.user_pref.append(score)

            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            ask_id = predict.predict_pref_pre()
            generated_text = generated_text + ":picture:" + str(ask_id)
            q.put(generated_text)
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
                q.put(generated_text)
                return # スコアが上手く判定されなければ抜ける（turnは増えないのでもう一回聞かれる）
            
            predict.user_pref.append(score)
            recommend = predict.predict_finalpref()
            print(recommend)
            f.write("recommend: " + str(recommend) + '\n')
            
            commonGPT.conversation_history_tmp_reset() # 会話履歴を一旦消す
            print("<introduce_clothes>")
            generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
            generated_text = generated_text + ":move:" + str(recommend[0])
            q.put(generated_text)
            turn += 1
            # webに画像を表示
            common.set_id(recommend[0])
            common.process_id()


        elif turn == 7: # user「適当な感想（1個目の案内に対して）」 temi「つぎ案内するわ（2個目）; これどう？」
            print("<introduce_clothes>")
            generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
            generated_text = generated_text + ":move:" + str(recommend[1])
            q.put(generated_text)
            turn += 1
            # webに画像を表示
            common.set_id(recommend[1])
            common.process_id()


        elif turn == 8: # user「適当な感想（3個目の案内に対して）」 temi「つぎ案内するわ（3個目）; これどう？」
            print("<introduce_clothes>")
            generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
            generated_text = generated_text + ":move:" + str(recommend[2])
            q.put(generated_text)
            turn += 1
            # webに画像を表示
            common.set_id(recommend[2])
            common.process_id()


        elif turn == 9: # user「適当な感想（3個目の案内に対して）」 temi「全体通してどうだった？」
            commonGPT.conversation_history_tmp_reset()

            print("<result>")
            generated_text = commonGPT.GPT_result(input_prompt)
            generated_text = generated_text + ":none"
            q.put(generated_text)
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
                q.put(generated_text)
                turn += 1
            if result == 0: # 不満
                print("<introduce_clothes_more>")
                generated_text = commonGPT.GPT_introduce_clothes_more(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
                generated_text = generated_text + ":move:" + str(recommend[3])
                q.put(generated_text)
                turn += 1
                # webに画像を表示
                common.set_id(recommend[3])
                common.process_id()


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
                q.put(generated_text)
                turn += 1
            if result == 0: # 不満
                bad = True
                print("<badend>")
                generated_text = commonGPT.GPT_badend(input_prompt)
                generated_text = generated_text + ":none"
                q.put(generated_text)
                turn += 1


        else: # 終わった後
            print("<talk>")
            generated_text = commonGPT.GPT_talk(input_prompt)
            generated_text = generated_text + ":none"
            q.put(generated_text)
            turn += 1



    #ここから
    input_prompt = None
    print("[TURN: " + str(turn) + "]")

    if mode == True:
        input_prompt = common.record()
    else:
        input_prompt = input("[YOU] ")

    if input_prompt != None: # 入力があった場合
        input_prompt = common.text_modify(input_prompt)
        f.write("[YOU] " + input_prompt + '\n')
        q = Queue()

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

        generated_text = q.get()
        print("[GPT]", generated_text)
        f.write("[GPT] " + generated_text + '\n')

        if mode == True: # temiと通信を行う
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # サーバを指定
                s.connect((common.ip, common.port))
                # 回答をpepperに送信
                s.sendall((generated_text+'\r\n').encode())
                s.recv(1024).decode() # temiからOKサインが来るまで次の音声認識をはじめないようにしてる



#__main__内はグローバル変数
if __name__ == "__main__":

    turn = 1 # 会話ターン
    ask_id = -1 # 質問で使用
    recommend = [] # 好み推定結果を保存
    good = False # goodend
    bad = False # badend

    # f = 0
    with open('./log/log_'+ datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '_main.txt', mode='w') as f:
        while True:
            main(True)