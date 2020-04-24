# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 16:14:49 2020

@author: sasha
"""
import time
import requests
from bs4 import BeautifulSoup as bs
import csv
import os
#from utils import get_cvmde_path, write_to_db

# Установить текущую папку как рабочую директорию
#work_dir = os.path.dirname(os.path.realpath(__file__))
#os.chdir(work_dir)

# Названия файлов для входных/выходных данных
f_input = 'sverdl_objects.csv'
f_output = 'google-reviews-parser_avg_' + time.strftime('%Y%m%d%H%M%S') + '.csv'

# Установить конечный путь для результатов
#cvmde_path = get_cvmde_path()
#output_dir = os.path.join(cvmde_path, 'data/scrapy/google-reviews-parser')
output_dir = ''
#os.makedirs(output_dir, exist_ok=True)

file_output = os.path.join(output_dir, f_output)

#приведение кластеризованной семантики к двумерному массиву
semant_clast = []
with open(f_input, 'r', newline='', encoding='1251') as File_semant:
    reader = csv.reader(File_semant, delimiter=';')
    for row in reader:
        semant_clast.append(row)

#собираем объекты в список
objects = []
for i in range(1, len(semant_clast)):
    objects.append(semant_clast[i][4])

#Создаем словарь: ключ - объект, значение - ['регион','город','категория']
semant_dict = dict()
with open(f_input, 'r', newline='', encoding='1251') as File_region:
    reader = csv.DictReader(File_region, delimiter=';')
    for line in reader:
        semant_dict[line["object"]] = [line["region"], line["city"], line["cat"], line["comerc"]]

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}

#создаем файл с оценками
with open(f_output, 'w', newline='') as file:
    fields = ['region', 'city', 'cat', 'comerc', 'object', 'mark']
    writer = csv.DictWriter(file, fieldnames=fields, delimiter=';')
    writer.writeheader()
    for line in objects:
        #line=line.replace(' ','+')
        r = requests.get('https://www.google.com/search?q=' + line + ' ' + semant_dict[line][1] + '&oq=' + line + ' ' + semant_dict[line][1] + '&aqs=chrome.0.69i59j69i65j0l4.4212j0j7&sourceid=chrome&ie=UTF-8', headers = headers)
        time.sleep(1)
        soup = bs(r.text, 'lxml')
        mark = str(soup.select("span.Aq14fc"))
        s = mark.find('>')
        f = mark.find('<',s)
        writer.writerow({'region':semant_dict[line][0],
                         'city':semant_dict[line][1],
                         'cat':semant_dict[line][2],
                         'comerc':semant_dict[line][3],
                         'object':line,
                         'mark': mark[s+1:f]})
        print(line + semant_dict[line][1] + ' ' + mark[s+1:f])
        print('____')
        time.sleep(1)
        