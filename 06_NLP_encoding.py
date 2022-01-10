
###### NLTK 패키지를 사용해서 영문 기사를 전처리하자.
###### NLTK 다운로드 필수. pip install nltk.  설치 전에 반드시 아나콘다 환경 백업해주세요.
###### 특정 패키지 설치 시 텐서플로 케라스 버젼이 바뀔 가능성 있음.


############################ 영문 자연어 처리 토큰화
### 관련 웹페이지 참조 :  https://wikidocs.net/21698

import pandas as pd
from nltk.tokenize import sent_tokenize   ### 문장 단위 토큰화
from nltk.tokenize import word_tokenize   ### 단어 단위 토큰화
from nltk.corpus import stopwords       ### nltk 패키지 안의 불용어 사전
import re      # 정규표현식으로 필요한 문자만 받자.

df = pd.read_csv('./coindesk_news/파일 불러오기.csv')
# df.info()

stop_words = set(stopwords.words('english'))   # nltk의 불용어 사전을 불러옴.

preprocessed_sentences_1 = []   # 토큰화 된 문장을 받을 리스트 생성.

for i in range(len(df['one_sentences'])):
    text = df['one_sentences'][i]
    sentences = sent_tokenize(text)
    # 문장 단위 토큰화 sent_tokenize는 영어로 작성된 글을 문장 단위로 나눠준다.
    # 가공되지 않은 문장 자체를 넣어주어야 문장 구분 성능이 뛰어남을 개인적으로 확인.
    # 예시) 어떤 기사의 내용을 10문장 단위로 구분함.

    preprocessed_sentences_2 = []

    for sentence in sentences:  # 예시) 10문장을 1문장 씩 체크
        sentence = sentence.lower()
        # 영어 문장을 모두 소문자화. 보통 영문 자연어 처리에서는 같은 의미의 단어라도 대소문자에 따라 다르게 구분된다.
        # 예시) buy,Buy,BUY 모두 같은 단어지만 각각 다르게 토큰화되고 정수 인코딩 된다.
        sentence = re.compile('[^a-z]').sub(' ', sentence)
        # 불필요한 기호, 문자, 숫자 등을 제거
        tokenizied_sentence = word_tokenize(sentence)
        # 위의 과정을 거친 문장을 단어 단위로 토큰화 하자.
        result = []

        for word in tokenizied_sentence:  # 단어 단위로 나눠진 문장을 전처리 한다.
            if word not in stop_words:
                if len(word) > 2:    # 1글자 삭제
                    result.append(word)
        preprocessed_sentences_2.append(result)   # 전처리 된 단어를 문장 단위로 리스트에 추가.
    preprocessed_sentences_1.append(preprocessed_sentences_2)
    # 다시 리스트에 추가. 위 과정으로 기사의 내용이 전처리 되서 토큰화된다.

df['preprocessed_sentences'] = preprocessed_sentences_1
df.info()

df.to_csv('./coindesk_news/저장저장.csv', index=False)















