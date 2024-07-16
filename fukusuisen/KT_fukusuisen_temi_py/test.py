import predict
import socket
import common

# ask_id = predict.show_image(predict.candidate[0])
# print(ask_id)
# predict.main()

# list = [1,2,3]

# print(str(list))


ip = "192.168.1.64"
port = 5530


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# サーバを指定
s.connect((common.ip, common.port))
# 回答をpepperに送信
s.sendall((generated_text+'\r\n').encode())

servermessege = s.recv(1024).decode()
