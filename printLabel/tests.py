from django.test import TestCase
import json
import ctypes
# Create your tests here.
tsclibrary = ctypes.WinDLL("./printLabel/TSCLIB.dll")
"""翻譯成中文"""
def translate():
    with open("./printLabel/translate.json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)
    english = list(labelMessage.keys())
    chinese = list(labelMessage.values())
    print(english)
    print(chinese)

"""統合執行命令"""
def integratedExecutionCommand(paperName="test",copy=1):
    with open("./printLabel/commandTxt/"+paperName+".json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)

    labelOfPaper = list(labelMessage["%s"%paperName].keys())[3:]

    for i in range(0,len(labelOfPaper)):
        detailOfLabel = labelMessage["%s"%paperName]["%s"%labelOfPaper[i]]
    
        if detailOfLabel["type"] == "文字":
            X = detailOfLabel["X"]
            Y = detailOfLabel["Y"]
            size = detailOfLabel["size"]
            content = detailOfLabel["content"]
            # send text command
            tsclibrary.sendcommandW('TEXT '+str(X)+', '+str(Y)+',"'+str(size)+'", 0, 1, 1, "'+content+'"')
            print("send command : ",'TEXT '+str(X)+', '+str(Y)+',"'+str(size)+'", 0, 1, 1, "'+content+'"')

        elif detailOfLabel["type"] == "QRcode":
            X = detailOfLabel["X"]
            Y = detailOfLabel["Y"]
            width = detailOfLabel["width"]
            ECC = detailOfLabel["ECC"]
            rotation = detailOfLabel["rotation"]
            content = detailOfLabel["content"]
            # send QRcode command
            tsclibrary.sendcommandW('QRCODE '+str(X)+','+str(Y)+','+ECC+','+str(width)+',A,'+str(rotation)+',M2,S7,"'+content+'"')
            print("send command : ",'QRCODE '+str(X)+','+str(Y)+','+ECC+','+str(width)+',A,'+str(rotation)+',M2,S7,"'
                            +content+'"')
        else:
            X = detailOfLabel["X"]
            Y = detailOfLabel["Y"]
            weight = detailOfLabel["weight"]
            servings = detailOfLabel["servings"]
            optionList = list(detailOfLabel.keys())[5:]
            option = list(detailOfLabel.values())[5:]
            length = len(option)

            # BOX
            tsclibrary.sendcommandW('TEXT '+str(X+80)+','+str(Y+20)+',"chinese",0,1,1,"Nutrition Facts"')
            tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y)+', '+str(X+400)+', '+str(Y+50)+', 1')
            tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y+50)+', '+str(X+400)+', '+str(Y+110)+', 1')
            tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y+110)+', '+str(X+400)+', '+str(Y+150)+', 1')
            tsclibrary.sendcommandW('BOX '+str(X)+', '+str(Y+150)+', '+str(X+400)+', '+str(Y+160+25*length)+', 1')

            # serving size
            tsclibrary.sendcommandW('TEXT '+str(X+10)+', '+str(Y+60)+',"chinese", 0, 1, 1, "Each contains '+str(weight)+' grams"')
            tsclibrary.sendcommandW('TEXT '+str(X+10)+', '+str(Y+85)+',"chinese", 0, 1, 1, "This contains '+str(servings)+' package"')
            tsclibrary.sendcommandW('TEXT '+str(X+200)+', '+str(Y+120)+',"chinese", 0, 1, 1, "1 pack"')
            tsclibrary.sendcommandW('TEXT '+str(X+300)+', '+str(Y+120)+',"chinese", 0, 1, 1, "100 g"')

            # option
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

    tsclibrary.printlabelW("1",str(copy))     

def translate():
    with open("./printLabel/translate.json","r",encoding='utf-8') as jsonFile:
        labelMessage = json.load(jsonFile)
    english = list(labelMessage.keys())
    chinese = []
    for lan in labelMessage.values():
        chinese.append(lan[0])
    print(chinese)
if __name__ == "__main__":
    translate()