# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 16:14:49 2020

@author: sasha
"""
import time
from datetime import datetime, timedelta
import requests
import csv
import re


#функция для поиска позиции n-го вхождения строки
def find_nth(string, needle, n):
    start = string.find(needle)
    while start >= 0 and n > 0:
        start = string.find(needle, start+len(needle))
        n -= 1
    return start

file_input = 'sverdl_objects.csv'
file_output = 'google_marks_3m_' + time.strftime('%Y%m%d%H%M%S') + '.csv'


#приведение кластеризованной семантики к двумерному массиву
semant_clast = []
with open(file_input, 'r', newline='') as File_semant:
    reader = csv.reader(File_semant, delimiter=';')
    for row in reader:
        semant_clast.append(row)

#собираем объекты в список, убираем дубли
objects = []
for i in range(1, len(semant_clast)):
    objects.append(semant_clast[i][4])

#Создаем словарь: ключ - объект, значение - ['регион', 'город', 'категория']
semant_dict = dict()
with open(file_input, 'r', newline='') as File_region:
    reader = csv.DictReader(File_region, delimiter=';')
    for line in reader:
        semant_dict[line["object"]] = [line["region"], line["city"], line["cat"], line["comerc"]]

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}


with open(file_output, 'w', newline='') as file:
    fields = ['region', 'city', 'cat', 'comerc', 'object', 'mark', 'date']
    writer = csv.DictWriter(file, fieldnames=fields, delimiter=';')
    writer.writeheader()
    for line in objects:
        r = requests.get('https://www.google.com/maps/?q=' + line + ' ' + semant_dict[line][1] + '&oq=' + line + ' ' + semant_dict[line][1], headers = headers)
        page = r.text
        m = re.compile('",[1-5],null,') # маска поиска оценки
        i1 = page.count('месяц назад\\",null') # считаем количество вхождений фразы "месяц назад"
        if i1 > 0:
            for i in range(i1):
                dp = find_nth(page, 'месяц назад\\",null', i) # ищем, на какой позиции встречается фраза в i-й раз
                mark_p = re.search(m, page[dp:]) # ищем оценку по маске в срезанной строке
                mp = mark_p.start() # записываем номер позиции оценки
                #записываем дату оценки
                now = datetime.now()
                t = now-timedelta(30)
                writer.writerow({'region':semant_dict[line][0],
                                 'city':semant_dict[line][1],
                                 'cat':semant_dict[line][2],
                                 'comerc':semant_dict[line][3],
                                 'object':line,
                                 'mark': page[dp+mp+2:dp+mp+3],
                                 'date': t.strftime("%Y-%m")
                                 })
        #повторяем для оценок за 2 и 3 месяца назад
        i2 = page.count('2 месяца назад\\",null')
        if i2 > 0:
            for i in range(i2):
                dp = find_nth(page, '2 месяца назад\\",null', i)
                mark_p = re.search(m, page[dp:])
                mp = mark_p.start()
                now = datetime.now()
                t = now-timedelta(60)
                writer.writerow({'region':semant_dict[line][0],
                                 'city':semant_dict[line][1],
                                 'cat':semant_dict[line][2],
                                 'comerc':semant_dict[line][3],
                                 'object':line,
                                 'mark': page[dp+mp+2:dp+mp+3],
                                 'date': t.strftime("%Y-%m")
                                 })

        i3=page.count('3 месяца назад\\",null')
        if i3 > 0:
            for i in range(i3):
                dp = find_nth(page, '3 месяца назад\\",null', i)       
                mark_p = re.search(m, page[dp:])
                mp = mark_p.start()
                now = datetime.now()
                t = now-timedelta(90)
                writer.writerow({'region':semant_dict[line][0],
                                 'city':semant_dict[line][1],
                                 'cat':semant_dict[line][2],
                                 'comerc':semant_dict[line][3],
                                 'object':line,
                                 'mark': page[dp+mp+2:dp+mp+3],
                                 'date': t.strftime("%Y-%m")
                                 })
    time.sleep(1)
    