###########################################  (번외 정보)   #########################################
import pybithumb    # 비트코인 거래소 빗썸의 코인 정보를 얻을 수 있는 모듈
import time
import pandas as pd

tickers = pybithumb.get_tickers()    # 티커들 소환
print(tickers) # 정보를 불러올 수 있는 코인들의 티커 리스트 출력
for i in tickers[0:1] :    # 티커들 100개 이상이지만 가장 첫번쨰 요소인 비트코인의 티커만 부르자. ex)BTC
    time.sleep(1)     # 중요!! 1초에 10번 이상 불러오기하면 빗썸측에서 디도스로 간주.. 차단시켜버림. 그래서 time sleep을 준다.
    btc = pybithumb.get_ohlcv('{}'.format(i))   # get_ohlcv 함수는 해당 티커의 가격 정보를 리턴.
print(btc) # 날짜, 종가,시가,고가,저가,거래량  정보가 출력.
df = pd.DataFrame(btc)
df.info()
##### 이외의 정보는 구글링. pybithumb외에도 yahoo finance도 비슷한 모듈이 있으니 구글링.

##### 중요중요!!! 플랫폼이 제공하는 정보는 오로지 해당 플랫폼의 정보이다. 플랫폼의 거래 중지, 영업 중단 등의 사유로 인해
##### 결측치가 존재하기 마련이니 반드시 확인할 것. 또한 종가, 시가 등 가격 정보 선언 시간대를 반드시 확인하길 바람.

##### 코인은 24시간 연중무휴 거래인데, 빗썸 가격정보는 결측 날짜가 확인됨. 아래의 코드로 확인함.
##### 2014년 부터 현재까지 비교해봄.
years = ['2014','2015','2016','2017','2018','2019','2020','2021']
months = ['01','02','03','04','05','06','07','08','09','10','11','12']
day = range(1,32)  # 1일1부터 31일까지
for i in years :
    for j in months :
        for k in day :
            k = '%02d' % k   # 한자리 수는 앞에 0을 붙여줌.
            if '{}-{}-{}'.format(i,j,k) not in df['time'].unique() :  # 해당 날짜가 데이터에 없으면 표기.
                print('{}-{}-{}'.format(i,j,k))

###################################################################################################

################################ 본편. 비트코인 가격 데이터는 인베스팅닷컴에서 다운로드함. 결측치 없음  #########

##### 비트코인 가겨의 날짜 데이터 타입을 timestamp 한다.

import pandas as pd
df = pd.read_csv('./datasets/Bitcoin.csv')    # 비트코인 데이터 csv파일 경로 확인.
df.info()
to_time = []
for i in df['날짜'] :    # 예시) 2021년 12월 25일   ~> 2021-12-25  로 바꾸자.
    time = '{}-{}-{}'.format(i[:4],i[6:8],i[10:12])
    pd.to_datetime(time)
    to_time.append(time)
df['날짜'] = to_time
df['time'] = pd.to_datetime(df["날짜"])     # 컬럼명도 왠만하면 영어로 맞추자.

##### 종가 데이터의 타입이 숫자가 아니라 문자열 타입이니 바꿔주자. ex) 500,000  <~ 이 경우 , 도 문자이니 제거한다.

to_int = []
for i in df['종가'] :
    i = i.replace(',','')    # , 제거
    i = float(i)            # int든 float든 아무거자 숫자 타입으로 변경.
    to_int.append(i)
df['close'] = to_int      # 컬럼명을 영어로 바꿔준다.

##### 데이터 컬럼  합치기 /// 당장 필요한 것은 날짜와 종가 데이터뿐.
df = df.loc[:,['time','close']]
df.to_csv('./datasets/bitcoin_data.csv', index=False)   # 저장.
print(df.info())

##################################################################################################

####################################### 지금부터 비트코인 가격 데이터를 가공해보자.

#######################################        step 1. 이동평균선 구하기

df = pd.read_csv('./datasets/Bitcoin.csv')
df.sort_values(by='time', inplace=True)  # 시간 순 정렬
##### 주의!! 반드시 시간 순으로 정렬해야한다. 이동평균선은 과거 일자의 데이터의 평균값이니,
##### 정렬이 최근순으로 된다면 미래 데이터로 평균을 구하는 셈이 된다.

close = df['종가']     # close 변수명으로 종가 데이터를 받음.
window = close.rolling(7)  # rolling(숫자) 컬럼을 해당 숫자만큼 묶어준다.   예시) df['종가']의 1행~7행, 2행~8행, 3행~9행
ma7 = window.mean()         # mean()은 숫자만큼 묶여진 컬럼들의 평균값
df['ma7'] = ma7     # 새로운 컬럼으로 선언해주면, 이동평균선 정보를 담은 데이터 프레임이 생긴다.
df.to_csv('./datasets/Bitcoin.csv', index=False)

##### 중요.. 중요..
## 예시) df['종가']의 1행~7행의 가격 정보의 평균값은  df['ma7']의 7행이 입력된다. 따라서 df['ma7']의 1~6행은 NaN값이 된다.
## 이유는 rolling(7)에서 7개 미만으로 묶였기 때문이다.


#######################################   step 2. 종가와 가공된 가격정보 비교를 통해 상승 하락 횡보장 구분.

import pandas as pd
import numpy as np
df = pd.read_csv('./datasets/Bitcoin.csv')
df.sort_values(by=['time'], ascending=True, ignore_index=True, inplace=True)  ## 날짜 정보가 중요하니 날짜 컬럼으로 정렬.
df = df[['time','종가','ma7','ma30']]   ### (step 1)과 같은 작업으로 이동평균선 7일과 30일 가격을 구함.


##### 전날 종가대비 상승 하락 레이블 부여.

df['updown_on_yesterday'] = np.nan
# 전날 종가대비 경우 첫 행은 전날 종가 데이터가 없으니 NaN처리를 위해 그냥 데이터프레임 전체에 NaN 선언. 상승 하락 정보를 담을 데이터 프레임.
for i in range(1, len(df)) :   # 인덱싱1번부터 시작.
    try : # try,except문으로 혹시 모를 에러에 대비.
        if df['종가'][i] > df['종가'][i-1] :      # 예시) 1행 종가(당일)가 0행 종가(전날)보다 크면 'bull', 작거나 같으면 'bear'
            df['updown_on_yesterday'][i-1] = 'bull'

            ### 코인 기사가 가격 정보에 미치는 영향을 알아보기 위함이니.. 상승하락의 레이블은 전날 기사 데이터 프레임의 행과 일치시킨다.
            ### 예시) 데이터프레임의 행은  당일 기사 정보와 다음날 코인 가격 정보의 레이블을 담아야 한다.
            ### 코인 기사의 비트코인 가격 영향의 선행 후행 관계를 알아보기 위해 레이블을 여러개 만들었다.

            ### 예시) df['updown_on_yesterday'][i-1] = 'bull' 의 경우 선행 관계를 알아보기 위해
            ### 예시) df['updown_on_yesterday'][i] = 'bull'   의 경우 후행 관계를 알아보기 위함.

        else :
            df['updown_on_yesterday'][i-1] = 'bear'
    except :
        pass

##### 7일 이동평균선 대비 상승 하락 레이블 부여.

df['updown_ma7'] = np.nan   # 상동.
for i in range(1, len(df)) :
    try :
        if df['종가'][i] > df['ma7'][i-1] :    # 당일 종가가 전날 7일 이평선 보다 크면 bull, 작거나 같으면 bear
            df['updown_ma7'][i-1] = 'bull'

        elif df['종가'][i] <= df['ma7'][i-1] :
            df['updown_ma7'][i-1] = 'bear'
    except :
        pass

##### 30일 이동평균선 대비 상승 횡보 하락 레이블 부여.  3가지로 분류

df['updown_ma30'] = np.nan
for i in range(1, len(df)):
    rate = ((df['종가'][i] - df['ma30'][i - 1]) / df['ma30'][i - 1]) * 100
    # 가격 변화률, 현재 종가가 30일 이평선 위인지 아래인지 판단.
    try:
        if rate >= 5:    # 5퍼센트 이상 상승 시 bull
            df['updown_ma30'][i-1] = 'bull'

        elif rate <= - 5:       # 5퍼센트 이상 하락 시 bear
            df['updown_ma30'][i-1] = 'bear'

        elif -5 < rate < 5:         #  플러스마이너스 5퍼센트 이내 움직임 시 횡보장으로 판단.
            df['updown_ma30'][i-1] = 'neut'

    except:
        pass

##### 각각 가격 정보의 가공이 끝나면 벨류값 분포를 확인하기 위해 그래프를 보자.
##### 레이블의 분포가 균등하게 분포해야 데이터셋 몰림 현상을 방지한다.

import matplotlib.pyplot as plt

df['updown_ma30'].value_counts().plot(kind='bar')
# 확인하기 원하는 컬럼값 입력,   bar 챠트로 확인...
plt.show()
# 확인이 끝나면 저장~~
df.to_csv('./datasets/Bitcoin_6_before.csv', index=False)

##################################################################################

##### 중요중요... 위의 코드를 통해  시간 기준, 가격 기준으로 레이블을 나누었다 총 여섯 컬럼의 레이블

##### 전날 종가대비 상승 하락 여부(선행), 전날 종가대비 상승 하락 여부(후행)      # 이진 분류 또는 2개 카테고리
##### 7일 이평선 상승 하락 여부(선행), 7일 이평선 상승 하락 여부(후행)               # 이진 분류 또는 2개 카테고리
##### 30일 이평선 횡보 상승 하락 여부(선행), 7일 이평선 횡보 상승 하락 여부(후행)    # 3개 카테고리











