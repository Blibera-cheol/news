from bs4 import BeautifulSoup
import urllib.request
import time
import re
import requests
import pymysql
import datetime

# 시작날짜 설정   11일~20일
start_date = 20170201
end_date = 20170231
input_date = 20170201

# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='root123', db='test', charset='utf8')

# Connection 으로부터 Cursor 생성
curs = conn.cursor()

# 페이지 긁는 범위 설정
page_num = 1
max_page_num = 30

# 사진 뉴스 중복 제거하기 위한 변수
before_url = ""

# 페이지 커팅
find_next = "다음"

# 정치, 경제, 사회, 생활/문화, 세계, IT/과학
sid1 = [100, 101, 102, 103, 104, 105]

# 정치, 경제, 사회, 생활/문화, 세계, IT/과학 순
sid_0 = [264, 265, 266, 267, 268, 269]
sid_1 = [258, 259, 260, 261, 262, 263, 310, 771]
sid_2 = [249, 250, 251, 252, 254, 255, 256, 257, 276, '59b']
sid_3 = [237, 238, 239, 240, 241, 242, 243, 244, 245, 248, 376]
sid_4 = [231, 232, 233, 234, 322]
sid_5 = [226, 227, 228, 229, 230, 283, 731, 732]

# 모르겠음
user_agent = "'Mozilla/5.0"
headers = {"User-Agent": user_agent}


# 입력받은 URL에서 바디 반환
def get_body(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
    text = soup.select('div[id="articleBodyContents"]')
    text = str(text)
    text = text.split('추가')[1]
    text = text.split('본문 내용')[0]
    text = text.rstrip()
    text = text.lstrip()
    return text


# 입력받은 URL에서 제목 반환
def get_head(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
    text = ''
    for item in soup.find_all('h3', id='articleTitle'):                         # articleTitle 부분만 잘라냄
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
    if text != None :               # 이메일양식에 맞는 이메일이 없으면 None 리턴
        text = str(text)
        text = text.split("'")[1]
    else :
        pass
    return text

# 입력받은 URL에서 시간, 날짜 값 리턴
def get_date(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
    text = str(soup)
    a = 0
    a = text.find('id="newsEndContents"')
    # 혹시몰라서 b = text.find('id = "main_content"')
    if a < 1 :                                          #id="newsEndContents" 이 있으면 if실행 id = "main_content"가 있으면 elif실행
        text = soup.select('span[class="t11"]')
        text = str(text)
        text = text.split('t11">')[1]
        text = text.split("</span")[0]
        text = text.lstrip()
    elif a > 1 :
        text = soup.select('div[class="info"]')
        text = str(text)
        text = text.split('기사입력')[1]
        text = text.split("</span")[0]
        text = text.lstrip()
    return text

# 입력받으 URL에서 신문사 값 리턴
def get_company(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
    text = str(soup)
    a = 0
    a = text.find('id="newsEndContents"')
    if a < 1 :                                          #id="newsEndContents" 이 있으면 if실행 id = "main_content"가 있으면 elif실행
        text = soup.select('div[class="press_logo"]')
        text = str(text)
        text = text.split('title="')[1]
        text = text.split('"')[0]
    elif a > 1 :
        text = soup.select('a[class="link"]')
        text = str(text)
        text = text.split('alt="')[1]
        text = text.split('"')[0]
    return text

# 예외처리부분
def clean_text(text):
    cleaned_text = re.sub('[a-zA-Z]', '', text)                                 # 일단은 영어 없앰
    cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', # 예외처리 단어부분
                          '', cleaned_text)
    cleaned_text = re.sub('[0-9]','', cleaned_text)
    cleaned_text = cleaned_text.lstrip()
    return cleaned_text

# 페이지 커팅    (페이지에 관련된 부분 커팅)
def page_cut(URL):
    source_code_from_URL = urllib.request.urlopen(URL)
    soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
    text = soup.select('div[class="paging"]')
    text = str(text)
    text = text.rstrip()
    text = text.lstrip()
    return text

# 페이지 커팅2   (페이지 수 커팅하는 함수)
def page_cut2(text):
    page_cut2 = text.count('nclicks')
    text = text.split('">')[page_cut2]
    text = text.split("<")[0]
    return text

# 이래야 날짜 차이만큼 루프함
for start_date in range(start_date, (end_date + 1)):
    for i in range(0, 6):
        print(input_date)
        print("현재 루프 날짜")
        datetimed = datetime.datetime.now()
        print(datetimed)
        if sid1[i] == 100:  # 정치
            for i_0 in range(0, 6):
                page_num = 1
                tol = 99
                while page_num <= max_page_num:
                    try:
                        # 대분류,소분류,시작날짜,페이지 번호를 입력받아서 html로 저장(?)
                        page_url = "http://news.naver.com/main/list.nhn?sid2=" + str(sid_0[i_0]) + "&sid1=" + str(
                            sid1[i]) + "&mid=shm&mode=LS2D&date=" + str(input_date) + "&page=" + str(page_num) + ""
                        response = requests.get(page_url, headers=headers)
                        html = response.text

                        # check는 해당 html에서 대분류,소분류가 일치하는 url만 긁어오기 위한 변수 설정
                        check = "sid1=" + str(sid1[i]) + "&sid2=" + str(sid_0[i_0]) + ""

                        # 주어진 HTML에서 기사 URL을 추출한다.
                        url_frags = re.findall('<a href="(.*?)"', html)

                        # urls에 배열로 담는듯 보임
                        urls = []

                        # urls전 배열을 담아서 전과 동일한 url이 발생하면 저장하지 않게 하기위함
                        url_i = ""

                        # check변수를 통해 sid1와 sid2가 일치하는 url만 크롤링한다
                        for url_frag in url_frags:
                            if check in url_frag and "aid" in url_frag:
                                if url_frag == url_i:
                                    pass
                                else:
                                    urls.append(url_frag)
                                    url_i = url_frag

                        # 페이지 커팅
                        tell = page_cut(page_url)  # page_cut 함수에 page_url(url주소)를 넣어서 리턴값을 tell에 저장
                        finding = tell.find(find_next)  # find함수를 사용해 tell에서 '다음'이라는 단어를 찾음 (있으면 해당 문자열번호, 없으면 -1)
                        if tol == 99:  # 번호수인데 1번만 루프 되게 하려고 tol에 99값을 부여함
                            if finding == -1:  # '다음' 이라는 단어가 찾아질때 수행되는 if문
                                tol = page_cut2(tell)  # page_cut2 함수에서 tol(페이지 끝)을 얻어냄
                                tol = int(tol)  # tol을 int 시켜서 아래의 if문이 수행되게함 (page_num과 tol의 속성을 같게 설정)
                            else:  # '다음' 이라는 단어가 없으면 pass
                                pass
                        if tol == "[":
                            break
                        if page_num == tol:  # page_num이 tol과 같을시 해당 루프문을 빠져나옴
                            break

                        # 배열에 저장된 url을 하나씩 꺼내서 텍스트처리를 하고 DB에 저장한다
                        for url in urls:
                            if (before_url == url):
                                # 사진뉴스를 예외처리
                                pass
                            else :
                                # 해당 url에서 본문내용을 긁음, 그리고 예외처리를 하여 다시 text에 저장한다
                                body = get_body(url)
                                body = clean_text(body)
                                head = get_head(url)
                                email = get_email(url)
                                company = get_company(url)
                                sql = "INSERT INTO po (Sid1, Sid2, Date, Head, Body, email, url, company) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                                curs.execute(sql, (
                                    str(sid1[0]), str(sid_0[i_0]), str(input_date), str(head), str(body), str(email),
                                    str(url),
                                    str(company)))
                                conn.commit()
                                before_url = url
                    except:
                        print("오류발생")
                        print(input_date)
                        pass
                    # 정확히는 모르겠지만 크롤링 텀 주는 부분인듯
                    time.sleep(2)
                    # 해당 html에서 모두 긁으면 다음페이지로 넘어간다
                    page_num += 1
        elif sid1[i] == 101:  # 경제
            for i_1 in range(0, 8):
                page_num = 1
                tol = 99
                while page_num <= max_page_num:
                    try:
                        page_url = "http://news.naver.com/main/list.nhn?sid2=" + str(sid_1[i_1]) + "&sid1=" + str(
                            sid1[i]) + "&mid=shm&mode=LS2D&date=" + str(input_date) + "&page=" + str(page_num) + ""
                        response = requests.get(page_url, headers=headers)
                        html = response.text

                        check = "sid1=" + str(sid1[i]) + "&sid2=" + str(sid_1[i_1]) + ""
                        url_frags = re.findall('<a href="(.*?)"', html)
                        urls = []
                        url_i = ""

                        for url_frag in url_frags:
                            if check in url_frag and "aid" in url_frag:
                                if url_frag == url_i:
                                    pass
                                else:
                                    urls.append(url_frag)
                                    url_i = url_frag

                        # 페이지 커팅
                        tell = page_cut(page_url)  # page_cut 함수에 page_url(url주소)를 넣어서 리턴값을 tell에 저장
                        finding = tell.find(find_next)  # find함수를 사용해 tell에서 '다음'이라는 단어를 찾음 (있으면 해당 문자열번호, 없으면 -1)
                        if tol == 99:  # 번호수인데 1번만 루프 되게 하려고 tol에 99값을 부여함
                            if finding == -1:  # '다음' 이라는 단어가 찾아질때 수행되는 if문
                                tol = page_cut2(tell)  # page_cut2 함수에서 tol(페이지 끝)을 얻어냄
                                tol = int(tol)  # tol을 int 시켜서 아래의 if문이 수행되게함 (page_num과 tol의 속성을 같게 설정)
                            else:  # '다음' 이라는 단어가 없으면 pass
                                pass
                        if tol == "[":
                            break
                        if page_num == tol:  # page_num이 tol과 같을시 해당 루프문을 빠져나옴
                            break

                        for url in urls:
                            if (before_url == url):
                                pass
                            else :
                                body = get_body(url)
                                body = clean_text(body)
                                head = get_head(url)
                                email = get_email(url)
                                company = get_company(url)
                                sql = "INSERT INTO po (Sid1, Sid2, Date, Head, Body, email, url, company) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                                curs.execute(sql, (
                                    str(sid1[1]), str(sid_1[i_1]), str(input_date), str(head), str(body), str(email),
                                    str(url),
                                    str(company)))
                                conn.commit()
                                before_url = url
                    except:
                        print("해당부분 오류발생")
                        print(input_date)
                        print(url)
                        pass

                    time.sleep(2)

                    page_num += 1
        elif sid1[i] == 102:  # 사회
            for i_2 in range(0, 10):
                page_num = 1
                tol = 99
                while page_num <= max_page_num:
                    try:
                        page_url = "http://news.naver.com/main/list.nhn?sid2=" + str(sid_2[i_2]) + "&sid1=" + str(
                            sid1[i]) + "&mid=shm&mode=LS2D&date=" + str(input_date) + "&page=" + str(page_num) + ""
                        response = requests.get(page_url, headers=headers)
                        html = response.text

                        check = "sid1=" + str(sid1[i]) + "&sid2=" + str(sid_2[i_2]) + ""
                        url_frags = re.findall('<a href="(.*?)"', html)
                        urls = []
                        url_i = ""
                        for url_frag in url_frags:
                            if check in url_frag and "aid" in url_frag:
                                if url_frag == url_i:
                                    pass
                                else:
                                    urls.append(url_frag)
                                    url_i = url_frag

                        # 페이지 커팅
                        tell = page_cut(page_url)  # page_cut 함수에 page_url(url주소)를 넣어서 리턴값을 tell에 저장
                        finding = tell.find(find_next)  # find함수를 사용해 tell에서 '다음'이라는 단어를 찾음 (있으면 해당 문자열번호, 없으면 -1)
                        if tol == 99:  # 번호수인데 1번만 루프 되게 하려고 tol에 99값을 부여함
                            if finding == -1:  # '다음' 이라는 단어가 찾아질때 수행되는 if문
                                tol = page_cut2(tell)  # page_cut2 함수에서 tol(페이지 끝)을 얻어냄
                                tol = int(tol)  # tol을 int 시켜서 아래의 if문이 수행되게함 (page_num과 tol의 속성을 같게 설정)
                            else:  # '다음' 이라는 단어가 없으면 pass
                                pass
                        if tol == "[":
                            break
                        if page_num == tol:  # page_num이 tol과 같을시 해당 루프문을 빠져나옴
                            break

                        for url in urls:
                            if (before_url == url):
                                pass
                            else :
                                body = get_body(url)
                                body = clean_text(body)
                                head = get_head(url)
                                email = get_email(url)
                                company = get_company(url)
                                sql = "INSERT INTO po (Sid1, Sid2, Date, Head, Body, email, url, company) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                                curs.execute(sql, (
                                    str(sid1[2]), str(sid_2[i_2]), str(input_date), str(head), str(body), str(email),
                                    str(url),
                                    str(company)))
                                conn.commit()
                                before_url = url
                    except:
                        print("오류발생")
                        print(input_date)
                        print(url)
                        pass

                    time.sleep(2)

                    page_num += 1
        elif sid1[i] == 103:  # 생활/문화
            for i_3 in range(0, 11):
                page_num = 1
                tol = 99
                while page_num <= max_page_num:
                    try:
                        page_url = "http://news.naver.com/main/list.nhn?sid2=" + str(sid_3[i_3]) + "&sid1=" + str(
                            sid1[i]) + "&mid=shm&mode=LS2D&date=" + str(input_date) + "&page=" + str(page_num) + ""
                        response = requests.get(page_url, headers=headers)
                        html = response.text

                        check = "sid1=" + str(sid1[i]) + "&sid2=" + str(sid_3[i_3]) + ""
                        url_frags = re.findall('<a href="(.*?)"', html)
                        urls = []
                        url_i = ""
                        for url_frag in url_frags:
                            if check in url_frag and "aid" in url_frag:
                                if url_frag == url_i:
                                    pass
                                else:
                                    urls.append(url_frag)
                                    url_i = url_frag

                        # 페이지 커팅
                        tell = page_cut(page_url)  # page_cut 함수에 page_url(url주소)를 넣어서 리턴값을 tell에 저장
                        finding = tell.find(find_next)  # find함수를 사용해 tell에서 '다음'이라는 단어를 찾음 (있으면 해당 문자열번호, 없으면 -1)
                        if tol == 99:  # 번호수인데 1번만 루프 되게 하려고 tol에 99값을 부여함
                            if finding == -1:  # '다음' 이라는 단어가 찾아질때 수행되는 if문
                                tol = page_cut2(tell)  # page_cut2 함수에서 tol(페이지 끝)을 얻어냄
                                tol = int(tol)  # tol을 int 시켜서 아래의 if문이 수행되게함 (page_num과 tol의 속성을 같게 설정)
                            else:  # '다음' 이라는 단어가 없으면 pass
                                pass
                        if tol == "[":
                            break
                        if page_num == tol:  # page_num이 tol과 같을시 해당 루프문을 빠져나옴
                            break

                        for url in urls:
                            if (before_url == url):
                                pass
                            else :
                                body = get_body(url)
                                body = clean_text(body)
                                head = get_head(url)
                                email = get_email(url)
                                company = get_company(url)
                                sql = "INSERT INTO po (Sid1, Sid2, Date, Head, Body, email, url, company) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                                curs.execute(sql, (
                                    str(sid1[3]), str(sid_3[i_3]), str(input_date), str(head), str(body), str(email),
                                    str(url),
                                    str(company)))
                                conn.commit()
                                before_url = url
                    except:
                        print("오류발생")
                        print(input_date)
                        print(url)
                        pass

                    time.sleep(2)

                    page_num += 1
        elif sid1[i] == 104:  # 세계
            for i_4 in range(0, 5):
                page_num = 1
                tol = 99
                while page_num <= max_page_num:
                    try:
                        page_url = "http://news.naver.com/main/list.nhn?sid2=" + str(sid_4[i_4]) + "&sid1=" + str(
                            sid1[i]) + "&mid=shm&mode=LS2D&date=" + str(input_date) + "&page=" + str(page_num) + ""
                        response = requests.get(page_url, headers=headers)
                        html = response.text

                        check = "sid1=" + str(sid1[i]) + "&sid2=" + str(sid_4[i_4]) + ""
                        url_frags = re.findall('<a href="(.*?)"', html)
                        urls = []
                        url_i = ""
                        for url_frag in url_frags:
                            if check in url_frag and "aid" in url_frag:
                                if url_frag == url_i:
                                    pass
                                else:
                                    urls.append(url_frag)
                                    url_i = url_frag

                        # 페이지 커팅
                        tell = page_cut(page_url)  # page_cut 함수에 page_url(url주소)를 넣어서 리턴값을 tell에 저장
                        finding = tell.find(find_next)  # find함수를 사용해 tell에서 '다음'이라는 단어를 찾음 (있으면 해당 문자열번호, 없으면 -1)
                        if tol == 99:  # 번호수인데 1번만 루프 되게 하려고 tol에 99값을 부여함
                            if finding == -1:  # '다음' 이라는 단어가 찾아질때 수행되는 if문
                                tol = page_cut2(tell)  # page_cut2 함수에서 tol(페이지 끝)을 얻어냄
                                tol = int(tol)  # tol을 int 시켜서 아래의 if문이 수행되게함 (page_num과 tol의 속성을 같게 설정)
                            else:  # '다음' 이라는 단어가 없으면 pass
                                pass
                        if tol == "[":
                            break
                        if page_num == tol:  # page_num이 tol과 같을시 해당 루프문을 빠져나옴
                            break

                        for url in urls:
                            if (before_url == url):
                                pass
                            else :
                                body = get_body(url)
                                body = clean_text(body)
                                head = get_head(url)
                                email = get_email(url)
                                company = get_company(url)
                                sql = "INSERT INTO po (Sid1, Sid2, Date, Head, Body, email, url, company) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                                curs.execute(sql, (
                                    str(sid1[4]), str(sid_4[i_4]), str(input_date), str(head), str(body), str(email),
                                    str(url),
                                    str(company)))
                                conn.commit()
                                before_url = url
                    except:
                        print("오류발생")
                        print(input_date)
                        print(url)
                        pass

                    time.sleep(2)

                    page_num += 1
        elif sid1[i] == 105:  # IT/과학
            for i_5 in range(0, 8):
                page_num = 1
                tol = 99
                while page_num <= max_page_num:
                    try:
                        page_url = "http://news.naver.com/main/list.nhn?sid2=" + str(sid_5[i_5]) + "&sid1=" + str(
                            sid1[i]) + "&mid=shm&mode=LS2D&date=" + str(input_date) + "&page=" + str(page_num) + ""
                        response = requests.get(page_url, headers=headers)
                        html = response.text

                        check = "sid1=" + str(sid1[i]) + "&sid2=" + str(sid_5[i_5]) + ""
                        url_frags = re.findall('<a href="(.*?)"', html)
                        urls = []
                        url_i = ""
                        for url_frag in url_frags:
                            if check in url_frag and "aid" in url_frag:
                                if url_frag == url_i:
                                    pass
                                else:
                                    urls.append(url_frag)
                                    url_i = url_frag

                        # 페이지 커팅
                        tell = page_cut(page_url)  # page_cut 함수에 page_url(url주소)를 넣어서 리턴값을 tell에 저장
                        finding = tell.find(find_next)  # find함수를 사용해 tell에서 '다음'이라는 단어를 찾음 (있으면 해당 문자열번호, 없으면 -1)
                        if tol == 99:  # 번호수인데 1번만 루프 되게 하려고 tol에 99값을 부여함
                            if finding == -1:  # '다음' 이라는 단어가 찾아질때 수행되는 if문
                                tol = page_cut2(tell)  # page_cut2 함수에서 tol(페이지 끝)을 얻어냄
                                tol = int(tol)  # tol을 int 시켜서 아래의 if문이 수행되게함 (page_num과 tol의 속성을 같게 설정)
                            else:  # '다음' 이라는 단어가 없으면 pass
                                pass
                        if tol == "[":
                            break
                        if page_num == tol:  # page_num이 tol과 같을시 해당 루프문을 빠져나옴
                            break

                        for url in urls:
                            if (before_url == url):
                                pass
                            else :
                                body = get_body(url)
                                body = clean_text(body)
                                head = get_head(url)
                                email = get_email(url)
                                company = get_company(url)
                                sql = "INSERT INTO po (Sid1, Sid2, Date, Head, Body, email, url, company) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                                curs.execute(sql, (
                                    str(sid1[5]), str(sid_5[i_5]), str(input_date), str(head), str(body), str(email),
                                    str(url),
                                    str(company)))
                                conn.commit()
                                before_url = url
                    except:
                        print("오류발생")
                        print(input_date)
                        print(url)
                        pass

                    time.sleep(2)

                    page_num += 1
        input_date+=1
conn.close()
print("끝")