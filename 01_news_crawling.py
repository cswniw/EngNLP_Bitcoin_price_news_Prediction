import pandas as pd
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
import time
import pickle
from selenium.webdriver.common.keys import Keys

################################################################### step 1. 크롬 웹브라우저 실행  ##################

options = webdriver.ChromeOptions()
options.add_argument('lang=ko_KR')
# 한국어로 실행되도록 설정.

options.add_argument('disable_gpu')
# 가속 사용 X 옵션. gpu 에러 시 사용 // 기본적으로 브라우저는 cpu의 부담을 줄이고 빠른 화면 렌더링을 위해 gpu를 통해 그래픽을 사용하는데,
# 간혹 이 부분이 크롬에서 버그를 일으키는 현상이 있다.

options.add_argument('--no-sandbox')
# 리눅스 서버와 같이 GUI를 제공하지 않는 환경에서는 [ no-sandbox ] 옵션을 추가해줘야 함.

options.add_argument('--disable-dev-shm-usage')
# /deb/shm 디렉토리를 사용하지 않는다는 의미. 이 디렉토리는 공유 메모리를 담당하는 부분. 보통 헤드리스 옵션과 함께 쓰인다.

options.add_argument("headless")
# 크롬을 직접 띄우지 않고 가상의 화면으로 돌릴 때 사용하는 코드.

options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
# headless 옵션 시.. 특정 웹사이트는 headless 접속을 차단한다. 이 경우 위의 같이 user-agent 이름을 설정한다.

# options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
# 현재 띄워진 크롬창에서 셀레늄 웹드라이버를 사용하고 싶다면.. 디버깅 모드로 실행해야하므로 위의 옵션을 준다.

driver = webdriver.Chrome(executable_path=r'C:\Users\Administrator\PycharmProjects\individual_pr\chromedriver.exe', options=options)
# 크롬드라이버 버젼 이슈 때문에 해당 크롬드라이버의 경로를 직접 넣어줬다.


################################################################### step 2. url 수집  ##################

######  코인데스크 경우 driver.get(url)을 이용해서 원하는 정보를 담은 페이지의 고유 웹주소로 접근이 되지 않아,
######  해당 페이지에 수동으로 접근한 뒤, 현재 실행중인 구글 윈도우 창에서 바로 크롤링을 실행했다. (이를 위해 디버깅 모드로 실행)

###### 2만여개 기사가 1페이지당 10개 총 2023 페이지에 걸쳐 웹페이지를 방문해야 하니 url을 먼저 크롤링한다.
url_list = []     # url 주소를 넣을 리스트 생성.
for k in range(1, 2023) :   # 총 2023개의 페이지
    for i in range(3,13) :    # 페이지당 10개 주소
        try :
            url_xpath = '//*[@id="queryly_advanced_container"]/div[4]/div[1]/div[{}]/div/div/a'.format(i)  # 해당 x_path
            url_addr = driver.find_element_by_xpath(url_xpath).get_attribute('href')  # href 속성, 즉 url 주소
            url_list.append(url_addr)
            print(url_addr)
        except :
            pass   # href 속성이 없으면 pass로 에러를 무시한다.

    if k % 100 == 0 :   # 100개 페이지 방문마다 url 주소를 저장한다.
        with open('./pickled_ones/url_list_{}'.format(k), 'wb') as f:  # url 주소를 피클화 한다. pickled_ones 폴더에 저장.
            pickle.dump(url_list, f)
        url_list = []    # 저장했으면 url 다시 초기화한다. 초기화하지 않으면 불필요한 중복값이 생긴다.
        print('hit the ', k)  # 진행 현황 파악.

    try :
        next_btn_xpath = '//*[@id="queryly_advanced_container"]/div[4]/div[2]/button[8]'
        # 한 페이지 url주소 다 모으면 넥스트 버튼을 클릭하여 넘어간다.
        driver.find_element_by_xpath(next_btn_xpath).send_keys(Keys.ENTER)   # .click()이 먹히지 않아 해당 함수를 주었다.
        time.sleep(0.5)  # 디도스 공격으로 의심받지 않기 위해 타임 슬립을 주었다.
        print('to the next')   # 진행 현황 파악.
    except :
        print(k)    # 에러 시 해당 페이지 번호를 알 수 있게 한다.
        break

with open('./pickled_ones/url_list_remain.pickle', 'wb') as f:
    pickle.dump(url_list, f)     # url 수집 마지막 단계에서 100 단위 미만으로 수집된 url을 저장하자.

##### 이 작업으로 2만여개 기사의 웹페이지 주소가 피클화 되어 pickled_ones 폴더에 저장되었다.
##### 이제부터 각 url을 방문하여 정보를 수집하자.


########################################################## step 3. 날짜, 헤드라인, 서브라인, 기사 내용 수집  ##################

######  url 수집 후.. 셀레늄 드라이버로 주소를 지정해서 크롤링 하자. headless로 크롤링 작업 시작.

for i in range(100,2100,100) :  # url 피클 파일이 10개 기사 * 100페이지 단위로 저장. 파일명 또한 100 페이지단위로 저장되었으니 range를 이렇게 줌.
    print(i)
    with open('./pickled_ones/url_list_{}.pickle'.format(i), 'rb') as f:      # url 주소를 담은 피클파일 불러오기.
        url_list = pickle.load(f)
    no_need = 'www.coindesk.com/podcasts/'     # url 주소 중 다음과 같은 주소는 동영상만 존재한다.
    url_list = [url for url in url_list if no_need not in url in url_list]
    # 위의 no_need로 시작하는 url 주소는 걸러준다.

    dates = []    # 날짜 정보를 저장할 리스트
    titles = []         # 헤드라인 정보를 저장할 리스트
    subtitles = []          # 부제 정보를 저장할 리스트
    articles = []           # 기사 정보를 저장할 리스트
    failed_url = []     # 크롤링에 실패한 url주소 정보를 저장할 리스트
                        # 각 웹페이지마다 html 형식이 다를 경우 크롤링에 실패하므로 이 경우 try, except 문으로 실패한 url을 수집하고
                        # 추후에 해당 url을 접속하여 html 형식을 파악하고 x_path를 수정하여 다시 크롤링 작업한다.
                        # 이와 같은 이유으로 3가지 버젼의 x_path 코드 작업을 하였다.
    count = 1   # 진행 현황 체크

    for url in url_list :
        try :    # url 주소가 정상적으로 접근 가능하면 try. 아니면 except로 failed_url로 저장됨.

            driver.get(url)
            time.sleep(0.5)
            title_xpath = '//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div[2]/div/div[2]/h1'
            subtitle_xpath = '//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div[2]/div/div[3]/h2'
            date_xpath = '//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div[2]/div/div[4]/div[2]/div/span'
            article_xpath = '//*[@id="fusion-app"]/div/div[2]/main/div[1]/div/section'
            ## 위의 xpath는 코인데스크 기사 html의 통상적인 xpath 경로이다.

            print(count, url)    # 몇번쨰 url 인지 확인.

            try :      # 첫 번째 try,except문의 try.
                title = driver.find_element_by_xpath(title_xpath).text
                # print(title)
                subtitle = driver.find_element_by_xpath(subtitle_xpath).text
                # print(subtitle)
                date = driver.find_element_by_xpath(date_xpath).text
                # print(date)
                article = driver.find_element_by_xpath(article_xpath).text
                # print(article)
                dates.append(date)              # 크롤링 한 정보를 각각의 상위 리스트에 저장.
                titles.append(title)
                subtitles.append(subtitle)
                articles.append(article)
                print('succeed')
            except :
                try :  # 두 번째 try,except문의 try.
                    title_xpath = '//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div[2]/div/div/div[2]/h1'
                    subtitle_xpath = '//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div[2]/div/div/div[3]/h2'
                    date_xpath = '//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div[2]/div/div/div[5]/div[1]/div/span'
                    article_xpath = '//*[@id="fusion-app"]/div/div[2]/main/div[1]/div/section'

                    title = driver.find_element_by_xpath(title_xpath).text
                    # print(title)
                    subtitle = driver.find_element_by_xpath(subtitle_xpath).text
                    # print(subtitle)
                    date = driver.find_element_by_xpath(date_xpath).text
                    # print(date)
                    article = driver.find_element_by_xpath(article_xpath).text
                    # print(article)
                    dates.append(date)          # 크롤링 한 정보를 각각의 상위 리스트에 저장.
                    titles.append(title)
                    subtitles.append(subtitle)
                    articles.append(article)
                    print('second try succeed')
                except :
                    try :    # 세 번째 try,except문의 try.
                        title_xpath = '//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div/div[1]/div/div/div[2]/h1'
                        subtitle_xpath = '//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div/div[1]/div/div/div[3]/h2'
                        date_xpath = '//*[@id="fusion-app"]/div/div[2]/main/article/div/header/div/div[1]/div/div/div[6]/div[1]/div/span'
                        article_xpath = '//*[@id="fusion-app"]/div/div[2]/main/div[1]/div/section/div'
                        title = driver.find_element_by_xpath(title_xpath).text
                        # print(title)
                        subtitle = driver.find_element_by_xpath(subtitle_xpath).text
                        # print(subtitle)
                        date = driver.find_element_by_xpath(date_xpath).text
                        # print(date)
                        article = driver.find_element_by_xpath(article_xpath).text
                        # print(article)
                        dates.append(date)          # 크롤링 한 정보를 각각의 상위 리스트에 저장.
                        titles.append(title)
                        subtitles.append(subtitle)
                        articles.append(article)
                        print('third try succeed')
                    except:     # 세 번째 try,except문에서도 크롤링에 실패하면 failed_url에 저장. 이후 해당 url을 방문하여 실패 이유를 조사하자.
                        failed_url.append(url)
                        print('failed')
                        pass

        except :        # url 주소가 정상적으로 접근 가능하면 try. 아니면 except로 failed_url로 저장됨.
            failed_url.append(url)
            print('getting url failed')
            pass

        if count % 100 == 0 :       # 100번 크롤링 하면 저장하도록 하자.
            df = pd.DataFrame({'date': dates, 'title': titles, 'sub_title': subtitles, 'article': articles})
            df.to_csv('./coindesk_news/coin_news_i_{}_{}.csv'.format(i, count), index=False)
            # 100단위 저장 몇번째인지 파일명에 기록하여 저장.
            print('{} saved saved saved saved saved saved saved saved saved'.format(count))

            df_failed = pd.DataFrame({'failed_url': failed_url})     # 크롤링 수집에 실패한 url도 저장하자.
            df_failed.to_csv('./coindesk_news/failed/failed_url_i_{}_{}.csv'.format(i, count), index=False)
            print('{} failed save failed save failed save failed save failed'.format(count))

            dates = []              # 저장이 끝났으면 중복을 피하고 다음 크롤링 정보를 저장하기 위해 상위 리스트를 초기화 한다.
            titles = []
            subtitles = []
            articles = []
            failed_url = []

            driver.quit()           ###### 중요중요중요!!!! 크롤링 작업이 누적되면 셀레늄 드라이버가 컴퓨터의 메모리를 계속 잡아먹는다.
                                    ###### 메모리가 한도에 이르면 셀레늄 드라이버가 중단되어버린다. (코드에 문제가 없어도.)
                                    ###### 메모리 초기화를 위해 셀레늄 드라이버를 일정 작업마다 꼭 닫아준다.
                                    ###### driver.close()보다 driver.quit()을 쓴다.
            ###### driver.close() : 현재 셀레늄이 컨트롤하고 있는 (활성화된) 창을 닫는 기능. 탭이 여러개면 활성화된 창 하나만 종료.
                                    #셀레늄 서비스가 메모리에 그대로 상주하고 있음.
            ###### driver.quit() : 웹드라이버, 열린 모든 창을 닫음.


            driver = webdriver.Chrome(
                executable_path=r'C:\Users\Administrator\PycharmProjects\individual_pr\chromedriver.exe',
                options=options)      ##### 드라이버를  닫았으면 다시 열어주자.


        count += 1    # 1개의 url에서 크롤링이 끝나면 count를 해준다.


    ##### 이하 코드는 100단위 미만의 저장을 위한 것.
    df = pd.DataFrame({'date': dates, 'title': titles, 'sub_title': subtitles, 'article': articles})
    df.to_csv('./coindesk_news/coin_news_{}_remain.csv'.format(i), index=False)
    print('saved saved saved saved saved saved saved saved saved saved')

    df_failed = pd.DataFrame({'failed_url':failed_url})
    df_failed.to_csv('./coindesk_news/failed/failed_url_{}_remain.csv'.format(i), index=False)
    print('failed save failed save failed save failed save failed save')

    dates = []
    titles = []
    subtitles = []
    articles = []
    failed_url = []

    driver.quit()
    driver = webdriver.Chrome(
        executable_path=r'C:\Users\Administrator\PycharmProjects\individual_pr\chromedriver.exe',
        options=options)

driver.quit()