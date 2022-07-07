from sys import argv as av
from os import getuid, getcwd


def main():
    tmp_first = av[0]
    tmp_second = getuid()
    tmp_third = getcwd()


if __name__ == '__main__':
    main()
