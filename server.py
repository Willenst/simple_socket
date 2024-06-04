import socket
import json
import sys
from _thread import *
import concurrent.futures
import argparse
import re
import os 
import shutil

host = ""
port = 12345

catalog = "quaranteen" #базовый каталог

'''
Перенос файла в карантин
    filename - название файла
    создается каталог и через shutil переносится сам файл
'''
def move_to_quaranteen(filename):
    if not os.path.exists(catalog): 
        os.mkdir(catalog)
    file_path = os.path.basename(filename)
    try:
        shutil.move(file_path, os.path.join(catalog, filename))
        return "Successful transition to quaranteen."
    except:
        return "transition error:"

'''
Поиск смещений сигнатур
filename - название файла
pattern - набор байтов в виде hex строки
с помощью регулярок цепляем индексы элементов и выводим в виде списка-строки
'''
def sigfinder(filename,pattern):
    res1=''
    file=open(filename, 'rb') #побайтовое чтение файла для поиска сигнатур
    content=file.read()
    pattern = bytes.fromhex(pattern) #переход из обычной интерпритации хекса в воспринимаемый питоном байт код
    for match in re.finditer(pattern, content): #регулярка ловит все позиции вхождения
            res1=res1+str(match.start())+' '
    print(res1)
    if len(res1)==0: #в случае отсуствия вхождений - возвращаем информацию о том, что сигнатура не обнаружина
        res1='signature not found'
    return res1 #возвращаем именно строку для удобства, но по сути это список, можно распарсить через re.sub

'''
Обработчик команды - получает на вход json строку и парсит из нее параметры 
json_string - строка сообщения в json формате
соотвественно в зависимости от переданной команды выбирает необходимую функцию
'''
def handler(json_string):
    parsed_json = json.loads(json_string) #парсинг данных для дальнейшего разбиения
    print(parsed_json)
    cmd=parsed_json["command"]
    print(cmd)
    filename=parsed_json["params"]["file"]
    print(filename)
    pattern=parsed_json["params"]["pattern"]
    res = 'wrong' #флаг сигнализирующий о том, что команда не считалась, в текущей конфигурации клиента по сути не должен работать
    if cmd=='CheckLocalFile': #проверка типа команды
        if pattern==None:
            res = 'wrong pattern'
            return res
        try:
            open(filename, 'rb')
        except:
            res = 'wrong file'
            return res
        else:
            res = sigfinder(filename,pattern)
    elif cmd=='QuarantineLocalFile':
        res = move_to_quaranteen(filename)
    else:
        return 'no ans'
    return res

'''
Парсер командной строчки
'''
def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-t', '--threads', default=1)
    parser.add_argument ('-c', '--catalog', default='quaranteen')
    return parser

'''
Прием сообщений, реализовано согласно тз через многопоточку
c - сокет с активным соединением
'''
def threaded(c):
    received = c.recv(2048) #входной пул ограничен 2кб
    data = received.decode("utf-8") #декодирование сообщения
    ans=handler(data)
    c.send(bytes(ans,encoding="utf-8")) #кодирование и отправка ответа
    c.close()
 
'''
Само тело сервера
threads - входящие потоки
'''
def recieve(threads):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #создание простейшего сокета
    s.bind((host, port)) #в качестве хоста мы ничего не указали, та что берется локалхост, порт - сверху
    print("socket binded to port", port)

    s.listen(threads) #количетсво соединений, решил что будет неплохо сделать равным числу рабочих потоков
    print("socket is listening")
 
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor: #создание пула потоков, по мере поступления соединений создаются потоки, при отсуствии свободных - клиент ждет
        while True:
            c, addr = s.accept() #прием соединения
            print('Connected to :', addr[0], ':', addr[1])
            executor.submit(threaded, c) #запуск потока с сокетом и его дальнейшей обработкой
        s.close()
 
'''
Инициализирующий блок кода, запускает парсер и тело сервера
'''
if __name__ == '__main__':
    parser = createParser() 
    namespace = parser.parse_args(sys.argv[1:]) #задаем парсер и читаем поступившие аргументы, в данном случае создаются "подклассы" каждый со своим аргументов
    if namespace.catalog:
        catalog = namespace.catalog #т.е. то что мы именовали в парсере как --catalog тут вызывается через namespace.catalog
    recieve(int(namespace.threads))
