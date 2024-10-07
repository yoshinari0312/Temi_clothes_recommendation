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
SEED = 0

# NMFで特徴の強いのをいくつ聞くか
NMF_ASK = 2
# ユーザの好みのをいくつ聞くか(NMF_ASK+PREF_ASK回の質問をする)
PREF_ASK = 2

def set_seed(seed):
	SEED = seed
	random.seed(SEED)

def show_image(id):
	ask_image = cv2.imread(f"images/{id}.jpg")
	cv2.imshow(f"image_{id}", ask_image)
	cv2.waitKey(300)
	return id

def user_ask(id):
	pref = input(f"input preference of {id} (0-10):")
	pref = int(pref)
	return pref

def predict_pref_pre():
	lasso = sklearn.linear_model.Lasso()
	x_train = train[candidate]
	y_train = train.drop(candidate, axis=1)
	column_names = y_train.columns

	lasso.fit(x_train, y_train)
	x_test = np.array([user_pref])

	y_pred = lasso.predict(x_test)

	pref_predict = y_pred[0].argsort()[::-1]

# 	ask_id = y_train.columns[pref_predict[0]]
	#N番目に好みそうなのは，y_train.columns[pref_predict[N]]で表せる

	train_cov = train.cov()

	user_cov = []
	for j in range(100):
		if j+1 in candidate:
			continue
		user_cov.append((j+1, train_cov[candidate[-1]].iloc[j]))

	user_cov.sort(key=lambda x:x[1])

	ask_id = user_cov[0][0]

	candidate.append(ask_id)
	show_image(ask_id)
	
	return ask_id

def predict_pref(ask_id):
	score = user_ask(ask_id)
	user_pref.append(score)

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
	# print("1st:", final_id, y_pred[0][pref_predict[0]])
	# print("2nd:", y_train.columns[pref_predict[1]], y_pred[0][pref_predict[1]])
	# print("3rd:", y_train.columns[pref_predict[2]], y_pred[0][pref_predict[2]])
	# print("4th:", y_train.columns[pref_predict[3]], y_pred[0][pref_predict[3]])
	# print("5th:", y_train.columns[pref_predict[4]], y_pred[0][pref_predict[4]])

	# 最も好む服
	final_image = cv2.imread(f"images/{final_id}.jpg")
	cv2.imshow(f"image_{final_id}", final_image)
	cv2.waitKey(300)

# 	return [77,69,71,50] #(A)
	return [final_id, y_train.columns[pref_predict[1]], y_train.columns[pref_predict[2]], y_train.columns[pref_predict[3]], y_train.columns[pref_predict[4]]]



set_seed(SEED)

data = pd.read_csv("all_data.csv")
data = data.drop("No", axis=1)
data = data.set_axis(list(range(1,101)), axis=1)

train, test = train_test_split(data, test_size=130, random_state=0) #ここはseed0固定
test_data = np.array(test).flatten()

nmf = sklearn.decomposition.NMF(n_components=10, random_state=SEED)
W = nmf.fit_transform(train.T)

#NMFで最も特徴の強いのを聞く
# candidate = list(np.ndarray.argmax(W, axis=0))[:NMF_ASK]

candidate = [50]

# ゲテモノ*2, 人気*1
# candidate = [74,56,50]
# candidate = [74,56]

user_pref = []


def main():
	for i in range(NMF_ASK):
		show_image(candidate[i])
		user_pref.append(user_ask(candidate[i]))

	for i in range(PREF_ASK):
		ask_id = predict_pref_pre()
		predict_pref(ask_id)

	predict_finalpref()

