from os import getuid
from sys import argv as av


def main():
    tmp_first = av[0]
    tmp_second = getuid()


if __name__ == '__main__':
    main()
