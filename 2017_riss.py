from bs4 import BeautifulSoup
import urllib.request
import time
import re
import requests
import pymysql
import datetime

# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='root123', db='test', charset='utf8')

# Connection 으로부터 Cursor 생성
curs = conn.cursor()

# 모르겠음
user_agent = "'Mozilla/5.0"
headers = {"User-Agent": user_agent}

# 기술이름
name = "led"

# 루프용
i=0
j=0
zero = 0

url_kor = "http://www.riss.kr/search/Search.do?detailSearch=false&viewYn=OP&query=" + str(name) + "&queryText=&strQuery=" + str(name) + "&iStartCount=0&iGroupView=5&icate=re_a_kor&colName=re_a_kor&exQuery=&pageScale=20&strSort=RANK&order=%2FDESC&onHanja=false&keywordOption=0&searchGubun=true&p_year1=&p_year2=&dorg_storage=&mat_type=&mat_subtype=&fulltext_kind=&t_gubun=&learning_type=&language_code=&ccl_code=&language=&inside_outside=&fric_yn=&image_yn=&regnm=&gubun=&kdc=&resultSearch=false&listFlag=&h_groupByField="
html_kor = requests.get(str(url_kor))
html_kor = html_kor.text
soup_kor = BeautifulSoup(html_kor, 'html.parser')
soup_kor = str(soup_kor)
tag_kor = soup_kor.split("발행년도")[1]
tag_kor = tag_kor.split('SearchGroupContent_3">')[1]
tag_kor = tag_kor.split("언어종류")[0]
print(tag_kor)

tag_kor_num = tag_kor.split("hidden")[2]
tag_kor_num = tag_kor_num.split('="')[1]
tag_kor_num = tag_kor_num.split('"')[0]

tag_kor_num = int(tag_kor_num)

url_eng = "http://www.riss.kr/search/Search.do?detailSearch=false&viewYn=OP&query=" + str(name) + "&queryText=&strQuery=" + str(name) + "&iStartCount=0&iGroupView=5&icate=all&colName=re_a_over&exQuery=&pageScale=20&strSort=RANK&order=%2FDESC&onHanja=false&keywordOption=0&searchGubun=true&p_year1=&p_year2=&dorg_storage=&mat_type=&mat_subtype=&fulltext_kind=&t_gubun=&learning_type=&language_code=&ccl_code=&language=&inside_outside=&fric_yn=&image_yn=&regnm=&gubun=&kdc=&resultSearch=false&listFlag=&h_groupByField=&ids=&titles=&taxonIds=&description_kos=&kind="
html_eng = requests.get(str(url_eng))
html_eng = html_eng.text
soup_eng = BeautifulSoup(html_eng, 'html.parser')
soup_eng = str(soup_eng)
tag_eng = soup_eng.split("발행년도")[1]
tag_eng = tag_eng.split('SearchGroupContent_2">')[1]
tag_eng = tag_eng.split("언어종류")[0]
print(tag_eng)
tag_eng_num = tag_eng.split("hidden")[2]
tag_eng_num = tag_eng_num.split('="')[1]
tag_eng_num = tag_eng_num.split('"')[0]

tag_eng_num = int(tag_eng_num)

while i <= (tag_kor_num-1):
    try:
        if zero == 0:
            tag_year = tag_kor.split("<em>")[i]
            tag_year = tag_year.split("label")[1]
            tag_year = tag_year.split(">")[1]
            tag_year = tag_year.lstrip()
            zero += 1
        elif zero == 1:
            tag_year = tag_kor.split("<em>")[i]
            tag_year = tag_year.split("<label")[1]
            tag_year = tag_year.split('">')[1]
            tag_year = tag_year.split("<")[0]
            zero += 1
        else:
            tag_year = tag_kor.split("<em>")[i]
            tag_year = tag_year.split('">')[1]

        j=j+1
        tag_count = tag_kor.split("<em>(")[j]
        tag_count = tag_count.split(")</em>")[0]

        tag_yearr = int(tag_year)
        tag_countt = int(tag_count)
        print(i)
        print(tag_kor_num)
        sql = "INSERT INTO test_cycle (name, year, num) VALUES (%s, %s, %s)"
        curs.execute(sql,(str(name), int(tag_yearr), int(tag_countt)))
        conn.commit()
        i+=1
    except:
        print("오류발생")
        print(tag_yearr)
        i += 1
        pass
i=0
j=0
zero = 0

while i <= (tag_eng_num-1):
    try:
        if zero == 0:
            tag_year = tag_eng.split("<em>")[i]
            tag_year = tag_year.split("label")[1]
            tag_year = tag_year.split(">")[1]
            tag_year = tag_year.lstrip()
            zero += 1
        elif zero == 1:
            tag_year = tag_eng.split("<em>")[i]
            tag_year = tag_year.split("<label")[1]
            tag_year = tag_year.split('">')[1]
            tag_year = tag_year.split("<")[0]
            zero += 1
        else:
            tag_year = tag_eng.split("<em>")[i]
            tag_year = tag_year.split('">')[1]

        j=j+1
        tag_count = tag_eng.split("<em>(")[j]
        tag_count = tag_count.split(")</em>")[0]
        tag_yearr = int(tag_year)
        tag_countt = int(tag_count)

        sql = "INSERT INTO test_cycle_10 (name, year, num) VALUES (%s, %s, %s)"
        curs.execute(sql,(str(name), int(tag_yearr), int(tag_countt)))
        conn.commit()
        i+=1
    except:
        print("오류발생")
        print(tag_yearr)
        i += 1
        pass
