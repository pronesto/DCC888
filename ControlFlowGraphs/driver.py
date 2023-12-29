import sys
from todo import *

if __name__ == "__main__":
    lines = sys.stdin.readlines()

    options_map = {
        "test_min": test_min(int(lines[1]), int(lines[2])),
        "test_min3": test_min3(int(lines[1]), int(lines[2]), int(lines[3])),
        "test_div": test_div(int(lines[1]), int(lines[2])),
        "fact": test_fact(int(lines[1]))
    }
    option = lines[0].strip()

    print(options_map.get(option))
