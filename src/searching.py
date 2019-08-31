import sys
import os
import re
import _pickle as pickle
import textprocessing
import heapq
import gzip

index_file_name = "my_index.pkl"
docid_file_name = "docid_title.pkl"


def read_index(index_path):
    index ={}
    file_path = os.path.join(index_path,index_file_name)
    if(os.path.isfile(file_path)):
        statinfo = os.stat(file_path)
        # print("Index File size - ",statinfo.st_size)
        with open(file_path, 'rb') as file:
            index = pickle.load(file)
    else:
        print("index does not exist")
        sys.exit(1)
    return index


def read_docid(index_path):
    docid_dict = {}
    file_path = os.path.join(index_path,docid_file_name)
    if(os.path.isfile(file_path)):
        statinfo = os.stat(file_path)
        # print("Docid File size - ",statinfo.st_size)
        with open(file_path, 'rb') as file:
            docid_dict = pickle.load(file)
    else:
        print("docid_title file does not exist")
        sys.exit(1)
    return docid_dict


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

def get_score(doc_score,weights=[0.3,0.2,0.1,0.1,0.1,0.2]):
    docid = doc_score[0]
    counts = doc_score[1]
    #If sum of weights 0 -some error -again give same weights
    w_sum = 0
    for weight in weights:
        w_sum+=weight
    if(w_sum == 0):
        weights = [0.3,0.2,0.1,0.1,0.1,0.2]
    #Get score with counts and weights
    score = 0        # Negative to insert into min heap
    score -= (counts[0]*weights[0])+(counts[1]*weights[1])+(counts[2]*weights[2])+(counts[3]*weights[3])+(counts[4]*weights[4])+(counts[5]*weights[5])
    # score -= counts[0]+counts[1]+counts[2]+counts[3]+counts[4]+counts[5]
    return score,docid


def search(index_path, queries):
    outputs = []
    index = read_index(index_path)
    docid_dict = read_docid(index_path)
    num_res = 10    #Number of results
    for query in queries:
        doc_heap = []
        output = []
        if( re.search('title:|body:|infobox:|category:|ref:|link:',query)):
            # Search with Fields
            query_fields = query.split()
            length = len(query_fields)
            for qf in query_fields:
                field,word = qf.split(':')
                weights = [0,0,0,0,0,0]
                if(field == 'title'):
                    weights[0] = 1
                if(field == 'infobox'):
                    weights[1] = 1
                if(field == 'ref'):
                    weights[2] = 1
                if(field == 'link'):
                    weights[3] = 1
                if(field == 'category'):
                    weights[4] = 1
                if(field == 'body'):
                    weights[5] = 1
                word = textprocessing.process_query(word)    ##Get only 1 word ??
                if ( word[0] in index):
                    docs_list = index[word[0]]
                    for doc in docs_list:
                        #find if that doc is already present
                        ind = -1
                        i = 0
                        if(len(doc_heap)):
                            for doc_pair in doc_heap:
                                if(doc_pair[1] == doc[0]):
                                    ind = i
                                    break
                                i+=1
                            if(ind != -1):
                                old_val = doc_heap[ind][0]
                                new_list = get_score(doc,weights)
                                new_val = old_val+new_list[0]
                                doc_heap[ind][0] = new_val
                                heapq._siftdown(doc_heap,0,ind)
                            else:
                                score,docid = get_score(doc,weights)
                                heapq.heappush(doc_heap,[score,docid])
                        else:
                            score,docid = get_score(doc,weights)
                            heapq.heappush(doc_heap,[score,docid])
            if(len(doc_heap)):
                results = heapq.nsmallest(num_res,doc_heap)
                for res in results:
                    # if(res[0] <= -length):      #To match all conditions in field???-does not work
                    output.append(docid_dict[res[1]])
            else:
                print("No documents matching")
                    
        else:
            #Simple Query
            query_words = textprocessing.process_query(query)
            if(len(query_words) == 1):
                if ( query_words[0] in index ):
                    docs_list = index[query_words[0]]
                    for doc in docs_list:
                        score,docid = get_score(doc)
                        heapq.heappush(doc_heap,[score,docid])
                    results = heapq.nsmallest(num_res,doc_heap)
                    for res in results:
                        output.append(docid_dict[res[1]])
                else:
                    print("No documents matching")

            else:
                # NUmber of words in query - merge
                for word in query_words:
                    if ( word in index):
                        docs_list = index[word]
                        for doc in docs_list:
                            #find if that doc is already present
                            ind = -1
                            i = 0
                            if(len(doc_heap)):
                                for doc_pair in doc_heap:
                                    if(doc_pair[1] == doc[0]):
                                        ind = i
                                        break
                                    i+=1
                                if(ind != -1):
                                    old_val = doc_heap[ind][0]
                                    new_list = get_score(doc)
                                    new_val = old_val+new_list[0]
                                    doc_heap[ind][0] = new_val
                                    heapq._siftdown(doc_heap,0,ind)
                                else:
                                    score,docid = get_score(doc)
                                    heapq.heappush(doc_heap,[score,docid])
                            else:
                                score,docid = get_score(doc)
                                heapq.heappush(doc_heap,[score,docid])
                if(len(doc_heap)):
                    results = heapq.nsmallest(num_res,doc_heap)
                    for res in results:
                        output.append(docid_dict[res[1]])
                else:
                    print("No documents matching")
        outputs.append(output)
    return outputs


def main():
    if len(sys.argv)!= 4:
        print("Error:Syntax: python3 searching.py <index_path> <path_to_input> <path_to_output>")
        sys.exit(0)
    else:
        index_path=sys.argv[1]
        input_path=sys.argv[2]
        output_path=sys.argv[3]
        queries = read_inputfile(input_path)
        outputs = search(index_path, queries)
        write_file(outputs, output_path)


if __name__ == "__main__":
    main()
