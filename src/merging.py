import sys
import os
import heapq
try:
    import cPickle as pickle
except:
    import pickle
from sortedcontainers import SortedDict


file_pointers = []
size_in_file = 500000000   # 0.5GB (RAM min 2GB)
# size_in_file = 1000000


#Elements in heap - Node
class Node:
    def __init__(self, t , dl , i):
        self.term = t
        self.doc_list = dl
        self.index_list = i      

    #For comparision
    def __lt__(self, other):
        return self.term < other.term


def is_ele_present(heap,term):
    if(len(heap)):
        for i in range(len(heap)):
            if(term == heap[i].term):
                return i
    return -1


def read_index(term_dict):
    index = SortedDict()
    if(len(term_dict)):
        terms = term_dict
        term,doclist = terms.split(':')
        docs_list = doclist.split('|')
        docs_list = docs_list[:-1]      #Last is \n empty as we have |\n at end
        doc_list = []
        for doc in docs_list:
            d_list = []
            if(doc != ''): 
                docid,counts = doc.split('[')
                counts = counts.split("]")[0]
                counts_list = counts.split(',')
                c_list = []
                for count in counts_list:
                    c_list.append(float(count))
                d_list.append(int(docid))
                d_list.append(c_list)
                doc_list.append(d_list)
        index[term]=doc_list
    return index



def get_file_pointers(no_index_files,index_path):
    global file_pointers
    #Create file_pointers
    file_pointers = [0]*no_index_files  #This function called only at start
    for i in range(1,no_index_files+1):
        f = index_path+str(i)
        if(os.path.isfile(f)):
            file_pointers[i-1]=open(f,'r')
        else:
            print("index file does not exist - ",f)
            sys.exit(1)


def read_line_index ( file_pointers_index ):
    global file_pointers
    i = file_pointers_index
    line = file_pointers[i].readline()
    if( line == ''):
        return -1
    index = read_index(line)
    return index



#BSBI
#K-way merge using  heaps
#parameters - no_index_files, final_index file name
def merge_indexes(no_index_files,prev_index_file_path,final_index_file):

    global file_pointers

    heap = []
    count_files = 1 #No of index_files

    end_words = []
    get_file_pointers(no_index_files,prev_index_file_path)

    file_not_fin = [0]*no_index_files   #maintaining flag if file is finished

    indexes_array = ['']*no_index_files
    final_index = {} #already sorted and merge - no need sort dict
    end_word = ''

    #Fill first elements in heap
    for i in range(no_index_files):
        temp_index = read_line_index(i)
        if(temp_index != -1):
            indexes_array[i] = temp_index
            file_not_fin[i] = 1

    for i in range(no_index_files):
        if( len(indexes_array[i])):
            key = indexes_array[i].keys()[0]
            heap_index =  is_ele_present(heap,key)
	    #Element present in heap(do merge-not push)
            if(heap_index != -1):
                #Add to doc_list
                prev_doc_list = heap[heap_index].doc_list
                curr_doc_list = indexes_array[i][key]
                prev_doc_list.extend(curr_doc_list)
                heap[heap_index].doc_list = prev_doc_list
                #Add to index_list
                heap[heap_index].index_list.append(i)
            else:
                heapq.heappush(heap,Node(key,indexes_array[i][key],[i]))   #(term,doc_list,[index_no])  #Store only key-term(as value),indexno in array

	    #Read new lines from file
            temp_index = read_line_index(i)
            if(temp_index == -1):
                file_not_fin[i] = 0
                # print("file finished ",i)
                file_pointers[i].close()
                indexes_array[i]=''
                #TODO:Remove file
            else:
                indexes_array[i] = temp_index

    #Repeat until all files finish
    while((any(file_not_fin) == 1)):

        curr = heapq.heappop(heap)
        final_index[curr.term]=curr.doc_list
        end_word = curr.term
        # print(curr.term)
        #Loop through all indexes the word was present and add to heap
        curr_index_file_list = curr.index_list
        for curr_index_file in curr_index_file_list:
            if(file_not_fin[curr_index_file]):
                key = indexes_array[curr_index_file].keys()[0]
                heap_index =  is_ele_present(heap,key)
	        #Element present in heap(do merge-not push)
                if(heap_index != -1):
                    #Add to doc_list
                    prev_doc_list = heap[heap_index].doc_list
                    curr_doc_list = indexes_array[curr_index_file][key]
                    prev_doc_list.extend(curr_doc_list)
                    heap[heap_index].doc_list = prev_doc_list
                    #Add to index_list
                    heap[heap_index].index_list.append(curr_index_file)
                else:
                    heapq.heappush(heap,Node(key,indexes_array[curr_index_file][key],[curr_index_file]))   #(term,doc_list,[index_no])  #Store only key-term(as value),indexno in array
                
                #Read new lines from file
                temp_index = read_line_index(curr_index_file)
                if(temp_index == -1):
                    file_not_fin[curr_index_file] = 0
                    # print("file finished ",curr_index_file)
                    file_pointers[curr_index_file].close()
                    indexes_array[curr_index_file]=''
                    #TODO:Remove file
                else:
                    indexes_array[curr_index_file] = temp_index
                

        if(sys.getsizeof(final_index) >= size_in_file):
            #Write into a index file after size exceeds
            f = final_index_file+str(count_files)+".pkl"
            count_files+=1
            with open(f, 'wb') as file:
                pickle.dump(final_index,file)
            final_index = {}
            end_words.append(end_word)

    #1 element remaining in heap
    while(len(heap)):
        curr = heapq.heappop(heap)
        final_index[curr.term]=curr.doc_list
        end_word = curr.term
        # print(curr.term)

    f = final_index_file+str(count_files)+".pkl"
    # count_files+=1
    with open(f, 'wb') as file:
        pickle.dump(final_index,file)
    end_words.append(end_word)

    return count_files,end_words
