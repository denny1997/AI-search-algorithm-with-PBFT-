import threading
import time
from maze import Maze

from search import astar_multi


class TraditionalNode(threading.Thread):
    def __init__(self, threadname,filename,startPos,messageQueue):
        threading.Thread.__init__(self, name=threadname)
        self.maze=Maze(filename+self.name)
        self.startPos=startPos
        self.index = self.maze.getStart().index(tuple(eval(self.name)))
        self.robotNum=len(self.maze.getStart())
        self.messageQueue = messageQueue

    def run(self):
        print('%s:Now timestamp is %s'%(self.name,time.time()))

        print("from"+self.name)

        l = len(self.maze.getObjectives())
        num = len(self.maze.getStart())
        if self.index+1 == num:
            self.messageQueue.path[self.name] = astar_multi(self.maze, self.startPos, self.maze.getObjectives()[self.index * l // num:])  # 调用A*算法，返回路径
        else:
            self.messageQueue.path[self.name]=astar_multi(self.maze, self.startPos,self.maze.getObjectives()[self.index*l//num:(self.index+1)*l//num]) #调用A*算法，返回路径


