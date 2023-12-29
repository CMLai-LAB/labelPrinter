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
    global language

    # Get paper size and density
    paperWidth = request.POST.get('paperWidth')
    paperHeight = request.POST.get('paperHeight')
    density = request.POST.get('density')
    paperName = request.POST.get('paperName')
    try:
        paperWidth = float(paperWidth)
        paperHeight = float(paperHeight)
        density = int(float(density))
    except:
        return HttpResponse("請依照提示輸入正確的型態")
    # Connect to printer and .dll
    try:
        # Connect to printer and .dll
        tsclibrary = ctypes.WinDLL("./printLabel/TSCLIB.dll")
        # tsclibrary = ctypes.WinDLL("./printLabel/tsclibnet.dll")
        tsclibrary.openportW("USB")
    except:
        print("open port fail")
        return render(request,'index.html',{"warning":"沒有連接標籤機"})
    
    # Setup printer
    tsclibrary.sendcommandW("DENSITY "+str(density))
    tsclibrary.sendcommandW("SIZE " + str(paperWidth) +" mm, " + str(paperHeight) +" mm")
    tsclibrary.clearbuffer()
    tsclibrary.sendcommandW("CLS")

    with open("./printLabel/commandTxt/"+str(paperName)+".json","w",encoding='utf-8') as labelMessage:
        json.dump({"%s"%paperName:{"paperWidth":paperWidth,"paperHeight":paperHeight,"density":density}},labelMessage)

    # Send message to label.html
    paperSize = str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = str(density)
    paperWidth = int(paperWidth)*4
    paperHeight = int(paperHeight)*4
    if language == 'chinese':
        return render(request,'label.html',{"paperName":paperName,"density":density,"paperSize":paperSize,"paperWidth":paperWidth,"paperHeight":paperHeight})
    elif language == 'english':
        return render(request,'label_en.html',{"paperName":paperName,"density":density,"paperSize":paperSize,"paperWidth":paperWidth,"paperHeight":paperHeight})
    elif language == 'vietnamese':
        return render(request,'label_vie.html',{"paperName":paperName,"density":density,"paperSize":paperSize,"paperWidth":paperWidth,"paperHeight":paperHeight})

"""setup 列印設定
- paperWidth : 紙張寬度
- paperHeight : 紙張高度
- density : 印刷濃度
"""

def nutritionFacts(request):
    global language
    nutritionName = request.POST.get('nutritionName')
    X = float(request.POST.get('nutritionX')) *8
    Y = float(request.POST.get('nutritionY')) *8
    option = request.POST.getlist('options')
    weight = float(request.POST.get('weight'))
    servings = request.POST.get('servings')
    optionList = request.POST.get('optionList')
    optionList = list(eval(optionList).keys())

    with open("./printLabel/commandTxt/"+str(paperName)+".json","r") as jsonFile:
            labelMessage = json.load(jsonFile)

    labelMessage["%s"%paperName]["%s"%nutritionName] = {
        "type":"營養標籤",
        "X":X,
        "Y":Y,
        "weight":weight,
        "servings":servings}
    # 看optionList的值有沒有在translatex裡面，一律翻譯成translate.json裡面的keys
    with open("./printLabel/translate.json","r",encoding='utf-8') as jsonFile:
        translate = json.load(jsonFile)
    language_dict = list(translate.values())
    for n in range(0,len(language_dict[0])):
        chinese = []
        for lan in translate.values():
            chinese.append(lan[n])
        for i in range(0,len(optionList)):
            for j in range(0,len(chinese)):
                if optionList[i] == chinese[j]:
                    optionList[i] = list(translate.keys())[j]
    print(optionList)
    # 把營養標籤的內容存到json檔
    for i in range(0,len(option)):
        labelMessage["%s"%paperName]["%s"%nutritionName].update({"%s"%optionList[i]:option[i]})
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

    paperSize = str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = str(density)

    # 把標籤名稱跟累型合在一起
    createdList = dict(zip(createdList,typeList))
    # Define language
    if language == 'chinese':
        return render(request,'label.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})
    elif language == 'english':
        return render(request,'label_en.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})
    elif language == 'vietnamese':
        return render(request,'label_vie.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})

def qrCode(request):
    global language
    qrName = request.POST.get('qrName')
    X = float(request.POST.get('qrX'))*8
    Y = float(request.POST.get('qrY'))*8
    ECC = request.POST.get('ECC')
    width = request.POST.get('width')
    rotation = request.POST.get('rotation')
    content = request.POST.get('qrContent')
    
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

    paperSize = str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = str(density)
    
    # 把標籤名稱跟累型合在一起
    createdList = dict(zip(createdList,typeList))

    # Define language
    if language == 'chinese':
        return render(request,'label.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})
    elif language == 'english':
        return render(request,'label_en.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})
    elif language == 'vietnamese':
        return render(request,'label_vie.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})
    
def text(request):
    global language
    textName = request.POST.get('textName')
    X = float(request.POST.get('textX'))*8
    Y = float(request.POST.get('textY'))*8
    size = request.POST.get('textSize')
    content = request.POST.get('textContent')

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

    paperSize = str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = str(density)

    # 把標籤名稱跟累型合在一起
    createdList = dict(zip(createdList,typeList))
    if language == 'chinese':
        return render(request,'label.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})
    elif language == 'english':
        return render(request,'label_en.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})
    elif language == 'vietnamese':
        return render(request,'label_vie.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})

def startPrint(request):
    global language
    copy = request.POST.get('copy')
    integratedExecutionCommand(paperName,int(copy))
    if language == 'chinese':
        return render(request,'finishPrint.html')
    elif language == 'english':
        return render(request,'finishPrint_en.html')
    elif language == 'vietnamese':
        return render(request,'finishPrint_vie.html')

def index_en(request):
    global language
    # Get all papers
    papers = os.listdir("./printLabel/commandTxt")
    for i in range(0,len(papers)):
        if 'json' in papers[i]:
            papers[i] = papers[i].replace('.json','')
    return render(request,'index_en.html',{"papers":papers})

def index_vie(request):
    global language
    # Get all papers
    papers = os.listdir("./printLabel/commandTxt")
    for i in range(0,len(papers)):
        if 'json' in papers[i]:
            papers[i] = papers[i].replace('.json','')
    return render(request,'index_vie.html',{"papers":papers})

def index(request):
    global language
    language = request.POST.get('language')
    # set default language to chinese
    if language == None:
        language = 'chinese'

    # Get all papers
    papers = os.listdir("./printLabel/commandTxt")
    for i in range(0,len(papers)):
        if 'json' in papers[i]:
            papers[i] = papers[i].replace('.json','')
    # Define language
    if language == 'english':
        return render(request,'index_en.html',{"papers":papers})
    elif language == 'vietnamese':
        return render(request,'index_vie.html',{"papers":papers})
    return render(request,'index.html',{"papers":papers})

def textSettings(request):
    global language
    if language == 'chinese':
        return render(request,'textSettings.html',{"X":"X","Y":"Y"})
    elif language == 'english':
        return render(request,'textSettings_en.html',{"X":"X","Y":"Y"})
    elif language == 'vietnamese':
        return render(request,'textSettings_vie.html',{"X":"X","Y":"Y"})

def qrSettings(request):
    global language
    if language == 'chinese':
        return render(request,'qrSettings.html')
    elif language == 'english':
        return render(request,'qrSettings_en.html')
    elif language == 'vietnamese':
        return render(request,'qrSettings_vie.html')

def printSettings(request):
    global language
    if language == 'chinese':
        return render(request,'printSettings.html')
    elif language == 'english':
        return render(request,'printSettings_en.html')
    elif language == 'vietnamese':
        return render(request,'printSettings_vie.html')
    
def restart(request):
    global language
    language = request.POST.get('language')
    # restart printerf
    tsclibrary.sendcommandW(chr(27) + '!R')
    tsclibrary.closeport()
    # 回初始頁面
    papers = os.listdir("./printLabel/commandTxt")
    for i in range(0,len(papers)):
        if 'json' in papers[i]:
            papers[i] = papers[i].replace('.json','')
    if language == 'chinese':
        return render(request,'index.html',{"papers":papers})
    elif language == 'english':
        return render(request,'index_en.html',{"papers":papers})
    elif language == 'vietnamese':
        return render(request,'index_vie.html',{"papers":papers})


def nutritionOption(request):
    global language
    if language == 'chinese':
        return render(request,'nutritionOption.html')
    elif language == 'english':
        return render(request,'nutritionOption_en.html')
    elif language == 'vietnamese':
        return render(request,'nutritionOption_vie.html')

def nutritionSettings(request):
    global language
    optionValues = request.POST.getlist('option')
    optionTitles = []
    with open("./printLabel/translate.json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)
    key = list(labelMessage.keys())
   
    if language == 'chinese':
        chinese = []
        for lan in labelMessage.values():
            chinese.append(lan[0])
        for i in range(0,len(optionValues)):
            if optionValues[i] in key:
                optionTitles.append(chinese[i])
        options = dict(zip(optionValues,optionTitles))
        return render(request,'nutritionFacts.html',{"options":options})
    elif language == 'english':
        english = []
        for lan in labelMessage.values():
            english.append(lan[1])
        for i in range(0,len(optionValues)):
            if optionValues[i] in key:
                optionTitles.append(english[i])
        options = dict(zip(optionValues,optionTitles))
        return render(request,'nutritionFacts_en.html',{"options":options})
    elif language == 'vietnamese':
        vietnamese = []
        for lan in labelMessage.values():
            vietnamese.append(lan[2])
        for i in range(0,len(optionValues)):
            if optionValues[i] in key:
                optionTitles.append(vietnamese[i])
        options = dict(zip(optionValues,optionTitles))
        return render(request,'nutritionFacts_vie.html',{"options":options})
    
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
    global language
    with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)
    itemName = request.POST.get('deleteItemButton')
    
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

    paperSize = str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = str(density)

    # 把標籤名稱跟累型合在一起
    createdList = dict(zip(createdList,typeList))

    # Define language
    if language == 'chinese':
        return render(request,'label.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})
    elif language == 'english':
        return render(request,'label_en.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})
    elif language == 'vietnamese':
        return render(request,'label_vie.html',{"paperName":paperName,"paperSize":paperSize,"density":density,"createdList":createdList})

def detail(request):
    global language
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
        """"""
        # Define language
        if language == 'chinese':
            return render(request,'textDetail.html',{"itemName":itemName,"size":size,"content":content,"X":X,"Y":Y})
        elif language == 'english':
            return render(request,'textDetail_en.html',{"itemName":itemName,"size":size,"content":content,"X":X,"Y":Y})
        elif language == 'vietnamese':
            return render(request,'textDetail_vie.html',{"itemName":itemName,"size":size,"content":content,"X":X,"Y":Y})
    
    elif itemType == "QRcode":
        X = labelMessage["%s"%paperName]["%s"%itemName]["X"] //8
        Y = labelMessage["%s"%paperName]["%s"%itemName]["Y"] //8
        content = labelMessage["%s"%paperName]["%s"%itemName]["content"]
        ECC = labelMessage["%s"%paperName]["%s"%itemName]["ECC"]
        width = labelMessage["%s"%paperName]["%s"%itemName]["width"]
        rotation = labelMessage["%s"%paperName]["%s"%itemName]["rotation"]

        """Delete item first"""
        with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
            labelMessage = json.load(jsonFile)
        del labelMessage["%s"%paperName]["%s"%itemName]

        with open("./printLabel/commandTxt/"+str(paperName)+".json","w",encoding='utf-8') as jsonFile:
            json.dump(labelMessage,jsonFile)
        """"""
        # Define language
        if language == 'chinese':

            return render(request,'qrDetail.html',{"itemName":itemName,"content":content,"X":X,"Y":Y,"ECC":ECC,"width":width,"rotation":rotation})
        elif language == 'english':
            return render(request,'qrDetail_en.html',{"itemName":itemName,"content":content,"X":X,"Y":Y,"ECC":ECC,"width":width,"rotation":rotation})
        elif language == 'vietnamese':
            return render(request,'qrDetail_vie.html',{"itemName":itemName,"content":content,"X":X,"Y":Y,"ECC":ECC,"width":width,"rotation":rotation})
    
    elif itemType == "營養標籤":
        option = list(labelMessage["%s"%paperName]["%s"%itemName].keys())[5:]
        optionValue = list(labelMessage["%s"%paperName]["%s"%itemName].values())[5:]
        X = labelMessage["%s"%paperName]["%s"%itemName]["X"] //8
        Y = labelMessage["%s"%paperName]["%s"%itemName]["Y"] //8
        weight = labelMessage["%s"%paperName]["%s"%itemName]["weight"]
        servings = labelMessage["%s"%paperName]["%s"%itemName]["servings"]

        """Delete item first"""
        with open("./printLabel/commandTxt/"+str(paperName)+".json","r",encoding='utf-8') as jsonFile:
            labelMessage = json.load(jsonFile)
    
        del labelMessage["%s"%paperName]["%s"%itemName]
        
        """"""
        with open("./printLabel/translate.json","r",encoding='utf-8') as jsonFile:
            labelMessage = json.load(jsonFile)
        key = list(labelMessage.keys())
          
        # Define language
        if language == 'chinese':
            # translate option to chinese       
            for i in range(0,len(option)):
                if option[i] in key:
                    option[i] = labelMessage["%s"%option[i]][0]
            option = dict(zip(option,optionValue))

            return render(request,'nutritionDetail.html',{"itemName":itemName,"option":option,"X":X,"Y":Y,"weight":weight,"servings":servings})
        elif language == 'english':
            for i in range(0,len(option)):
                if option[i] in key:
                    option[i] = labelMessage["%s"%option[i]][1]
            option = dict(zip(option,optionValue))
        
            return render(request,'nutritionDetail_en.html',{"itemName":itemName,"option":option,"X":X,"Y":Y,"weight":weight,"servings":servings})
        ### Nutrition Detail multi-language page ###
        elif language == 'vietnamese':
            for i in range(0,len(option)):
                if option[i] in key:
                    option[i] = labelMessage["%s"%option[i]][2]
            option = dict(zip(option,optionValue))

            return render(request,'nutritionDetail_vie.html',{"itemName":itemName,"option":option,"X":X,"Y":Y,"weight":weight,"servings":servings})
    
def findLabel(request):
    global paperName
    global tsclibrary
    global language

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
   
    if paperName is None:
        if language is None or language == 'chinese':
            return render(request,'index.html')
        elif language == 'english':
            return render(request,'index_en.html')
        elif language == 'vietnamese':
            return render(request,'index_vie.html')
    # 刪除
    if "delete" in paperName:
        paperName = paperName.replace("delete","") + ".json"
      
        # 取得commandTxt資料夾的檔案清單
        papers = os.listdir("./printLabel/commandTxt")
    
        for i in range(0,len(papers)):
            if paperName == papers[i]:
                os.remove(os.path.join("./printLabel/commandTxt", paperName))
                break

        # 回傳index.html
        papers = os.listdir("./printLabel/commandTxt")
        if len(papers) == 0:
            return render(request,'index.html')
        for i in range(0,len(papers)):
            if 'json' in papers[i]:
                papers[i] = papers[i].replace('.json','')
            # Define language
            if language == 'chinese':
                return render(request,'index.html',{"papers":papers})
            elif language == 'english':
                return render(request,'index_en.html',{"papers":papers})
            elif language == 'vietnamese':
                return render(request,'index_vie.html',{"papers":papers})
        
    # 回傳label.html
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
    paperSize = str(paperWidth)+"mm * "+str(paperHeight)+"mm"
    density = str(density)
    paperWidth = int(paperWidth)*4.1
    paperHeight = int(paperHeight)*4
    # Define language
    if language == 'chinese':
        return render(request,'label.html',{"paperName":paperName,"density":density,"paperSize":paperSize,"paperWidth":paperWidth,"paperHeight":paperHeight,"createdList":createdList})
    elif language == 'english':
        return render(request,'label_en.html',{"paperName":paperName,"density":density,"paperWidth":paperWidth,"paperHeight":paperHeight,"createdList":createdList,"paperSize":paperSize})
    elif language == 'vietnamese':
        return render(request,'label_vie.html',{"paperName":paperName,"density":density,"paperWidth":paperWidth,"paperHeight":paperHeight,"createdList":createdList,"paperSize":paperSize})
# 統合執行指令
def integratedExecutionCommand(paperName="test",copy=1):
    global language
    with open("./printLabel/commandTxt/"+paperName+".json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)

    labelOfPaper = list(labelMessage["%s"%paperName].keys())[3:]

    for i in range(0,len(labelOfPaper)):
        detailOfLabel = labelMessage["%s"%paperName]["%s"%labelOfPaper[i]]
        
        # 印文字
        if detailOfLabel["type"] == "文字":
            X = detailOfLabel["X"]
            Y = detailOfLabel["Y"]
            size = detailOfLabel["size"]
            content = detailOfLabel["content"]
            if language == 'english':
                # send text command
                tsclibrary.sendcommandW('TEXT '+str(X)+', '+str(Y)+',"'+str(size)+'", 0, 1, 1, "'+content+'"')
            elif language == 'chinese':
                printCommand = 'TEXT '+str(X)+', '+str(Y)+',"FONT001", 0, '+str(size)+', '+str(size)+', "'+content+'"'
                bytes_code = bytes(printCommand, 'big5')
                tsclibrary.sendcommand(bytes_code)
            elif language == 'vietnamese':
                printCommand = 'TEXT '+str(X)+', '+str(Y)+',"NotoSans.TTF", 0, '+str(size)+', '+str(size)+', "'+content+'"'
                bytes_code = bytes(printCommand, 'utf-8')
                tsclibrary.sendcommand(bytes_code)

        # 印QRcode
        elif detailOfLabel["type"] == "QRcode":
            X = detailOfLabel["X"]
            Y = detailOfLabel["Y"]
            width = detailOfLabel["width"]
            ECC = detailOfLabel["ECC"]
            rotation = detailOfLabel["rotation"]
            content = detailOfLabel["content"]
            # send QRcode command
            tsclibrary.sendcommandW('QRCODE '+str(X)+','+str(Y)+','+ECC+','+str(width)+',A,'+str(rotation)+',M2,S7,"'+content+'"')
        # 印營養標示
        else:
            X = detailOfLabel["X"]
            Y = detailOfLabel["Y"]
            weight = detailOfLabel["weight"]
            servings = detailOfLabel["servings"]
            optionList = list(detailOfLabel.keys())[5:]
            option = list(detailOfLabel.values())[5:]
            length = len(option)
            # 營養標示文字
            if language == 'english':
                tsclibrary.sendcommandW('TEXT '+str(X+80)+','+str(Y+20)+',"FONT001",0,1,1,"Nutrition Facts"')
            elif language == 'chinese':
                printCommand = 'TEXT '+str(X+180)+','+str(Y+20)+',"FONT001",0,1,1,"營養標示"'
                bytes_code = bytes(printCommand, 'big5')
                tsclibrary.sendcommand(bytes_code)
            # 要改的地方
            elif language == 'vietnamese':
                printCommand = 'TEXT '+str(X+180)+','+str(Y+20)+',"NotoSans.TTF",0,7,7,"營養標示"'
                bytes_code = bytes(printCommand, 'utf-8')
                tsclibrary.sendcommand(bytes_code)

            # 營養標示框框
            tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y)+', '+str(X+400)+', '+str(Y+50)+', 1')
            tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y+50)+', '+str(X+400)+', '+str(Y+110)+', 1')
            tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y+110)+', '+str(X+400)+', '+str(Y+150)+', 1')
            tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y+150)+', '+str(X+400)+', '+str(Y+160+25*length)+', 1')

            # 每份&每100公克的文字
            if language == 'english':
                tsclibrary.sendcommandW('TEXT '+str(X+10)+', '+str(Y+60)+',"FONT001", 0, 1, 1, "Servings size    ('+str(weight)+'g)"')
                tsclibrary.sendcommandW('TEXT '+str(X+10)+', '+str(Y+85)+',"FONT001", 0, 1, 1, "'+str(servings)+' servings per container"')
                print('TEXT '+str(X+10)+', '+str(Y+85)+',"FONT001", 0, 1, 1, "'+str(servings)+' servings per container"')
                tsclibrary.sendcommandW('TEXT '+str(X+150)+', '+str(Y+120)+',"FONT001", 0, 1, 1, "Per Serving"')
                tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+120)+',"FONT001", 0, 1, 1, "Per 100g"')
            elif language == 'chinese':
                eachCommand = 'TEXT '+str(X+10)+', '+str(Y+60)+',"FONT001", 0, 1, 1, "每一份量 '+str(weight)+'公克"'
                thisCommand = 'TEXT '+str(X+10)+', '+str(Y+85)+',"FONT001", 0, 1, 1, "本包裝含 '+str(servings)+'份"'
                packCommand = 'TEXT '+str(X+200)+', '+str(Y+120)+',"FONT001", 0, 1, 1, "每份"'
                gCommand = 'TEXT '+str(X+280)+', '+str(Y+120)+',"FONT001", 0, 1, 1, "每100公克"'
                eachBytes = bytes(eachCommand, 'big5')
                thisBytes = bytes(thisCommand, 'big5')
                packBytes = bytes(packCommand, 'big5')
                gBytes = bytes(gCommand, 'big5')
                tsclibrary.sendcommand(eachBytes)
                tsclibrary.sendcommand(thisBytes)
                tsclibrary.sendcommand(packBytes)
                tsclibrary.sendcommand(gBytes)
            #  要改的地方
            elif language == 'vietnamese':
                eachCommand = 'TEXT '+str(X+10)+', '+str(Y+60)+',"NotoSans.TTF", 0, 7, 7, "每一份量 '+str(weight)+'公克"'
                thisCommand = 'TEXT '+str(X+10)+', '+str(Y+85)+',"NotoSans.TTF", 0, 7, 7, "本包裝含 '+str(servings)+'份"'
                packCommand = 'TEXT '+str(X+200)+', '+str(Y+120)+',"NotoSans.TTF", 0, 7, 7, "每份"'
                gCommand = 'TEXT '+str(X+280)+', '+str(Y+120)+',"NotoSans.TTF", 0, 7, 7, "每100公克"'
                eachBytes = bytes(eachCommand, 'utf-8')
                thisBytes = bytes(thisCommand, 'utf-8')
                packBytes = bytes(packCommand, 'utf-8')
                gBytes = bytes(gCommand, 'utf-8')
                tsclibrary.sendcommand(eachBytes)
                tsclibrary.sendcommand(thisBytes)
                tsclibrary.sendcommand(packBytes)
                tsclibrary.sendcommand(gBytes)

            # 營養標示內容
            """列印語言轉換"""
            with open("./printLabel/translate.json","r",encoding='utf-8') as jsonFile:
                translation = json.load(jsonFile)
            key = list(translation.keys())
            optionList_in_language = []
            for l in range(0,len(optionList)):
                if optionList[l] in key:
                    if language == 'english':
                        optionList_in_language.append(translation["%s"%optionList[l]][1])
                    elif language == 'chinese':
                        optionList_in_language.append(translation["%s"%optionList[l]][0])
                    elif language == 'vietnamese':
                        optionList_in_language.append(translation["%s"%optionList[l]][2])
            """"""""""""""""""""""""
            for l in range(0,len(option)):
                # 熱量
                if optionList[l] == 'calories':
                    # 熱量文字
                    # 中文的字型也可以印英文的，所以英文跟中文可以寫一個就好
                    if language == 'chinese' or language == 'english':
                        printString = 'TEXT '+str(X+10)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+optionList_in_language[l]+'"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                    elif language == 'vietnamese':
                        printString = 'TEXT '+str(X+10)+', '+str(Y+160+25*l)+',"NotoSans.TTF", 0, 7, 7, "'+optionList_in_language[l]+'"'
                        bytes_code = bytes(printString, 'utf-8')
                        tsclibrary.sendcommand(bytes_code)
                    # 熱量的數值
                    if language == 'chinese':
                        # 每份的數值
                        printString = 'TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+option[l]+'大卡"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                        # 每100公克的數值
                        printString = 'TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'大卡"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                    # 除了中文的單位要寫中文，其他的好像都是英文單位
                    else:
                        tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+option[l]+'k"')
                        tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'k"')
                # 飽和脂肪、反式脂肪、糖要縮排
                elif optionList[l] == 'saturated fat'or optionList[l] == 'trans fat' or optionList[l] == 'sugar':
                    # 飽和脂肪、反式脂肪、糖的文字
                    # 中文的字型也可以印英文的，所以英文跟中文可以寫一個就好
                    if language == 'chinese' or language == 'english':
                        printString = 'TEXT '+str(X+15)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+optionList_in_language[l]+'"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                    elif language == 'vietnamese':
                        printString = 'TEXT '+str(X+15)+', '+str(Y+160+25*l)+',"NotoSans.TTF", 0, 7, 7, "'+optionList_in_language[l]+'"'
                        bytes_code = bytes(printString, 'utf-8')
                        tsclibrary.sendcommand(bytes_code)
                    # 飽和脂肪、反式脂肪、糖的數值
                    if language == 'chinese':
                        # 每份的數值
                        printString = 'TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+option[l]+'公克"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                        # 每100公克的數值
                        printString = 'TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'公克"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                    # 除了中文的單位要寫中文，其他的好像都是英文單位
                    else:
                        tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+option[l]+'g"')
                        tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'g"')
                # 鈉的單位是毫克
                elif optionList[l] == 'sodium':
                    # 鈉的文字
                    # 中文的字型也可以印英文的，所以英文跟中文可以寫一個就好
                    if language == 'chinese' or language == 'english':
                        printString = 'TEXT '+str(X+10)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+optionList_in_language[l]+'"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                    elif language == 'vietnamese':
                        printString = 'TEXT '+str(X+10)+', '+str(Y+160+25*l)+',"NotoSans.TTF", 0, 7, 7, "'+optionList_in_language[l]+'"'
                        bytes_code = bytes(printString, 'utf-8')
                        tsclibrary.sendcommand(bytes_code)
                    # 鈉的數值
                    if language == 'chinese':
                        # 每份的數值
                        printString = 'TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+option[l]+'毫克"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                        # 每100公克的數值
                        printString = 'TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'毫克"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                    # 除了中文的單位要寫中文，其他的好像都是英文單位
                    else:
                        tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+option[l]+'mg"')
                        tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'mg"')
                # 剩下不用縮排，單位是公克的營養素
                else :
                    # 營養素的文字
                    # 中文的字型也可以印英文的，所以英文跟中文可以寫一個就好
                    if language == 'chinese' or language == 'english':
                        printString = 'TEXT '+str(X+10)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+optionList_in_language[l]+'"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                    elif language == 'vietnamese':
                        printString = 'TEXT '+str(X+10)+', '+str(Y+160+25*l)+',"NotoSans.TTF", 0, 7, 7, "'+optionList_in_language[l]+'"'
                        bytes_code = bytes(printString, 'utf-8')
                        tsclibrary.sendcommand(bytes_code)
                    # 營養素的數值
                    if language == 'chinese':
                        # 每份的數值
                        printString = 'TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+option[l]+'公克"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                        # 每100公克的數值
                        printString = 'TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'公克"'
                        bytes_code = bytes(printString, 'big5')
                        tsclibrary.sendcommand(bytes_code)
                    # 除了中文的單位要寫中文，其他的好像都是英文單位
                    else:
                        tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+option[l]+'g"')
                        tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+160+25*l)+',"FONT001", 0, 1, 1, "'+str(int(float(option[l])/weight*100))+'g"')

    tsclibrary.printlabelW("1",str(copy))  