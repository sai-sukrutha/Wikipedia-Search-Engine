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


def read_index(index_path):
    index ={}
    if(os.path.isfile(index_path)):
        statinfo = os.stat(index_path)
        print("Index File size - ",convert_bytes(statinfo.st_size))
        with open(index_path, 'rb') as file:
            index = pickle.load(file)
        # with open(index_path, 'rb') as file:
        #     index = json.loads(file)
        #print("index - ",index)
    else:
        print("index does not exist")
    return index


def read_docid(index_path):
    docid = {}
    docid_path = '/'.join((index_path.split('/')[:-1]))
    docid_path = os.path.join(docid_path,"docid_title.pkl")
    print("Docid path -",docid_path)
    if(os.path.isfile(docid_path)):
        statinfo = os.stat(docid_path)
        print("Docid File size - ",convert_bytes(statinfo.st_size))
        with open(docid_path, 'rb') as file:
            docid = pickle.load(file)
        #print("docid - ",docid)
    else:
        print("docid_title file does not exist")
    return docid


def read_inputfile(input_path):
    with open(input_path, 'r') as file:
        queries = file.readlines()
    return queries


def write_file(outputs, output_path):
    '''outputs should be a list of lists.
        len(outputs) = number of queries
        Each element in outputs should be a list of titles corresponding to a particular query.'''
    with open(output_path, 'w') as file:
        for output in outputs:
            for line in output:
                file.write(line.strip() + '\n')
            file.write('\n')


def search(index_path, queries):
    outputs = []
    print("Received Query",queries)
    index = read_index(index_path)
    docid = read_docid(index_path)
    return outputs
    #Perform searching



def main():
    if len(sys.argv)!= 4:
        print("Error:Syntax: python3 searching.py <index_path> <path_to_input> <path_to_output>")
        sys.exit(0)
    else:
        index_path=sys.argv[1]
        input_path=sys.argv[2]
        output_path=sys.argv[3]
        print("index_path - ",index_path)
        print("input_path - ",input_path)
        print("output_path - ",output_path)

        queries = read_inputfile(input_path)
        outputs = search(index_path, queries)
        # write_file(outputs, output_path)


if __name__ == "__main__":
    main()