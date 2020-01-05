from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64

# 生成 private key and pulic key
def generateKeyPairs():
    # 伪随机数生成器
    random_generator = Random.new().read
    # rsa算法生成实例
    rsa = RSA.generate(1024, random_generator)
    privateKey=rsa.exportKey()
    publicKey=rsa.publickey().exportKey()
    return (bytes.decode(privateKey),bytes.decode(publicKey))

def sign(privateKey,msg):
    rsakey = RSA.importKey(str.encode(privateKey))
    signer = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(msg.encode("utf8"))
    sign = signer.sign(digest)
    signature = base64.b64encode(sign)
    return bytes.decode(signature)

def verify(publicKey,msg,signature):
    rsakey = RSA.importKey(str.encode(publicKey))
    verifier = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    # Assumes the data is base64 encoded to begin with
    digest.update(msg.encode("utf8"))
    is_verify = verifier.verify(digest, base64.b64decode(str.encode(signature)))
    return is_verify

def getHash(msg):
    digest = SHA.new()
    digest.update(msg.encode("utf8"))
    return digest.hexdigest()

# private,public = generateKeyPairs()
# print(private)
# signature=sign(private,str((1,2)))
# print(signature)
# print(verify(public,str((1,2)),signature))
#
# print(getHash("32dw"))
