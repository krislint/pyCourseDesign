import requests
from bs4 import BeautifulSoup
from model import Movie
import  json,datetime

req_session = requests.session()

headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.3988.0 Safari/537.36",
    "Cookie":"__mta=156080772.1575508263479.1575793798268.1575793801316.19; uuid_n_v=v1; uuid=0CC2BCC016FC11EAACB1A96ED7E7765B381829D5F28D40FE9EBFDCA27AC991AB; _lxsdk_cuid=16ed39c3ef69-09d1cbc2e1f142-6f547821-144000-16ed39c3ef7c8; _lxsdk=0CC2BCC016FC11EAACB1A96ED7E7765B381829D5F28D40FE9EBFDCA27AC991AB; __mta=156080772.1575508263479.1575508645127.1575508741443.10; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; _csrf=37a3527877aaab9479cc0e4bc424de13bb7cb23a82db0a67182d4e3018cbbe2d; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1575508263,1575508741,1575508741,1575781779; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1575793801; _lxsdk_s=16ee493ea4e-2d3-84-4e8%7C%7C8"
    ,"Host": "maoyan.com",
    "Upgrade-Insecure-Requests":"1",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"

}

def WriteToJSON(obj)->(str,bool):
    filename = datetime.datetime.now().strftime("%Y-%m-%d") + "maoyan.json"
    try:
        with open(filename,"w",encoding="utf-8") as f:
            json.dump(obj,f)
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
    movielink_list = []
    for link in links:
        href =  domain+link["href"]
        movielink_list.append(href)

    return movielink_list


def PaseMovieItem(item_str:str)->Movie:
    bs = BeautifulSoup(item_str,features="html.parser")


    movie = Movie()

    return movie
def SeconLevelParse(movies:list):

    movie_list = []
    for movie in movies:
       res =  req_session.get(movie)
       if (res.status_code != 200):
           print(movie+" 请求错误")
           continue
       movie_obj =  PaseMovieItem(res.text)
       movie_list.append(movie_obj)

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