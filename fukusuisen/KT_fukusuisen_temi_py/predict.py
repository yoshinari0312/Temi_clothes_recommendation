import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
import random
import numpy as np
from collections import Counter
import cv2

#seed決定
SEED = random.randint(0, 10**9)
# SEED = 1

# NMFで特徴の強いのをいくつ聞くか
NMF_ASK = 3
# ユーザの好みのをいくつ聞くか(NMF_ASK+PREF_ASK回の質問をする)
PREF_ASK = 3

def set_seed(seed):
	SEED = seed
	random.seed(SEED)

def user_ask(id):
	ask_image = cv2.imread(f"images/{id}.jpg")
	cv2.imshow(f"image_{id}", ask_image)
	cv2.waitKey(300)
	pref = input(f"input preference of {id} (0-10):")
	pref = int(pref)
	return pref

def predict_finalpref():
	lasso = sklearn.linear_model.Lasso()
	x_train = train[candidate]
	y_train = train.drop(candidate, axis=1)
	column_names = y_train.columns

	lasso.fit(x_train, y_train)
	x_test = np.array([user_pref])

	y_pred = lasso.predict(x_test)

	pref_predict = y_pred[0].argsort()[::-1]
	final_id = y_train.columns[pref_predict[0]]

	# 好み1～5位
	print("1st:", final_id, y_pred[0][pref_predict[0]])
	print("2nd:", y_train.columns[pref_predict[1]], y_pred[0][pref_predict[1]])
	print("3rd:", y_train.columns[pref_predict[2]], y_pred[0][pref_predict[2]])
	print("4th:", y_train.columns[pref_predict[3]], y_pred[0][pref_predict[3]])
	print("5th:", y_train.columns[pref_predict[4]], y_pred[0][pref_predict[4]])

	# 最も好む服
	final_image = cv2.imread(f"images/{final_id}.jpg")
	cv2.imshow(f"image_{final_id}", final_image)
	cv2.waitKey(10000)

def predict_pref():
	lasso = sklearn.linear_model.Lasso()
	x_train = train[candidate]
	y_train = train.drop(candidate, axis=1)
	column_names = y_train.columns

	lasso.fit(x_train, y_train)
	x_test = np.array([user_pref])

	y_pred = lasso.predict(x_test)

	pref_predict = y_pred[0].argsort()[::-1]

	ask_id = y_train.columns[pref_predict[0]]
	#N番目に好みそうなのは，y_train.columns[pref_predict[N]]で表せる

	candidate.append(ask_id)
	score = user_ask(ask_id)
	user_pref.append(score)


set_seed(SEED)

data = pd.read_csv("all_data.csv")
data = data.drop("No", axis=1)
data = data.set_axis(list(range(1,101)), axis=1)

train, test = train_test_split(data, test_size=130, random_state=0) #ここはseed0固定
test_data = np.array(test).flatten()

nmf = sklearn.decomposition.NMF(n_components=10, random_state=SEED)
W = nmf.fit_transform(train.T)

#NMFで最も特徴の強いのを聞く
candidate = list(np.ndarray.argmax(W, axis=0))[:NMF_ASK]

# ゲテモノ*2, 人気*1
# candidate = [74,56,50]

user_pref = []

for i in range(NMF_ASK):
	user_pref.append(user_ask(candidate[i]))

for i in range(PREF_ASK):
	predict_pref()

predict_finalpref()