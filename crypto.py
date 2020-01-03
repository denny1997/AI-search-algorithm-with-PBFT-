from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
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
    return (privateKey,publicKey)

def sign(privateKey,msg):
    rsakey = RSA.importKey(privateKey)
    signer = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(msg.encode("utf8"))
    sign = signer.sign(digest)
    signature = base64.b64encode(sign)
    return signature

def verify(publicKey,msg,signature):
    rsakey = RSA.importKey(publicKey)
    verifier = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    # Assumes the data is base64 encoded to begin with
    digest.update(msg.encode("utf8"))
    is_verify = verifier.verify(digest, base64.b64decode(signature))
    return is_verify

def getHash(msg):
    digest = SHA.new()
    digest.update(msg.encode("utf8"))
    return digest.hexdigest()

# private,public = generateKeyPairs()
# signature=sign(private,str((1,2)))
# print(signature)
# print(verify(public,str((1,2)),signature))
#
# print(getHash("32dw"))


# # 加密和解密
# print "2、加密和解密"
# # Master使用Ghost的公钥对内容进行rsa 加密
#
# message = 'hello ghost, this is a plian text'
# print "message: " + message
# with open('ghost-public.pem') as f:
#     key = f.read()
#     rsakey = RSA.importKey(key)
#     cipher = Cipher_pkcs1_v1_5.new(rsakey)
#     cipher_text = base64.b64encode(cipher.encrypt(message))
#     print "加密（encrypt）"
#     print cipher_text
#
# # Ghost使用自己的私钥对内容进行rsa 解密
#
# with open('ghost-private.pem') as f:
#     key = f.read()
#     rsakey = RSA.importKey(key)
#     cipher = Cipher_pkcs1_v1_5.new(rsakey)
#     text = cipher.decrypt(base64.b64decode(cipher_text), random_generator)
#
#     print "解密（decrypt）"
#     print "message:" + text
#
#     assert text == message, 'decrypt falied'
#
# # 签名与验签
# print "3、 签名与验签"
#
# # Master 使用自己的私钥对内容进行签名
# print "签名"
# with open('master-private.pem') as f:
#     key = f.read()
#     rsakey = RSA.importKey(key)
#     signer = Signature_pkcs1_v1_5.new(rsakey)
#     digest = SHA.new()
#     digest.update(message)
#     sign = signer.sign(digest)
#     signature = base64.b64encode(sign)
#
# print signature
#
# print "验签"
# with open('master-public.pem') as f:
#     key = f.read()
#     rsakey = RSA.importKey(key)
#     verifier = Signature_pkcs1_v1_5.new(rsakey)
#     digest = SHA.new()
#     # Assumes the data is base64 encoded to begin with
#     digest.update(message)
#     is_verify = verifier.verify(digest, base64.b64decode(signature))
#
# print is_verify