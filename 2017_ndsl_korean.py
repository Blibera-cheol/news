from bs4 import BeautifulSoup
import urllib.request
import time
import re
import requests
import pymysql
import time

start_time = time.time()
# 시작날짜 설정
start_date = 20180115
end_date = 20180116

# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='root123', db='test', charset='utf8')

# Connection 으로부터 Cursor 생성
curs = conn.cursor()

# 페이지 긁는 범위 설정
page_num = 1
max_page_num = 3

# 테스트용 카운트
count = 0

# 모르겠음
user_agent = "'Mozilla/5.0"
headers = {"User-Agent": user_agent}



# 저장된 10개의 뭉텅이
tag_list = []
# 원하는 뒷패턴을 뽑아내기 위해서 리스트잘라내기 사용하려고 만듬
test_list = []
# 10개를 다시 돌려서 초록,저자 그런거 저장
url_10 = []

# mysql에 저장할 배열

i = 0
j = 0

# 루프 수 확인하려고 만든 변수
count_num = 0
r=0

while page_num<=max_page_num:
    html = requests.get("http://www.ndsl.kr/ndsl/search/list/article/articleSearchResultList.do?page=" + str(page_num)+ "&query=ai&prefixQuery=%3CALIAS:contains:%EA%B5%AD%EB%82%B4%EB%85%BC%EB%AC%B8%3E%20&collectionQuery=&showQuery=ai&resultCount=10&sortName=RANK&sortOrder=DESC&colType=scholar&colTypeByUser=&filterValue=")
    html = html.text
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup.select('a[title=상세화면]'):
        tag_list.append(tag)
        count_one = 0

        tag_str = str(tag)
        tag_cut = tag_str.split("('")[1]
        tag_cut = tag_cut.split("',")[0]

        # 1차 파싱한 html에서 원하는 값을 얻어내기 위해 다시한번 url
        urlll = "http://www.ndsl.kr/ndsl/search/detail/article/articleSearchResultDetail.do?cn="+str(tag_cut)+""

        html_second = requests.get(str(urlll))
        html_second = html_second.text
        soup_second = BeautifulSoup(html_second, 'html.parser')

        tag_one = soup_second.select('h3')
        tag_second = soup_second.select('div[class="txt_st2 detail_css"]')
        tag_three = soup_second.select('p[class=detail_css]')

        tag_one_str = str(tag_one)
        tag_second_str = str(tag_second)
        tag_three_str = str(tag_three)

        # Head 부분
        body_cut_one_first = tag_one_str.split("타이틀 -->")[1]  # 앞에 쓰레기 문장 제거
        count_one = body_cut_one_first.count('button')
        if count_one == 0:
            body_cut_one_end = body_cut_one_first.split("<!--")[0]  # 뒤에 쓰레기 문장 제거
        else:
            body_cut_one_end = body_cut_one_first.split("<button")[0]  # 뒤에 쓰레기 문장 제거
        one = body_cut_one_end.lstrip()  # 왼쪽 공백제거
        one = one.rstrip()

        # Name 부분
        body_cut_first = tag_second_str[34:]
        body_cut_end = body_cut_first.split("<div")[0]

        count_button = body_cut_end.count("<button")    # <button이 몇개있는지 체크
        count_stack = body_cut_end.count("-->")         # -->가 몇개있는지 체크
        test_count = body_cut_end.count(str(tag_cut))         # 특정경우 체크
        num=0
        stack=0
        stack_s=0

        # Body 부분

        body_cut_three_start = tag_three_str.split(">")[1]  # 뒤에 쓰레기 문장 제거
        body_cut_three_end = body_cut_three_start.split("</p>")[0]  # 뒤에 쓰레기 문장 제거


        else_i = 1  # else 문에서 수행할 i
        list = []

        if count_button < count_stack :
            num = 1
        else :
            num = 2

        if count_button == 1:  # 저자가 1명일때

            body_cut_end = body_cut_end.split("-->")[1]
            body_cut_end = body_cut_end.split("<button")[0]
            s = body_cut_end.lstrip()
            s = s.rstrip()
            list.append(s)
        else:  # 저자가 여러명일경우 count 수만큼 루프함

            # button 수와 --> 수가 같은 경우
            if test_count == 0 and num == 1:
                while else_i < (count_button + 1):
                    first = body_cut_end.split("-->")[else_i]
                    end = first.split("<button")[0]
                    s = end.lstrip()
                    s = s.rstrip()
                    else_i += 1
                    list.append(s)
            elif test_count == 0 and num == 2:
                while else_i < (count_button + 1):
                    if stack_s==0:
                        count_button = count_button / 2
                        stack_s = stack_s + 1
                    first = body_cut_end.split("-->")[else_i]
                    end = first.split("<button")[0]
                    s = end.lstrip()
                    s = s.rstrip()
                    else_i += 1
                    list.append(s)

            # 특정 상황
            else :
                while else_i < (count_button + 1):
                    body_cut_end = body_cut_first.split(str(tag_cut))[else_i]
                    body_cut_end = body_cut_end.split(",")[2]
                    body_cut_end = body_cut_end.split(",")[0]

                    if else_i > 1 :
                        if str(list[stack])==str(body_cut_end):
                            r=r+1
                        else:
                            list.append(body_cut_end)
                            stack = stack + 1
                    else :
                        list.append(body_cut_end)
                    else_i += 1

        sql = "insert into ttxt(Head, Named, Body)values( % s, % s, % s)"
        curs.execute(sql, (str(one), str(list), str(body_cut_three_end)))
        conn.commit()

        count_num = count_num + 1  # 몇번 수행되었는지 확인
        print(str(count_num) + "번 수행되었습니다")




    # 페이지 넘어가기
    page_num = page_num + 1
    endTime = time.time() - start_time
    print(endTime)
# sql 종료
conn.close()