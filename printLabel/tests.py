from django.test import TestCase
import json
# Create your tests here.
# translate option to chinese
with open("./printLabel/translate.json","r",encoding='utf-8') as jsonFile:
    labelMessage = json.load(jsonFile)
english = list(labelMessage.keys())
chinese = list(labelMessage.values())
print(english)
print(chinese)