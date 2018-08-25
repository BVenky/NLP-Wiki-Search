import re
import sumy
import string
import wikipedia
import parsedatetime
import random
from nltk import sent_tokenize
from lexrank import STOPWORDS, LexRank
from path import Path
from datetime import datetime
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from gensim.models import word2vec
from gensim.test.utils import common_texts
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.test.utils import get_tmpfile

#Sentence Embedding- Training Model
documents_d2c = [TaggedDocument(doc, [i]) for i, doc in enumerate(common_texts)]
model = Doc2Vec(documents_d2c, vector_size=5, window=2, min_count=1, workers=4)
fname = get_tmpfile("my_doc2vec_model")
model.save(fname)
model = Doc2Vec.load(fname)
model.delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)
#Done

documents = []
documents_dir = Path('bbc/politics')

for file_path in documents_dir.files('*.txt'):
    with file_path.open(mode='rt', encoding='utf-8') as fp:
        documents.append(fp.readlines())

lxr = LexRank(documents, stopwords=STOPWORDS['en'])

lookup_dict = {'rt':'Retweet', 'dm':'direct message', "awsm" : "awesome", "luv" :"love"}
def _remove_noise(input_text):      #Remove noise like the words and notations in noise list
    #words = re.split('\w',input_text)
    words=input_text.split()
    stop_words = stopwords.words('english')
    noise_free_words = [w for w in words if not w in stop_words]
    noise_free_text = " ".join(noise_free_words)
#    print(noise_free_words)
#    print(noise_free_text)
    return noise_free_text, noise_free_words #return complete string as well as a list of all words in the input text

def _remove_regex(input_text, regex_pattern):     #remove regex patterns like #[word]
    urls = re.finditer(regex_pattern, input_text)
    for i in urls:
        input_text = re.sub(i.group().strip(), '', input_text)
        #print(input_text)
    return input_text    #updated input text sentence/Paragraph

def _lexicon_norm(txt_f_r):      # lexicon normalisation
    x=len(txt_f_r)
#    print(x)
    txt_f=[None]*(len(txt_f_r))
    lem = WordNetLemmatizer()
    stem = PorterStemmer()
    new_words = []
    for i in range(0,len(txt_f_r)):
         #txt_f[i]=lem.lemmatize(txt_f_r[i], "v")
         txt_f[i]=stem.stem(txt_f_r[i])
         new_words.append(txt_f[i])
    txt_f_e = " ".join(new_words)
    return txt_f_e   # updated input sentence/Paragraph where ing, es, ed, etc are removed from a word

def check(user_input):
        try:
            wiki=wikipedia.summary(user_input)
            j=0
            x=0
        except wikipedia.exceptions.DisambiguationError as e:
            x=e.options
            j=1
        except wikipedia.exceptions.PageError:
            j=2
            x=0
            print("")

        except requests.exceptions.ConnectionError:
            j=3
            x=0
            print("")
        return x, j

def _lookup_words(input_text):
    words = input_text.split()
    new_words = []
    for word in words:
        if word.lower() in lookup_dict:
            word = lookup_dict[word.lower()]
        new_words.append(word)
    new_text = " ".join(new_words)
    return new_text
def pre_proc(input_text):
    lookup_txt=_lookup_words(input_text)     #look for short forms
    #print(lookup_txt)
    [n_f_txt,n_f_wrd]=_remove_noise(lookup_txt)     # list of all words in input sentence and the combined string are loaded
    #print("n_f_txt= %s and n_f_wrd= %s" % (n_f_txt,n_f_wrd) )
    regex_pattern = "#[\w]*"
    txt=_remove_regex(n_f_txt, regex_pattern) # remove regex patterns
    #print(txt)
    sentences = sent_tokenize(txt)   # Seperate out the sentences from paragraphs
    #print(sentences[0])
    txt_f_r=txt.split()
    rem = str.maketrans('', '', string.punctuation)
    stripped_punc = [w.translate(rem) for w in sentences]   #strip punctuation
    #print(stripped_punc)
    #print(len(txt_f_r))
    processed_txt=_lexicon_norm(stripped_punc)   #Final Pre-processed( Noise is removed ) Output for given input
    #print(processed_txt)
    return processed_txt

def timelinesentences(sentences,n):
    try:
        num=int(n)
    except:
        num=0
    timeline_sentences=[]
    sent_t=[]
    j=[]
    cal=0
    proc_sen=[]
    t_summary=""
    error_t=""
    cal = parsedatetime.Calendar()
    p_t, parse_status = cal.parse("")
    present_t=datetime(*p_t[:6])
    present_time=present_t.strftime('%m/%Y')
    p_time_ref=present_t.strftime('%d/%m/%Y')
    print(present_time)
    print("YYYY")
    for sent in sentences:
        call = parsedatetime.Calendar()
        t_s, parse_status = call.parse(sent)
        time_s=datetime(*t_s[:6])
        tim_s=time_s.strftime('%b/%Y')
        time_sent=time_s.strftime('%m/%Y')
        time_ref=time_s.strftime('%d/%m/%Y')
        if(time_sent < present_time) and (time_ref != p_time_ref):
            print(time_sent)
            print("YYYY")
            sent_t.append(tim_s)
            #new_sent_t=" ".join(sent_t)
            timeline_sentences.append(sent)
        else:
            continue
    print(sent_t)
    ln=len(timeline_sentences)
    print(ln)
    if (num<=ln) and (num>0):
        t_summary = lxr.get_summary(timeline_sentences, summary_size=num, threshold=.1)
    elif (num==0):
        t_summary = lxr.get_summary(timeline_sentences, summary_size=4, threshold=.1)
    else:
        t_summary = lxr.get_summary(timeline_sentences, summary_size=ln, threshold=.1)
    for sen in t_summary:
        proc_sum=pre_proc(sen)
        vector = model.infer_vector(proc_sum.split())
        proc_sen.append(vector)
    print(proc_sen)
    scores_cont=lxr.rank_sentences(timeline_sentences,threshold=.1,fast_power_method=False,)
    print(scores_cont)
    print("YYYY")
    max_num=max(scores_cont)
    print(max_num)
    for num in scores_cont:
        if num == max_num:
            j.append(scores_cont.tolist().index(num))
            print(scores_cont.tolist().index(num))
    print(j)
    if len(j)>1:
        z=random.choice(j)
    else:
        z=j[0]
    print(z)
    print(timeline_sentences[z])
    return error_t, sent_t[z], t_summary, proc_sen


def search_func(search_word,n,lang,num_res):
    [x,j]=check(search_word)
    error=" "
    input_text=" "
    #timeline=[None]SSS
    #word_2_vec=[None]
    wiki_link=" "
    timeline_sentences=[]
    sent_t=[]
    d2v_vector=[]
    error_t=""
    if(x != 0 and j == 1):
        word=x[0]
        wikipedia.set_lang(lang)
        inp_pg=wikipedia.page(word)
        input_text=wikipedia.summary(inp_pg.title,sentences=8)
        wiki_link=inp_pg.url
        processed_txt=pre_proc(input_text)
        sentences=sent_tokenize(inp_pg.content)
        [error_t, sent_t, timeline_sentences, d2v_vector]= timelinesentences(sentences,n)
        error=("There is no wikipedia file named by %s.\n But here is a page related to your search...\n%s " %  (search_word,word))
    elif (j==3 and x==0):
        error=(" Please Wait or Retry")
    elif (j==2 and x==0):
        error=("There is no wikipedia file named by %s" %  search_word)
    else:
        wikipedia.set_lang(lang)
        gt=wikipedia.search(search_word, results=num_res)
        inp_pg=wikipedia.page(search_word)
        input_text=wikipedia.summary(inp_pg.title,sentences=8)
        wiki_link=inp_pg.url
        processed_txt= pre_proc(input_text)
        sentences= sent_tokenize(inp_pg.content)
        [error_t, sent_t, timeline_sentences, d2v_vector]= timelinesentences(sentences,n)
        #print(" ")
        #print(input_text)
    return wiki_link,input_text,j,error,sent_t,timeline_sentences,n,d2v_vector, error_t
