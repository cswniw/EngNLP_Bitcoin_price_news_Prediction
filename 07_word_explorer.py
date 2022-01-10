
#################################### 토큰화된 영어 문장을 좀 더 자세히 들여다 보자


#################################  step 1. 원하는 데이터를 불러오기.
import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer

df = pd.read_csv('./coindesk_news/불러오기.csv')
df = df[['time','preprocessed_sentences','before_updown_yesterday','before_updown_ma7',
         'before_updown_ma30','after_updown_yesterday','after_updown_ma7','after_updown_ma30']]
### 위 설명. 대충 내가 원하는 컬럼을 불러옴.

df = df[['time','preprocessed_sentences','after_updown_ma30']]
### 기사 내용과 비트코인 레이블을 불러오기. time컬럼을 불러온 이유는 그냥 정렬을 위해서.
### 위의 after_updown_ma30컬럼 부분은 원하는 비트코인 정보 레이블을 불러온다.

df.dropna(inplace=True)
# 이동평균선을 구하는 과정에서 비트코인 가격 정보에 NaN이 반드시 있으므로 드롭시켜준다.
df.sort_values(by=['time'], ascending=True, ignore_index=True, inplace=True)
# 시간순으로 정렬~~
df.info()
print(df.head())

Y_column = 'after_updown_ma30'
# 위의 변수는 6개의 레이블마다 결과값을 따로 저장하기 위해 입력하기 위한 것으로 무시해도 좋다.


X = df['preprocessed_sentences']
# 토큰화된 기사 데이터
Y = df['after_updown_ma30']
# 비트코인 가격 정보 레이블

############################################## 데이터 불러오기 끝  ##################################

#################################  step 2. 정수 인코딩을 하면서 단어에 대한 정보를 알아보자.

token = Tokenizer()
token.fit_on_texts(X)
tokened_X = token.texts_to_sequences(X)

################################ tokened_X 의 최대 길이, 평균 길이, 표준편차 길이를 알아보자.

import matplotlib.pyplot as plt

print('기사의 최대 길이 : %d' % max(len(sample) for sample in tokened_X))
print('기사의 평균 길이 : %f' % (sum(map(len, tokened_X))/len(tokened_X)))
plt.hist([len(sample) for sample in X], bins=1000)
plt.xlabel('length of samples')
plt.ylabel('number of samples')
plt.show()

import numpy as np
len_tokened_X = [len(item) for item in tokened_X]

np_mean = np.mean(len_tokened_X)
np_std = np.std(len_tokened_X)
print('평균길이 :',np_mean)
print('표준편차 :', np_std)
print('6시그마 :', np_mean + (np_std*3))

### 평균 길이 약 400, 표준편차 약 300, 6시그마 : 1258.9743018860388
## 최대 길이 4800

##### 위의 작업을 통해 기사의 최대 길이와 평균 길이를 알 수 있다. 6시그마 룰을 적용하면
##### 패딩 작업 시 어느 정도의 길이까지만 써도 별 영향이 없을 지 알 수 있다..

##################################################################################################


############################################  등장 단어의 빈도수를 알아보자.

word_to_index = token.word_index   # 단어 집합의 딕셔너리.
# print(word_to_index)
threshold = 11    # 일단 확인하고픈 빈도수를 설
total_cnt = len(word_to_index) # 단어 집합의 수
rare_cnt = 0 # 등장 빈도수가 threshold보다 작은 단어의 개수를 카운트
total_freq = 0 # 훈련 데이터의 전체 단어 빈도수 총 합
rare_freq = 0 # 등장 빈도수가 threshold보다 작은 단어의 등장 빈도수의 총 합

for key, value in token.word_counts.items():
    total_freq = total_freq + value

    # 단어의 등장 빈도수가 threshold보다 작으면
    if(value < threshold):
        rare_cnt = rare_cnt + 1
        rare_freq = rare_freq + value

print('등장 빈도가 %s번 이하인 희귀 단어의 수: %s'%(threshold - 1, rare_cnt))
print("단어 집합(vocabulary)에서 희귀 단어의 비율:", (rare_cnt / total_cnt)*100)
print("전체 등장 빈도에서 희귀 단어 등장 빈도 비율:", (rare_freq / total_freq)*100)
vocab_size = len(word_to_index) + 1
print('단어 집합의 크기: {}'.format((vocab_size)))


# 단어 집합의 크기 : 75546
# 등장 빈도가 10번 이하인 희귀 단어의 수: 53695
# 단어 집합(vocabulary)에서 희귀 단어의 비율: 71.07684161757892
# 전체 등장 빈도에서 희귀 단어 등장 빈도 비율: 2.2698709028105664


# 위를 통해 빈도수 11번 이상인 약 20000개의 단어 집합만을 사용해도 유의미한 결과를 도출할 수 있을 것이다.

##################################################################################################


####################################################  step 3. 토크나이저 재정의

# 이제 토큰화된 단어의 정보를 알았으니 유의미한 부분만 사용해서 정수 인코딩을 한다.

total_vocab_size = 75546
wanted_vocab_size = 20000   # 등장 빈도 상위 20000개만 쓸것이다.

token = Tokenizer(num_words= wanted_vocab_size + 1, oov_token = 'OOV')
# num_words=숫자+1   : 등장 빈도 상위 단어 수,   플러스1은 패딩값을 위해 ,
# oov_token은 20000개에 들지 못한 단어들은 'OOV'값으로 처리한다. 정수 인코딩 시 0이 부여된다.

token.fit_on_texts(X)
tokened_X = token.texts_to_sequences(X)

from tensorflow.keras.preprocessing.sequence import pad_sequences

max_len = 1260
### 6시그마 : 1258.9743018860388

X_pad = pad_sequences(tokened_X, maxlen = max_len)
## 최대 길이 4800개를 모두 넣는 것은 무의미 하니 패딩 시퀀스의 길이는 1260으로 제한한다.

print("훈련 데이터의 크기(shape):", X_pad.shape)


#################      이로써 기사 내용의 인코딩 작업 완료.
##############################################################################################################



###########################################    step 4. 비트코인 가격 레이블 엔코딩

from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder

encoder = LabelEncoder()
labeled_Y = encoder.fit_transform(Y)
label = encoder.classes_
print(labeled_Y[0])
print(label)
import pickle
with open("./models/encoder/encoder_{}.pickle".format(Y_column), "wb") as f:
    pickle.dump(encoder, f)   # 엔코더 저장.
onehot_Y = to_categorical(labeled_Y)   # 원핫 엔코딩.
print(onehot_Y)

###########################################################################################


##############################################  step 5.    훈련 검증용 데이터 나누자.
from sklearn.model_selection import train_test_split

X_train, X_test, Y_train, Y_test = train_test_split(X_pad, onehot_Y, test_size=0.2, stratify=onehot_Y)
# stratify에 레이블을 부여하면 레이블의 분포를 고려해 균등하게 테스트검증셋을 나눠준다.

print(X_train.shape, Y_train.shape)
print(X_test.shape, Y_test.shape)
xy = X_train, X_test, Y_train, Y_test

np.save("./np_saved/article_data_{}_max_{}_wordsize_{}".format(Y_column, max_len, wanted_vocab_size), xy)
## 모델링 작업을 위해 세이브한다.