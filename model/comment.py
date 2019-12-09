import  json

class Comment(object):
    def __init__(self,name="",date=None,score=0,context=""):
        self.name = name
        self.date = date
        self.score = score
        self.context = context

    def toJSON(self):
        return json.dumps(self,default=lambda o: o.__dict__)