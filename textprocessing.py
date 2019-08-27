import re
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer


nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

SYMBOLS = re.compile('<br>|<\/br>|<ref>|<\/ref>|<def>|<\/def>|[/(){}\[\]\|@,;:\*\+\n=\'\"_%\?!&#\-<>]')     #[&quot;|&lt;|&gt;]
SYMBOLS_References = re.compile('[(){}\[\]\|,;\*\+\n\'\"\!\-<>]')   #Removed / , :
BAD_SYMBOLS_RE = re.compile('[^0-9a-zA-Z \/:\.<>{}\[\]]')       #check this
STOPWORDS = set(stopwords.words('english'))
STOPWORDS.add("reflist")
STOPWORDS.add("defaultsort")
# STOPWORDS.add("redirect")
# STOPWORDS.add("summary")

def cleanUp(r,is_ref):
    #Cleaning Text
    r = BAD_SYMBOLS_RE.sub('', r)
    if(is_ref):
        r = SYMBOLS_References.sub(' ', r)
        if(("http://" not in r) and ("https://" not in r) and ( "www" not in r)):
            r = SYMBOLS.sub(' ', r)
            r.strip(' ')
            r = r.lower()
            r = ' '.join(word for word in r.split() if word not in STOPWORDS)
            r = tokenization_stemming(r)
        else:
            r = [r]
    else:
        r = SYMBOLS.sub(' ', r)
        #Case Folding
        r = r.lower()
        #Stopwords Removal
        r = ' '.join(word for word in r.split() if word not in STOPWORDS)
    return r

def tokenization_stemming(r):
    #Tokenization
    words = word_tokenize(r)
    #Lemmatizing - instead of Stemming
    #s = [ lemmatizer.lemmatize(w) for w in words]
    #Stemming
    s =[ stemmer.stem(w) for w in words ]
    return s


def process_text(text):
    #Extraction of text
    bodytext = []
    infobox = []
    category = []
    links = []
    references = []
    
    data_lines = text.split('\n')
    flag = 0
    length = len(data_lines)
    i=0
    while  i<length:
        #print("line - ",data_lines[i])
        #Reading Infobox
        if '{{Infobox' in data_lines[i]:
            #print("Under Infobox")
            flag = 1
            temp = data_lines[i].split('{{Infobox')[1:]
            infobox.append(temp)
            while True:
                if( i< length-1):
                    i+=1
                else:
                    break
                if ('{{' in data_lines[i]) or ('}}' in data_lines[i]):
                    flag += data_lines[i].count('{{')
                    flag -= data_lines[i].count('}}')
                infobox.append(data_lines[i])
                if flag <= 0:
                    break
        #Reading References      
        elif '==References==' in data_lines[i]:
            #print("Under References")
            temp = data_lines[i].split('==References==')[1:]   #Mostly Nothing on that line-creating empty list['']
            references.append(temp)
            if( i< length-1):
                i+=1
            else:
                break
            while ((data_lines[i] != '') and ('{{DEFAULTSORT:' not in data_lines[i]) and ('==External links==' not in data_lines[i])):
                references.append(data_lines[i])
                if( i< length-1):
                    i+=1
                else:
                    break
        #Reading External links
        elif '==External links==' in data_lines[i]:
            #print("Under External links")
            temp = data_lines[i].split('==External links==')[1:]   #Mostly Nothing on that line-creating empty list['']
            links.append(temp)
            while ((data_lines[i] != '') and ('{{DEFAULTSORT:' not in data_lines[i])):
                if( i< length-1):
                    i+=1
                else:
                    break
                links.append(data_lines[i])
        #Reading Category
        elif '[[Category' in data_lines[i] or '[[category' in data_lines[i]:
            #print("Under Category")
            while( ('[[Category' in data_lines[i]) or ('[[category' in data_lines[i])):
                category.append(data_lines[i].strip('[').strip(']').split(':')[1:])
                if( i< length-1):
                    i+=1
                else:
                    break
                
        #Reading Body Text
        #else:
        #print("Under BodyText")
        if('{{R from move}}') in data_lines[i]:
            if( i< length-1):
                i+=1
            else:
                break
        else:
            bodytext.append(data_lines[i])
        i+=1
    
    # print("Infobox - ",infobox)
    # print("References - ",references)
    # print("links - ",links)
    # print("category - ",category)
    # print("Body Text - ",bodytext)

    temp = []
    for s in infobox:
        temp.append(cleanUp(str(s),0))
    infobox = " ".join(temp)
    infobox = tokenization_stemming(infobox)
    # print("Cleaned Infobox -",infobox)
    infobox_dict ={}
    for w in infobox:
        if( w != ''):
            if(w not in infobox_dict):
                infobox_dict[w]=1
            else:
                infobox_dict[w]+=1
    # print("Infobox dict-",infobox_dict)

    #Donot clean references of /,: and Not Tokenizing and Stemming
    temp = []
    for s in references:
        temp.extend(cleanUp(str(s),1))
    references = temp
    #references = tokenization_stemming(references)
    # print("Cleaned References -",references)
    references_dict ={}
    for w in references:
        if( w != ''):
            if(w not in references_dict):
                references_dict[w]=1
            else:
                references_dict[w]+=1
    # print("References dict-",references_dict)

    temp = []
    for s in links:
        temp.append(cleanUp(str(s),0))
    links = " ".join(temp)
    links = tokenization_stemming(links)
    # print("Cleaned External links -",links)
    links_dict ={}
    for w in links:
        if( w != ''):
            if(w not in links_dict):
                links_dict[w]=1
            else:
                links_dict[w]+=1
    # print("links dict -",links_dict)

    temp = []
    for s in category:
        temp.append(cleanUp(str(s),0))
    category = " ".join(temp)
    category = tokenization_stemming(category)
    # print("Cleaned Category -",category)
    category_dict ={}
    for w in category:
        if( w != ''):
            if(w not in category_dict):
                category_dict[w]=1
            else:
                category_dict[w]+=1
    # print("Category dict -",category_dict)

    temp = []
    for s in bodytext:
        temp.append(cleanUp(str(s),0))
    bodytext = " ".join(temp)
    bodytext = tokenization_stemming(bodytext)
    # print("Cleaned Text -",bodytext)
    bodytext_dict ={}
    for w in bodytext:
        if( w != ''):
            if(w not in bodytext_dict):
                bodytext_dict[w]=1
            else:
                bodytext_dict[w]+=1
    # print("BodyText dict-",bodytext_dict)
    
    return infobox_dict,references_dict,links_dict,category_dict,bodytext_dict


def process_title(title):
    #print("Title Received - ",title)
    #Preprocessing
    clean_title= cleanUp(title,0)
    #Do Tokenization , Stemming on Title ??
    clean_title = tokenization_stemming(clean_title)
    # print("***Title - ",clean_title)
    title_dict ={}
    for w in clean_title:
        if( w != ''):
            if(w not in title_dict):
                title_dict[w]=1
            else:
                title_dict[w]+=1
    # print("Title dict- ",title_dict)
    return title_dict

