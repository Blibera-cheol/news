from bs4 import BeautifulSoup
import requests
import pymysql
import datetime


# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='autoset', db='test', charset='utf8')

# Connection 으로부터 Cursor 생성
curs = conn.cursor()

# 페이지 긁는 범위 설정
page_num = 16770
max_page_num = 20000

# 테스트용 카운트
count = 0

# 모르겠음
user_agent = "'Mozilla/5.0"
headers = {"User-Agent": user_agent}

time_stack =0

while page_num <= max_page_num:
    html = requests.get("http://www.ndsl.kr/ndsl/search/list/article/articleSearchResultList.do?page="+str(page_num)+"&query=q|w|e|r|t|y|u|i|o|p|a|s|d|f|g|h&prefixQuery=%3CALIAS:contains:%ED%95%B4%EC%99%B8%EB%85%BC%EB%AC%B8%3E%20&collectionQuery=&showQuery=q|w|e|r|t|y|u|i|o|p|a|s|d|f|g|h&resultCount=10&sortName=RANK&sortOrder=DESC&colType=scholar&colTypeByUser=&filterValue=")
    html = html.text
    soup = BeautifulSoup(html, 'html.parser')
    try:
        for tag in soup.select('a[title=상세화면]'):
            tag_str = str(tag)
            tag_cut = tag_str.split("('")[1]
            tag_cut = tag_cut.split("',")[0]

            urlll = "http://www.ndsl.kr/ndsl/search/detail/article/articleSearchResultDetail.do?cn=" + str(tag_cut) + ""
            html_second = requests.get(str(urlll))
            html_second = html_second.text
            soup_second = BeautifulSoup(html_second, 'html.parser')

            # Head 부분
            count = 0
            html_second = requests.get(str(urlll))  # urlll을 받아서 html_second로 저장

            html_second = html_second.text  # html_second을 text처리하여 html_second에 재저장

            soup_second = BeautifulSoup(html_second, 'html.parser')  # 파싱한 내용을 soup_second에 저장

            tag_second = soup_second.select('h3')  # h3인 부분만 추출 (제목부분)

            tag_second_str = str(tag_second)  # 이것을 수행하지 않으면 list라고 오류남 그래서 문자열로 재 저장해주는것

            body_cut_first = tag_second_str.split("타이틀 -->")[1]  # 앞에 쓰레기 문장 제거
            count = body_cut_first.count('button')
            if count == 0:
                body_cut_end = body_cut_first.split("<!--")[0]  # 뒤에 쓰레기 문장 제거
            else:
                body_cut_end = body_cut_first.split("<button")[0]  # 뒤에 쓰레기 문장 제거
            name = body_cut_end.lstrip()  # 왼쪽 공백제거
            name = name.rstrip()  # 오른쪽 공백제거

            # Name 부분
            tag_name = soup_second.select('div[class="txt_st2 detail_css"]')
            tag_name_str = str(tag_name)
            body_name_first = tag_name_str[34:]
            body_name_end = body_name_first.split("<div")[0]
            count = body_name_end.count("<button")  # 몇명의 저자가 있는지 체크
            else_i = 1  # else 문에서 수행할 i
            list = []

            if count == 1:  # 저자가 1명일때

                body_name_end = body_name_end.split("-->")[1]
                body_name_end = body_name_end.split("<button")[0]
                s = body_name_end.lstrip()
                s = s.rstrip()
                list.append(s)
            else:  # 저자가 여러명일경우 count 수만큼 루프함
                while else_i < (count + 1):
                    first = body_name_end.split("->")[else_i]
                    end = first.split("<button")[0]
                    s = end.lstrip()
                    s = s.rstrip()
                    else_i += 1
                    list.append(s)

            # Body 부분
            tag_body = soup_second.select('p[class=detail_css]')  # p로 묶인 부분에서 class=detail_css부분만 잘라내서 tag_second에 저장
            tag_body_str = str(tag_body)  # 이것을 수행하지 않으면 list라고 오류남 그래서 문자열로 재 저장해주는것

            body_body_start = tag_body_str.split(">")[1]  # 뒤에 쓰레기 문장 제거
            body_body_end = body_body_start.split("</p>")[0]  # 뒤에 쓰레기 문장 제거

            # MySql에 저장
            sql = "insert into eng(Head, Named, Body)values( % s, % s, % s)"
            curs.execute(sql, (str(name), str(list), str(body_body_end)))
            conn.commit()
    except:
        print("오류발생")
    finally:
        page_num = page_num + 1
        time_stack = time_stack + 1
    # sql 종료
    count_num = count_num + 1  # 몇번 수행되었는지 확인
    while time_stack > 10:
        datetimed = datetime.datetime.now()
        print(datetimed)
        time_stack = 0
    print(str(count_num) + "번 수행되었습니다")
    print(" ")
conn.close()