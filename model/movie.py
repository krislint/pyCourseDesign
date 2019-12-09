import  datetime
import  json
class Movie(object):
    def __init__(self, name="", stars="", score=0, releasetime=None,Plot="",tags="",cumulative_sales=0):
        self.name = name
        self.stars = stars
        self.score = score
        self.tags = tags
        self.cumulative_sales = cumulative_sales
        self.Plot = Plot
        self.comments = []
        self.releasetime = releasetime if releasetime else ""

    def toJSON(self):
        return json.dumps(self,default=lambda o: o.__dict__)