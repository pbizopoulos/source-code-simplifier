from os import getppid
from os import getuid


def main():
    tmp_first = getuid()
    tmp_second = getppid()


if __name__ == '__main__':
    main()
