
import os,sys,base64
import string,random
class DeviceInformation:
    def __init__(self):
        pass

    def GetDeviceMac(self):
        str = ''
        if sys.platform == "win32":

            for line in os.popen('ipconfig /all'):
                if  line.strip() != '':
                    str += line.strip()+'\n'
        basestr = base64.b64encode(str.encode()).decode()
        if basestr[-1:]=='=':
            basestr = basestr[:-1]
            if basestr[-1:]=='=':
                basestr = basestr[:-1]

        letter = string.ascii_lowercase
        key = ''
        enc = ''
        for i in range(0,len(basestr)):

            c = letter[random.randint(0, 25)]
            enc += chr(ord(c) + ord(basestr[i]))
            key +=  c

        value = basestr
        return  key,enc
    def encode(self,key,enc):
        if len(key) != len(enc):
            print("密文和密钥不匹配")
            return None
        value = ''
        for i in range(0,len(enc)):
            value += chr(ord(enc[i]) - ord(key[i]))
            pass
        return value

if __name__=="__main__":
    test = DeviceInformation()
    key,enc = test.GetDeviceMac()
    print(enc)