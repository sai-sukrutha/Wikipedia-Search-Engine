import sys
import os
import re
import _pickle as pickle
import textprocessing
import heapq
import gzip
from sortedcontainers import SortedDict
from math import log2

index_file_name = "my_index.pkl"
docid_file_name = "docid_title.pkl"
docsno_file_name = "docs_no.txt"

# def convert_bytes(num):
#     """
#     this function will convert bytes to MB.... GB... etc
#     """
#     for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
#         if num < 1024.0:
#             return "%3.1f %s" % (num, x)
#         num /= 1024.0


def read_index(index_path):
    index = SortedDict()
    file_path = os.path.join(index_path,index_file_name)
    if(os.path.isfile(file_path)):
        statinfo = os.stat(file_path)
        # print("Index File size - ",convert_bytes(statinfo.st_size))
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
        # print("Docid File size - ",convert_bytes(statinfo.st_size))
        with open(file_path, 'rb') as file:
            docid_dict = pickle.load(file)
    else:
        print("docid_title file does not exist")
        sys.exit(1)
    return docid_dict


def read_docsno(index_path):
    total_docs = 0
    file_path = os.path.join(index_path,docsno_file_name)
    if(os.path.isfile(file_path)):
        statinfo = os.stat(file_path)
        # print("docsno File size - ",convert_bytes(statinfo.st_size))
        with open(file_path, 'r') as file:
            total_docs = file.read()
    else:
        print("docsno file does not exist")
        sys.exit(1)
    return int(total_docs)


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

#Score assigns weights to diff fields of text
#Count now has tf - so this returns tf score(-ve)
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

#
#Same for a word(diff values for diff fields).For each doc we call get_score() using idf_scores as weights (also 0s are 0s in idf_scores also)
def get_idf_scores(docs_list,weights,total_docs):
    idf_scores = [0,0,0,0,0,0]
    for i in range(len(idf_scores)):
        if(weights[i]!=0):
            count=0
            for doc in docs_list:
                if(doc[1][i]>0):
                    count+=1
            if(count > 0):
                idf_scores[i]=log2(total_docs/float(count))
    return idf_scores


def search(index_path, queries):
    outputs = []
    index = read_index(index_path)
    docid_dict = read_docid(index_path)
    total_docs = read_docsno(index_path)
    num_res = 10    #Number of results

    #When we have queries of more than 1 word - Calculate IDF score and push to heap
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
                    idf_scores = get_idf_scores(docs_list,weights,total_docs)
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
                                new_list = get_score(doc,idf_scores)
                                new_val = old_val+new_list[0]
                                doc_heap[ind][0] = new_val
                                heapq._siftdown(doc_heap,0,ind)
                            else:
                                score,docid = get_score(doc,idf_scores)
                                heapq.heappush(doc_heap,[score,docid])
                        else:
                            score,docid = get_score(doc,idf_scores)
                            heapq.heappush(doc_heap,[score,docid])
            if(len(doc_heap)):
                results = heapq.nsmallest(num_res,doc_heap)
                for res in results:
                    # if(res[0] <= -length):      #To match all conditions in field???-does not work
                    output.append(docid_dict[res[1]])
            else:
                print("No documents matching ",query)
                    
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
                    print("No documents matching ",query)

            else:
                # NUmber of words in query - merge
                for word in query_words:
                    if ( word in index):
                        docs_list = index[word]
                        idf_score = (log2(total_docs/float(len(docs_list))))
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
                                    new_val = old_val+(new_list[0]*idf_score)
                                    doc_heap[ind][0] = new_val
                                    heapq._siftdown(doc_heap,0,ind)
                                else:
                                    score,docid = get_score(doc)
                                    heapq.heappush(doc_heap,[score*idf_score,docid])
                            else:
                                score,docid = get_score(doc)
                                # tfidf_score = score*idf_score
                                heapq.heappush(doc_heap,[score*idf_score,docid])
                if(len(doc_heap)):
                    results = heapq.nsmallest(num_res,doc_heap)
                    for res in results:
                        output.append(docid_dict[res[1]])
                else:
                    print("No documents matching ",query)
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
        # queries = []
        # #remove |^
        outputs = search(index_path, queries)
        write_file(outputs, output_path)


if __name__ == "__main__":
    main()
