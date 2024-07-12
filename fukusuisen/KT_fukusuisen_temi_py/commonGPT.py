import os
from openai import OpenAI
import random

# OpenAI key
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
conversation_history = [] # 会話履歴を格納するためのリストを初期化
conversation_history_tmp = [] # 会話履歴を格納するためのリスト（定期的にリセットする）


# conversation_history_tmpのリセット
def conversation_history_tmp_reset():
    conversation_history_tmp.clear()
    return


# 挨拶と質問
def GPT_greet_and_question(prompt):

    # ユーザーの質問を会話履歴に追加
    conversation_history.append({"role": "user", "content": prompt})
    conversation_history_tmp.append({"role": "user", "content": prompt})
    
    # GPT-4モデルを使用してテキストを生成
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {
            "role": "system",
            "content": "・あなたは服推薦ロボットのtemiです。\n\
                        ・50文字以内で話してください。\n\
                        ・会話の始めに自己紹介をし、これから見せる服を10点満点で評価するようuserに話してください。\n\
                        ・ただし、質問や雑談には適宜回答してください。\n\
                        ・服は3回見せます。\n\n\
                        ＜会話例＞\n\
                        user「こんにちは。」\n\
                        temi「こんにちは、私は服推薦ロボットのtemiです。今からいくつか服を見せるので、10点満点で評価してください。」\n\
                        user「わかりました。」\n\
                        temi「こちらは何点ですか？」\n\
                        user「5点かな。」\n\
                        temi「ふむふむ、ではこちらは？」\n\
                        user「8点。」\n\
                        temi「なるほど、ではこちらはいかがでしょう？」\n\
                        user「7点だな。」"
        }] + conversation_history_tmp,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = response.choices[0].message.content.strip()
    
    # アシスタントの回答を会話履歴に追加
    conversation_history.append({"role": "assistant", "content": message})
    conversation_history_tmp.append({"role": "assistant", "content": message})
    
    return message

# 案内
def GPT_introduce_clothes(prompt):

    # ユーザーの質問を会話履歴に追加
    conversation_history.append({"role": "user", "content": prompt})
    conversation_history_tmp.append({"role": "user", "content": prompt})

    # GPT-4モデルを使用してテキストを生成
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {
            "role": "system",
            "content": "・あなたは服推薦ロボットのtemiです。\n\
                        ・50文字以内で話してください。\n\
                        ・おすすめの服まで案内することを伝えた後、|と出力し、続いて服の感想を尋ねてください。\n\
                        ・3回くりかえしてください。\n\n\
                        ＜会話例＞\n\
                        user「8点。」\n\
                        temi「ありがとうございます。ではおすすめの服まで案内します。|こちらはいかがでしょうか？」\n\
                        user「結構いいね。」\n\
                        temi「続いて他のも案内します。|こちらはどうでしょう？」\n\
                        user「これもいいね。」\n\
                        temi「もう一つ案内します。|こちらはいかがでしょう？」\n\
                        user「これはまあまあかな。」"
        }] + conversation_history_tmp,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = response.choices[0].message.content.strip()
    
    # アシスタントの回答を会話履歴に追加
    conversation_history.append({"role": "assistant", "content": message})
    conversation_history_tmp.append({"role": "assistant", "content": message})
    
    return message

# 感想を聞く
def GPT_result(prompt):
    thanks_list = ['お好みの服はありましたか？', 'お好みの服はございましたか？']
    x = random.randint(0, len(thanks_list)-1)
    message = thanks_list[x]

    conversation_history.append({"role": "user", "content": prompt})
    conversation_history_tmp.append({"role": "user", "content": prompt})
    conversation_history.append({"role": "assistant", "content": message})
    conversation_history_tmp.append({"role": "assistant", "content": message})

    return message

# 気に入ったのがあれば
def GPT_goodend(prompt):
    thanks_list = ['気に入っていただけたら何よりです。また何かございましたらお気軽にお申し付けください。', 'お気に召したのなら幸いです。また何かございましたらお気軽にお申し付けください。']
    x = random.randint(0, len(thanks_list)-1)
    message = thanks_list[x]

    conversation_history.append({"role": "user", "content": prompt})
    conversation_history_tmp.append({"role": "user", "content": prompt})
    conversation_history.append({"role": "assistant", "content": message})
    conversation_history_tmp.append({"role": "assistant", "content": message})

    return message

# 気に入ったのがなければもう一個追加で案内
def GPT_introduce_clothes_more(prompt):

    # ユーザーの質問を会話履歴に追加
    conversation_history.append({"role": "user", "content": prompt})
    conversation_history_tmp.append({"role": "user", "content": prompt})
    
    # GPT-4モデルを使用してテキストを生成
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {
            "role": "system",
            "content": "・あなたは服推薦ロボットのtemiです。\n\
                        ・50文字以内で話してください。\n\
                        ・追加でもう一個おすすめの服まで案内することを伝えた後、|と出力し、続いて服の感想を尋ねてください。\n\
                        ・ただし、質問や雑談には適宜回答してください。\n\n\
                        ＜会話例＞\n\
                        user「どれもあんまりかな。」\n\
                        temi「そうですか、ではもう一つだけ案内させてください。|こちらはいかがでしょうか？」"
        }] + conversation_history_tmp,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = response.choices[0].message.content.strip()
    
    # アシスタントの回答を会話履歴に追加
    conversation_history.append({"role": "assistant", "content": message})
    conversation_history_tmp.append({"role": "assistant", "content": message})
    
    return message

# 追加で案内してもダメだったら
def GPT_badend(prompt):
    thanks_list = ['お力になれず申し訳ございません。また何かございましたらお気軽にお申し付けください。', 'お力添えできず申し訳ございません。また何かございましたらお気軽にお申し付けください。']
    x = random.randint(0, len(thanks_list)-1)
    message = thanks_list[x]

    conversation_history.append({"role": "user", "content": prompt})
    conversation_history_tmp.append({"role": "user", "content": prompt})
    conversation_history.append({"role": "assistant", "content": message})
    conversation_history_tmp.append({"role": "assistant", "content": message})

    return message

# エンディング後の会話は全てここで処理
def GPT_talk(prompt):

    # ユーザーの質問を会話履歴に追加
    conversation_history.append({"role": "user", "content": prompt})
    conversation_history_tmp.append({"role": "user", "content": prompt})
    
    # GPT-4モデルを使用してテキストを生成
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {
            "role": "system",
            "content": "・あなたは服推薦ロボットのtemiです。\n\
                        ・50文字以内で話してください。"
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
    conversation_history_tmp.append({"role": "assistant", "content": message})
    
    return message


# userの点数を抽出
def GPT_score_judge(prompt):

    content = "・userが何点と言っているか答えてください。\n\
                ・半角数字のみで回答してください。"

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {
            "role": "system",
            "content": content
        },
        {
            "role": "user",
            "content": prompt
        }],
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = response.choices[0].message.content.strip()
    
    e = int(message)

    return e

# userの感想を数値化
def GPT_reaction_judge(prompt):

    content = "・userが不満に思っているかどうかをを0か1で評価してください。\n\
                ・0が不満に思っている、1が満足しているです。\n\
                ・半角数字のみで回答してください。\n\n\
                ＜例＞\n\
                user「よかったよ」 -> 1\n\
                user「最初のかな」 -> 1\n\
                user「2つ目」 -> 1\n\
                user「3つ目のやつ」 -> 1\n\
                user「まあまあ」 -> 0\n\
                user「微妙」 -> 0\n\
                user「特にない」 -> 0\n\
                user「あんまり」 -> 0"

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {
            "role": "system",
            "content": content
        },
        {
            "role": "user",
            "content": prompt
        }],
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    message = response.choices[0].message.content.strip()
    
    e = int(message)

    return e

