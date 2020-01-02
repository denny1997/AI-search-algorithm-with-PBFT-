import pygame
import sys
import argparse
import time
import threading
import math
import private_chain
import util

from pygame.locals import *
from maze import Maze
from search import astar_multi

class thread(threading.Thread):
    def __init__(self, threadname,maze,startPos):
        threading.Thread.__init__(self, name=threadname)
        self.maze=maze
        self.startPos=startPos
        self.robotNum=len(maze.getStart())

    def run(self):
        print('%s:Now timestamp is %s'%(self.name,time.time()))
        self.privateChain = private_chain.PrivateChain() #创建私有链
        self.privateChain.map = set(self.maze.getObjectives()) #构建私有地图
        #dic[self.name]=set(self.maze.getObjectives())
        ByzantineSystem[self.name]=self.privateChain #私有链加入拜占庭共识系统
        ByzantineSystem[self.name].sysout()

        # while len(dic)<self.robotNum:
        #     pass
        while len(ByzantineSystem)<self.robotNum:  #等待所有节点上线
            pass
        count={}
        # for i in dic:
        #     if tuple(dic[i]) in count:
        #         count[tuple(dic[i])]+=1
        #     else:
        #         count[tuple(dic[i])]=1
        for i in ByzantineSystem:  #地图拜占庭共识开始
            if tuple(ByzantineSystem[i].map) in count:
                count[tuple(ByzantineSystem[i].map)]+=1
            else:
                count[tuple(ByzantineSystem[i].map)]=1
        self.privateChain.map=set(max(count,key=lambda x:count[x])) #完成拜占庭共识，对私有链中的地图进行修正，依照少数服从多数规则
        ByzantineSystem[self.name].sysout()

        #weightPos[self.startPos] = self.startPos
        self.privateChain.weightPos=self.startPos #路径重心初始化

        util.syncthreads(ByzantineSystem,self.privateChain) #线程同步
        ByzantineSystem[self.name].sysout()

        # while len(weightPos)<self.robotNum:
        #     pass
        #waitCount[self.name]=0
        self.startPoints=self.maze.getStart()[:]
        print("from" + self.name, id(self.startPoints))
        self.startPoints.remove(self.startPos)
        self.newObjectPos=[]

        # modification starts
        #pendingTaskNum[self.name] = len(self.newObjectPos)
        self.privateChain.pendingTaskNum = len(self.newObjectPos)
        objectNum = len(self.privateChain.map)
        agentNum = len(ByzantineSystem)
        averageNum = math.ceil(objectNum/agentNum)


        # modification ends
        print("from" + self.name, self.startPoints,self.startPos)
        # for i in dic[self.name]:
        for i in self.privateChain.map:
            eagerness = (averageNum - len(self.newObjectPos))/averageNum
            if eagerness<0:
                eagerness = 0
            #eagerWait[self.name]=0
            #eagernessGlob[self.startPos] = (1.5-eagerness)**5
            self.privateChain.eagernessGlob = (1.5-eagerness)**5
            # eagerWait[self.name] = 1
            # while sum(eagerWait.values()) < agentNum:
            #     pass
            util.syncthreads(ByzantineSystem,self.privateChain) #线程同步
            #dis = abs(weightPos[self.startPos][0] - i[0]) + abs(weightPos[self.startPos][1] - i[1])
            dis=abs(self.privateChain.weightPos[0]-i[0])+abs(self.privateChain.weightPos[1]-i[1]) #计算当前节点到目标点的距离
            #print(eagernessGlob)
            #dis = dis * eagernessGlob[self.startPos]
            dis = dis * self.privateChain.eagernessGlob
            # print(self.name, dis)
            for p in self.startPoints: #计算其他点到目标点是否有更短距离
                # if abs(weightPos[p][0]-i[0])+abs(weightPos[p][1]-i[1])<dis/eagernessGlob[p]:
                if abs(ByzantineSystem[str(p)].weightPos[0] - i[0]) + abs(ByzantineSystem[str(p)].weightPos[1] - i[1]) < dis / ByzantineSystem[str(p)].eagernessGlob:
                    # waitCount[self.name]=1
                    # while waitCount[self.name]:
                    #     pass
                    util.semaphoreWait(self.privateChain) #有更短距离，线程中断，等待该节点的信号量通知
                    break
                # elif abs(weightPos[p][0]-i[0])+abs(weightPos[p][1]-i[1])==dis/eagernessGlob[p] and weightPos[p][0]<weightPos[self.startPos][0]:
                elif abs(ByzantineSystem[str(p)].weightPos[0] - i[0]) + abs(ByzantineSystem[str(p)].weightPos[1] - i[1]) == dis / ByzantineSystem[str(p)].eagernessGlob and ByzantineSystem[str(p)].weightPos[0] < self.privateChain.weightPos[0]:
                    # waitCount[self.name] = 1
                    # while waitCount[self.name]:
                    #     pass
                    util.semaphoreWait(self.privateChain)
                    break
                # elif abs(weightPos[p][0]-i[0])+abs(weightPos[p][1]-i[1])==dis/eagernessGlob[p] and weightPos[p][0]==weightPos[self.startPos][0] and weightPos[p][1]<weightPos[self.startPos][1]:
                elif abs(ByzantineSystem[str(p)].weightPos[0] - i[0]) + abs(ByzantineSystem[str(p)].weightPos[1] - i[1]) == dis / ByzantineSystem[str(p)].eagernessGlob and ByzantineSystem[str(p)].weightPos[0] == self.privateChain.weightPos[0] and ByzantineSystem[str(p)].weightPos[1] < self.privateChain.weightPos[1]:
                    # waitCount[self.name] = 1
                    # while waitCount[self.name]:
                    #     pass
                    util.semaphoreWait(self.privateChain)
                    break
            else: #更新属于自己的目标集合
                self.newObjectPos.append(i)
                #pendingTaskNum[self.name] = len(self.newObjectPos)
                self.privateChain.pendingTaskNum = len(self.newObjectPos)
                # while sum(waitCount[x] for x in waitCount)<self.robotNum-1:
                #     pass
                util.semaphoreWaitToNotify(ByzantineSystem) #等待其他线程同步
                self.privateChain.weightPos=((self.privateChain.weightPos[0]+i[0])//2,(self.privateChain.weightPos[1]+i[1])//2) #更新重心位置
                # for k in waitCount:
                #     waitCount[k]=0
                util.semaphoreNotify(ByzantineSystem) #信号量通知其他线程继续运行
        print("from"+self.name,self.newObjectPos)
        self.path = astar_multi(self.maze, self.startPos,self.newObjectPos) #调用A*算法，返回路径
        self.privateChain.path=self.path

class Application:
    def __init__(self, scale=20, fps=30,alt_color=False):
        self.running = True
        self.displaySurface = None
        self.scale = scale
        self.fps = fps
        self.windowTitle = "Multi-A* with PBFT Algorithm demo "
        self.alt_color = alt_color

    # Initializes the pygame context and certain properties of the maze
    def initialize(self, filename):
        self.windowTitle += filename

        self.maze = Maze(filename)
        self.gridDim = self.maze.getDimensions()

        self.windowHeight = self.gridDim[0] * self.scale
        self.windowWidth = self.gridDim[1] * self.scale

        self.blockSizeX = int(self.windowWidth / self.gridDim[1])
        self.blockSizeY = int(self.windowHeight / self.gridDim[0])

    # Once the application is initiated, execute is in charge of drawing the game and dealing with the game loop
    def execute(self, filename, save):
        self.initialize(filename)

        if self.maze is None:
            print("No maze created")
            raise SystemExit

        threads = []
        for a,b in self.maze.getStart():  # 线程个数
            threads.append(thread("("+str(a)+", "+str(b)+")",self.maze,(a,b)))
        for t in threads:  # 开启线程
            t.start()
        for t in threads:  # 阻塞线程
            t.join()
        print('END')
        #print([x.path for x in ByzantineSystem.values()])
        print(max(len(x.path) for x in ByzantineSystem.values()))

        pygame.init()
        self.displaySurface = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self.displaySurface.fill((255, 255, 255))
        pygame.display.flip()
        pygame.display.set_caption(self.windowTitle)

        self.drawMaze()
        self.drawStart()
        self.drawObjective()


        #self.drawPath(path)
        self.drawPath(ByzantineSystem)

        self.drawMaze()
        self.drawStart()
        self.drawObjective()

        pygame.display.flip()
        if save is not None:
            pygame.image.save(self.displaySurface, save)
            self.running = False

        clock = pygame.time.Clock()

        while self.running:
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            clock.tick(self.fps)

            if (keys[K_ESCAPE]):
                    raise SystemExit

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit

    # Implementation of a color scheme for the path taken
    # If Red-Green does not work for you while debugging (for e.g. color blindness),
    # you can edit the start and end colors by picking appropriate (R, G, B) values
    def getColor(self, pathLength, index,alt_color):
        # start_color = (r0, g0, b0)
        # end_color = (r1, g1, b1)
        # example:
        if alt_color:
            start_color = (64, 224, 208)
            end_color = (139, 0, 139)
        else:
            start_color = (255, 0, 0)
            end_color = (0, 255, 0)
        # default:


        r_step = (end_color[0] - start_color[0]) / pathLength
        g_step = (end_color[1] - start_color[1]) / pathLength
        b_step = (end_color[2] - start_color[2]) / pathLength

        red = start_color[0] + index * r_step
        green = start_color[1] + index * g_step
        blue = start_color[2] + index * b_step

        return (red, green, blue)

    # Draws the path (given as a list of (row, col) tuples) to the display context
    # def drawPath(self, path):
    #     maxlen=max(len(path[x]) for x in path)
    #     for i in range(maxlen):
    #         for j in path:
    #             if len(path[j])>i:
    #                 color = self.getColor(len(path[j]), i, self.alt_color)
    #                 self.drawCircle(path[j][i][0], path[j][i][1], color)
    #         pygame.display.flip()
    #         time.sleep(0.5)
    def drawPath(self, system):
        maxlen=max(len(x.path) for x in system.values())
        for i in range(maxlen):
            for j in system.values():
                if len(j.path)>i:
                    color = self.getColor(len(j.path), i, self.alt_color)
                    self.drawCircle(j.path[i][0], j.path[i][1], color)
            pygame.display.flip()
            time.sleep(0.5)

    # Simple wrapper for drawing a wall as a rectangle
    def drawWall(self, row, col):
        pygame.draw.rect(self.displaySurface, (0, 0, 0), (col * self.blockSizeX, row * self.blockSizeY, self.blockSizeX, self.blockSizeY), 0)

    # Simple wrapper for drawing a circle
    def drawCircle(self, row, col, color, radius=None):
        if radius is None:
            radius = min(self.blockSizeX, self.blockSizeY) / 4
        pygame.draw.circle(self.displaySurface, color, (int(col * self.blockSizeX + self.blockSizeX / 2), int(row * self.blockSizeY + self.blockSizeY / 2)), int(radius))


    def drawSquare(self, row, col, color):
        pygame.draw.rect(self.displaySurface, color , (col * self.blockSizeX, row * self.blockSizeY, self.blockSizeX, self.blockSizeY), 0)

    # Draws the objectives to the display context
    def drawObjective(self):
        for obj in self.maze.getObjectives():
            self.drawCircle(obj[0], obj[1], (0, 0, 0))

    # Draws start location of path
    def drawStart(self):
        start = self.maze.getStart()
        for row,col in start:
            pygame.draw.rect(self.displaySurface, (0,0,255), (col * self.blockSizeX + self.blockSizeX/4, row * self.blockSizeY + self.blockSizeY/4, self.blockSizeX * 0.5, self.blockSizeY * 0.5), 0)

    # Draws the full maze to the display context
    def drawMaze(self):
        for row in range(self.gridDim[0]):
            for col in range(self.gridDim[1]):
                if self.maze.isWall(row, col):
                    self.drawWall(row, col)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='CS440 MP1 Search')

    parser.add_argument('filename',
                        help='path to maze file [REQUIRED]')
    parser.add_argument('--method', dest="search", type=str, default = "bfs",
                        choices = ["bfs", "dfs", "astar","astar_multi","extra"],
                        help='search method - default bfs')
    parser.add_argument('--scale', dest="scale", type=int, default = 20,
                        help='scale - default: 20')
    parser.add_argument('--fps', dest="fps", type=int, default = 30,
                        help='fps for the display - default 30')
    parser.add_argument('--human', default = False, action = "store_true",
                        help='flag for human playable - default False')
    parser.add_argument('--save', dest="save", type=str, default = None,
                        help='save output to image file - default not saved')
    parser.add_argument('--altcolor', dest="altcolor", default = False, action = "store_true",
                        help='View in an alternate color scheme.')

    ByzantineSystem={}
    # dic={}  # all objects
    # path={} # tasks for each agent
    # weightPos={} # Weight
    # waitCount={}
    #
    # pendingTaskNum = {}
    # eagernessGlob = {}
    # eagerWait = {}

    args = parser.parse_args()
    app = Application(args.scale, args.fps,args.altcolor)
    app.execute(args.filename, args.save)
