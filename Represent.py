import pygame
from pygame.locals import *
import time

from ByzantineSystem import ByzantineSystem

class Represent():
    def __init__(self, scale=20, fps=30,alt_color=False):
        self.running = True
        self.displaySurface = None
        self.scale = scale
        self.fps = fps
        self.windowTitle = "Multi-A* with PBFT Algorithm demo "
        self.alt_color = alt_color

    # Initializes the pygame context and certain properties of the maze
    def initialize(self, filename, gridDim, maze):
        self.windowTitle += filename
        self.gridDim=gridDim
        self.maze=maze

        self.windowHeight = gridDim[0] * self.scale
        self.windowWidth = gridDim[1] * self.scale

        self.blockSizeX = int(self.windowWidth / gridDim[1])
        self.blockSizeY = int(self.windowHeight / gridDim[0])

        # Implementation of a color scheme for the path taken
        # If Red-Green does not work for you while debugging (for e.g. color blindness),
        # you can edit the start and end colors by picking appropriate (R, G, B) values
    def getColor(self, pathLength, index, alt_color):
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
        maxlen = max(len(x.curBlock.path) for x in system.values())
        for i in range(maxlen):
            for j in system.values():
                if len(j.curBlock.path) > i:
                    color = self.getColor(len(j.curBlock.path), i, self.alt_color)
                    self.drawCircle(j.curBlock.path[i][0], j.curBlock.path[i][1], color)
            pygame.display.flip()
            time.sleep(0.5)

    # Simple wrapper for drawing a wall as a rectangle
    def drawWall(self, row, col):
        pygame.draw.rect(self.displaySurface, (0, 0, 0),
                         (col * self.blockSizeX, row * self.blockSizeY, self.blockSizeX, self.blockSizeY), 0)

    # Simple wrapper for drawing a circle
    def drawCircle(self, row, col, color, radius=None):
        if radius is None:
            radius = min(self.blockSizeX, self.blockSizeY) / 4
        pygame.draw.circle(self.displaySurface, color, (
        int(col * self.blockSizeX + self.blockSizeX / 2), int(row * self.blockSizeY + self.blockSizeY / 2)),
                           int(radius))

    def drawSquare(self, row, col, color):
        pygame.draw.rect(self.displaySurface, color,
                         (col * self.blockSizeX, row * self.blockSizeY, self.blockSizeX, self.blockSizeY), 0)

    # Draws the objectives to the display context
    def drawObjective(self):
        for obj in self.maze.getObjectives():
            self.drawCircle(obj[0], obj[1], (0, 0, 0))

    # Draws start location of path
    def drawStart(self):
        start = self.maze.getStart()
        for row, col in start:
            pygame.draw.rect(self.displaySurface, (0, 0, 255), (
            col * self.blockSizeX + self.blockSizeX / 4, row * self.blockSizeY + self.blockSizeY / 4,
            self.blockSizeX * 0.5, self.blockSizeY * 0.5), 0)

    # Draws the full maze to the display context
    def drawMaze(self):
        for row in range(self.gridDim[0]):
            for col in range(self.gridDim[1]):
                if self.maze.isWall(row, col):
                    self.drawWall(row, col)

    def draw(self,save):
        pygame.init()
        self.displaySurface = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self.displaySurface.fill((255, 255, 255))
        pygame.display.flip()
        pygame.display.set_caption(self.windowTitle)

        self.drawMaze()
        self.drawStart()
        self.drawObjective()

        # self.drawPath(path)
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