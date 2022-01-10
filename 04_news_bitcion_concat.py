
######################################### 기사 데이터 csv와 비트코인 가격 데이터 csv를 합치자. 날짜에 맞춰서

##### 기사 데이터를 기준으로 비트코인 가격정보의 레이블을 붙여한다.
##### 기사는 특정 날짜의 결측값이 존재하니 해당 기사의 날짜를 확인하고 해당 날짜의 비트코인 가격정보의 레이블을 부여한다.

import pandas as pd
import numpy as np

df = pd.read_csv('../coindesk_news/예시_뉴스기사 데이터.csv')    # 뉴스 기사 데이터
df.sort_values(by=['time'], ascending=True, ignore_index=True, inplace=True)

df_btc_before = pd.read_csv('../datasets/예시_비트코인.csv')      # 선행 비트코인 가격 정보 데이터
df_btc_before.sort_values(by=['time'], ascending=True, ignore_index=True, inplace=True)

df_btc_after = pd.read_csv('../datasets/Bitcoin_6_after.csv')       # 후행 비트코인 가격 정보 데이터
df_btc_after.sort_values(by=['time'], ascending=True, ignore_index=True, inplace=True)

df['after_updown_yesterday'] = np.nan
# 위의 컬럼에는 (후행 전날 종가 대비 상승 하락 여부) 레이블이 들어간다.
# 즉, 6개의 레이블을 위한 컬럼이 생성되야 한다.

# 뉴스 기사 csv 파일에  비트코인 가격 정보를 붙일 것임. 총 6개 컬럼이니 컬럼명을 다르게 하고 일단 NaN값으로 채우자.
# 주의! 작업의 모든 기준 파일은 뉴스기사 데이터이다.

for i in range(len(df)) :
    time = df['time'][i]   # 뉴스 기사 데이터의 날짜 확인.
    for j in range(len(df_btc_after['time'])) :
        if time == df_btc_after['time'][j] :    # 비트코인 가격정보 데이터의 날짜를 비교하여 일치한다면?
            updown = df_btc_after['updown_on_yesterday'][j]     # 해당 날짜의 가격 정보를 받아서
            df['after_updown_yesterday'][i] = updown            # 뉴스기사 데이터프레임에 붙여준다.

###### 위의 코드를 사용하여 비트코인 데이터의 6개 레이블을 뉴스기사 데이터에 붙여넣자.

df.to_csv('../coindesk_news/저장저장저장.csv', index=False)

##### 마지막으로는 저장~~~