import sys
import os
import xml.sax
import textprocessing
import _pickle as pickle
from sortedcontainers import SortedDict
import merging

index = SortedDict()
docid = {}
docs_no = 0
indexfile_path = "my_index"
docid_path = "docid_title.pkl"
docsno_path = "docs_no.txt"
end_words_file = "file_ends.pkl"

index_file_no = 0
size_in_file = 100000000       # 100MB or 0.1GB (RAM min 2GB) (merging 100 files together)
# size_in_file = 100000


def write_index_file():
    global index_file_no
    index_file_no+=1
    f = indexfile_path+str(index_file_no)
    # with open(f, 'wb') as file:
    #     pickle.dump(index,file)
    file_str = ""
    keys = index.keys()
    for key in keys:
        file_str += key+":"
        for doc in index[key]:
            file_str += str(doc[0])
            file_str += str(doc[1])
            file_str += "|"
        file_str += "\n"
    with open(f, 'w') as file:
        file.write(file_str)


def write_docid_file():
    f = docid_path
    with open(f, 'wb') as file:
        pickle.dump(docid,file)


def write_docsno_file(final_no_indexfiles):
    f = docsno_path
    with open(f, 'w') as file:
        file.write(str(docs_no))
        file.write(" ")
        file.write(str(final_no_indexfiles))

def write_endwords_file(end_words):
    f = end_words_file
    with open(f, 'wb') as file:
        pickle.dump(end_words,file)


class WikiHandler(xml.sax.ContentHandler):
    titleflag = 0
    textflag = 0
    count = 1

    def __init(self):
        self.current = ""
        self.title = ""
        self.id = ""
        # self.redirect_title = ""
        self.text = ""

    def startElement(self,tag,attributes):
        self.current = tag
        # if tag == "redirect":
        #     self.redirect_title = attributes["title"]

    def endElement(self,tag):
        global docs_no
        global index
        if tag == "page":
            self.id = WikiHandler.count
            docid[self.id]=self.title
            docs_no = WikiHandler.count
            WikiHandler.count += 1 
            WikiHandler.create_index(self)
            WikiHandler.idflag = 0
            WikiHandler.titleflag = 0
            WikiHandler.textflag = 0
            WikiHandler.__init(self)
            #Write temp_index if size reached
            if(sys.getsizeof(index) >= size_in_file ):
                write_index_file()
                index = SortedDict()


    def characters(self,content):
        if self.current == "title":
            if( WikiHandler.titleflag == 0):
                self.title = content
                WikiHandler.titleflag = 1
        if self.current == "text":
            if( WikiHandler.textflag == 0):
                self.text = content
                WikiHandler.textflag = 1
            else:
                self.text += content
        
        
    def create_index(self):
        global index
        global indexfile_path
        title_dict = textprocessing.process_title(self.title)
        infobox_dict,references_dict,links_dict,category_dict,bodytext_dict = textprocessing.process_text(self.text)
    
        vocabulary = set(title_dict.keys())
        if(len(infobox_dict.keys())):
            vocabulary.update(set(infobox_dict.keys()))
        if(len(references_dict.keys())):
            vocabulary.update(set(references_dict.keys()))
        if(len(links_dict.keys())):
            vocabulary.update(set(links_dict.keys()))
        if(len(category_dict.keys())):
            vocabulary.update(set(category_dict.keys()))
        if(len(bodytext_dict.keys())):
            vocabulary.update(set(bodytext_dict.keys()))
        #print("vocabulary - ",vocabulary)

        #Calculating tf(term frequency and storing in index) for fields seperately
        for term in vocabulary:
            temp_list = []
            counts = []
            temp_list.append(self.id)
            if(len(title_dict) and (term in title_dict)):
                counts.append(round(title_dict[term]/float(len(title_dict)),5))
            else:
                counts.append(0)
            if(len(infobox_dict) and (term in infobox_dict)):
                counts.append(round(infobox_dict[term]/float(len(infobox_dict)),5))
            else:
                counts.append(0)
            if(len(references_dict) and (term in references_dict)):
                counts.append(round(references_dict[term]/float(len(references_dict)),5))
            else:
                counts.append(0)
            if(len(links_dict) and (term in links_dict)):
                counts.append(round(links_dict[term]/float(len(links_dict)),5))
            else:
                counts.append(0)
            if(len(category_dict) and (term in category_dict)):
                counts.append(round(category_dict[term]/float(len(category_dict)),5))
            else:
                counts.append(0)
            if(len(bodytext_dict) and (term in bodytext_dict)):
                counts.append(round(bodytext_dict[term]/float(len(bodytext_dict)),5))
            else:
                counts.append(0)
            temp_list.append(counts)

            if(not index.__contains__(term)):
                index[term]=[]
            index[term].append(temp_list)


def main():
    global indexfile_path
    global docid_path
    global docsno_path
    global end_words_file
    final_index_name = "final_index"

    if len(sys.argv)!= 3:
        print("Error:Syntax: python3 indexer.py <path_to_data> <path_to_index>")
        sys.exit(0)
    else:
        data_path=sys.argv[1]
        index_path=sys.argv[2]
        indexfile_path = os.path.join(index_path,indexfile_path)
        docid_path = os.path.join(index_path,docid_path)
        docsno_path = os.path.join(index_path,docsno_path)
        final_index_name = os.path.join(index_path,final_index_name)
        end_words_file = os.path.join(index_path,end_words_file)
        if( os.path.isfile(data_path) ):
            #If data present ,crete directory of index if not present(saving index file in between)
            if( not os.path.isdir(index_path)):
                os.mkdir(index_path)
            #XMLParser
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_namespaces, 0)
            Handler = WikiHandler()
            parser.setContentHandler(Handler)
            parser.parse(data_path)

            if(len(index)):
                write_index_file()
            write_docid_file()
            print("Primary Indexing Completed - Total files=",index_file_no)
            #Merging index files

            final_no_indexfiles,end_words = merging.merge_indexes(index_file_no,indexfile_path,final_index_name)
            write_docsno_file(final_no_indexfiles)
            # print(end_words)
            write_endwords_file(end_words)
            print("Merging Indexes Completed ")
        else:
            # print("Data file does not exist")
            sys.exit(1)

if __name__ == "__main__":
    main()
