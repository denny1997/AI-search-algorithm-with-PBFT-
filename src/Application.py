import argparse

from maze import Maze

from ByzantineNode import ByzantineNode
from Represent import Represent
from message_queue import MessageQueue
import util

class Application:
    def __init__(self, scale=20, fps=30,alt_color=False):
        self.represent = Represent(scale,fps,alt_color)

    # Initializes the pygame context and certain properties of the maze
    def initialize(self, filename):

        self.maze = Maze(filename)
        self.gridDim = self.maze.getDimensions()
        self.represent.initialize(filename,self.gridDim,self.maze)
        self.messageQueue = MessageQueue(app.maze.getStart())

    # Once the application is initiated, execute is in charge of drawing the game and dealing with the game loop
    def execute(self, filename, save):
        util.clearLagacyRecord()

        self.initialize(filename)

        if self.maze is None:
            print("No maze created")
            raise SystemExit

        threads = []
        for a,b in self.maze.getStart():  # 线程个数
            threads.append(ByzantineNode("("+str(a)+", "+str(b)+")",filename,(a,b), self.messageQueue))
        for t in threads:  # 开启线程
            t.start()
        for t in threads:  # 阻塞线程
            t.join()
        print('END')

        print(max(len(x) for x in self.messageQueue.path.values()))

        self.represent.draw(self.messageQueue.path.values(),save)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='CS440 MP1 Search')

    parser.add_argument('filename',
                        help='path to maze file [REQUIRED]')
    parser.add_argument('--scale', dest="scale", type=int, default = 20,
                        help='scale - default: 20')
    parser.add_argument('--fps', dest="fps", type=int, default = 30,
                        help='fps for the display - default 30')
    parser.add_argument('--save', dest="save", type=str, default = None,
                        help='save output to image file - default not saved')
    parser.add_argument('--altcolor', dest="altcolor", default = False, action = "store_true",
                        help='View in an alternate color scheme.')

    args = parser.parse_args()

    app = Application(args.scale, args.fps,args.altcolor)

    app.execute(args.filename, args.save)
