# !/usr/bin/ python
# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.db import connection
import ctypes
import json
import os

# Create your views here.
def setup(request):
    global paperName
    global tsclibrary

    # Get paper size and density
    paperWidth = request.POST.get('paperWidth')
    paperHeight = request.POST.get('paperHeight')
    density = request.POST.get('density')
    paperName = request.POST.get('paperName')

    # Connect to printer and .dll
    try:
        # Connect to printer and .dll
        tsclibrary = ctypes.WinDLL("./printLabel/TSCLIB.dll")
        # tsclibrary = ctypes.WinDLL("./printLabel/tsclibnet.dll")
        tsclibrary.openportW("USB")
    except:
        print("open port fail")
        return render(request,'index.html',{"warning":"沒有連接標籤機"})
    # create table
    cursor = connection.cursor()
    cursor.execute("""if not exists (select * from sysobjects where name='paperSetup')CREATE TABLE paperSetup("paperName" varchar(255) PRIMARY KEY,"paperWidth" float,"paperHeight" float,"density" int);""")
    # insert into SQL
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM paperSetup;")
    papers = cursor.fetchall()
    for name in papers:
        name = list(name)
        print(name[0])
        if paperName == name[0]:
            papers = os.listdir("./printLabel/commandTxt")
            for i in range(0,len(papers)):
                if 'json' in papers[i]:
                    papers[i] = papers[i].replace('.json','')
            print(papers)
            return render(request,'index.html',{"warning":"標籤名稱重複","papers":papers})
        
    cursor.execute("""INSERT INTO paperSetup("paperName","paperWidth","paperHeight","density")VALUES ('%s','%f','%f','%d');"""%(paperName,float(paperWidth),float(paperHeight),int(density)))
    
    # Setup printer
    tsclibrary.sendcommandW("DENSITY "+str(density))
    tsclibrary.sendcommandW("SIZE " + str(paperWidth) +" mm, " + str(paperHeight) +" mm")
    tsclibrary.clearbuffer()
    tsclibrary.sendcommandW("CLS")

    with open("./printLabel/commandTxt/"+str(paperName)+".json","w",encoding='utf-8') as labelMessage:
        json.dump({"%s"%paperName:{"paperWidth":paperWidth,"paperHeight":paperHeight,"density":density}},labelMessage)

    # Send message to label.html
    paperSize = "紙張大小: "+str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = "濃度: "+str(density)

    return render(request,'label.html',{"paperName":paperName,"density":density,"paperSize":paperSize})

"""setup 列印設定
- paperWidth : 紙張寬度
- paperHeight : 紙張高度
- density : 印刷濃度
"""

def nutritionFacts(request):
    nutritionName = request.POST.get('nutritionName')
    X = float(request.POST.get('nutritionX')) *8
    Y = float(request.POST.get('nutritionY')) *8
    option = request.POST.getlist('options')
    weight = float(request.POST.get('weight'))
    servings = request.POST.get('servings')
    optionList = request.POST.get('optionList')
    optionList = list(eval(optionList).keys())

    ### translate option to english ###
    with open("./printLabel/translate.json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)
    english = list(labelMessage.keys())
    chinese = list(labelMessage.values())

    for i in range(0,len(option)):
        for j in range(0,len(english)):
            if optionList[i] == chinese[j]:
                optionList[i] = english[j]
    ############################

    # create table
    cursor = connection.cursor()
    cursor.execute("""if not exists (select * from sysobjects where name='nutrition')
                   create table nutrition(
                    "paperName" varchar(255),
                    "nutritionName" varchar(255),
                    "X" float,
                    "Y" float,
                    "weight" float,
                    "servings" float,
                    "heat" float,
                    "portain" float,
                    "fat" float,
                    "saturated" float,
                    "trans" float,
                    "carbohydrate" float,
                    "sugar" float,
                    "sodium" float,
                    "cholesterol" float,
                    "amino" float,
                    "vitamins" float,
                    "minerals" float,
                    "fiber" float,
                    "potassium" float,
                    "calcium" float,
                    "iron" float,
                    PRIMARY KEY (nutritionName),
                    FOREIGN KEY(paperName)REFERENCES paperSetup(paperName) ON DELETE CASCADE);""")
                   
    with open("./printLabel/commandTxt/"+str(paperName)+".json","r") as jsonFile:
            labelMessage = json.load(jsonFile)

    labelMessage["%s"%paperName]["%s"%nutritionName] = {
        "type":"營養標籤",
        "X":X,
        "Y":Y,
        "weight":weight,
        "servings":servings}
    
    # insert into SQL
    cursor.execute("SELECT * FROM nutrition;")
    nutritions = cursor.fetchall()
    for name in nutritions:
        name = list(name)
        if nutritionName == name[1]:
            return render(request,'nutritionOption.html',{"warning":"營養標籤名稱重複"})
    cursor.execute("""INSERT INTO nutrition("paperName","nutritionName","X","Y","weight","servings" )
                   VALUES ('%s','%s','%f','%f','%f','%d');"""%(paperName,nutritionName,X/8,Y/8,weight,float(servings)))
    # 把營養標籤的內容存到json檔
    for i in range(0,len(option)):
        labelMessage["%s"%paperName]["%s"%nutritionName].update({"%s"%optionList[i]:option[i]})
        with open("./printLabel/commandTxt/"+str(paperName)+".json","w") as jsonFile:
            json.dump(labelMessage,jsonFile)
    # insert into SQL
    for i in range(0,len(optionList)):
        cursor.execute("""UPDATE nutrition SET "%s" = '%f' WHERE "paperName" = '%s' AND "nutritionName" = '%s';"""
                       %(optionList[i],float(option[i]),paperName,nutritionName))
    
    length = len(option)
    # BOX
    tsclibrary.sendcommandW('TEXT '+str(X+80)+','+str(Y+20)+',"chinese",0,1,1,"Nutrition Facts"')
    tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y)+', '+str(X+400)+', '+str(Y+50)+', 1')
    tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y+50)+', '+str(X+400)+', '+str(Y+110)+', 1')
    tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y+110)+', '+str(X+400)+', '+str(Y+150)+', 1')
    tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y+150)+', '+str(X+400)+', '+str(Y+160+25*length)+', 1')

    # serving size
    tsclibrary.sendcommandW('TEXT '+str(X+10)+', '+str(Y+60)+',"chinese", 0, 1, 1, "Each contains '
                            +str(weight)+' grams"')
    
    tsclibrary.sendcommandW('TEXT '+str(X+10)+', '+str(Y+85)+',"chinese", 0, 1, 1, "This contains '
                            +str(servings)+' package"')

    tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+120)+',"chinese", 0, 1, 1, "1 pack"')
    tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+120)+',"chinese", 0, 1, 1, "100 g"')

    with open("./printLabel/commandTxt/"+str(paperName)+".json","r") as jsonFile:
            labelMessage = json.load(jsonFile)

    for l in range(0,len(option)):
        if optionList[l] == 'heat':
            tsclibrary.sendcommandW('TEXT '+str(X+10)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+optionList[l]+'"')
            tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+option[l]+'k"')
            tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'k"')
        elif optionList[l] == 'saturated'or optionList[l] == 'trans' or optionList[l] == 'sugar':
            tsclibrary.sendcommandW('TEXT '+str(X+15)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+optionList[l]+'"')
            tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+option[l]+'g"')
            tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'g"')
        elif optionList[l] == 'sodium':
            tsclibrary.sendcommandW('TEXT '+str(X+10)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+optionList[l]+'"')
            tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+option[l]+'mg"')
            tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'mg"')
        else :
            tsclibrary.sendcommandW('TEXT '+str(X+10)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+optionList[l]+'"')
            tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+option[l]+'g"')
            tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"chinese", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'g"')

    # 讀取已建立的內容
    with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)
    created = labelMessage['%s'%paperName].keys()
    createdList = list(created)
    createdList = createdList[3:]
    typeList = []
    for i in range(0,len(createdList)):
        types = labelMessage['%s'%paperName]['%s'%createdList[i]]['type']
        typeList.append(types)

    # 顯示到label.html
    paperWidth = labelMessage['%s'%paperName]['paperWidth']
    paperHeight = labelMessage['%s'%paperName]['paperHeight']
    density = labelMessage['%s'%paperName]['density']

    paperSize = "紙張大小: "+str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = "濃度: "+str(density)

    # 把標籤名稱跟累型合在一起
    createdList = dict(zip(createdList,typeList))

    return render(request,'label.html',{"paperName":paperName,"paperSize":paperSize,
                                        "density":density,"createdList":createdList})

def qrCode(request):
    qrName = request.POST.get('qrName')
    X = float(request.POST.get('qrX'))*8
    Y = float(request.POST.get('qrY'))*8
    ECC = request.POST.get('ECC')
    width = request.POST.get('width')
    rotation = request.POST.get('rotation')
    content = request.POST.get('qrContent')

    # create table
    cursor = connection.cursor()
    cursor.execute("""if not exists (select * from sysobjects where name='qrcode')
                   CREATE TABLE qrcode(
                   "paperName" varchar(255),
                   "qrName" varchar(255),
                   "X" float,
                   "Y" float,
                   "ECC" varchar(255),
                   "width" int,
                   "rotation" int,
                   "content" varchar(255),
                   PRIMARY KEY (qrName),
                   FOREIGN KEY(paperName)REFERENCES paperSetup(paperName) ON DELETE CASCADE);""")
    # insert into SQL
    cursor.execute("SELECT * FROM qrcode;")
    qrcodes = cursor.fetchall()
    for name in qrcodes:
        name = list(name)
        if qrName == name[1]:
            return render(request,'qrSettings.html',{"warning":"QRcode名稱重複"})
        
    cursor.execute("""INSERT INTO qrcode("paperName","qrName","X","Y","ECC","width","rotation","content")
                     VALUES ('%s','%s','%f','%f','%s','%d','%d','%s');"""
                   %(paperName,qrName,X/8,Y/8,ECC,int(width),int(rotation),content))
    
    
    # 儲存已建立的內容
    with open("./printLabel/commandTxt/"+str(paperName)+".json","r") as jsonFile:
        labelMessage = json.load(jsonFile)
    labelMessage["%s"%paperName]["%s"%qrName] = {"type":"QRcode","X":X,"Y":Y,"ECC":ECC,"width":width,
                                                 "rotation":rotation,"content":content}
    with open("./printLabel/commandTxt/"+str(paperName)+".json","w") as jsonFile:
        json.dump(labelMessage,jsonFile)

    # 讀取已建立的內容
    with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)
    created = labelMessage['%s'%paperName].keys()
    createdList = list(created)
    createdList = createdList[3:]
    typeList = []
    for i in range(0,len(createdList)):
        types = labelMessage['%s'%paperName]['%s'%createdList[i]]['type']
        typeList.append(types)

    # 顯示到label.html
    paperWidth = labelMessage['%s'%paperName]['paperWidth']
    paperHeight = labelMessage['%s'%paperName]['paperHeight']
    density = labelMessage['%s'%paperName]['density']

    paperSize = "紙張大小: "+str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = "濃度: "+str(density)

    tsclibrary.sendcommandW('QRCODE '+str(X)+','+str(Y)+','+ECC+','+str(width)+',A,'+str(rotation)+',M2,S7,"'
                            +content+'"')
    
    # 把標籤名稱跟累型合在一起
    createdList = dict(zip(createdList,typeList))

    return render(request,'label.html',{"paperName":paperName,"paperSize":paperSize,"density":density,
                                        "createdList":createdList})

def text(request):
    textName = request.POST.get('textName')
    X = float(request.POST.get('textX'))*8
    Y = float(request.POST.get('textY'))*8
    size = request.POST.get('textSize')
    content = request.POST.get('textContent')

    # create table
    cursor = connection.cursor()
    cursor.execute("""if not exists (select * from sysobjects where name='text')
                   CREATE TABLE text(
                   "paperName" varchar(255),
                   "textName" varchar(255),
                   "X" float,
                   "Y" float,
                   "size" int,
                   "content" varchar(255),
                   PRIMARY KEY (textName),
                   FOREIGN KEY(paperName)REFERENCES paperSetup(paperName) ON DELETE CASCADE);""")
    # insert into SQL
    cursor.execute("SELECT * FROM text;")
    texts = cursor.fetchall()
    for name in texts:
        name = list(name)
        if textName == name[1]:
            return render(request,'textSettings.html',{"warning":"文字名稱重複"})
    
    cursor.execute("""INSERT INTO text("paperName","textName","X","Y","size","content")
                   VALUES ('%s','%s','%f','%f','%d','%s');"""%(paperName,textName,X/8,Y/8,int(size),content))

    tsclibrary.sendcommandW('TEXT '+str(X)+', '+str(Y)+',"'+str(size)+'", 0, 1, 1, "'+content+'"')
    tsclibrary.printerfontW('"'+str(X)+'"', '"'+str(Y+120)+'"', "TST24.BF2","0", "1", "1", "新北市")
    # 儲存已建立的內容
    with open("./printLabel/commandTxt/"+str(paperName)+".json","r") as jsonFile:
        labelMessage = json.load(jsonFile)
    labelMessage["%s"%paperName]["%s"%textName] = {"type":"文字","X":X,"Y":Y,"size":size,"content":content}
    with open("./printLabel/commandTxt/"+str(paperName)+".json","w") as jsonFile:
        json.dump(labelMessage,jsonFile)

    # 讀取已建立的內容
    with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)

    # 標籤名稱
    created = labelMessage['%s'%paperName].keys()
    createdList = list(created)
    createdList = createdList[3:]

    # 標籤類型
    typeList = []
    for i in range(0,len(createdList)):
        types = labelMessage['%s'%paperName]['%s'%createdList[i]]['type']
        typeList.append(types)

    # 重新顯示紙張資訊到 label.html
    paperWidth = labelMessage['%s'%paperName]['paperWidth']
    paperHeight = labelMessage['%s'%paperName]['paperHeight']
    density = labelMessage['%s'%paperName]['density']

    paperSize = "紙張大小: "+str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = "濃度: "+str(density)

    # 把標籤名稱跟累型合在一起
    createdList = dict(zip(createdList,typeList))

    return render(request,'label.html',{"paperName":paperName,"paperSize":paperSize,"density":density,
                                        "createdList":createdList})

def printLabel(request):
    copy = request.POST.get('copy')
    tsclibrary.printlabelW("1",str(copy))
    return render(request,'finishPrint.html')

def index(request):

    papers = os.listdir("./printLabel/commandTxt")
    for i in range(0,len(papers)):
        if 'json' in papers[i]:
            papers[i] = papers[i].replace('.json','')
    return render(request,'index.html',{"papers":papers})

def textSettings(request):
    return render(request,'textSettings.html',{"X":"X","Y":"Y"})

def qrSettings(request):
    return render(request,'qrSettings.html')

def printSettings(request):
    return render(request,'printSettings.html')

def restart(request):
    # restart printer
    # tsclibrary.sendcommandW(chr(27) + '!R')
    tsclibrary.closeport()
    return render(request,'index.html')

def nutritionOption(request):
    return render(request,'nutritionOption.html')

def nutritionSettings(request):

    optionValues = request.POST.getlist('option')
    optionTitles = []
    for i in range(0,len(optionValues)):
        if optionValues[i] == 'heat':
            optionTitles.append('熱量')
        elif optionValues[i] == 'portain':
            optionTitles.append('蛋白質')
        elif optionValues[i] == 'fat':
            optionTitles.append('脂肪')
        elif optionValues[i] == 'saturated':
            optionTitles.append('飽和脂肪')
        elif optionValues[i] == 'trans':
            optionTitles.append('反式脂肪')
        elif optionValues[i] == 'carbohydrate':
            optionTitles.append('碳水化合物')
        elif optionValues[i] == 'sugar':
            optionTitles.append('糖')
        elif optionValues[i] == 'sodium':
            optionTitles.append('鈉')
        elif optionValues[i] == 'cholesterol':
            optionTitles.append('膽固醇')
        elif optionValues[i] == 'amino':
            optionTitles.append('胺基酸')
        elif optionValues[i] == 'vitamins':
            optionTitles.append('維生素')
        elif optionValues[i] == 'minerals':
            optionTitles.append('礦物質')
        elif optionValues[i] == 'fiber':
            optionTitles.append('膳食纖維')
        elif optionValues[i] == 'potassium':
            optionTitles.append('鉀')
        elif optionValues[i] == 'calcium':
            optionTitles.append('鈣')
        elif optionValues[i] == 'iron':
            optionTitles.append('鐵')    
    options = dict(zip(optionValues,optionTitles))
    return render(request,'nutritionFacts.html',{"options":options})

def drawOnHtml(request):
    if request.method == 'GET':
        
        # 讀取已建立的內容
        with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
            labelMessage = json.load(jsonFile)
    
    labelMessage = labelMessage["%s"%paperName]
    created = list(labelMessage.keys())[:3]
    for i in range(0,len(created)):
        labelMessage.pop(created[i])
    return JsonResponse(labelMessage)

def deleteItem(request):
    with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)
    itemName = request.POST.get('deleteItemButton')
    """刪除"""
    classification = labelMessage["%s"%paperName]["%s"%itemName]["type"]
    if classification == "文字":
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM text WHERE "paperName" = '%s' AND "textName" = '%s';"""%(paperName,itemName))
    elif classification == "QRcode":
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM qrcode WHERE "paperName" = '%s' AND "qrName" = '%s';"""%(paperName,itemName))
    elif classification == "營養標籤":
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM nutrition WHERE "paperName" = '%s' AND "nutritionName" = '%s';"""%(paperName,itemName))
    """"""
    del labelMessage["%s"%paperName]["%s"%itemName]

    with open("./printLabel/commandTxt/"+str(paperName)+".json","w",encoding='utf-8') as jsonFile:
        json.dump(labelMessage,jsonFile)
    """"""""""""

    # 讀取已建立的內容
    with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)

    # 標籤名稱
    created = labelMessage['%s'%paperName].keys()
    createdList = list(created)
    createdList = createdList[3:]

    # 標籤類型
    typeList = []
    for i in range(0,len(createdList)):
        types = labelMessage['%s'%paperName]['%s'%createdList[i]]['type']
        typeList.append(types)

    # 重新顯示紙張資訊到 label.html
    paperWidth = labelMessage['%s'%paperName]['paperWidth']
    paperHeight = labelMessage['%s'%paperName]['paperHeight']
    density = labelMessage['%s'%paperName]['density']

    paperSize = "紙張大小: "+str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = "濃度: "+str(density)

    # 把標籤名稱跟累型合在一起
    createdList = dict(zip(createdList,typeList))

    return render(request,'label.html',{"paperName":paperName,"paperSize":paperSize,"density":density,
                                        "createdList":createdList})

def detail(request):
    itemName = request.POST.get('editButton')

    with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)
    
    itemType = labelMessage["%s"%paperName]["%s"%itemName]["type"]
   
    if itemType == "文字":
        size = labelMessage["%s"%paperName]["%s"%itemName]["size"]
        content = labelMessage["%s"%paperName]["%s"%itemName]["content"]
        X = labelMessage["%s"%paperName]["%s"%itemName]["X"] //8
        Y = labelMessage["%s"%paperName]["%s"%itemName]["Y"] //8

        """Delete item first"""
        with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
            labelMessage = json.load(jsonFile)
        del labelMessage["%s"%paperName]["%s"%itemName]

        with open("./printLabel/commandTxt/"+str(paperName)+".json","w",encoding='utf-8') as jsonFile:
            json.dump(labelMessage,jsonFile)

        cursor = connection.cursor()
        cursor.execute("""DELETE FROM text WHERE "paperName" = '%s' AND "textName" = '%s';"""%(paperName,itemName))
        """"""
        return render(request,'textDetail.html',{"itemName":itemName,"size":size,"content":content,"X":X,"Y":Y})
    
    elif itemType == "QRcode":
        X = labelMessage["%s"%paperName]["%s"%itemName]["X"] //8
        Y = labelMessage["%s"%paperName]["%s"%itemName]["Y"] //8
        content = labelMessage["%s"%paperName]["%s"%itemName]["content"]
        ECC = labelMessage["%s"%paperName]["%s"%itemName]["ECC"]
        width = labelMessage["%s"%paperName]["%s"%itemName]["width"]
        rotation = labelMessage["%s"%paperName]["%s"%itemName]["rotation"]

        """Delete item first"""
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM qrcode WHERE "paperName" = '%s' AND "qrName" = '%s';"""%(paperName,itemName))
        """"""
        with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
            labelMessage = json.load(jsonFile)
        del labelMessage["%s"%paperName]["%s"%itemName]

        with open("./printLabel/commandTxt/"+str(paperName)+".json","w",encoding='utf-8') as jsonFile:
            json.dump(labelMessage,jsonFile)
        """"""
        return render(request,'qrDetail.html',{"itemName":itemName,"content":content,"X":X,"Y":Y,"ECC":ECC,"width":width,"rotation":rotation})
    
    elif itemType == "營養標籤":
        option = list(labelMessage["%s"%paperName]["%s"%itemName].keys())[5:]
        optionValue = list(labelMessage["%s"%paperName]["%s"%itemName].values())[5:]
        X = labelMessage["%s"%paperName]["%s"%itemName]["X"] //8
        Y = labelMessage["%s"%paperName]["%s"%itemName]["Y"] //8
        weight = labelMessage["%s"%paperName]["%s"%itemName]["weight"]
        servings = labelMessage["%s"%paperName]["%s"%itemName]["servings"]

        # translate option to chinese
        with open("./printLabel/translate.json","r",encoding='utf-8') as jsonFile:
            labelMessage = json.load(jsonFile)
        english = list(labelMessage.keys())
        chinese = list(labelMessage.values())

        for i in range(0,len(option)):
            for j in range(0,len(english)):
                if option[i] == english[j]:
                    option[i] = chinese[j]
        option = dict(zip(option,optionValue))
        

        """Delete item first"""
        with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
            labelMessage = json.load(jsonFile)
        del labelMessage["%s"%paperName]["%s"%itemName]

        with open("./printLabel/commandTxt/"+str(paperName)+".json","w",encoding='utf-8') as jsonFile:
            json.dump(labelMessage,jsonFile)
        """"""
        return render(request,'nutritionDetail.html',{"itemName":itemName,"option":option,"X":X,"Y":Y,"weight":weight,"servings":servings})
    
def findLabel(request):
    global paperName
    global tsclibrary

    # Connect to printer and .dll
    try:
        # Connect to printer and .dll
        tsclibrary = ctypes.WinDLL("./printLabel/TSCLIB.dll")
        # tsclibrary = ctypes.WinDLL("./printLabel/tsclibnet.dll")
        tsclibrary.openportW("USB")
    except:
        print("open port fail")
        return render(request,'index.html',{"warning":"沒有連接標籤機"})
    
    paperName = request.POST.get('paperName')

    with open("./printLabel/commandTxt/"+str(paperName)+".json","r") as jsonFile:
        labelMessage = json.load(jsonFile)
    created = labelMessage['%s'%paperName].keys()
    createdList = list(created)
    createdList = createdList[3:]
    typeList = []
    for i in range(0,len(createdList)):
        types = labelMessage['%s'%paperName]['%s'%createdList[i]]['type']
        typeList.append(types)
    # 把標籤名稱跟累型合在一起
    createdList = dict(zip(createdList,typeList))

    paperWidth = labelMessage['%s'%paperName]['paperWidth']
    paperHeight = labelMessage['%s'%paperName]['paperHeight']
    density = labelMessage['%s'%paperName]['density']

    # Send message to label.html
    paperSize = "紙張大小: "+str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = "濃度: "+str(density)
    return render(request,'label.html',{"paperName":paperName,"density":density,"paperSize":paperSize,"createdList":createdList})
