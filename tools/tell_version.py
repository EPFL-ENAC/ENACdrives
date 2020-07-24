import sys

sys_path = sys.path
sys_path.insert(0, '/home/sbancal/Projects/enacdrives/client')
sys.path = sys_path

from enacdrives import utility

if __name__ == "__main__":
    print(utility.CONST.VERSION)
