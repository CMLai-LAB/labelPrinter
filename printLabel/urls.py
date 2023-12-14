from django.contrib import admin
from django.urls import path, include
from printLabel import views

urlpatterns = [
    path('',views.index,name='index'),
    path('setup/',views.setup,name='setup'),
    path('textSettings/',views.textSettings,name='textSettings'),
    path('text/',views.text,name='text'),
    path('qrSettings/',views.qrSettings,name='qrSettings'),
    path('qrCode/',views.qrCode,name='qrCode'),
    path('nutritionFacts/',views.nutritionFacts,name='nutritionFacts'),
    path('printSettings/',views.printSettings,name='printSettings'),
    path('printLabel/',views.printLabel,name='printLabel'),
    path('restart/',views.restart,name='restart'),
    path('nutritionOption/',views.nutritionOption,name='nutritionOption'),
    path('nutritionSettings/',views.nutritionSettings,name='nutritionSettings'),
    path('drawOnHtml/',views.drawOnHtml,name='drawOnHtml'),
    path('deleteItem/',views.deleteItem,name='deleteItem'),
    path('detail/',views.detail,name='detail'),
    path('findLabel/',views.findLabel,name='findLabel'),
    path('index_en/',views.index_en,name='index_en'),
    path('index_vie/',views.index_vie,name='index_vie'),
]