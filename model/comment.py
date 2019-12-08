

class Comment(object):
    def __init__(self,name="",date=None,score=0,context=""):
        self.name = name
        self.date = date
        self.score = score
        self.context = context