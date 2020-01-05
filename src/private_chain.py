from block import Block
from crypto import getHash
import copy

class PrivateChain:
    def __init__(self):
        self.blocks=[]
        self.blocks.append(Block())
        self.curIndex=0
        self.headBlock=self.blocks[self.curIndex]
        self.curBlock=self.blocks[self.curIndex]

    def generateNextBlock(self):
        nextBlock=copy.deepcopy(self.curBlock)
        nextBlock.lastBlockHash = getHash(str(self.curBlock))
        self.blocks.append(nextBlock)
        self.curIndex+=1
        self.curBlock = self.blocks[self.curIndex]


# p = PrivateChain()
# p.curBlock.map={4:6}
# p.generateNextBlock()


