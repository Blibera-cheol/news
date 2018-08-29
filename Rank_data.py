from collections import Counter
from konlpy.tag import Twitter, Kkma
import pymysql

# 해당 날짜의 가장 많은 키워드를 랭킹으로 저장하는 파이썬 코드입니다

# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='root123', db='test', charset='utf8')

# Connection 으로부터 Cursor 생성

curs = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from news_make_test"      # 뉴스테이블에 접근
curs.execute(sql)

twitter = Twitter()
kkma = Kkma()

noun_count = 100
rows = curs.fetchall()
zero = "0"
def get_tags_kkma(text, ntags=50):
    spliter = Twitter()
    # konlpy의 Twitter객체
    nouns = spliter.nouns(text)
    # nouns 함수를 통해서 text에서 명사만 분리/추출
    count = Counter(nouns)
    # Counter객체를 생성하고 참조변수 nouns할당
    return_list = []  # 명사 빈도수 저장할 변수
    for n, c in count.most_common(ntags):
        if len(n) > 2:
            temp = {'tag': n, 'count': c}
            return_list.append(temp)
        else :
            pass
    # most_common 메소드는 정수를 입력받아 객체 안의 명사중 빈도수
    # 큰 명사부터 순서대로 입력받은 정수 갯수만큼 저장되어있는 객체 반환
    # 명사와 사용된 갯수를 return_list에 저장합니다.
    return return_list

for row in rows:
    noun_count = 100
    year = row['date_year']
    month = row['date_month']
    day = row['date_day']

    day = int(day)
    month = int(month)          # 숫자 비교를 위한 int화

    if day < 10:                 # 0~9월일 경우 앞에 0을 붙이는 조건문
        day = str(day)
        day = zero + day
    if month < 10:
        month = str(month)
        month = zero + month


    name_kkma = row['keyword_name_kkma']
    name_twitter = row['keyword_name_twitter']
    body_kkma = row['keyword_body_kkma']
    body_twitter = row['keyword_body_twitter']
    body_kkma = str(body_twitter)
    tags = get_tags_kkma(name_kkma, noun_count)  # get_tags 함수 실행

    rank = 1                # 랭킹 초기화

    day = str(day)          # int오류 방지를 위한 str선언
    month = str(month)
    date = year+month+day   # date형식으로 제작
    print(date)
    for tag in tags:
        noun = tag['tag']
        count = tag['count']
        print(noun, count,rank)
        sql = "INSERT INTO news_keyword_kkma(date, date_year, date_month, date_day, rank, count, name) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        curs.execute(sql, (year, month, day, rank, count, str(noun)))
        conn.commit()
        rank = rank + 1
    print("")



