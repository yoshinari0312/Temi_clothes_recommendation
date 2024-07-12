import socket
import datetime
import common
import commonGPT
import threading
import time
from queue import Queue
import random


# メイン
def main(mode):

    def generating_text():
        global turn
        global recommend
        global good
        global bad
        


        generated_text = ""
        score = -1
        result = -1
        
        # 挨拶と質問
        if 1<= turn and turn < 5:
            print("<greet_and_question>")
            generated_text = commonGPT.GPT_greet_and_question(input_prompt)
            
            if 2<= turn:

                '''
                画像を送る
                '''
            
            if 3 <= turn:
                score = commonGPT.GPT_score_judge(input_prompt)
                print("score: " + str(score))
                f.write("score: " + str(score) + '\n')

                '''
                predictにスコアを入れる
                '''

        # 案内
        elif 5<= turn and turn < 8:
            if turn == 5:
                commonGPT.conversation_history_tmp_reset()

            print("<introduce_clothes>")
            generated_text = commonGPT.GPT_introduce_clothes(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする

            if turn == 5:
                score = commonGPT.GPT_score_judge(input_prompt)
                print("score: " + str(score))
                f.write("score: " + str(score) + '\n')

                '''
                predictにスコアを入れる
                '''
                '''
                好み推定
                recommendに保存
                '''

        # 感想
        elif turn == 8:
            commonGPT.conversation_history_tmp_reset()

            print("<result>")
            generated_text = commonGPT.GPT_result(input_prompt)

        # 感想の分岐
        elif turn == 9:
            commonGPT.conversation_history_tmp_reset()

            result = commonGPT.GPT_reaction_judge(input_prompt)
            print("result: " + str(result))
            f.write("result: " + str(result) + '\n')
            
            if result == 1: # 満足
                good = True # goodend
                print("<goodend>")
                generated_text = commonGPT.GPT_goodend(input_prompt)
            if result == 0: # 不満
                print("<introduce_clothes_more>")
                generated_text = commonGPT.GPT_introduce_clothes_more(input_prompt) # | はここに移動を挟むことを表す。javaの方でsplitする

        # もう一回聞く
        elif turn == 10 and good == False:
            commonGPT.conversation_history_tmp_reset()

            result = commonGPT.GPT_reaction_judge(input_prompt)
            print("result: " + str(result))
            f.write("result: " + str(result) + '\n')

            if result == 1: # 満足
                good = True # goodend
                print("<goodend>")
                generated_text = commonGPT.GPT_goodend(input_prompt)
            if result == 0: # 不満
                bad = True
                print("<badend>")
                generated_text = commonGPT.GPT_badend(input_prompt)

        # 終わった後
        else:
            print("<talk>")
            generated_text = commonGPT.GPT_talk(input_prompt)


        turn += 1

        q.put(generated_text)


    input_prompt = None

        

    print("[TURN: " + str(turn) + "]")

    if mode == True:
        input_prompt = common.record()
    else:
        input_prompt = input("[YOU] ")

    if input_prompt != None: # 入力があった場合
        f.write("[YOU] " + input_prompt + '\n')
        q = Queue()
        thread1 = threading.Thread(target=generating_text)
        thread1.start() # スレッドの実行

        backchannel = ['うーんと^', 'えーと']
        
        # y = random.uniform(1.5, 2)
        while(thread1.is_alive()): # スレッドの実行が終わるまでループ
            x = random.randint(0, 1)
            y = 4
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
        commonGPT.one_round = True
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
    recommend = [] # 好み推定結果を保存
    good = False # goodend
    bad = False # badend

    # f = 0
    with open('./log/log_'+ datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '_main.txt', mode='w') as f:
        while True:
            main(False)