# -*- coding : UTF-8 -*-

# 0.ライブラリのインポートと変数定義
import socket

target_ip = "192.168.1.59"
target_port = 5540
buffer_size = 4096

# 1.ソケットオブジェクトの作成
tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2.サーバに接続
tcp_client.connect((target_ip,target_port))

# 3.サーバにデータを送信
tcp_client.send(b"Data by TCP Client!!")

# 4.サーバからのレスポンスを受信
response = tcp_client.recv(buffer_size)
print("[*]Received a response : {}".format(response))