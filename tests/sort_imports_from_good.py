from os import getcwd, getuid
from sys import argv as av


def main():
    tmp_first = av[0]
    tmp_second = getuid()
    tmp_third = getcwd()


if __name__ == '__main__':
    main()
