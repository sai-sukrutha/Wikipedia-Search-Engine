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

SYMBOLS = re.compile('<br>|<\/br>|<def>|<\/def>|#REDIRECT|[/(){}\[\]\|@,;:\*\+\n=\'\"_%\?!&#\-<>\.]')     #[&quot;|&lt;|&gt;]
#SYMBOLS_References = re.compile('[(){}\[\]\|,;\*\+\n\'\"\!\-<>]')   #Removed / , :
BAD_SYMBOLS_RE = re.compile('[^0-9a-zA-Z \.<>{}\[\]]\/:')       #check this
NUMBERS = re.compile('[0-9]+')
formating_text = 'align=|bgcolor=|rowspan=|colspan=|class=|style=|border=|cellpadding=|cellspacing='
# match_string = 'align=.*\||bgcolor=.*\||rowspan=.*\||colspan=.*\||class=.*\||style=.*\||border=.*\||cellpadding=.*\||cellspacing=.*\|'
match_string = 'align=.*?\||bgcolor=.*?\||rowspan=.*?\||colspan=.*?\||class=.*?\||style=.*?\||border=.*?\||cellpadding=.*?\||cellspacing=.*?\|'
# FORMATING = re.compile('align=|bgcolor=|rowspan=|colspan=|class=|style=|border=|cellpadding=|cellspacing=')
FORMATING = re.compile(formating_text)
FORMATING2 = re.compile('<\.\*>')
URL = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
STOPWORDS = set(stopwords.words('english'))
STOPWORDS.add("reflist")
STOPWORDS.add("defaultsort")
STOPWORDS.add("file")
STOPWORDS.add("jpg")
STOPWORDS.add("png")
STOPWORDS.add("pdf")
STOPWORDS.add("see")
STOPWORDS.add("also")
STOPWORDS.add("name")
STOPWORDS.add("author")
STOPWORDS.add("publisher")
STOPWORDS.add("website")
STOPWORDS.add("article")
STOPWORDS.add("legend2")
STOPWORDS.add("aspx")
STOPWORDS.add("php")
STOPWORDS.add("index")
# STOPWORDS.add("grid")
# STOPWORDS.add("summary")

def cleanUp(r):
    #Cleaning Text
    r = BAD_SYMBOLS_RE.sub(' ', r)
    # r = NUMBERS.sub(' ',r)
    if((len(r) == 1) or(len(r)== 2)):
        return ''
    if( len(r) > 4 and NUMBERS.fullmatch(r)):
        return ''
    r = re.sub(URL, '', r)
    # if( URL.fullmatch(r)):
    #     r = ' '.join(r.split('.')[1])

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

def is_good_word(r):
    if(r == ''):
        return False
    # if(re.compile(' \*').fullmatch(r)):
    #     return False
    if(len(r) <= 2):
        return False
    if( len(r) > 4 and NUMBERS.fullmatch(r)):
        return False
    return True


def process_text(text):
    #Extraction of text
    bodytext = []
    infobox = []
    category = []
    links = []
    references = []
    
    data_lines = text.split('\n')
    flag = 0
    citeflag = 0
    commentsflag = 0
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
                infobox.append(data_lines[i].split("=")[1:])
                if flag <= 0:
                    break
        if '{{information' in data_lines[i]:
            #print("Under Infobox")
            flag = 1
            temp = data_lines[i].split('{{information')[1:]
            bodytext.append(temp)
            while True:
                if( i< length-1):
                    i+=1
                else:
                    break
                if ('{{' in data_lines[i]) or ('}}' in data_lines[i]):
                    flag += data_lines[i].count('{{')
                    flag -= data_lines[i].count('}}')
                bodytext.append(data_lines[i].split("=")[1:])
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
        if(citeflag):
            if('}} in datalines[i]'):
                citeflag=0
                data_lines[i] = re.sub('.*?}}','',data_lines[i])
            else:
                i+=1
                continue

        if(commentsflag):
            if("-->" in data_lines[i]):
                commentsflag = 0
                data_lines[i] = re.sub('.*?-->','',data_lines[i])
            else:
                i+=1
                continue
        
        #<ref> checks
        data_lines[i] = re.sub('<.*?>.*?</.*?>|<.*?/>','',data_lines[i])

        if('{{R from move}}') in data_lines[i]:
            i+=1
            continue

        if(('{|' in data_lines[i]) or ('|}' in data_lines[i])):    #ignore table formatting
            i+=1
            continue

        # if( '{{cite' in data_lines[i] or '{{legend' in data_lines[i]):     #ignore data in cite
        #     # print("3")
        #     if( '}}' in data_lines[i]):
        #         data_lines[i] = re.sub('{{cite.*?}}|{{legend.*?}}','',data_lines[i])
        #     else:
        #         citeflag = 1
        #         data_lines[i] = re.sub('{{cite.*?|{{legend.*?','',data_lines[i])
        #     # print("data-line becomes ",data_lines[i])
        if( '{{' in data_lines[i]):     #ignore data in cite
            # print("3")
            if( '}}' in data_lines[i]):
                data_lines[i] = re.sub('{{.*?}}','',data_lines[i])
            else:
                citeflag = 1
                data_lines[i] = re.sub('{{.*?','',data_lines[i])
            # print("data-line becomes ",data_lines[i])

        if( '<!--' in data_lines[i]):     #ignore data in <!-- -->
            # print("5")
            if('-->' in data_lines[i]):
               data_lines[i] = re.sub('<!--.*?-->','',data_lines[i]) 
            else:
                commentsflag = 1
                data_lines[i] = re.sub('<!--.*?','',data_lines[i])
            # print("data-line becomes ",data_lines[i])

        if(FORMATING.search(data_lines[i])):
            # print("matched format - ",data_lines[i])
            # data_lines[i] = ' '.join(data_lines[i].split('|')[2:])
            if (data_lines[i].count('|') >= 2):
                #FORMATING_string = FORMATING+re.compile('=.*?|')
                FORMATING_string = re.compile(match_string)
                data_lines[i] = re.sub(FORMATING_string,'',data_lines[i])
            else:
                i+=1
                continue
            # print("data-line becomes ",data_lines[i])

        #<ref> checks
        data_lines[i] = re.sub('<.*?>.*?</.*?>|<.*?/>','',data_lines[i])
        #Do ref check among lines ??
        data_lines[i] = re.sub('<.*?>','',data_lines[i])   #for <br><small> etc

        # print("final adding to body",data_lines[i])
        bodytext.append(data_lines[i])
        i+=1
    
    # print("Infobox - ",infobox)
    # print("References - ",references)
    # print("links - ",links)
    # print("category - ",category)
    # print("Body Text - ",bodytext)

    temp = []
    for s in infobox:
        temp.append(cleanUp(str(s)))
    infobox = " ".join(temp)
    infobox = tokenization_stemming(infobox)
    # print("Cleaned Infobox -",infobox)
    infobox_dict ={}
    for w in infobox:
        if( is_good_word(w)):
            if(w not in infobox_dict):
                infobox_dict[w]=1
            else:
                infobox_dict[w]+=1
    # print("Infobox dict-",infobox_dict)

    #Donot clean references of /,: and Not Tokenizing and Stemming
    temp = []
    # for s in references:
    #     temp.extend(cleanUp(str(s),1))
    # references = temp
    for s in references:
        temp.append(cleanUp(str(s)))
    references = " ".join(temp)
    references = tokenization_stemming(references)
    # print("Cleaned References -",references)
    references_dict ={}
    for w in references:
        if( is_good_word(w)):
            if(w not in references_dict):
                references_dict[w]=1
            else:
                references_dict[w]+=1
    # print("References dict-",references_dict)

    temp = []
    for s in links:
        temp.append(cleanUp(str(s)))
    links = " ".join(temp)
    links = tokenization_stemming(links)
    # print("Cleaned External links -",links)
    links_dict ={}
    for w in links:
        if(is_good_word(w)):
            if(w not in links_dict):
                links_dict[w]=1
            else:
                links_dict[w]+=1
    # print("links dict -",links_dict)

    temp = []
    for s in category:
        temp.append(cleanUp(str(s)))
    category = " ".join(temp)
    category = tokenization_stemming(category)
    # print("Cleaned Category -",category)
    category_dict ={}
    for w in category:
        if(is_good_word(w)):
            if(w not in category_dict):
                category_dict[w]=1
            else:
                category_dict[w]+=1
    # print("Category dict -",category_dict)

    temp = []
    for s in bodytext:
        temp.append(cleanUp(str(s)))
    bodytext = " ".join(temp)
    bodytext = tokenization_stemming(bodytext)
    # print("Cleaned Text -",bodytext)
    bodytext_dict ={}
    for w in bodytext:
        if(is_good_word(w)):
            if(w not in bodytext_dict):
                bodytext_dict[w]=1
            else:
                bodytext_dict[w]+=1
    # print("BodyText dict-",bodytext_dict)
    
    return infobox_dict,references_dict,links_dict,category_dict,bodytext_dict


def process_title(title):
    #print("Title Received - ",title)
    #Preprocessing
    clean_title= cleanUp(title)
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


def process_query(query):
    #Bad Symbols
    query = BAD_SYMBOLS_RE.sub(' ', query)
    query = SYMBOLS.sub(' ', query)
    #Case Folding
    query = query.lower()
    #Stop words
    query = ' '.join(word for word in query.split() if word not in STOPWORDS)
    #Tokenization and Stemming
    query_words = tokenization_stemming(query)
    return query_words


