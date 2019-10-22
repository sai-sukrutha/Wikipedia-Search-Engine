import sys
import os
import heapq
try:
    import cPickle as pickle
except:
    import pickle
from sortedcontainers import SortedDict


file_pointers = []
file_names_pointers_dict = {}

prev_no_index_files = 0
curr_no_index_files = 0

no_files_to_merge = 5
size_in_file = 1000000
# no_files_to_merge = 10
# size_in_file = 1000000

count_files = 1
end_words = []



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
                    try:
                        c_list.append(float(count))
                    except:
                        print("count exception occured ",count)
                        c_list.append(0.0);
                d_list.append(int(docid))
                d_list.append(c_list)
                doc_list.append(d_list)
        index[term]=doc_list
    return index



def get_final_file_pointers(no_index_files,index_path):
    global file_pointers
    global file_names_pointers_dict

    file_pointers = []
    file_names_pointers_dict = {}
    #Create file_pointers
    file_pointers = [0]*no_index_files  #This function called only at start
    for i in range(1,no_index_files+1):
        f = index_path+str(i)
        if(os.path.isfile(f)):
            file_pointers[i-1]=open(f,'r')
            file_names_pointers_dict[i-1]=f
        else:
            print("index file does not exist - ",f)
            sys.exit(1)


def get_file_pointers(start_index_no,end_index_no,index_path):
    global file_pointers
    global file_names_pointers_dict

    file_pointers = []
    file_names_pointers_dict = {}
    #Create file_pointers
    diff = (end_index_no-start_index_no)+1
    file_pointers = [0]*diff  #This function called only at start
    for i in range(diff):
        f = index_path+str(start_index_no+i)
        if(os.path.isfile(f)):
            file_pointers[i]=open(f,'r')
            file_names_pointers_dict[i]=f
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

#Write in file after every line(big string)
def write_index_file(file_path , index):
    global curr_no_index_files

    curr_no_index_files+=1
    f = file_path+str(curr_no_index_files)
    file = open(f, 'w')
    file_str = ""
    print("Writing into file - ",f)
    file_str = ""
    keys = index.keys()
    for key in keys:
        file_str = ""
        file_str += key+":"
        for doc in index[key]:
            file_str += str(doc[0])
            file_str += str(doc[1])
            file_str += "|"
        file_str += "\n"
        file.writelines(file_str)
    file.close()
    #with open(f, 'w') as file:
    #    file.write(file_str)
    return


#K-way merge using  heaps
#parameters - no_index_files, final_index file name
def merge_final_indexes(no_index_files,prev_index_file_path,final_index_file):

    global file_pointers
    global file_names_pointers_dict
    global count_files
    global end_words

    heap = []

    #TODO:check
    get_final_file_pointers(no_index_files,prev_index_file_path)

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
                file_pointers[i].close()
                indexes_array[i]=''
                file_name = file_names_pointers_dict[i]
                indexes_array[i]=''
                print("File finished ",i , "Deleting ",file_name)
                os.remove(file_name)

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
                    file_pointers[curr_index_file].close()
                    file_name = file_names_pointers_dict[curr_index_file]
                    indexes_array[curr_index_file]=''
                    print("File finished ",curr_index_file , "Deleting ",file_name)
                    os.remove(file_name)
                else:
                    indexes_array[curr_index_file] = temp_index
                

        if(sys.getsizeof(final_index) >= size_in_file):
            #Write into a index file after size exceeds
            f = final_index_file+str(count_files)
            print("Writing into file - ",f)
            count_files+=1
            #with open(f, 'wb') as file:
            #    pickle.dump(final_index,file)
	    write_index_file(file , final_index)
            final_index = {}
            end_words.append(end_word)

    #1 element remaining in heap
    while(len(heap)):
        curr = heapq.heappop(heap)
        final_index[curr.term]=curr.doc_list
        end_word = curr.term
        # print(curr.term)

    f = final_index_file+str(count_files)
    print("Writing into file - ",f)
    #with open(f, 'wb') as file:
    #    pickle.dump(final_index,file)
    write_index_file(file , final_index)
    end_words.append(end_word)
    return


def merge_indexes_intermediate(start_index_no , end_index_no , prev_index_file_path , new_index_file_path):
    global file_pointers
    global prev_no_index_files
    global curr_no_index_files 
    global count_files

    if( start_index_no == end_index_no):
        #Just rename file-no need of merge
        prev_file_path = prev_index_file_path+str(start_index_no)
        curr_no_index_files+=1
        new_file_path = prev_index_file_path+str(curr_no_index_files)
        print("Only one file no merge - Renaming ",prev_file_path," to ",new_file_path)
        os.rename(prev_file_path,new_file_path)
	return

    heap = []
    get_file_pointers(start_index_no,end_index_no,prev_index_file_path)
    diff = (end_index_no-start_index_no)+1
    file_not_fin = [0]*diff  #maintaining flag if file is finished
    indexes_array = ['']*diff
    temp_final_index = {} #already sorted and merge - no need sort dict

    #Fill first elements in heap
    for i in range(diff):
        temp_index = read_line_index(i)  #file_pointers are also stored accordingly
        if(temp_index != -1):
            indexes_array[i] = temp_index
            file_not_fin[i] = 1

    for i in range(diff):
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
                file_pointers[i].close()
                indexes_array[i]=''
                file_name = file_names_pointers_dict[i]
                indexes_array[i]=''
                print("File finished ",i , "Deleting ",file_name)
                os.remove(file_name)
            else:
                indexes_array[i] = temp_index

    #Repeat until all files finish
    while((any(file_not_fin) == 1)):

        curr = heapq.heappop(heap)
        temp_final_index[curr.term]=curr.doc_list
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
                    file_pointers[curr_index_file].close()
                    file_name = file_names_pointers_dict[curr_index_file]
                    indexes_array[curr_index_file]=''
                    print("File finished ",curr_index_file , "Deleting ",file_name)
                    os.remove(file_name)
                else:
                    indexes_array[curr_index_file] = temp_index

    #1 element remaining in heap
    while(len(heap)):
        curr = heapq.heappop(heap)
        temp_final_index[curr.term]=curr.doc_list
        # print(curr.term)

    #Write index as text only (intermediate indices)
    write_index_file(new_index_file_path,temp_final_index)
    return


#First we merge all indexes ( intermediately by merging 5 files) and then do final merge saving final index files
def merge_indexes(no_index_files,prev_index_file_path,new_index_file_path):

    global prev_no_index_files
    global curr_no_index_files

    prev_no_index_files = no_index_files
    curr_no_index_files = 0
    temp = 1
    while(temp <= no_index_files):
    	start_index_no = temp
        if(temp+no_files_to_merge <= no_index_files):
            end_index_no = temp+no_files_to_merge-1
            temp +=no_files_to_merge
        else:
            end_index_no = no_index_files
            temp = no_index_files+1
            # print("Merging indexes from ",start_index_no," - ",end_index_no)

            merge_indexes_intermediate(start_index_no,end_index_no,prev_index_file_path,prev_index_file_path)  #Same name for indexes-previous deleted before new ones wrote

        print("Previous no_index_files ",prev_no_index_files)
        print("Current no_index_files ",curr_no_index_files)

    count_files,end_words = merge_final_indexes(curr_no_index_files,prev_index_file_path,new_index_file_path)
   
    return count_files,end_words

        




