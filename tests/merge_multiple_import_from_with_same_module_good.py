from os import getppid, getuid


def main():
    tmp_first = getuid()
    tmp_second = getppid()


if __name__ == '__main__':
    main()
