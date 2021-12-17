print("pyplant.__main__")

from pyplant.parser import python_ast as python
#from pyplant.parser import python

from pyplant.plotter import plantuml

import sys

def main():
    if len(sys.argv) < 1:
        print("At least one parameter is needed")
        exit(1)

    data = python.parse_module(sys.argv[1])

    print("\n--------> PPrint Data <----------\n")

    for package in data:
        print(package)

    print("\n--------> Plotting <----------\n")
    plantuml.plant(data)


if __name__ == "__main__":
    main()
