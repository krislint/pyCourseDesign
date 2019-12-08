import  datetime

class Movie(object):
    def __init__(self, name="", star="", score=0, releasetime=None,Plot="",tags="",cumulative_sales=0):
        self.name = name
        self.star = star
        self.score = score
        self.tags = tags
        self.cumulative_sales = cumulative_sales
        self.Plot = Plot
        self.comments = []
        self.releasetime = releasetime if releasetime else datetime.datetime.now()
