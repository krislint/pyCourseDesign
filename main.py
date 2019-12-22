import requests
from bs4 import BeautifulSoup
from model import Movie,Comment
import  json,datetime
import statistics

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

def generatorFileName()->str:
    return datetime.datetime.now().strftime("%Y-%m-%d") + "maoyan.json";

def WriteToJSON(obj)->(str,bool):
    filename =generatorFileName()
    try:
        with open(filename,"w",encoding="utf-8") as f:
            json_str = json.dumps(obj,default=lambda o:o.__dict__,ensure_ascii=False,indent=4)
            f.write(json_str)
    except Exception as  ex:
        return  str(ex.args), False

    return filename,True

def FirstLevelParse(res:requests.Response,domain = "https://maoyan.com"):
    """

    :param res: requests.Response
    :return: movie link list
    :rtype: list
    """
    bs = BeautifulSoup(res.content, features="html.parser")
    links = bs.select("p.name a")
    score_list = bs.select(".score")
    movielink_list = []
    for link in links:
        href =  domain+link["href"]
        movielink_list.append(href)

    return movielink_list,score_list


def PaseMovieItem(item_str:str)->Movie:
    # item_str = replace_font(item_str)
    movie = Movie()
    bs = BeautifulSoup(item_str,features="html.parser")
    movie.tags = bs.select_one("body > div.banner > div > div.celeInfo-right.clearfix > div.movie-brief-container > h3").string
    # score = bs.select_one(".movie-stats-container .score .info-num span.stonefont").string #.encode("utf-8")
    # cumulative_sales = bs.select_one("body > div.banner > div > div.celeInfo-right.clearfix > div.movie-stats-container > div:nth-child(2) > div").text
    # 人家有字体仿反扒技术 如要获取字体中的数据 有两种思路： 1.破解人家的字体生成算法 2. OCR 识别字体中的数据
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

def SeconLevelParse(movies:list,score_list:list):

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
        movie_obj.score = score_list[cnt-1].text
        movie_list.append(movie_obj)

    return  movie_list

def main():
    # 获取数据
    url = "https://maoyan.com/board/7"

    response = req_session.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("无法成功访问,请修改 cookie等参数")

    movielink_list,score_list = FirstLevelParse(response)

    movie_list =  SeconLevelParse(movielink_list,score_list)

    msg,res = WriteToJSON(movie_list)
    if res:
        print("数据保存成功 保存地址为%s"%(msg))
    else:
        print("数据保存失败， 错误原因为%s"%(msg))


    # 数据统计分析
def analysis_data(file:str=''):
    from pathlib import Path
    from collections import  Counter
    import  jieba
    from wordcloud import WordCloud
    from matplotlib  import pyplot as plt

    if not file:file = generatorFileName()
    dic = {}
    
    path = Path(file)
    if  not path.exists():
        print("file is not exist")
        exit(0)

    with open(file,'r',encoding='utf-8')as f:
        dic = json.load(f)

    m =  Movie()

    def analysize_movie(movie:Movie):
        counter = Counter()
        for comm in m.comments:
            after_filter =  filter(lambda word: len(word)>=2,jieba.cut(comm['context']))
            counter.update(after_filter)
            
        wordcloud = WordCloud(font_path='simsun.ttf',background_color="white").fit_words(counter)
        plt.imshow(wordcloud)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.title(m.name)
        plt.axis("off")
        plt.show()

    for movie in dic:

        m.dict_to_object(movie)
        analysize_movie(m)


if __name__ == '__main__':
    import  sys
    if len(sys.argv)>2:
        action = sys.argv[2]
    else:
        action = input("Please enter the action crawler or analysis: ")
    if action == "crawler":
        main()
    elif action == "analysis":
        analysis_data('2019-12-12maoyan.json')
    else:
        print("error enter")