#! /bin/bash
python3 display_main.py &

sleep 10
#!/bin/bash

# # WebサーバのIPアドレス
# WEB_SERVER_IP="192.168.1.26:4999"

# # タイムアウトを設定（秒）
# TIMEOUT=2

# # サーバステータスチェック
# curl --connect-timeout $TIMEOUT -s $WEB_SERVER_IP > /dev/null

# while [ $? -ne 0 ]; do
#     echo "Webサーバが稼働していません。"
#     sleep 1
# done
python3 display1.py &
python3 display2.py &
python3 display3.py &
python3 coordinates.py &

