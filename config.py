import json
import copy
import bloon

class GameConfig:
    def __init__(self,filename):
        js = json.load(open(filename))
        self.path = js['path']
        self.levels = js['levels']
        self.pathimg = js['pathimg']
        self.remark = ""
        self.reward = 0
        self.currentlevel = []
        self.parse_next_level()
        self.done = False
        self.intermission = False
    def next_bloon(self):
        if not len(self.currentlevel):
            if len(self.levels):
                self.intermission = True
            else:
                self.done = True
        else:
            if type(self.currentlevel[0]) is int:
                if self.currentlevel[0] == 0:
                    self.currentlevel.pop(0)
                    return self.next_bloon()
                else:
                    self.currentlevel[0] -= 1
                    return None
            else:
                return self.currentlevel.pop(0)
    def end_intermission(self):
        self.intermission = False
        self.parse_next_level()
    def parse_next_level(self):
        js = self.levels.pop(0)
        self.remark = js["remark"]
        self.reward = js["reward"]
        def go(js):
            if(type(js) is list):
                result = []
                for i in map(go,js):
                    if(type(i) is list):
                        result += i
                    else:
                        result.append(i)
                return result
            if(js["what"] == "normal"):
                return bloon.Bloon(copy.deepcopy(self.path),js["level"])
            elif(js["what"] == "wait"):
                return js["time"]
            elif(js["what"] == "repeat"):
                result = []
                for i in range(js["times"]):
                    result += go(js["seq"])
                return result
            elif(js["what"] == "tank"):
                return bloon.TankBloon(copy.deepcopy(self.path),js["hp"])
        self.currentlevel = go(js["waves"])
