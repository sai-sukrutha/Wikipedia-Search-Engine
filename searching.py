import sys
import os
import _pickle as pickle
import json

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def readIndex(index_path):
    if(os.path.isfile(index_path)):
        statinfo = os.stat(index_path)
        print("File size - ",convert_bytes(statinfo.st_size))
        with open(index_path, 'rb') as file:
            index = pickle.load(file)
        # with open(index_path, 'rb') as file:
        #     index = json.loads(file)
        print("index - ",index)
    else:
        print("index does not exist")



def main():
    if len(sys.argv)!= 4:
        print("Error:Syntax: python3 searching.py <path_to_index> <path_to_input> <path_to_output>")
        sys.exit(0)
    else:
        index_path=sys.argv[1]
        input_path=sys.argv[2]
        output_path=sys.argv[3]
        print("index_path - ",index_path)
        print("input_path - ",input_path)
        print("output_path - ",output_path)
        readIndex(index_path)


if __name__ == "__main__":
    main()
