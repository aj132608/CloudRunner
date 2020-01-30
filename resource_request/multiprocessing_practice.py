from multiprocessing import Process
import os


def info(title):
    print(title)
    print(f'module name: {__name__}')
    print(f'process id: {os.getpid()}')


def f(name):
    info('function f')
    print(f"hello {name}")


if __name__ == '__main__':
    # info('main line')
    for index in range(0, 10):
        Process(target=f, args=('bob',)).start()
    # p = Process(target=f, args=('bob',))
    # p.start()
    # p.join()
