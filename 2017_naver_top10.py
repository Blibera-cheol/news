from bs4 import BeautifulSoup
import re
import requests
import pymysql
import time

# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='root123', db='test', charset='utf8')

# Connection 으로부터 Cursor 생성

curs = conn.cursor(pymysql.cursors.DictCursor)

html = requests.get("http://news.naver.com/")
html = html.text
soup = BeautifulSoup(html, 'html.parser')

Big = 0     # 정치, IT 분류용
Small = 0   # 8번 루프용

def clean_text(text):
    cleaned_text = re.sub('[a-zA-Z]', '', text)                                 # 일단은 영어 없앰
    cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', # 예외처리 단어부분
                          '', cleaned_text)
    cleaned_text = cleaned_text.lstrip()
    return cleaned_text

while True:
    while Big < 2 :         # 정치, IT 루프
        while Small < 8 :   # 8개만 루프해서 8개만 돌게 설정
            if Big == 0 :
                text = soup.select('div[id="ranking_100"]') # Url을 파싱해서 div[id="ranking_100"]부분을 찾아서 text에 저장
            elif Big == 1 :
                text = soup.select('div[id="ranking_105"]')  # Url을 파싱해서 div[id="ranking_100"]부분을 찾아서 text에 저장
            text = str(text)                            # split기능을 사용하기 위해서 string으로 바꿈
            clean_url = ""
            url_head = ""
            Small += 1
            text_url = text.split('href="')[Small]
            text_url = text_url.split('"')[0]
            clean_url = re.sub('&amp;', '&', text_url)  # url만 긁어내기

            url_head = text.split('href="')[Small]
            url_head = url_head.split('title=')[1]
            url_head = url_head.split('</a')[0]         # 해당 url의 제목 추출
            url_head = clean_text(url_head)             # 예외처리

            url = "http://news.naver.com"+str(clean_url) # 링크 형식으로 변형

            if Big == 0 :
                sql = "insert into news_politics8(num, head, url)values( % s, % s, % s)"
                curs.execute(sql, (Small, str(url_head), str(url)))
            elif Big == 1 :
                sql = "insert into news_it8(num, head, url)values( % s, % s, % s)"
                curs.execute(sql, (Small, str(url_head), str(url)))
            conn.commit()
        Big += 1
        Small = 0
    time.sleep(10)
    print("수행")
    Big = 0
    Small = 0
    curs.execute("TRUNCATE TABLE news_politics8")
    curs.execute("TRUNCATE TABLE news_it8")
    conn.commit()
conn.close()