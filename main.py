import requests
from bs4 import BeautifulSoup
from model import Movie,Comment
import  json,datetime
import re
from fontTools.ttLib import TTFont
import  os
req_session = requests.session()

headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.3988.0 Safari/537.36",
    "Host": "maoyan.com",
    "Upgrade-Insecure-Requests":"1",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Mode":"navigate",
    "Sec-Fetch-Site":"none",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Cache-Control":"max-age=0",
    "Connection":"keep-alive"
}

def WriteToJSON(obj)->(str,bool):
    filename = datetime.datetime.now().strftime("%Y-%m-%d") + "maoyan.json"
    try:
        with open(filename,"w",encoding="utf-8") as f:
            json_str = json.dumps(obj,default=lambda o:o.__dict__,ensure_ascii=False,indent=4)
            f.write(json_str)
    except Exception as  ex:
        return  str(ex.args), False

    return filename,True


def replace_font(response):
    base_font = TTFont('./fonts/base.woff')
    # base_font.saveXML('base_font.xml')
    base_dict = {'uniEC33': '7', 'uniF5EE': '4', 'uniEFA7': '1', 'uniEB46': '8', 'uniE57C': '9',
                 'uniEED6': '3', 'uniF3F7': '2', 'uniF548': '6', 'uniF10C': '5', 'uniECDC': '0'}
    base_list = base_font.getGlyphOrder()[2:]

    font_file = re.findall(r'vfile\.meituan\.net\/colorstone\/(\w+\.woff)', response)[0]
    font_url = 'http://vfile.meituan.net/colorstone/' + font_file

    new_file = req_session.get(font_url)
    with open('./fonts/' + font_file, 'wb') as f:
        f.write(new_file.content)

    new_font = TTFont('./fonts/' + font_file)
    # new_font.saveXML('new_font.xml')
    new_list = new_font.getGlyphOrder()[2:]

    new_dict = {}
    for name2 in new_list:
        obj2 = new_font['glyf'][name2]
        for name1 in base_list:
            obj1 = base_font['glyf'][name1]
            if obj1 == obj2:
                new_dict[name2] = base_dict[name1]
    try:
        for i in new_list:
            pattern = i.replace('uni', f'&#x').lower() + ';'
            response = response.replace(pattern, new_dict[i])
    except Exception as ex:
        pass
    finally:
        os.remove('./fonts/' + font_file)
    return response

def FirstLevelParse(res:requests.Response,domain = "https://maoyan.com"):
    """

    :param res: requests.Response
    :return: movie link list
    :rtype: list
    """
    bs = BeautifulSoup(res.content, features="html.parser")
    links = bs.select("p.name a")
    movielink_list = []
    for link in links:
        href =  domain+link["href"]
        movielink_list.append(href)

    return movielink_list


def PaseMovieItem(item_str:str)->Movie:
    # item_str = replace_font(item_str)
    movie = Movie()
    bs = BeautifulSoup(item_str,features="html.parser")
    movie.tags = bs.select_one("body > div.banner > div > div.celeInfo-right.clearfix > div.movie-brief-container > h3").string
    score = bs.select_one(".movie-stats-container .score .info-num span.stonefont").string #.encode("utf-8")
    cumulative_sales = bs.select_one("body > div.banner > div > div.celeInfo-right.clearfix > div.movie-stats-container > div:nth-child(2) > div").string

    movie.score = score
    movie.cumulative_sales = cumulative_sales
    movie.tags = bs.select_one("body > div.banner > div > div.celeInfo-right.clearfix > div.movie-brief-container > ul > li:nth-child(1)").string
    movie.name = bs.select_one("body > div.banner > div > div.celeInfo-right.clearfix > div.movie-brief-container > h3").string
    movie.releasetime = bs.select_one("body > div.banner > div > div.celeInfo-right.clearfix > div.movie-brief-container > ul > li:nth-child(3)").string

    movie.Plot = bs.select_one(".dra").string
    stars = bs.select(".celebrity-group:nth-child(2) ul.celebrity-list.clearfix .info a")[:5]
    movie.stars = ",".join([e.string.replace("\n","").replace(" ","") for e in stars])

    # 解析评论
    comment_list = []
    comments_divs = bs.select(".main")

    def comment_parse(comments_tag)->Comment:
        com = Comment()

        com.name  = comments_tag.select_one(".user .name").string
        com.score = len(comments_tag.select(".score-star li i.active"))
        com.context = comments_tag.select_one(".comment-content").string
        com.date = comments_tag.select_one(".time")["title"]
        return com
    for comm in comments_divs:
        comm_ent =  comment_parse(comm)
        comment_list.append(comm_ent)

    movie.comments = comment_list

    return movie
def SeconLevelParse(movies:list):

    movie_list = []
    cnt = 0
    for movie in movies:
        cnt += 1
        print("开始解析第 %s 个网页 %s"%(cnt,movie))
        res =  req_session.get(movie,headers=headers)
        if (res.status_code != 200):
           print(movie+" 请求错误" +str(res.status_code)+ str(res.request))
           continue
        movie_obj =  PaseMovieItem(res.text)
        movie_list.append(movie_obj)

    return  movie_list

def main():
    # 获取数据
    url = "https://maoyan.com/board/7"

    response = req_session.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("无法成功访问,请修改 cookie等参数")

    movielink_list = FirstLevelParse(response)

    movie_list =  SeconLevelParse(movielink_list)

    msg,res = WriteToJSON(movie_list)
    if res:
        print("数据保存成功 保存地址为%s"%(msg))
    else:
        print("数据保存失败， 错误原因为%s"%(msg))


    # 数据统计分析

if __name__ == '__main__':
    main()