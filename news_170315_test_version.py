from bs4 import BeautifulSoup
import urllib.request
import time
import re
import requests
import pymysql

# 시작날짜 설정
start_date = 20180115
end_date = 20180116

# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='root123', db='test', charset='utf8')

# Connection 으로부터 Cursor 생성
curs = conn.cursor()

# 페이지 긁는 범위 설정
page_num = 1
max_page_num = 10

# 정치, 경제, 사회, 생활/문화, 세계, IT/과학
sid1 = [100, 101, 102, 103, 104, 105]

# 정치, 경제, 사회, 생활/문화, 세계, IT/과학 순
sid_0 = [264, 265, 266, 267, 268, 269]
sid_1 = [258, 259, 260, 261, 262, 263, 310, 771]
sid_2 = [249, 250, 251, 252, 254, 255, 256, 257, 276, '59b']
sid_3 = [237, 238, 239, 240, 241, 242, 243, 244, 245, 248, 376]
sid_4 = [231, 232, 233, 234, 322]
sid_5 = [226, 227, 228, 229, 230, 283, 731, 732]

# 테스트용 카운트
count = 0

# 모르겠음
user_agent = "'Mozilla/5.0"
headers = {"User-Agent": user_agent}


# 입력받은 URL을 크롤링해서 반환
def get_body(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
    text = ''
    for item in soup.find_all('div', id='articleBodyContents'):
        text = text + str(item.find_all(text=True))
    return text


# 입력받은 URL을 제목 반환
def get_head(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
    text = ''
    for item in soup.find_all('h3', id='articleTitle'):
        text = text + str(item.find_all(text=True))
    return text


# 입력받은 URL에서 email 반환
def get_email(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
    text = ''
    for item in soup.find_all('div', id='articleBodyContents'):
        text = text + str(item.find_all(text=True))
    text = re.search(r"(\w+[\w\.]*)@(\w+[\w\.]*)\.([A-Za-z]+)", text)
    if text != None :
        text = str(text)
        text = text.split("'")[1]
    else :
        pass
    return text

# 입력받은 URL에서 시간, 날짜 값 리턴
def get_date(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    text = BeautifulSoup(source_code_from_URL, 'html.parser')
    text = text.select('span[class="t11"]')
    text = str(text)
    text = text.split('t11">')[1]
    text = text.split("</span")[0]
    return text

# 입력받으 URL에서 신문사 값 리턴
def get_company(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    text = BeautifulSoup(source_code_from_URL, 'html.parser')
    text = text.select('div[class="press_logo"]')
    text = str(text)
    text = text.split('title="')[1]
    text = text.split('"')[0]
    return text

# 예외처리부분
def clean_text(text):
    cleaned_text = re.sub('[a-zA-Z]', '', text)                                 # 일단은 영어 없앰
    cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', # 예외처리 단어부분
                          '', cleaned_text)
    cleaned_text = cleaned_text.lstrip()
    return cleaned_text


# 날짜 루프
for start_date in range(start_date, end_date):
    # 페이지 루프
    while page_num <= max_page_num:
        page_url = "http://news.naver.com/main/list.nhn?sid2=" + str(sid_0[0]) + "&sid1=" + str(
            sid1[0]) + "&mid=shm&mode=LS2D&date=" + str(start_date) + "&page=" + str(page_num) + ""
        response = requests.get(page_url, headers=headers)
        html = response.text

        check = "sid1=" + str(sid1[0]) + "&sid2=" + str(sid_0[0]) + ""
        # 주어진 HTML에서 기사 URL을 추출한다.
        url_frags = re.findall('<a href="(.*?)"', html)
        urls = []

        # sid1와 sid2가 일치하는 url만 크롤링한다
        for url_frag in url_frags:
            if check in url_frag and "aid" in url_frag:
                urls.append(url_frag)

        # 배열에 저장된 url을 하나씩 꺼내서 텍스트처리를 하고 DB에 저장한다
        for url in urls:
            body = get_body(url)
            body = clean_text(body)
            head = get_head(url)
            email = get_email(url)
            date = get_date(url)
            company = get_company(url)
            sql = "INSERT INTO news (Sid1, Sid2, Date, Head, Body, email, url, company) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            curs.execute(sql, (str(sid1[0]), str(sid_0[0]), str(date), str(head), str(body), str(email), str(url), str(company)))
            conn.commit()
            print(" ")

        # 정확히는 모르겠지만 크롤링 텀 주는 부분인듯
        time.sleep(2)

        # 해당 html에서 모두 긁으면 다음페이지로 넘어간다
        page_num += 1

conn.close()
print(count)