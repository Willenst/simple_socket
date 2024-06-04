import sys
import argparse
import os

'''
Генерация файла забитого случайными байтами, создание парсера параметров, да и в целом все.
'''
def dummyfile(fileSizeInBytes,name):
    try:
        file.close()
    except:
        pass
    dummyname=name
    with open(dummyname, 'wb') as file:
        file.write(os.urandom(fileSizeInBytes))
    file.close()
    return dummyname

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-s', '--size', default=1024)
    parser.add_argument ('-n', '--name', default='dummy.bin')
    return parser

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    dummyfile(int(namespace.size),namespace.name)