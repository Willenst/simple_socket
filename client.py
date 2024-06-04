import socket
import json
import sys
import argparse

host = '127.0.0.1'
port = 12345

'''
Парсер командной строчки
'''
def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-r', '--request', choices=['CheckLocalFile', 'QuarantineLocalFile'], required=True)
    parser.add_argument ('-f', '--file', required=True)   
    parser.add_argument ('-p', '--pattern')

    if parser.parse_args(sys.argv[1:]).request == "CheckLocalFile" and parser.parse_args(sys.argv[1:]).pattern == None: #т.к. в случае CheckLocalFile паттерн обязателен, кидаем ошибку если его нет
        parser.error("CheckLocalFile requires pattern (-p PATTERN)")
    return parser

'''
реализация клиента на базе сокетов.
'''
def send(file,request,pattern):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #создание простейшего сокета
    s.connect((host,port))
    message = {"command": request, "params": {"file":file,"pattern":pattern}} #Генерация сообщения в json формате, изначально задаем его как питоновский словарь
    data = json.dumps(message) #затем библиотека json сама его дорабатывает до нужного нам объекта
    s.send(bytes(data,encoding="utf-8")) #кодировка в байты и отправка сообщения
    data = s.recv(1024) #получение ответа
    s.close()
    return 'Received from the server :'+str(data.decode('utf8')) #возвращаем строку с ответом
 
'''
Инициализирующий блок кода, запускает парсер и клиента
'''
if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:]) #задаем парсер и читаем поступившие аргументы, в данном случае создаются "подклассы" каждый со своим аргументов
    file=namespace.file #т.е. то что мы именовали в парсере как --file тут вызывается через namespace.file
    request=namespace.request
    pattern=namespace.pattern
    print(pattern)
    if len(pattern)%2!=0: #проверка на корректность вводимого паттерна сигнатуры
        raise ValueError('even number of symbols, wrong byte chain')
    if len(pattern)==0: #проверка на пустую строку
        pattern=None

    print(send(file,request,pattern))