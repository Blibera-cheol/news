from bs4 import BeautifulSoup
import urllib.request
import time
import re
import requests
import pymysql
import datetime

# 시작날짜 설정
start_date = 20160101
end_date = 20160131
input_date = 20160101

# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='autoset', db='test', charset='utf8')

# Connection 으로부터 Cursor 생성
curs = conn.cursor()

# 페이지 긁는 범위 설정 하려면 해당부분 수정
page_num = 1
max_page_num = 30

# 정치, 경제, 사회, 생활/문화만 긁을거라서
sid1 = [100, 101, 102, 103]

# 정치, 경제, 사회, 생활/문화, 세계, IT/과학 순 (세부 부분 건들려면)
sid_0 = [264, 265, 266, 267, 268, 269]
sid_1 = [258, 259, 260, 261, 262, 263, 310, 771]
sid_2 = [249, 250, 251, 252, 254, 255, 256, 257, 276, '59b']
sid_3 = [237, 238, 239, 240, 241, 242, 243, 244, 245, 248, 376]
sid_4 = [231, 232, 233, 234, 322]
sid_5 = [226, 227, 228, 229, 230, 283, 731, 732]

# 모르겠음
user_agent = "'Mozilla/5.0"
headers = {"User-Agent": user_agent}

# 변수설정 (오류날까봐)
page_count = 1
Ten_count = 0
stop_page = 99999
url_second = ""
html_second = ""
Head = ""
Body = ""

for start_date in range(start_date, (end_date + 1)):
    for i in range(0,4):
        # 대분류를 한번 루프하고 초기화 해주는 변수
        page_count = 1
        Ten_count = 0
        # 얼마나 page_count가 있는지 모르니까 무한루프
        # 만약 다음페이지가 없으면 빠져나옴
        print(str(sid1[i]) + " : 현재 대분류 루프    " + str(input_date) + " : 현재날짜")
        j = 0
        try:
            while True:

                # 50개 크롤링후 2초 쉼
                time.sleep(2)

                j = 0
                url = "https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=" + str(sid1[i]) + "&listType=title&date=" + str(start_date) + "&page=" + str(page_count) + ""

                # request파싱시 type02가 10개가 안나와서 beautifulsoup으로 파싱
                source_code_from_URL = urllib.request.urlopen(url)
                soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')

                # split을 사용하기 위해 str로 변환
                html = str(soup)

                # 마지막 부분에 type02가 10개 미만이라 체크하는 부분
                type02_count = html.count('type02')

                # paging을 체크해서 마지막 부분에서 10번 루프안하게
                paging_count = html.split('paging')[1]
                paging_count = paging_count.split('</div>')[0]
                paging_count = paging_count.count('fls.page')

                # 10미만일 경우는 -1을 해주어 누락이 있어도 크롤링의 안정성 확보
                if (type02_count < 10):
                    type02_count = type02_count - 1
                    print("1실행되었습니다")

                # 10개 미만일 경우 10n + paging_count을 더한 page_count만 읽기 위해서
                if (paging_count < 10):
                    Ten_count = page_count // 10
                    stop_page = (Ten_count * 10) + paging_count - 1

                    # 멈추기 직전에 10개에 딱걸릴 경우 -1을 해주어 누락이 있어도 크롤링의 안정성 확보
                    if (page_count == stop_page):
                        if (type02_count == 10):
                            type02_count = type02_count - 1
                    print("2실행되었습니다")

                # url 추출 및 제목 수집
                while j < type02_count:

                    # for문에서 매번 선언 안하기 위해서
                    html_second = html.split('type02')[j + 1]

                    for k in range(1, 6):
                        # 본문 파싱을 위한 url 추출
                        url_second = html_second.split('<li>')[k]
                        url_second = url_second.split('href=\"')[1]
                        url_second = url_second.split('\"')[0]
                        url_second = url_second.strip()

                        # &뒤에 amp;가 붙어서 나와서 제거하기 위함
                        url_second = re.sub('amp;', '', url_second)

                        # 제목 추출
                        Head = html_second.split('<li>')[k]
                        Head = Head.split('nclicks(fls.list)')[1]
                        Head = Head.split('>')[1]
                        Head = Head.split('<')[0]
                        Head = Head.strip()

                        # 본문 추출
                        source_code_from_URL = urllib.request.urlopen(url_second)
                        response = requests.get(url_second, headers=headers)
                        html_body = response.text
                        html_body = html_body.split('오류를 우회하기 위한 함수 추가')[1]
                        html_body = html_body.split('<!-- // 본문 내용 -->')[0]

                        # 앞의 변수 뒤의 변수를 유기적으로 자르기 위한 코드
                        br_find = html_body.find('<br />')
                        html_body = html_body[br_find:]
                        html_body = html_body.split('<a')[0]

                        # br, p ,이메일 제거
                        html_body = re.sub('<br>', '', html_body)
                        html_body = re.sub('<p>', '', html_body)
                        html_body = re.sub('<br />', '', html_body)
                        html_body = re.sub(r"(\w+[\w\.]*)@(\w+[\w\.]*)\.([A-Za-z]+)", '', html_body)
                        html_body = html_body.strip()
                        sql = "INSERT INTO news (Date, Head, Body) VALUES (%s, %s, %s)"
                        curs.execute(sql, (str(input_date), str(Head), str(html_body)))
                        conn.commit()

                        print(url_second)
                        print(html_body)

                    # j를 증가시켜 다음 type02로 넘어가기 위해서
                    j = j + 1
                    print(j)

                # break문
                if (page_count == stop_page):
                    print("빠져나옵니다")
                    break
                # 페이지 증가 부분
                page_count = page_count + 1
        except:
            pass

    input_date = input_date + 1


