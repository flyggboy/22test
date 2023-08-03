from random import randint
import math
from gmpy2 import invert
import random
import binascii
iv = "7380166F4914B2B9172442D7DA8A0600A96F30BC163138AAE38DEE4DB0FB0E4E"
T = (0x79cc4519, 0x7a879d8a)
index = "0123456789ABCDEF"
W = []
W_ = []

#SM2 encode
def LeftShift(num, left):
    return (((num << left)&((1<<32)-1)) | (num >> (32 - left)))


def Ti(x):
    return (T[1]) if x > 15 else (T[0])


def FFi(x, y, z, n):
    return ((x & y) | (y & z) | (x & z)) if n > 15 else (x ^ y ^ z)


def GGi(x, y, z, n):
    return ((x & y) | ((~x) & z)) if n > 15 else (x ^ y ^ z)


def P0(x):
    return (x ^ LeftShift(x, 9) ^ LeftShift(x, 17))


def P1(x):
    return (x ^ LeftShift(x, 15) ^ LeftShift(x, 23))


def padding(n, size,s):
    s=list(s)
    s.append('8')
    for i in range(0, n // 4):
        s.append("0")
    s=''.join(s)
    s+=hex(size)[2:].zfill(16).upper()
    return n,s





def Extend(B):
    for i in range(0, 16):
        W.append(int(B[(8 * i):(8 * i) + 8],16)%((1<<32)))

    for i in range(16, 68):
        W.append(int(hex((P1(W[i - 16] ^ W[i - 9] ^ LeftShift(W[i - 3], 15))) ^ (LeftShift(W[i - 13], 7) ^ W[i - 6])),16)%((1<<32)))

    for i in range(0, 64):
        W_.append(int(hex(W[i] ^ W[i + 4]),16)%((1<<32)))

index=['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
def uint_to_str(num,k = 8) :
    s=""
    for i in range(0,k):
        s+=index[num % 16]
        num//=16
    return  s[::-1]

def update(V, Bi):
    temp = []
    temp1 = []
    for i in range(0, 8):
        t="0x"+V[8 * i: (8 * i) + 8]
        temp.append(int(t,16))
        temp1.append(temp[i])
    for i in range(0, 64):
        SS1 = LeftShift((LeftShift(temp[0], 12) + temp[4] + LeftShift(Ti(i), i % 32))%(1<<32), 7)
        SS2 = (SS1 ^ LeftShift(temp[0], 12))
        t=(FFi(temp[0], temp[1], temp[2], i)+temp[3])%((1<<32))
        TT1 = (FFi(temp[0], temp[1], temp[2], i) + temp[3] + SS2 + W_[i])%(1<<32)
        TT2 = (GGi(temp[4], temp[5], temp[6], i) + temp[7] + SS1 + W[i])%(1<<32)
        temp[3] = temp[2]
        temp[2] = (LeftShift(temp[1], 9))
        temp[1] = temp[0]
        temp[0] = TT1
        temp[7] = temp[6]
        temp[6] = LeftShift(temp[5], 19)
        temp[5] = temp[4]
        temp[4] = P0(TT2)
    result = ""
    for i in range(0, 8):
        result += uint_to_str(temp1[i] ^ temp[i])
    return result.upper()


def Hash(m):
    size = len(m) * 4
    num = (size + 1) % 512
    t = 448 - num if num < 448 else 960 - num
    k ,m= padding(t,size,m)
    t=len(m)
    group_number = (size + 65 + k) // 512
    B = []
    IV = []
    IV.append(iv)
    for i in range(0, group_number):
        B.append(m[128 * i:128 * i + 128])
        Extend(B[i])
        IV.append(update(IV[i], B[i]))
        W.clear()
        W_.clear()
    temp = IV[group_number]
    return temp


p=0xBDB6F4FE3E8B1D9E0DA8C0D46F4C318CEFE4AFE3B6B8551F        #192  或  256
a=0xBB8E5E8FBC115E139FE6A814FE48AAA6F0ADA1AA5DF91985
b=0x1854BEBDC31B21B7AEFC80AB0ECD10D5B1B3308E6DBF11C1
n=0xBDB6F4FE3E8B1D9E0DA8C0D40FC962195DFAE76F56564677
Gx=0x4AD5F7048DE709AD51236DE65E4D4B482C836DC6E4106640
Gy=0x02BB3A02D4AAADACAE24817A4CA3A1B014B5270432DB27D2

da=0x58892B807074F53FBF67288A1DFAA1AC313455FE60355AFD

def add(x1,y1,x2,y2):
    if x1==x2 and y1==p-y2:
        return False
    if x1!=x2:
        lamda=((y2-y1)*invert(x2-x1, p))%p
    else:
        lamda=(((3*x1*x1+a)%p)*invert(2*y1, p))%p
    x3=(lamda*lamda-x1-x2)%p
    y3=(lamda*(x1-x3)-y1)%p
    return x3,y3

def mul_add(x,y,k):
    k=bin(k)[2:]
    qx,qy=x,y
    for i in range(1,len(k)):
        qx,qy=add(qx, qy, qx, qy)
        if k[i]=='1':
            qx,qy=add(qx, qy, x, y)
    return (qx,qy)

def KDF(z,klen):
    ct=1
    k=''
    for i in range(math.ceil(klen/256)):
        t=hex(int(z+'{:032b}'.format(ct),2))[2:]
        k=k+hex(int(Hash(t),16))[2:]
        ct=ct+1
    k='0'*((256-(len(bin(int(k,16))[2:])%256))%256)+bin(int(k,16))[2:]
    return k[:klen]

h=1

def encrypt(m):
    plen=len(hex(p)[2:])
    m='0'*((4-(len(bin(int(m.encode().hex(),16))[2:])%4))%4)+bin(int(m.encode().hex(),16))[2:]
    klen=len(m)
    while True:
        #k=randint(1,n)
        k=0x384F30353073AEECE7A1654330A96204D37982A3E15B2CB5
        while k==da:
            k=randint(1, n)
        x2,y2=mul_add(Pa[0],Pa[1],k)
        if(len(hex(p)[2:])*4==192):
            x2,y2='{:0192b}'.format(x2),'{:0192b}'.format(y2)
        else:
            x2, y2 = '{:0256b}'.format(x2), '{:0256b}'.format(y2)
        t=KDF(x2+y2, klen)
        if int(t,2)!=0:
            break
    x1,y1=mul_add(Gx, Gy,k)
    x1,y1=(plen-len(hex(x1)[2:]))*'0'+hex(x1)[2:],(plen-len(hex(y1)[2:]))*'0'+hex(y1)[2:]
    c1=x1+y1
    c2=((klen//4)-len(hex(int(m,2)^int(t,2))[2:]))*'0'+hex(int(m,2)^int(t,2))[2:]
    c3=Hash(hex(int(x2+m+y2,2))[2:].upper())
    return c1,c2,c3

def decrypt(c1,c2,c3):
    x1,y1=int(c1[:len(c1)//2],16),int(c1[len(c1)//2:],16)
    if pow(y1,2,p)!=(pow(x1,3,p)+a*x1+b)%p:
        return False
    x2,y2=mul_add(x1, y1, da)
    if (len(hex(p)[2:]) * 4 == 192):
        x2, y2 = '{:0192b}'.format(x2), '{:0192b}'.format(y2)
    else:
        x2, y2 = '{:0256b}'.format(x2), '{:0256b}'.format(y2)
    klen=len(c2)*4
    t=KDF(x2+y2, klen)
    if int(t,2)==0:
        return False
    m='0'*(klen-len(bin(int(c2,16)^int(t,2))[2:]))+bin(int(c2,16)^int(t,2))[2:]
    u=Hash(hex(int(x2+m+y2,2))[2:])
    if u!=c3:
        return False
    return hex(int(m,2))[2:]

#key-exchange
IDa="ALICE123@YAHOO.COM"
Pka=mul_add(Gx,Gy,da)

IDb="BILL456@YAHOO.COM"
Pkb=mul_add(Gx,Gy,db)

w=math.ceil(math.ceil(math.log2(n))/2)-1
h=1
klen=128



def B_key_exchange(*Ra):
    rb = 0x33FE21940342161C55619C4A0C060293D543C80AF19748CE176D83477DE71C80
    Rb = mul_add(Gx, Gy, rb)
    ida = hex(int(binascii.b2a_hex(IDa.encode()).decode(), 16)).upper()[2:]
    ENTLa = '{:04X}'.format(len(ida) * 4)
    ma = ENTLa + ida + '{:064X}'.format(a) + '{:064X}'.format(b) + '{:064X}'.format(Gx) + '{:064X}'.format(
        Gy) + '{:064X}'.format(Pka[0]) + '{:064X}'.format(Pka[1])
    Za = Hash(ma)
    idb = hex(int(binascii.b2a_hex(IDb.encode()).decode(), 16)).upper()[2:]
    ENTLb = '{:04X}'.format(len(idb) * 4)
    mb = ENTLb + idb + '{:064X}'.format(a) + '{:064X}'.format(b) + '{:064X}'.format(Gx) + '{:064X}'.format(
        Gy) + '{:064X}'.format(Pkb[0]) + '{:064X}'.format(Pkb[1])
    Zb = Hash(mb)
    x2=((1<<w)+(Rb[0]&((1<<w)-1)))%(1<<128)
    tb=(db+x2*rb)%n
    x1=((1<<w)+(Ra[0]&((1<<w)-1)))%(1<<128)
    x,y=mul_add(Ra[0],Ra[1],x1)
    x,y=add(Pka[0],Pka[1],x,y)
    V=mul_add(x,y,h*tb)
    t1, t2 = '{:064X}'.format(V[0]), '{:064X}'.format(V[1])
    m=t1+t2+Za+Zb
    m='{:01024b}'.format(int(m,16))
    Kb=KDF(m,klen)
    return hex(int(Kb,2)).upper()[2:]

def A_key_exchange(*Rb):
    ra = 0x83A2C9C8B96E5AF70BD480B472409A9A327257F1EBB73F5B073354B248668563
    Ra = mul_add(Gx, Gy, ra)
    ida = hex(int(binascii.b2a_hex(IDa.encode()).decode(), 16)).upper()[2:]
    ENTLa = '{:04X}'.format(len(ida) * 4)
    ma = ENTLa + ida + '{:064X}'.format(a) + '{:064X}'.format(b) + '{:064X}'.format(Gx) + '{:064X}'.format(
        Gy) + '{:064X}'.format(Pka[0]) + '{:064X}'.format(Pka[1])
    Za = Hash(ma)
    idb = hex(int(binascii.b2a_hex(IDb.encode()).decode(), 16)).upper()[2:]
    ENTLb = '{:04X}'.format(len(idb) * 4)
    mb = ENTLb + idb + '{:064X}'.format(a) + '{:064X}'.format(b) + '{:064X}'.format(Gx) + '{:064X}'.format(
        Gy) + '{:064X}'.format(Pkb[0]) + '{:064X}'.format(Pkb[1])
    Zb = Hash(mb)
    x1=((1<<w)+(Ra[0]&((1<<w)-1)))%(1<<128)
    ta=(da+x1*ra)%n
    x2=((1<<w)+(Rb[0]&((1<<w)-1)))%(1<<128)
    x,y=mul_add(Rb[0],Rb[1],x2)
    x,y=add(Pkb[0],Pkb[1],x,y)
    U=mul_add(x,y,h*ta)
    t1, t2 = '{:064X}'.format(U[0]), '{:064X}'.format(U[1])
    m=t1+t2+Za+Zb
    m='{:01024b}'.format(int(m,16))
    Ka=KDF(m,klen)
    return hex(int(Ka, 2)).upper()[2:]

#sign
def signature(m,Za):
    m1=Za+m
    e=Hash(m1)
    #k=randint(1,n)
    k=0x6CB28D99385C175C94F94E934817663FC176D925DD72B727260DBAAE1FB2F96F
    x1,y1=mul_add(Gx,Gy,k)
    r=(int(e,16)+x1)%n
    s=(invert(1+da,n)*(k-r*da))%n
    return (hex(r)[2:].upper(),hex(s)[2:].upper())

def Verify(r,s,Za,m,Pa):
    if int(r,16) not in range(1,n-1):
        return False
    if int(s,16) not in range(1,n-1):
        return False
    m1=Za+m
    e=Hash(m1)
    t=(int(r,16)+int(s,16))%n
    if t==0:
        return False
    x1,y1=mul_add(Pa[0],Pa[1],t)
    x2,y2=mul_add(Gx,Gy,int(s,16))
    x1,y1=add(x2,y2,x1,y1)
    R=(int(e,16)+x1)%n
    if(hex(R)[2:].upper()==r):
        return True
    return False



#ra=randint(1,n)
ra=0x83A2C9C8B96E5AF70BD480B472409A9A327257F1EBB73F5B073354B248668563
Ra=mul_add(Gx,Gy,ra)



Pa=mul_add(Gx,Gy,da)
m="huangtingchenyi"
c1,c2,c3=encrypt(m)
m2=decrypt(c1,c2,c3)
m2=binascii.a2b_hex(m2)
print(m2)

#rb=randint(1,n)
rb=0x33FE21940342161C55619C4A0C060293D543C80AF19748CE176D83477DE71C80
Rb=mul_add(Gx,Gy,rb)
print(B_key_exchange(*Ra))
print(A_key_exchange(*Rb))

#sign
Pax,Pay=mul_add(Gx,Gy,da)
Pa=(Pax,Pay)
m="Liu"
m=hex(int(binascii.b2a_hex(m.encode()).decode(),16)).upper()[2:]
IDa="ALICE123@YAHOO.COM" 
ida=hex(int(binascii.b2a_hex(IDa.encode()).decode(),16)).upper()[2:]
ENTLa='{:04X}'.format(len(ida)*4)
m1=ENTLa+ida+'{:064X}'.format(a)+'{:064X}'.format(b)+'{:064X}'.format(Gx)+'{:064X}'.format(Gy)+'{:064X}'.format(Pa[0])+'{:064X}'.format(Pa[1])
Za=hex(int(Hash(m1),16))[2:].upper()
sign=signature(m,Za)
print(Verify(*sign,Za,m,Pa))
