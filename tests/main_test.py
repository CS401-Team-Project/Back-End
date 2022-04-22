import os
import subprocess
import sys


def main(args):
    print('\n')
    os.system('pytest subtests/start_test.py -v ' + ' '.join(args))

    #exec(open('subtests/start_test.py').read())


if __name__ == "__main__":

    main(sys.argv)
