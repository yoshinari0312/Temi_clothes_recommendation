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
        
        # 挨拶と質問
        if 1<= turn and turn < 6:
            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)

            if turn == 1:
                generated_text = generated_text + ":none"
            
            if 3 <= turn:
                score = commonGPT.GPT_score_judge(input_prompt)

                print("score: " + str(score))
                f.write("score: " + str(score) + '\n')

                if score == -1 or score > 10:
                    generated_text = generated_text + ":picture:" + str(ask_id)
                    q.put(generated_text)
                    return # スコアが上手く判定されなければ抜ける（turnは増えないのでもう一回聞かれる）
            

                predict.user_pref.append(score)

            if 2 <= turn:
                if turn == 2: # NMF_ASK
                    ask_id = predict.show_image(predict.candidate[0])

                if turn == 3: # NMF_ASK
                    ask_id = predict.show_image(predict.candidate[1])

                if turn == 4: # PREF_ASK
                    ask_id = predict.predict_pref_pre()

                if turn == 5: # PREF_ASK
                    ask_id = predict.predict_pref_pre()

                generated_text = generated_text + ":picture:" + str(ask_id)

            
        # 案内
        elif 6 <= turn and turn < 9:
            
            

            if turn == 6:
                score = commonGPT.GPT_score_judge(input_prompt)

                print("score: " + str(score))
                f.write("score: " + str(score) + '\n')

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

                
                print("<introduce_clothes>")
                
                if turn == 6:
                    commonGPT.conversation_history_tmp_reset()
                
                generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする

                generated_text = generated_text + ":move:" + str(recommend[0])
                common.set_id(recommend[0])
                common.process_id()

            if turn == 7:
                generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
                generated_text = generated_text + ":move:" + str(recommend[1])
                common.set_id(recommend[1])
                common.process_id()

            if turn == 8:
                generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
                generated_text = generated_text + ":move:" + str(recommend[2])
                common.set_id(recommend[2])
                common.process_id()


        # 感想
        elif turn == 9:
            commonGPT.conversation_history_tmp_reset()

            print("<result>")
            generated_text = commonGPT.GPT_result(input_prompt)
            generated_text = generated_text + ":none"

        # 感想の分岐
        elif turn == 10:
            commonGPT.conversation_history_tmp_reset()

            result = commonGPT.GPT_reaction_judge(input_prompt)
            print("result: " + str(result))
            f.write("result: " + str(result) + '\n')
            
            if result == 1: # 満足
                good = True # goodend
                print("<goodend>")
                generated_text = commonGPT.GPT_goodend(input_prompt)
                generated_text = generated_text + ":none"
            if result == 0: # 不満
                print("<introduce_clothes_more>")
                generated_text = commonGPT.GPT_introduce_clothes_more(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする
                generated_text = generated_text + ":move:" + str(recommend[3])
                
                common.set_id(recommend[3])
                common.process_id()

        # もう一回聞く
        elif turn == 11 and good == False:
            commonGPT.conversation_history_tmp_reset()

            result = commonGPT.GPT_reaction_judge(input_prompt)
            print("result: " + str(result))
            f.write("result: " + str(result) + '\n')

            if result == 1: # 満足
                good = True # goodend
                print("<goodend>")
                generated_text = commonGPT.GPT_goodend(input_prompt)
                generated_text = generated_text + ":none"
            if result == 0: # 不満
                bad = True
                print("<badend>")
                generated_text = commonGPT.GPT_badend(input_prompt)
                generated_text = generated_text + ":none"

        # 終わった後
        else:
            print("<talk>")
            generated_text = commonGPT.GPT_talk(input_prompt)
            generated_text = generated_text + ":none"


        turn += 1

        q.put(generated_text)


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

                servermessege = s.recv(1024).decode()



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