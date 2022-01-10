import pandas as pd

############################## 크롤링 데이터 작업 결과물을 1개의 csv 파일로 합치자.

############################## (번외)  코인 데스크 크롤링 작업 시 실패한 url 주소를 담은 csv 파일들을 하나로 합치자. ####

import pandas as pd
import glob
data_paths = glob.glob('./coindesk_news/failed/failed_url*.csv')
# 해당 경로의 해당 조건명을 가진 파일의 경로를 리스트로 리턴하여 data_paths 변수명으로 선언.

df = pd.DataFrame()  # 빈 데이터 프레임을 만들어준다.
for data_path in data_paths :
    df_temp = pd.read_csv(data_path)  # 각 파일의 경로를 불러와 df_temp로 데이터프레임화 한다.
    df = pd.concat([df,df_temp], ignore_index=True)  # for문 사용. df로 계속 concat 작업. 인덱스는 무시하자.
df.drop_duplicates(inplace=True)  # 혹시 모를 중복을 위해 중복제거 작업.
df.info()


#### 이하 특정 조건의 url 주소를 걸러주는 작업.

wanted = []   # 크롤링 수집에 재도전할 url주소를 저장할 리스트.
for i in df['failed_url'] :
    try :
        if 'www.coindesk.com/podcasts/' not in i:   # 이 경우 url주소에 podcasts 가 있으면 거른다. 해당 주소는 영상만 있다.
            wanted.append(i)
    except : pass
df_2 = pd.DataFrame(wanted)    # 크롤링 수집에 재도전할 url주소를 데이터 프레임화. 추후 왜 크롤링에 실패했는지 파악하기 위함.
df_2.info()
import pickle
with open('../coindesk_news/failed/cleaned_failed_url.pickle', 'wb') as f :
    pickle.dump(wanted, f)     # 또는 피클로 담궈버릴수도있다.




################################################### 메인작업))) 수집한 크롤링 데이터를 concat하면서 간단한 전처리도 하자.

######  concat 작업
import pandas as pd
import glob

data_paths = glob.glob('./coindesk_news/코인데스크 뉴스기/coin_news_*.csv')

df = pd.DataFrame()

for data_path in data_paths :
    df_temp = pd.read_csv(data_path)
    df = pd.concat([df,df_temp], ignore_index=True)
df.info()
df.drop_duplicates(inplace=True)

###### 날짜 데이터 타입을 object에서 timestamp하자.  날짜 계산 또는 시계열 분석을 위해 미리 전처리한다.

from datetime import datetime
import re

times = []    # 가공할 데이터를 저장할 리스트
for i in df['date'] :    # 해당 컬럼을 for문으로 조회.
    try :   # try,except문으로 혹시 모를 에러에 대비한다.
        text = i.replace(',','')
        # 예시) raw_data : Dec, 25 2021 06:00:00
        text = text.split()
        # 공백으로 나누어 리스트화 시킨다.
        text = text[:3]
        # 예시) ['Dec', '25', '2021']    시간은 필요없다. 필요한 건 날짜
        text = ' '.join(text)
        # 다시 str 타입으로 바꿔줌.
        time = datetime.strptime(text, '%b %d %Y').strftime('%Y-%m-%d')
        # 예시) Dec 25 2021 형식의 날짜를 2021-12-25로 바꾼다.
        times.append(time)
        # 바꿨으면 리스트에 저장.
    except:
        times.append(i)
        # try문의 에러로 실패하면 일단 저장하고 나중에 확인해본다.

df['time'] = times   # 데이터 프레임에 저장.
df.info()
df = df[['time','title','sub_title','article']]    # 초기의 df['date']는 필요없으니 제외하고 새 데이터 프레임 컬럼을 선언.
df['time'] = pd.to_datetime(df['time'])  # 해당 컬럼 타입은 object.  to_datetime함수로 timestamp 타입으로 바꾼다.
df.sort_values(by=['time'], ascending=False, ignore_index=True, inplace=True) # 컬럼 시계열 기준으로 정렬.
df.info()
df.to_csv('../coindesk_news/concat_last_v1.csv',index=False)
### concat 끝났으면 저장해야지.

###### 이상 코인 기사 데이터 수집 단계 끝. 다음은 코인 정보 데이터를 모아보자.





#####################################################################

# 0. 데이터 csv 파일 합치기.
# import glob
# data_paths = glob.glob('./datasets/*.csv')
# df_btc = pd.read_csv('./datasets/btc.csv')
# print(data_paths)

# for data_path in data_paths:
#     if data_path != './datasets\\btc.csv':
#         df_temp = pd.read_csv(data_path)
#         df_btc = pd.merge(df_btc,df_temp,how='left')
#
# df_btc.fillna(method='ffill', inplace=True)
# df_btc.fillna(method='bfill', inplace=True)
#
# df_btc.to_csv('./datasets/01_merged.csv', index=False)

# df_btc = pd.read_csv('./datasets/btc.csv')
# df
# df_exchange = pd.read_csv('./datasets/KRW_USD.csv')
# df_merged = pd.merge(df_btc,df_exchange,how='left')
# ### 결측치 채우기 ####
# df_merged.fillna(method='pad', inplace=True)
# df_merged.head()
#
# df_merged.to_csv('./datasets/merged_btc_Ex.csv', index=False)


##################################################################################################
# 4. hash-rate.csv   타임 스탬프 변경.
# 5. miners-revenue.csv

# df = pd.read_csv('./datasets/miners-revenue.csv')
# df.info()
# df.set_index('Timestamp', inplace=True)
# df = df.loc['2013-12-01 00:00:00':'2021-12-25 00:00:00']
# df['miners-revenue'] = df['miners-revenue'].astype(int)
# df.reset_index(inplace=True)
# df['time'] = df['Timestamp']
# df.info()
# df['time'] = pd.to_datetime(df['time'])
# df = df.loc[:,['time','miners-revenue']]
# df.to_csv('./datasets/miners-revenue.csv',index=False)

#############################################################################################################
# 1. USD_KRW.csv
# 2. dollar_index.csv
# 3. gold_future.csv
# 4. kospi.csv
# 5. snp  //  us_bond  //  USD_CNY


  ###### timestamp 맞추기
# import pandas as pd
# df = pd.read_csv('./datasets/Bitcoin.csv')
# df.info()
# to_time = []
# for i in df['날짜'] :
#     time = '{}-{}-{}'.format(i[:4],i[6:8],i[10:12])
#     pd.to_datetime(time)
#     to_time.append(time)
# df['날짜'] = to_time
# df['time'] = pd.to_datetime(df["날짜"])


#
# ################## 문자열(, 쉼표 포함) 제거 및 실수 작업
# df['USD_CNY'] = df['종가']
# # to_int = []
# # for i in df['종가'] :
# #     i = i.replace(',','')
# #     i = float(i)
# #     to_int.append(i)
# # df['us_bond'] = to_int
# ######################## 데이터 컬럼  합치기
# df = df.loc[:,['time','USD_CNY']]
# df.to_csv('./datasets/USD_CNY.csv', index=False)
# print(df.info())

# 환율 전처리 끝





######################## ma7 구하기.
# df = pd.read_csv('./datasets/Bitcoin_2.csv')
#
# df.sort_values(by='time', inplace=True)
#
# close = df['종가']
# window = close.rolling(7)
# ma7 = window.mean()
# df['ma7'] = ma7
# df.to_csv('./datasets/Bitcoin_3.csv', index=False)


########################################################################################################################
# # ma7 상위 6개 값 채우기
# df = pd.read_csv('./datasets/Bitcoin_3.csv')
# for i in range(0,7):
#     df.loc[i,'ma7'] = df.loc[i,'종가']
# print(df[['종가','ma7']].head(10))
# df.to_csv('./datasets/Bitcoin_4.csv', index=False)
########################################################################

####### 블록체인 닷컴.. .. 해쉬레이트..채굴자 수입


################### 날짜 짝 맞추기

# years = ['2014','2015','2016','2017','2018','2019','2020','2021']
# months = ['01','02','03','04','05','06','07','08','09','10','11','12']
# day = range(1,32)
# for i in years :
#     for j in months :
#         for k in day :
#             k = '%02d' % k
#             if '{}-{}-{}'.format(i,j,k) not in df_btc['time'].unique() :
#                 print('{}-{}-{}'.format(i,j,k))


