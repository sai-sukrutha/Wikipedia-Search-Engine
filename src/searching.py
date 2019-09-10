import sys
import os
import re
# import _pickle as pickle
try:
    import cPickle as pickle
except:
    import pickle
import textprocessing
import heapq
from sortedcontainers import SortedDict
from math import log2
import time

index_path = ""
index_file_name = "final_index"
docid_file_name = "docid_title.pkl"
docsno_file_name = "docs_no.txt"
file_ends_file = "file_ends.pkl"
file_ends = []
total_docs = 0
no_index_files = 0
docid_dict = {}


def read_file_ends():
    global index_path
    global file_ends

    if(len(file_ends)):
        return file_ends
    else:
        file_path = os.path.join(index_path,file_ends_file)
        if(os.path.isfile(file_path)):
            with open(file_path, 'rb') as file:
                file_ends = pickle.load(file)
        else:
            print("end_words file does not exist")
            sys.exit(1)


def get_index_no(term):
    global file_ends

    if(len(file_ends)==0):
        read_file_ends()

    for i in range(len(file_ends)):
        if( term <= file_ends[i] ):
            return i+1
    return -1


def read_docsno():
    global index_path
    global total_docs
    global no_index_files

    file_path = os.path.join(index_path,docsno_file_name)
    if(os.path.isfile(file_path)):
        with open(file_path, 'r') as file:
            data = file.read()
        data = data.split(' ')
        total_docs = int(data[0])
        no_index_files = int(data[1])
    else:
        print("docsno file does not exist")
        sys.exit(1)


def read_index( index_file_no ):
    global index_path
    index = {}
    file_path = os.path.join(index_path,index_file_name)
    file_path += str(index_file_no)+".pkl"
    # print("Index file name - ",file_path)
    if(os.path.isfile(file_path)):
        with open(file_path, 'rb') as file:
            index = pickle.load(file)
    else:
        print("index does not exist - ",index_file_no)
        sys.exit(1)
    return index


def read_docid():
    global index_path
    global docid_dict

    docid_dict = {}
    file_path = os.path.join(index_path,docid_file_name)
    if(os.path.isfile(file_path)):
        with open(file_path, 'rb') as file:
            docid_dict = pickle.load(file)
    else:
        print("docid_title file does not exist")
        sys.exit(1)


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


def load_files():
    #First read no of index files from docs_no file and then indexes
    read_docid()
    read_docsno()
    read_file_ends()


def search( query):
    start = time.time()
    global docid_dict
    global total_docs

    num_res = 10    #Number of results

    #When we have queries of more than 1 word - Calculate IDF score and push to heap
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

            #Get index file no in which the word may be present and obtain the index
            index_no = get_index_no(word[0])
            if( index_no != -1):
                index = read_index(index_no)
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
            else:
                print("No documents matching ")
        if(len(doc_heap)):
            results = heapq.nsmallest(num_res,doc_heap)
            for res in results:
                # if(res[0] <= -length):      #To match all conditions in field???-does not work
                output.append(docid_dict[res[1]])
        else:
            print("No documents matching ")
                
    else:
        #Simple Query
        query_words = textprocessing.process_query(query)
        #Only 1 word query
        if(len(query_words) == 1):
            #Get index file no in which the word may be present and obtain the index
            index_no = get_index_no(query_words[0])
            if(index_no != -1):
                index = read_index(index_no)
                if ( query_words[0] in index ):
                    docs_list = index[query_words[0]]
                    for doc in docs_list:
                        score,docid = get_score(doc)
                        heapq.heappush(doc_heap,[score,docid])
                    results = heapq.nsmallest(num_res,doc_heap)
                    for res in results:
                        output.append(docid_dict[res[1]])
                else:
                    print("No documents matching ")
            else:
                print("No documents matching ")

        else:
            # NUmber of words in query - merge
            for word in query_words:
                #Get index file no in which the word may be present and obtain the index
                index_no = get_index_no(word)
                if(index_no != -1):
                    index = read_index(index_no)
                    if( word in index ):
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
                else:
                    print("No documents matching ")
            if(len(doc_heap)):
                results = heapq.nsmallest(num_res,doc_heap)
                for res in results:
                    output.append(docid_dict[res[1]])
            else:
                print("No documents matching ")
    end = time.time()
    time_diff = round(float(end - start),5)
    return output,time_diff

def print_list(output):
    for line in output:
        print(line)


def main():
    global index_path

    if len(sys.argv)!= 2:
        print("Error:Syntax: python3 searching.py <index_path>")
        sys.exit(0)
    else:
        print("Loading...")
        index_path=sys.argv[1]
        # input_path=sys.argv[2]
        # output_path=sys.argv[3]
        # queries = read_inputfile(input_path)
        load_files()
        query = ''
        # while( (query == 'quit') or (query == 'exit') ):
        while(True):
            query = input("Enter Query : ")
            if(query):
                print(query)
                print("---------------------")
                output,time_diff = search(query)
                print_list(output)
                print("Resp Time-",time_diff,"s")
                print("\n")


        # write_file(outputs, output_path)


if __name__ == "__main__":
    main()
