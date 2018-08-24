from django.shortcuts import render,render_to_response,redirect,get_object_or_404
from django.views.generic import TemplateView
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
import WSearch.NLP_proccessing

import re
import sumy
import wikipedia
import parsedatetime
@csrf_exempt
def form(request):
    '''try:
        search_word=form["s"].value
    except NameError:
        print(" ")
    except TypeError:
        print(" ")
    except (UnicodeError, UnicodeEncodeError) as e:
        print(e)'''


    if request.POST:
        errors=[]
        '''if( 's' in request.POST) and ('l' in request.POST) and ('w' in request.POST):
            search_word=request.POST['s']
            n=request.POST['l']
            lang=request.POST['w']'''
        if( 's' in request.POST) or ('l' in request.POST) or ('w' in request.POST):
            if ('s' in request.POST):
                search_word=request.POST['s']
                if not search_word:
                    search_word="nlpwikisearch"
                    ern="Search"
                    errors.append('Enter a search term.')
            '''else:
                search_word="nlpwikisearch"
                ern="Search"'''
            if ('l' in request.POST):
                n=request.POST['l']
                if not n:
                    n=""
                    ern="No.of timeline sentences"
            '''else :
                n=""
                ern="No.of timeline sentences"'''
            if ('w' in request.POST):
                lang=request.POST['w']
                if not lang:
                    lang="en"
                    ern="language"
            '''else:
                lang="en"
                ern="language"'''
            num_res=5
            [x,j]=WSearch.NLP_proccessing.check(search_word)
            error=" "
            input_text=" "
            #timeline=[None]SSS
            #word_2_vec=[None]
            wiki_link=" "
            timeline_sentences=[]
            sent_t=[]
            d2v_vector=[]
            if(x != 0 and j == 1):
                word=x[0]
                wikipedia.set_lang(lang)
                inp_pg=wikipedia.page(word)
                input_text=wikipedia.summary(inp_pg.title,sentences=8)
                wiki_link=inp_pg.url
                processed_txt=WSearch.NLP_proccessing.pre_proc(input_text)
                sentences=WSearch.NLP_proccessing.sent_tokenize(inp_pg.content)
                [sent_t, timeline_sentences, d2v_vector]=WSearch.NLP_proccessing.timelinesentences(sentences,n)
                error=("There is no wikipedia file named by %s.\n But here is a page related to your search...\n%s " %  (search_word,word))
            elif (j==3 and x==0):
                error=(" Please Wait or Retry")
            elif (j==4 ):
                error=(" %s field is empty" % ern)
            elif (j==2 and x==0):
                error=("There is no wikipedia file named by %s" %  search_word)
            else:
                wikipedia.set_lang(lang)
                gt=wikipedia.search(search_word, results=num_res)
                inp_pg=wikipedia.page(search_word)
                input_text=wikipedia.summary(inp_pg.title,sentences=8)
                wiki_link=inp_pg.url
                processed_txt=WSearch.NLP_proccessing.pre_proc(input_text)
                sentences=WSearch.NLP_proccessing.sent_tokenize(inp_pg.content)
                [sent_t, timeline_sentences, d2v_vector]=WSearch.NLP_proccessing.timelinesentences(sentences,n)
                #print(" ")
                #print(input_text)
            return render(request,'post_details.html',
                                 {'s_w':search_word,'wiki':wiki_link,
                                 'sum':input_text, 'msg':j,
                                 'err':error, 'time':sent_t,'timeline_sentences':timeline_sentences,
                                 'n':n, 'd2v':d2v_vector})
        else:
            return render_to_response('form.html')

    else:
        return render_to_response('form.html')

def post_details(request):
    return render(request, 'post_details.html')
from django.shortcuts import render

# Create your views here.
