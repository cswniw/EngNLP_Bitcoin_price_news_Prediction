########################### 날짜별 기사 수 카운팅 / 혹시 모르니까...

import pandas as pd
df = pd.read_csv('../coindesk_news/파일.csv')
df.info()
dates = []
for i in df['time'] :
    count = df['time'][df['time'] == i].count()   # 해당 컬럼의 해당 날짜와 동일한 값을 세준다.
    dates.append(count)
df['counts'] = dates


############################  메인타이틀 서브타이틀 기사내용 (총 3컬럼)  /// 한 문장으로 만들기.

import pandas as pd
df = pd.read_csv('./coindesk_news/파일 불러오기~.csv')
df.info()

one_sentences = []   # 한 문장으로 합쳐진 기사 내용을 저장할 리스트 생성.
for i in range(len(df)) :

    one_sentence = df['메인 타이틀'][i] +' ' + str(df['서브타이틀'][i]) + ' ' + df['기사 내용'][i]
    one_sentences.append(one_sentence)
df['one_sentences'] = one_sentences
df = df[['time','counts','one_sentences','no_ad_sentences','article','title','sub_title']]
## 필요한 컬럼만 추려서 다시 선언. 제 경우 모든 정보는 다 살리고 갔습니다. 전처리 전의 데이터까지 포함해서.
df.to_csv('./coindesk_news/저장 저장..csv', index=False)



########################################## 기사 내용에 포함된 광고 문자열 제거 작업  ##############
import pandas as pd
df = pd.read_csv('./coindesk_news/파일 불러오기.csv')
df.info()

no_ad_sentences = []   # 광고를 제거한 문장을 저장할 리스트 생성.


##### 중요 중요!~  기사 데이터를 일정 부분 추출해서 읽어보면 데이터의 형식이 다음과 같음을 확인했다.

### 예시)  메인제목+부제+기사내용+구독+좋아요+알림설정+광고내용
### 이러한 규칙을 발견해서 기사내용 이후 구독~ 이하가 시작되는 문자열의 특징을 찾아내 분리하는 작업을 한다.

for i in range(len(df['article'])):    # 데이터 프레임의 길이만큼 for문 작업.
    text = df['article'][i]
    # 기사 내용을 하나하나씩 읽자.
    text = text.replace('\n',' ')
    # 일단 줄바꿈 교체
    ad_start = 'disclosure the leader in news and information on cryptocurrency,'
    # 위 문자열은 구독~이하가 시작되는 부분
    bye_ad = text.split(ad_start)
    # ad_start를 기준으로 문자열을 2개로 분리하여 리스트화 한다.
    no_ad_sentences.append(bye_ad[:-1])
    # 리스트 슬라이싱으로 구독~이하는 제외하자.

df['no_ad_sentences'] = no_ad_sentences
df = df[['time','counts','no_ad_sentences','article','title','sub_title']]
df.to_csv('./coindesk_news/저장저장.csv', index=False)

### 광고 제거 시 특정 문구를 변수로 받아서 str.replace(변수, ' ')로 제거하는 방법도 가능하다.
#### 예시) text = '오늘 비트코인 폭등한다. 더 보고 싶으면 결제해~~~'
####      delet = '더 보고 싶으면 결제해~~~'
####      text.replace(delet, ' ')













