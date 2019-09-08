import sys
import os
import heapq
try:
    import cPickle as pickle
except:
    import pickle
from sortedcontainers import SortedDict

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


#function to read all indexes 
# returns - array of indexes each having a dict
#TODO : read only part of file ??
def get_all_indexes(no_index_files,index_path):
    indexes_array = []
    for i in range(1,no_index_files+1):
        f = index_path+str(i)+".pkl"
        print("reading ",f)
        if(os.path.isfile(f)):
            with open(f, 'rb') as file:
                indexes_array.append(pickle.load(file))
        else:
            print("*****************index does not exist - ",i)
    return indexes_array


#BSBI
#K-way merge using  heaps
#parameters - no_index_files, final_index file name
def merge_indexes(no_index_files,prev_index_file_path,final_index_file):

    heap = []
    count_files = 1
    indexes_array = get_all_indexes(no_index_files,prev_index_file_path)

    #Fill first elements in heap
    for i in range(len(indexes_array)):
        if( len(indexes_array[i])):
            key = indexes_array[i].keys()[0]
            heap_index =  is_ele_present(heap,key)
            if(heap_index != -1):
                # print("*****matched term - ",key)
                #Add to doc_list
                prev_doc_list = heap[heap_index].doc_list
                curr_doc_list = indexes_array[i][key]
                prev_doc_list.extend(curr_doc_list)
                # print("final list ",prev_doc_list)
                heap[heap_index].doc_list = prev_doc_list
                #Add to index_list
                heap[heap_index].index_list.append(i)
            else:
                heapq.heappush(heap,Node(key,indexes_array[i][key],[i]))   #(term,doc_list,[index_no])  #Store only key-term(as value),indexno in array
            indexes_array[i].popitem(0)

    final_index = {} #already sorted and merge - no need sort dict
    while(len(heap)):
        curr = heapq.heappop(heap)
        final_index[curr.term]=curr.doc_list
        # print("POPPED from heap& ADD to index - ",curr.term,curr.doc_list)
        #Loop through all indexes the word was present and add to heap
        curr_index_file_list = curr.index_list
        for curr_index_file in curr_index_file_list:
            if(len(indexes_array[curr_index_file])):
                key = indexes_array[curr_index_file].keys()[0]
                heap_index =  is_ele_present(heap,key)
                if(heap_index != -1):
                    # print("*****matched term - ",key)
                    #Add to doc_list
                    prev_doc_list = heap[heap_index].doc_list
                    curr_doc_list = indexes_array[curr_index_file][key]
                    prev_doc_list.extend(curr_doc_list)
                    heap[heap_index].doc_list = prev_doc_list
                    #Add to index_list
                    heap[heap_index].index_list.append(curr_index_file)
                else:
                    heapq.heappush(heap,Node(key,indexes_array[curr_index_file][key],[curr_index_file]))   #(term,doc_list,[index_no])  #Store only key-term(as value),indexno in array
                indexes_array[curr_index_file].popitem(0)

    # return final_index
    #Write to file
    final_index_file += str(count_files)+".pkl"
    # count_files +=1
    # final_index_file += ".pkl"
    with open(final_index_file, 'wb') as file:
        pickle.dump(final_index,file)
    
    #return f_no_index_files,offsets
    return count_files

    #TODO
    #Write to mul files based on word count and
    #No_files final index stored in - and offset - ending term of eac index
    #return f_no_index_files,offsets
