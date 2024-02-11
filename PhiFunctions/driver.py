import sys
from programs import *

if __name__ == "__main__":
    lines = sys.stdin.readlines()
    option = lines[0].strip()
    if option == "test_min":
        print(test_min(int(lines[1]), int(lines[2])))
    elif option == "test_min3":
        print(test_min3(int(lines[1]), int(lines[2]), int(lines[3])))
    elif option == "test_div":
        print(test_div(int(lines[1]), int(lines[2])))
    elif option == "fact":
        print(test_fact(int(lines[1])))
    elif option == "fib":
        print(test_fib(int(lines[1])))
    elif option == "fib_swap_problem":
        print(test_fib_swap_problem(int(lines[1])))
    elif option == "test_fib_swap_problem_fixed_with_phi_blocks":
        print(test_fib_swap_problem_fixed_with_phi_blocks(int(lines[1])))
    else:
        print("Invalid option: {option}")
