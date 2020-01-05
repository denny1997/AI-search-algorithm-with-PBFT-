import os
import shutil


def savePrivateKey(node,key):
    if not os.path.exists("../keys/"+node):
        os.makedirs("../keys/"+node)
    fp=open("../keys/"+node+"/rsa_private.pem","w")
    fp.write(key)

def savePublicKeys(node,keys):
    if not os.path.exists("../keys/"+node):
        os.makedirs("../keys/"+node)
    fp=open("../keys/"+node+"/rsa_public.pem","w")
    for key in keys:
        fp.write(key+": "+keys[key]+"\n")

def saveBlock(node,block,idx):
    if not os.path.exists("../blocks/"+node):
        os.makedirs("../blocks/"+node)
    fp = open("../blocks/" + node + "/block_"+str(idx)+".block", "w")
    fp.write(str(block))

def clearLagacyRecord():
    shutil.rmtree("../keys")
    shutil.rmtree("../blocks")
    os.mkdir("../keys")
    os.mkdir("../blocks")