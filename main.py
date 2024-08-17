# -*- coding: utf-8 -*-
# 混淆c++代码用
# by 丁豪 2024-08-06
import sys, shutil, os, string, platform
import re
import random
import csv
import codecs

FuncsInfo = {}

KeySign = [
    "&",
    "*",
    "\t"
]

SystemFuncStarts = [
    "CC",
    "//",
    "lua_",
    "toluafix_",
    "luaval_"
]

SystemWordsContain = [
    "//",
    "virtual"
]

IgnoreFiles = [
    "md5.h",
    "md5.cpp"
]

StaticFuncs = {}

WordList=[]
PinYinList=[]
usedWordList = {}
usedLetterList = {} # 每次读取新文件时，建议清空
# 随机名字生成库
def produceRandomWords(dirpath):
    global WordList
    global PinYinList
    with open(os.path.join(dirpath,'res/EnWords.csv'),'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            WordList.append(row["word"])

    with open(os.path.join(dirpath,'res/EnPinYin.csv'), 'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            PinYinList.append(row["word"])

####################随机名字生成##################
def getRandomWord():
    return WordList[random.randint(0,len(WordList)-1)]

def getRandomPinYin():
    return PinYinList[random.randint(0,len(PinYinList)-1)]

def getRandomLetter(count):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    letters = ""
    for _ in range(count):
        letters += random.choice(alphabet)
    return letters

def getRandomName(fname):
    global usedWordList
    name = None
    namelist = []
    count = random.randint(1,4)
    for i in range(count):
        namelist.append(getRandomWord())
    count = random.randint(1,2)
    for i in range(count):
        namelist.append(getRandomPinYin())
    # 打乱列表元素的顺序
    random.shuffle(namelist)
    for word in namelist:
        if name is None:
            name = word
        else:
            name = f"{name}_{word}"
        # elif random.randint(1,10) > 5:
        #     name = f"{name}_{word}"
        # else:
        #     name = f"{name}{word}"
    if  usedWordList.get(name) :
        name = getRandomName()
    else:
        usedWordList[name] = 1
    return name

def getShortRandomName():
    global usedWordList
    global usedLetterList
    onlyletter = random.randint(1,100)
    if onlyletter >= 85:
        # 仅需字母
        letterCount = round((random.randint(1,5) + random.randint(1,5)) / 2)
        letter = getRandomLetter(letterCount)
        while (usedLetterList.get(letter) == 1):
            print("chong fu le!!!!!!!!!!!!!!!!!!!!"+letter)
            letterCount = random.randint(1,5)
            letter = getRandomLetter(letterCount)
        usedLetterList[letter] = 1
        return letter
    name = None
    namelist = []
    namelist.append(getRandomWord())
    needpy = random.randint(1,100)
    if needpy >= 90:
        namelist.append(getRandomPinYin())
    # 打乱列表元素的顺序
    random.shuffle(namelist)
    for word in namelist:
        if name is None:
            name = word
        else:
            name = f"{name}_{word}"
        # elif random.randint(1,10) > 5:
        #     name = f"{name}_{word}"
        # else:
        #     name = f"{name}{word}"
    name += getRandomLetter(random.randint(0,2))
    if  usedWordList.get(name) :
        name = getShortRandomName()
    else:
        usedWordList[name] = 1
    return name

############################################

def getFuncName(strparam):
    words = re.findall(r'([a-zA-Z0-9_.]*)', strparam)
    retstr = strparam
    for word in words:
        if len(word) > 0:
            retstr = word
    return retstr

def cleanString(strparam):
    # 输入： int data = 0, int data = 0x03, int data = 0.3125, int *mapData=nullptr, char D=NULL,double ccc, float ddd=0 )
    # 输出 intintintint*chardoublefloat
    strparam = strparam.replace(")", "")
    strparam = strparam.replace(";", "")

    # 有些函数申明变量的时候会赋值，这里需要把=后面的数值布尔null字符串都去掉
    current = 0
    retstr = ""
    curStr = ""
    while current < len(strparam):
        curStr = strparam[current]
        if curStr != "=":
            retstr += curStr
        else:
            current += 1
            while current < len(strparam):
                curStr = strparam[current]
                if curStr == " ":
                    retstr += curStr
                    current += 1
                elif curStr >= '0' and curStr <= '9':
                    current += 1
                    if current >= len(strparam):
                        break
                    nextStr = strparam[current]
                    if curStr == '0' and (nextStr == 'x' or nextStr == 'X'):
                        current += 1
                        while current < len(strparam):
                            if strparam[current] >= '0' and strparam[current] <= '9':
                                current += 1
                            elif strparam[current] >= 'a' and strparam[current] <= 'f':
                                current += 1
                            elif strparam[current] >= 'A' and strparam[current] <= 'F':
                                current += 1
                            else:
                                break
                    else:
                        hasDot = False
                        while current < len(strparam):
                            if strparam[current] >= '0' and strparam[current] <= '9':
                                current += 1
                            elif strparam[current] == '.' and hasDot == False:
                                hasDot = True
                                current += 1
                            else:
                                break
                elif curStr == "'" or curStr == '"':
                    current += 1
                    while current < len(strparam):
                        curstrstr = strparam[current]
                        if curstrstr == curStr:
                            current += 1
                            break
                        else:
                            current += 1
                elif curStr == "n" and strparam[current:(current+7)] == "nullptr":
                    # 这里少加1，因为后面还有current += 1
                    current += 6
                    break
                elif curStr == "N" and strparam[current:(current+4)] == "NULL":
                    # 这里少加1，因为后面还有current += 1
                    current += 3
                    break
                else:
                    retstr += strparam[current]
                    break
        current += 1

    # 去除参数名，只保留参数类型
    cleanstr = cleanKeyWord(retstr)
    cleanstr = cleanstr.replace(" ", "")
    ignorelist = cleanstr.split(",")
    for ignore in ignorelist:
        pattern = r'\b{}\b'.format(re.escape(ignore))
        retstr = re.sub(pattern, "", retstr)
    retstr = retstr.replace(",", "")
    retstr = retstr.replace(" ", "")
    retstr = retstr.replace("cocos2d::", "")
    retstr = retstr.replace(":", "")
    retstr = retstr.replace("\t", "")
    retstr = retstr.replace("\n", "")
    return retstr

def checkStatic(strparam):
    strparam = strparam.replace(" ", "")
    if strparam[0:6] == "static":
        return True
    return False

# 通过函数名判断是否有必要混淆
def checkConfound(fname):
    for word in SystemFuncStarts:
        if fname.startswith(word) == True:
            return False 
    if fname.find(".") >= 0:
        return False
    elif fname.isupper() == True:
        return False
    return True

# 通过字段判断是否有必要混淆
def checkConfoundex(fname):
    for word in SystemWordsContain:
        if word in fname:
            return False 
    return True

def is_file_encoded_by(file_path, coding):
    # coding: "gbk" 'utf-8'
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
            content.decode(coding)
            return True
    except UnicodeDecodeError:
        return False

# 获取文件编码格式，目前只区分gbk和utf-8两种
def getFileCoding(file_path):
    clearFileAnnotation(file_path)
    return 'utf-8'
    # if is_file_encoded_by(file_path, 'gbk') == True:
    #     return 'gbk'
    # elif is_file_encoded_by(file_path, 'utf-8') == True:
    #     return 'utf-8'
    # return None

# 清除代码中注释的内容，并保存文件为utf8
# 因为文件中的乱码只可能在注释里，乱码会导致之后open操作失败
def clearFileAnnotation(file_path):
    # 打开源文件以二进制方式读取
    wdata = ""
    with open(file_path, 'rb') as file:
        data = file.read()
        if data.startswith(codecs.BOM_UTF8):
            # 判断是不是utf8 with bom 是则删除最前面三个标识
            data = data[3:]  # 移除BOM
        current = 0
        while current < len(data):
            curStr = chr(data[current])
            if curStr == '/':
                current += 1
                if current < len(data):
                    nextstr = chr(data[current])
                    if nextstr == "/":
                        current += 1
                        while current < len(data):
                            nextstr = chr(data[current])
                            if nextstr != "\n":
                                current += 1
                            else:
                                wdata += nextstr
                                break
                    elif nextstr == "*":
                        current += 1
                        starbegin = False
                        while current < len(data):
                            nextstr = chr(data[current])
                            if nextstr == "*":
                                current += 1
                                starbegin = True
                            elif starbegin == True and nextstr == "/":
                                break
                            else:
                                starbegin = False
                                current += 1
                    else:
                        wdata += curStr
                        wdata += nextstr
                else:
                    wdata += curStr
            else:
                wdata += curStr
            current += 1

    # 删除文件
    if os.path.exists(file_path):  # 先检查文件是否存在，避免错误
        os.remove(file_path)

    # 将读取的二进制数据转换为utf-8格式并保存到目标文件
    with open(file_path, 'w+', encoding='utf-8', newline='') as file:
        file.write(wdata)

# 判断相对应的cpp文件是否存在
def isCppExist(folder,filename):
    dotindex = filename.rfind(".")
    filename = filename[:dotindex]
    filename += ".cpp"
    cpppath = os.path.join(folder,filename)
    return os.path.exists(cpppath)

# 判断是否忽略不要混淆的文件
def isIgnoreFile(filename):
    for word in IgnoreFiles:
        if word == filename:
            return True 
    return False

#####################混淆.h文件#####################
def hunxiaoh(folder,filename):
    global FuncsInfo
    global StaticFuncs
    global usedLetterList
    usedLetterList = {}
    if not isCppExist(folder,filename):
        return
    print('start hunxiao:', filename)
    # class[ ]+([a-zA-Z0-9]*)
    # ([ 	/]*)([a-zA-Z:_<>]+)([ 	]+)([a-zA-Z0-9&*_/:. 	]+\()([a-zA-Z0-9 ,\n&*_=:<>\(\) 	]*\);)[ ]*\n
    rawname = filename[:-2]
    funckey = os.path.join(folder,rawname)
    FuncsInfo[funckey] = {}
    StaticFuncs[funckey] = {}
    coding = getFileCoding(os.path.join(folder,filename))
    if coding is None:
        print(os.path.join(folder,filename)+" has unknown encoding")
        return
    hfile = open(os.path.join(folder,filename),'r',encoding=coding)
    hcode = hfile.read()
    classnames = re.findall(r'class[ ]+([a-zA-Z0-9]*)', hcode)

    funcs = re.findall(r'([ 	/]*)([a-zA-Z0-9:_<>]+)([ 	]+)([a-zA-Z0-9&*_/:. 	]+\()([a-zA-Z0-9 ,\n&*_=:<>\(\) 	]*\);)[ ]*\n', hcode)
    for func in funcs:
        fname = getFuncName(func[3])
        if checkConfound(fname) == True and checkConfoundex(func[0] + func[1]) == True:
            # 这里将参数部分简单处理，之后和函数名拼起来，作为键值，应对c++中重载函数的情况
            fnameex = cleanString(func[4])
            needhx = True
            for classname in classnames:
                if classname == fname:
                    needhx = False
            if needhx == True:
                toname = getRandomName(fname)
                FuncsInfo[funckey][fname+fnameex] = toname
                if checkStatic(func[1]):
                    StaticFuncs[funckey][fname+fnameex] = 1
                replacefrom = ""
                for num in range(len(func)):
                    replacefrom = replacefrom + func[num]
                replaceto = ""
                replace2 = func[3].replace(fname, toname)
                for num in range(len(func)):
                    if num != 3:
                        replaceto += func[num]
                    else:
                        replaceto += replace2

                # print('replacefrom='+replacefrom+" replaceto="+replaceto)
                hcode = hcode.replace(replacefrom, replacefrom+'\n'+replaceto)
    hfile.close()
    hfile = open(os.path.join(folder,filename),'w',-1)
    hfile.write(hcode)
    hfile.flush()
    hfile.close()

def cleanKeyWord(strparam):
    # 去除参数中的类型
    # 输入： SignData& data, const mapData2D* mapData )
    # 输出 data, mapData)
    for key in KeySign:
        strparam = strparam.replace(key, "")
    strparam = re.sub(r'( [_a-zA-Z0-9:]*<[_a-zA-Z0-9:\(\)*, ]*>)','',strparam)
    current = 0
    retstr = ""
    word = ""
    while current < len(strparam):
        charactor = strparam[current]
        # print("charactor = "+charactor)
        if charactor == " ":
            current += 1
            while current < len(strparam):
                charactor = strparam[current]
                # print("charactor = "+charactor)
                if charactor == " " or charactor == "\n":
                    current += 1
                elif charactor == ",":
                    retstr += word
                    retstr += charactor
                    retstr += " "
                    word = ""
                    break
                elif charactor == ")":
                    retstr += word
                    retstr += " "
                    retstr += charactor
                    word = ""
                    break
                else:
                    word = charactor
                    break
        elif charactor == ",":
            retstr += word
            retstr += charactor
            retstr += " "
            word = ""
        elif charactor == ")":
            retstr += word
            retstr += " "
            retstr += charactor
            word = ""
        elif charactor == "\n":
            word = ""
        else:
            word += charactor
        current += 1
    retstr += word
    # print("cleanKeyWord retstr = "+retstr)
    return retstr

def getClassName(strparam):
    nameindex = strparam.rfind(" ", 0, len(strparam))
    nameindex = nameindex + 1
    strparam = strparam[nameindex:]
    for key in KeySign:
        strparam = strparam.replace(key, "")
    return strparam

#####################混淆.cpp文件#####################
def hunxiaocpp(folder,filename):
    global FuncsInfo
    global StaticFuncs
    global usedLetterList
    usedLetterList = {}
    print('start hunxiao:', filename)
    rawname = filename[:-4]
    # ([a-zA-Z0-9&*_: ]*)(::)([a-zA-Z0-9&*_ ]*)(\()([a-zA-Z0-9: ,\n&*_]*\))[ ]*(\n\{)
    funckey = os.path.join(folder,rawname)
    if FuncsInfo.get(funckey) is None:
        return
    coding = getFileCoding(os.path.join(folder,filename))
    if coding is None:
        print(os.path.join(folder,filename)+" has unknown encoding")
        return
    hfile = open(os.path.join(folder,filename),'r',encoding=coding)
    hcode = hfile.read()
    # 针对声明类的cpp文件 比如aiManager.cpp
    funcs = re.findall(r'([a-zA-Z0-9&*_:<> ]*)(::)([a-zA-Z0-9&*_ ]*)(\()([a-zA-Z0-9:,\n&*<>\(\)_ 	]*\))([ ]*)(\n\{)', hcode)
    if len(funcs) == 0:
        funcs = re.findall(r'([a-zA-Z0-9&*_:<> ]*)(::)([a-zA-Z0-9&*_ ]*)(\()([a-zA-Z0-9:,\n&*<>\(\)_ 	]*\))([ ]*)(\{\n)', hcode)
    classcpp = False
    for func in funcs:
        classcpp = True
        fname = getFuncName(func[2])
        # 这里将参数部分简单处理，之后和函数名拼起来，作为键值，应对c++中重载函数的情况
        fnameex = cleanString(func[4])
        if FuncsInfo[funckey].get(fname+fnameex) is not None:
            toname = FuncsInfo[funckey][fname+fnameex]
            replacefrom = ""
            for num in range(len(func)):
                replacefrom = replacefrom + func[num]
            
            replaceto = makeRandomCode()
            if StaticFuncs[funckey].get(fname+fnameex, 0) == 1:
                # 静态函数调用需要加 类名::函数名
                classname = getClassName(func[0])
                replaceto += "    return " + classname + "::" + toname + "(" + cleanKeyWord(func[4]) + ";\n}\n\n"
            else:
                replaceto += "    return " + toname + "(" + cleanKeyWord(func[4]) + ";\n}\n\n"
            for num in range(0, len(func)):
                if num == 2:
                    replaceto = replaceto + toname
                else:
                    replaceto = replaceto + func[num]
            # print('replacefrom='+replacefrom+" replaceto="+replaceto)
            hcode = hcode.replace(replacefrom, replacefrom+'\n'+replaceto)
        else:
            print("fname+fnameex="+(fname+fnameex))
    
    # 针对只有函数的cpp文件 比如lua_mmorpg_actorCustomMoveTo.cpp
    if classcpp == False:
        funcs = re.findall(r'([a-zA-Z0-9&*_<>: ]*\()([a-zA-Z0-9 ,\n&*_:<>]*\))([ ]*)(\n\{)', hcode)
        if len(funcs) == 0:
            funcs = re.findall(r'([a-zA-Z0-9&*_<>: ]*\()([a-zA-Z0-9 ,\n&*_:<>]*\))([ ]*)(\{\n)', hcode)
        for func in funcs:
            fname = getFuncName(func[0])
            # 这里将参数部分简单处理，之后和函数名拼起来，作为键值，应对c++中重载函数的情况
            fnameex = cleanString(func[1])
            if FuncsInfo[funckey].get(fname+fnameex) is not None:
                toname = FuncsInfo[funckey][fname+fnameex]
            else:
                toname = getRandomName(fname)
            replacefrom = ""
            for num in range(len(func)):
                replacefrom = replacefrom + func[num]
            replaceto = makeRandomCode()
            replaceto += "    return " + toname + "(" + cleanKeyWord(func[1]) + ";\n}\n\n"
            for num in range(0, len(func)):
                if num == 0:
                    replaceto = replaceto + func[num].replace(fname, toname)
                else:
                    replaceto = replaceto + func[num]
            # print('replacefrom='+replacefrom+" replaceto="+replaceto)
            newfuncdef = replacefrom.replace(fname, toname)
            newfuncdef = newfuncdef[0:(newfuncdef.rfind(")")+1)] + ";\n\n"
            hcode = hcode.replace(replacefrom, newfuncdef+replacefrom+'\n'+replaceto)

    hfile.close()

    hfile = open(os.path.join(folder,filename),'w',-1)
    hfile.write(hcode)
    hfile.flush()
    hfile.close()

#####################混淆.hpp文件#####################
def hunxiaohpp(folder,filename):
    global FuncsInfo
    global StaticFuncs
    global usedLetterList
    usedLetterList = {}
    if not isCppExist(folder,filename):
        return
    print('start hunxiao:', filename)
    # class[ ]+([a-zA-Z0-9]*)
    # ([a-zA-Z0-9&*_/:. 	]+\()([a-zA-Z0-9 ,\n&*_=:<>\(\) ]*\);)[ ]*\n
    rawname = filename[:-4]
    funckey = os.path.join(folder,rawname)
    FuncsInfo[funckey] = {}
    StaticFuncs[funckey] = {}
    coding = getFileCoding(os.path.join(folder,filename))
    if coding is None:
        print(os.path.join(folder,filename)+" has unknown encoding")
        return
    hfile = open(os.path.join(folder,filename),'r',encoding=coding)
    hcode = hfile.read()
    classnames = re.findall(r'class[ ]+([a-zA-Z0-9]*)', hcode)

    funcs = re.findall(r'([a-zA-Z0-9&*_/:. 	]+\()([a-zA-Z0-9 ,\n&*_=:<>\(\) ]*\);)[ ]*\n', hcode)
    for func in funcs:
        fname = getFuncName(func[0])
        if checkConfound(fname) == True:
        # 这里将参数部分简单处理，之后和函数名拼起来，作为键值，应对c++中重载函数的情况
            fnameex = cleanString(func[1])
            needhx = True
            for classname in classnames:
                if classname == fname:
                    needhx = False
            if needhx == True:
                toname = getRandomName(fname)
                FuncsInfo[funckey][fname+fnameex] = toname
                if checkStatic(func[0]):
                    StaticFuncs[funckey][fname+fnameex] = 1
                replacefrom = ""
                for num in range(len(func)):
                    replacefrom = replacefrom + func[num]
                replaceto = func[0].replace(fname, toname)
                for num in range(1, len(func)):
                    replaceto = replaceto + func[num]
                # print('replacefrom='+replacefrom+" replaceto="+replaceto)
                hcode = hcode.replace(replacefrom, replacefrom+'\n'+replaceto)
    hfile.close()
    hfile = open(os.path.join(folder,filename),'w',-1)
    hfile.write(hcode)
    hfile.flush()
    hfile.close()

#####################随机生成代码#####################
def makeRandomCode():
    retcode = ""
    rnum = random.randint(0,100)
    params = getRandomParamList()
    retcode += makeDefineCode(params)
    if rnum <= 60:
        retcode += makeOperationsCode(params)
    if rnum <= 50:
        retcode += makeForCode(params)
    return retcode

# 随机变量声明代码
def makeDefineCode(paramlist):
    isfloat = random.randint(1,10) >= 8
    rcode = "    " + getRandomParamType(isfloat) + " "
    for i in range(len(paramlist)):
        param = paramlist[i]
        rcode += param + " = "
        if isfloat:
            num = (random.randint(0,100)) / 10
            string_num = "%.1f" % num
            rcode += string_num
        else:
            rcode += str(random.randint(0,10))
        if i < len(paramlist) - 1:
            rcode += ", "
    rcode += ";\n"
    return rcode

# 随机四则运算赋值代码
def makeOperationsCode(paramlist):
    rcode = ""
    opercodes = random.randint(1,5)
    for i in range(opercodes):
        rcode += getRandomOperCode(paramlist)
    return rcode

# 随机for循环代码
def makeForCode(paramlist):
    charint = ["char", "int"]
    forcount = random.randint(1,10)
    spacebegin = "    "
    indexstr = getRandomLetter(1)
    if forcount <= 7:
        forcount = 1
    elif forcount <= 9:
        forcount = 2
    else:
        forcount = 3
    rcode = ""
    for i in range(0, forcount):
        rspacebegin = ""
        for icount in range(0, i+1):
            rspacebegin += spacebegin
        rtype = charint[random.randint(0,1)]
        rbegin = str(random.randint(0,1))
        rend = str(random.randint(1,2))
        rindex = indexstr
        if i > 0:
            rindex += str(i)
        rcode += rspacebegin + "for ( " + rtype + " " + rindex + " = " + rbegin + "; " + rindex + " <= " + rend + "; " + rindex + "++) {\n"
        opercodes = random.randint(0,10)
        if opercodes <= 7:
            opercodes = 0
        elif opercodes <= 9:
            opercodes = 1
        else:
            opercodes = 2
        if i == forcount - 1:
            opercodes = random.randint(1,4)
        for j in range(opercodes):
            rcode += rspacebegin + getRandomOperCode(paramlist)
    
    for i in range(forcount, 0, -1):
        rspacebegin = ""
        for icount in range(0, i):
            rspacebegin += spacebegin
        rcode += rspacebegin + "}\n"
    return rcode

# 随机while循环代码

# 随机dowhile循环代码

# 随机if else代码

# 随机switch case代码

# 获取随机参数名字
def getRandomParamList():
    paramcount = random.randint(3,5)
    paramlist = []
    for i in range(paramcount):
        paramlist.append(getShortRandomName())
    return paramlist

# 获取一行随机运算代码
def getRandomOperCode(params):
    # params类型为[]
    if len(params) <= 1:
        return ""
    random.shuffle(params)
    rcode = "    " + params[0] + " = " + params[1]
    for i in range(2, len(params)):
        param = params[i]
        # 随机不要除法，很难保证除数不为0
        useconstant = random.randint(1, 100)
        if useconstant <= 35:
            rcode += " " + getRandomOperater(True) + " "
            rcode += str(random.randint(1, 13))
        else:
            rcode += " " + getRandomOperater(False) + " "
            rcode += param
    rcode += ";\n"
    return rcode


# 随机参数类型
def getRandomParamType(isfloat):
    sign = ["unsigned", "signed"]
    long = ["short", "long"]
    charint = ["char", "int"]
    floatdouble = ["float", "double"]
    retType = ""
    if isfloat == False:
        # 随机生成整型
        ranres = random.randint(1,10)
        if ranres >= 8 and ranres <= 9:
            retType += sign[0] + " "
        elif ranres >= 10:
            retType += sign[1] + " "

        ranres = random.randint(1,10)
        if ranres >= 0 and ranres <= 6:
            retType += charint[0]
        else:
            ranres = random.randint(1,10)
            if ranres >= 5 and ranres <= 9:
                retType += long[0] + " "
            elif ranres >= 10:
                retType += long[1] + " "
            retType += charint[1]
    else:
        # 随机生成浮点型
        ranres = random.randint(1,10)
        if ranres >= 0 and ranres <= 6:
            retType += floatdouble[0]
        else:
            retType += floatdouble[1]
    return retType

# 随机运算符号
def getRandomOperater(needdivision):
    operaters = '+-*'
    if needdivision:
        operaters += "/"
    return random.choice(operaters)

def main(argv):
    project_tool_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    project_root_dir = os.path.abspath(os.path.join(project_tool_dir, os.path.pardir))
    print('cur_dir', project_tool_dir)
    print('cur_root_dir', project_root_dir)
    # 先生成随机名字库
    produceRandomWords(project_tool_dir)
    # 先遍历.h建立函数映射，再搞定.cpp
    for dirpath, dirnames, filenames in os.walk(project_tool_dir):
        for filename in filenames:
            if filename.endswith(".h") and not isIgnoreFile(filename):
                hunxiaoh(dirpath,filename)
            elif filename.endswith(".hpp") and not isIgnoreFile(filename):
                hunxiaohpp(dirpath,filename)
    # 先遍历.h建立函数映射，再搞定.cpp
    for dirpath, dirnames, filenames in os.walk(project_tool_dir):
        for filename in filenames:
            if filename.endswith(".cpp") and not isIgnoreFile(filename):
                hunxiaocpp(dirpath,filename)

    # 单元测试用
    # cleanKeyWord("int startX, int startY,                              \nint endX, int endY,                              \nconst mapData2D* mapData )")
    # ret = cleanString("int data = 0, int data1 = 0x03, const int data2 = 0.3125, int *mapData=nullptr, char D=NULL,double ccc, float ddd=0 )")
    # for i in range(0, 5):
    #     print(makeRandomCode())
    # print(makeRandomCode())

# -------------- main --------------
if __name__ == '__main__':
    main(sys.argv)