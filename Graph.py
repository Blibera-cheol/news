import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from konlpy.tag import Twitter, Kkma
import pymysql

# MySql 연결
conn = pymysql.connect(host='localhost', user='root', password='root123', db='test', charset='utf8')

curs = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from test_cycle"      # 뉴스테이블에 접근
curs.execute(sql)
rows = curs.fetchall()

x = []
y = []
name_select = []
num_count = 0
color = ["r","b","g","y","black","g","b","r"]
j=811
hi=0

# 루프용
i = 0

for row in rows:
    name = row['name']

    name_select.append(name)


# 중복제거
name_select = list(set(name_select))
# 배열개수
num_count = len(name_select)

while i < num_count :
    for row in rows:
        if name_select[i]==row['name']:
            year = row['year']
            num = row['num']
            x.append(year)
            y.append(num)
            if hi<row['num']:
                hi = row['num']

    plt.subplot(j)
    plt.plot(x, y, color[i],label=name_select[i])
    j+=1
    i+=1
    x = []
    y = []
    hi=0
    plt.legend()

plt.show()


