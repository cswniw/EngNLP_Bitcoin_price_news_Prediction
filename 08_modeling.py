import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Embedding
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import *
import pickle

#### 테스트검증셋 불러오기
xy = np.load('np_saved/article_data_after_updown_ma30_max_1260_wordsize_20000.npy', allow_pickle=True)
X_train, X_test, Y_train, Y_test = xy
print(X_train.shape, Y_train.shape)
print(X_test.shape, Y_test.shape)


##### 모델 구조
model = Sequential()
model.add(Embedding(20000 + 1, 300,
                    input_length=1260))
model.add(Conv1D(64, kernel_size=11, padding="same",
                 activation="relu"))
model.add(MaxPool1D(pool_size=1))
model.add(LSTM(64, activation="tanh",
               return_sequences=True))
model.add(Flatten())
model.add(Dense(64, activation="relu"))
model.add(Dense(2, activation="sigmoid"))  # 분류할 레이블의 수. 3개 이상의 경우 softmax
print(model.summary())


es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=2)
### val_loss를 감시하여 patience 2를 줌. 2epochs에도 성능이 나아지지 않으면 중단.
mc = ModelCheckpoint('models/after_ma7/best_model.h5', monitor='val_accuracy',
                     mode='max', verbose=1, save_best_only=True)
### val_accuracy를 감시하여 최대 성능을 뽑아낸 epochs의 모델을 해당 경로에 저장한다.


model.compile(loss="categorical_crossentropy", optimizer="adam",
              metrics=["accuracy"])

fit_hist = model.fit(X_train, Y_train, batch_size=100, epochs=8,
                     callbacks=[es, mc],validation_data=(X_test,Y_test))
### callback으로 얼리스타밍과 체크포인트.

model.save("./models/article_classification_model_{}.h5".format(
    fit_hist.history["val_accuracy"][-1]))

plt.plot(fit_hist.history["accuracy"], label="accuracy")
plt.plot(fit_hist.history["val_accuracy"], label="val_accuracy")
plt.legend()
plt.show()


##### 이 프로젝트는 영문기사와 비트코인 가격의 상관관계를 알아보기 위한 것이었으나,
##### 현 데이터와 모델링 구조로는 유의미한 결과를 찾아낼 수 없었다.(가격기준,시간기준)
##### 이진 분류시 50프로, 3가지 분류시 40프로로 단순 확률값이 나옴.
##### 일단은 여기서 프로젝트를 중지한다.