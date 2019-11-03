from requests_html import HTMLSession
import time
import re
import random
import pymysql


def get_request(url):
    '''
    使用 Session 能够跨请求保持某些参数。
    它也会在同一个 Session 实例发出的所有请求之间保持 cookie
    '''

    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36"
    ]

    header = {
        'User-agent': random.choice(user_agent_list),
    }

    cookie = {
        'cookie': ''
    }

    time.sleep(random.randint(5, 15))
    return session.get(url, header=header, timeout=3)


def get_doubanid(url, count):
    # douban_id pool
    cur_url = url.format(count * 20)
    try:
        item = get_request(cur_url).json()
    except:
        print('get_json_wrong')
        return

    for i in range(20):
        dict = item['data'][i]  # 取出字典中 'data' 下第 [i] 部电影的信息
        urlname = dict['url']
        # title = dict['title']
        # rate = dict['rate']
        douban_id = urlname.split('/')[-2]  # 根据id的规律，裁剪出douban_id
        douban_id_list.append(douban_id)
        dict['douban_id'] = douban_id
        # 存储
        movie[douban_id] = dict  # 以电影的豆瓣ID作为key

        # store_movie_info(dict)  # 存入数据库 已经爬完了


def get_comment(id, count):
    # middlewares
    comment_url = init_CMT_url.format(id, count * 20)

    try:
        comment_item = get_request(comment_url)
    except:
        print('get_comment_url_wrong')
        return

    for CMT_num in range(1, 21):
        # 现在为第CMT_num个短评

        # # 获取短评页的html
        # comment = comment_item.html.html
        # 评论内容
        css_content = '#comments > div:nth-child({}) > div.comment > p > span'.format(CMT_num)
        if comment_item.html.find(css_content, first=True):
            comment_content = comment_item.html.find(css_content, first=True).text
        else:
            print('This page has no information')
            return
        # 评论星级 有可能该影评人没打星，所以用正则
        css_star = '#comments > div:nth-child({}) > div.comment > h3 > span.comment-info'.format(CMT_num)
        html_star = comment_item.html.find(css_star, first=True).html
        pat_star = '<span class="allstar(\\d)0 rating" title'
        comment_star = re.findall(pat_star, html_star)
        if comment_star:
            comment_star = comment_star[0]
        else:
            comment_star = 'NaN'  # 该影评人没打分，当作NaN处理
        # 评论人id
        css_id = '#comments > div:nth-child({}) > div.comment > h3 > span.comment-info > a'.format(CMT_num)
        comment_id = comment_item.html.find(css_id, first=True).text
        # 评论时间
        css_time = '#comments > div:nth-child({}) > div.comment > h3 > span.comment-info > span.comment-time'.format(CMT_num)
        comment_time = comment_item.html.find(css_time, first=True).text
        # 评论点赞数
        css_votes = '#comments > div:nth-child({}) > div.comment > h3 > span.comment-vote > span'.format(CMT_num)
        comment_votes = comment_item.html.find(css_votes, first=True).text

        # 存储
        temp_dict = {'comment_id': comment_id,
                     'comment_content': comment_content,
                     'comment_star': comment_star,
                     'comment_time': comment_time,
                     'comment_votes': comment_votes}
        comment_list.append(temp_dict)
        store_movie_comment(temp_dict)

        time.sleep(2)


# def store_data(temp):
#     conn = pymysql.connect(
#         host='localhost',  # mysql服务器地址
#         port=3306,  # 端口号
#         user='root',  # 用户名
#         passwd='43210',  # 密码
#         db='douban_movie',  # 数据库名称
#         charset='utf8',  # 连接编码，根据需要填写
#     )
#     cur = conn.cursor()  # 创建并返回游标
#     # 创建movie_info表
#     sql_movie_info = "CREATE TABLE IF NOT EXISTS " \
#           "movie_info (movie_id VARCHAR(15),title VARCHAR(32),rate VARCHAR(5),url VARCHAR(100));"
#     cur.execute(sql_movie_info)  # 执行上述sql命令
#     # 创建movie_comment表
#     sql_movie_comment = "CREATE TABLE IF NOT EXISTS " \
#           "movie_comment (comment_id VARCHAR(15),content VARCHAR(1000),star VARCHAR(5),time VARCHAR(20),votes VARCHAR(10),title VARCHAR(32));"
#     cur.execute(sql_movie_comment)  # 执行上述sql命令
#
#     movie_id = temp['douban_id']
#     title = temp['title']
#     rate = temp['rate']
#     url = temp['url']
#
#     comment_id = temp['comment']['comment_id']
#     content = temp['comment']['comment_content']
#     star = temp['comment']['comment_star']
#     time = temp['comment']['comment_time']
#     votes = temp['comment']['comment_votes']
#
#     sql_insert_info = "insert into movie_info (movie_id,title,rate,url) values (" + "'" + movie_id + "'" + "," + "'" + title + "'" + "," + "'" + rate + "'" + "," + "'" + url + "'" + ");"
#     sql_insert_comment = "insert into movie_comment (comment_id,content,star,time,votes,title) values (" + "'" + comment_id + "'" + "," + "'" + content + "'" + "," + "'" + star + "'" + "," + "'" + time + "'" + "," + "'" + votes + "'" + "," + "'" + title + "'" + ");"
#     # sql_insert =("insert into daxue (code,charge,level,name,remark,prov) values (%s,%s,%s,%s,%s,%s);",value)
#     # sql_insert = sql_insert.encode("utf8")
#
#     cur.execute(sql_insert_info)  # 执行上述sql命令
#     cur.execute(sql_insert_comment)  # 执行上述sql命令
#
#     conn.commit()
#     conn.close()


def store_movie_info(temp):
    conn = pymysql.connect(
        host='localhost',  # mysql服务器地址
        port=3306,  # 端口号
        user='root',  # 用户名
        passwd='43210',  # 密码
        db='douban_movie',  # 数据库名称
        charset='utf8mb4',  # 连接编码，根据需要填写
    )
    cur = conn.cursor()  # 创建并返回游标
    # 创建movie_info表
    sql_movie_info = "CREATE TABLE IF NOT EXISTS " \
          "movie_info (movie_id VARCHAR(15),title VARCHAR(100),rate VARCHAR(5),url VARCHAR(100));"
    cur.execute(sql_movie_info)  # 执行上述sql命令

    movie_id = temp['douban_id']
    title = temp['title']
    rate = temp['rate']
    url = temp['url']
    # INSERT IGNORE INTO 过滤重复记录
    sql_insert_info = "INSERT IGNORE INTO movie_info (movie_id,title,rate,url) values (" + "'" + movie_id + "'" + "," + "'" + title + "'" + "," + "'" + rate + "'" + "," + "'" + url + "'" + ");"
    # sql_insert =("insert into daxue (code,charge,level,name,remark,prov) values (%s,%s,%s,%s,%s,%s);",value)
    # sql_insert = sql_insert.encode("utf8")

    cur.execute(sql_insert_info)  # 执行上述sql命令

    conn.commit()
    conn.close()


def store_movie_comment(temp):
    conn = pymysql.connect(
        host='localhost',  # mysql服务器地址
        port=3306,  # 端口号
        user='root',  # 用户名
        passwd='43210',  # 密码
        db='douban_movie',  # 数据库名称
        charset='utf8mb4',  # 连接编码，根据需要填写
    )
    cur = conn.cursor()  # 创建并返回游标
    # 创建movie_comment表
    sql_movie_comment = "CREATE TABLE IF NOT EXISTS " \
          "movie_comment (comment_id VARCHAR(15),content VARCHAR(5000),star VARCHAR(5),time VARCHAR(20),votes VARCHAR(10),movie_id VARCHAR(32));"
    cur.execute(sql_movie_comment)  # 执行上述sql命令

    comment_id = temp['comment_id']
    content = temp['comment_content']
    star = temp['comment_star']
    time = temp['comment_time']
    votes = temp['comment_votes']

    # 进行转义处理
    sql_insert_comment = "INSERT IGNORE INTO movie_comment (comment_id,content,star,time,votes,movie_id) " \
                         "values('%s','%s','%s','%s','%s','%s')"

    data = (pymysql.escape_string(comment_id), pymysql.escape_string(content), star, time, votes, douban_id)
    cur.execute(sql_insert_comment % data)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    session = HTMLSession()
    # 分类首页Request_url
    init_url = 'https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags=&start={}&genres=%E5%8A%A8%E7%94%BB'
    # 豆瓣id对应的评论页url 第一个为douban_id，第二个为迭代
    init_CMT_url = 'https://movie.douban.com/subject/{}/comments?start={}&limit=20'
    # 用于存储豆瓣ID
    douban_id_list = []
    # 用于存储电影信息
    movie = {}
    # 爬取的全部电影
    all_list = []

    for i in range(1, 50):  # 设置完主键之后，改成range(1,50)
        # 获取动漫类电影的豆瓣id
        get_doubanid(init_url, i)

    for douban_id in douban_id_list:
        comment_list = []
        for CMT_count in range(10):
            # 加载下一页，现在为第CMT_count页
            get_comment(douban_id, CMT_count)
            print(douban_id, '：第', CMT_count, "页")

        # 存储影评
        temp_mov = movie[douban_id]  # 当前所读取的电影
        temp_mov['comment'] = comment_list  # 将该部电影的所有短评加入字典temp_mov

        # store_data(temp_mov)

        all_list.append(temp_mov)
