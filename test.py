import pytest
import sys
import client
import server
from unittest import mock
import json
import time
import multiprocessing
'''
Небольшой модуль тестирования. Проверяет что работают все ключи, работает соединение клиент-сервер, работает обработчик команд и сами команды
'''
#фикстура под генерацию тестового файлика, для наглядности файл после тестов не удаляется
@pytest.fixture(scope="function")
def dummyfile():
    try:
        file.close()
    except:
        pass
    dummyname='dummy.bin'
    with open(dummyname, 'wb') as file:
        file.write(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09')
    file.close()
    return dummyname

'''
Задание параметров и предпологаемых результатов.
Разобрал 6 тест кейсов.
1 - поиск сигнатуры по паттерну
2 - поиск сигнатуры по паттерну, но паттерн не передан
3 - поиск сигнатуры по паттерну, но файл неверен
4 - помещение файла в карантин
5 - помещение файла в карантин, но паттерн не убран
6 - помещение файла в карантин, но файл неверен
'''
test_requests=[['CheckLocalFile','dummy.bin','02','2 12 '],
               ['CheckLocalFile','dummy.bin',None,'wrong pattern'],
               ['CheckLocalFile','wrong.bin','02','wrong file'],
               ['QuarantineLocalFile','dummy.bin',None,'Successful transition to quaranteen.'],
               ['QuarantineLocalFile','dummy.bin','02','Successful transition to quaranteen.'],
               ['QuarantineLocalFile','wrong.bin','02','transition error:']]
@pytest.fixture(params=test_requests, scope="function")
def request_param(request):
    return request.param

'''
тестирование парсера клиента
'''
def test_parser_client():
    test_args_client = ['program', '-r', 'CheckLocalFile', '-f', 'somefile', '-p', 'somepattern']
    with mock.patch.object(sys, 'argv', test_args_client):
        parser = client.createParser()
        args = parser.parse_args()
        assert args.request == 'CheckLocalFile'
        assert args.file == 'somefile'
        assert args.pattern == 'somepattern'

'''
тестирование парсера сервера
'''
def test_parser_server():
    test_args_server = ['program', '-t', '10']
    with mock.patch.object(sys, 'argv', test_args_server):
        parser = server.createParser()
        args = parser.parse_args()
        assert args.threads == '10'

'''
Проверка работоспособности соединения
'''
def test_connection():
    def start_server():
        def server1():
            server.recieve(5)
        p = multiprocessing.Process(target=server1)
        p.daemon=True
        p.start()
        time.sleep(0.5)
    start_server()
    ans=client.send('1','n.py','3')
    assert 'Received' in str(ans)

'''
Проверка работы функционала и обработчика команд
'''
def test_handler_and_cmds(dummyfile,request_param):
    message={"command": request_param[0], "params": {"file":request_param[1],"pattern":request_param[2]}} #
    data=json.dumps(message)
    send=bytes(data,encoding="utf-8")
    recieved=send.decode("utf-8")
    assert server.handler(recieved) == request_param[3]


