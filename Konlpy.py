from konlpy.tag import Twitter, Kkma
from konlpy.utils import pprint
import pymysql

# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='root123', db='test', charset='utf8')

# Connection 으로부터 Cursor 생성

curs = conn.cursor(pymysql.cursors.DictCursor)

twitter = Twitter()
kkma = Kkma()                     # 기능사용을 위해 설정

sql = "select * from news"      # 뉴스테이블에 접근
curs.execute(sql)

# 데이타 Fetch
rows = curs.fetchall()

Date = ""
Head = ""
Body = ""
i=0
date_year = 0
date_month = 0
date_day = 0
keyword_name_kkma = ""
keyword_name_twitter = ""
keyword_body_kkma = ""
keyword_body_twitter = ""           # 문자열 초기화

for row in rows:                    # 모든 열을 루프하기 위함
    Date = row['Date']
    Head = row['Head']
    Body = row['Body']              # 해당 열의 date, head, body 정보를 받아서 저장
    date_year = Date[:4]
    date_month = Date[4:6]
    date_day = Date[6:]             # html에서 사용하기 쉽게 날짜형식 재설정
    date_year = int(date_year)
    date_month = int(date_month)
    date_day = int(date_day)        # 오류방지를 위한 int화

    keyword_name_kkma = kkma.nouns(Head)
    keyword_name_twitter = kkma.nouns(Head)
    keyword_body_kkma = twitter.nouns(Body)
    keyword_body_twitter = twitter.nouns(Body)  # kkma, twitter를 이용해 nlp처리

    sql = "INSERT INTO news_make_test (date_year, date_month, date_day, keyword_name_kkma, keyword_name_twitter, keyword_body_kkma, keyword_body_twitter) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    curs.execute(sql, (
    date_year, date_month, date_day, str(keyword_name_kkma), str(keyword_name_twitter), str(keyword_body_kkma),
    str(keyword_body_twitter)))
    conn.commit()

conn.close()

