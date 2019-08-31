import sys
import os
import xml.sax
import textprocessing
import _pickle as pickle
import gzip

index = {}
docid = {}
index_path = ""
file_path = "my_index"
docid_path = "docid_title"


def write_index_file():
    f = file_path+".pkl"
    with open(f, 'wb') as file:
        pickle.dump(index,file)


def write_docid_file():
    f = docid_path+".pkl"
    with open(f, 'wb') as file:
        pickle.dump(docid,file)


class WikiHandler(xml.sax.ContentHandler):
    idflag = 0
    titleflag = 0
    textflag = 0
    count = 0

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
        if tag == "page":
            self.id = WikiHandler.count
            docid[self.id]=self.title
            WikiHandler.count += 1 
            WikiHandler.create_index(self)
            WikiHandler.idflag = 0
            WikiHandler.titleflag = 0
            WikiHandler.textflag = 0
            WikiHandler.__init(self)

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
        global file_path
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

        for term in vocabulary:
            temp_list = []
            counts = []
            temp_list.append(self.id)
            if(term in title_dict):
                counts.append(title_dict[term])
            else:
                counts.append(0)
            if(term in infobox_dict):
                counts.append(infobox_dict[term])
            else:
                counts.append(0)
            if(term in references_dict):
                counts.append(references_dict[term])
            else:
                counts.append(0)
            if(term in references_dict):
                counts.append(references_dict[term])
            else:
                counts.append(0)
            if(term in links_dict):
                counts.append(links_dict[term])
            else:
                counts.append(0)
            if(term in category_dict):
                counts.append(category_dict[term])
            else:
                counts.append(0)
            if(term in bodytext_dict):
                counts.append(bodytext_dict[term])
            else:
                counts.append(0)
            temp_list.append(counts)

            if( term not in index):
                index[term]=[]
            index[term].append(temp_list)


def main():
    global index_path
    global file_path
    global docid_path
    if len(sys.argv)!= 3:
        print("Error:Syntax: python3 indexer.py <path_to_data> <path_to_index>")
        sys.exit(0)
    else:
        data_path=sys.argv[1]
        index_path=sys.argv[2]
        file_path = os.path.join(index_path,file_path)
        docid_path = os.path.join(index_path,docid_path)
        if( os.path.isfile(data_path) ):
            #XMLParser
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_namespaces, 0)
            Handler = WikiHandler()
            parser.setContentHandler(Handler)
            parser.parse(data_path)
            #Write index
            if( not os.path.isdir(index_path)):
                os.mkdir(index_path)
                # print("Created directory ",index_path)
            write_index_file()
            write_docid_file()
            # print("Indexing Completed- Wrote Index file")
        else:
            print("Data file does not exist")
            sys.exit(1)
            

if __name__ == "__main__":
    main()
