from sys import argv as av
from os import getuid


def main():
    tmp_first = av[0]
    tmp_second = getuid()


if __name__ == '__main__':
    main()
