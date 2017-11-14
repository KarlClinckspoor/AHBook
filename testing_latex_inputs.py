# -*- coding: utf-8 -*-
import Authentication as Auth
import Parsing_submission_pandoc as Parse
import praw
from praw.models import MoreComments
import os

'''
url1 = 'https://www.reddit.com/r/AskHistorians/comments/2ba2ah/i_have_read_that_the_colonization_of_zimbabwe/cj3azuc'
url2 = 'https://www.reddit.com/r/AskHistorians/comments/20ctpz/how_many_genocides_were_committed_by_europeans_in/cg2tzct'
url3 = 'https://www.reddit.com/r/AskHistorians/comments/21fotl/what_was_an_englishman_doing_in_zimbabwe_1632/cgcmmeh?context=3'
url4 = 'https://www.reddit.com/r/AskHistorians/comments/35xps1/how_were_christian_missionaries_treated_by_the/crab5ic?context=3'
url5 = 'https://www.reddit.com/r/AskHistorians/comments/35bew8/what_was_life_like_for_former_slaves_sent_to/creib9g?context=3'
urls = [url1,url2,url3,url4,url5]
'''

'''
urls = open('wiki_africa_parsed.txt','r').read().split('\n'))
urls = urls[:-1] #workaround
'''
#%%
file_links = open('wiki_africa_parsed_2.txt','r')

links = []
lists = []

for link in file_links: #colocar safeties aqui
    link = link.rstrip()
    url, limits = link.split(' ')
    limits = limits.split(',')
    links.append(url)
    lists.append(list(map(int,limits)))
file_links.seek(0)
file_links.close()


#%%
'''
current_dir = os.getcwd()
texfilelocation = os.path.join(current_dir,'textest')
maintexlocation = os.path.join(texfilelocation,'main.tex')
'''
maintex = open('main.tex','w',encoding='utf-8')

#==============================================================================
# 
# preamble = ('+
#           '\\usepackage[subpreambles=true]{standalone}\n'+
#           #'\\usepackage{mdframed}\n'+
#           #'\\usepackage{hyperref}\n'+
#           #'\\usepackage[utf8]{inputenc}\n'+
#           '\\usepackage[english]{babel}\n'+
#           
#           )
# 
#==============================================================================
preamble = ('\\documentclass[10pt]{article}\n'+
            '\\usepackage[subpreambles=true]{standalone}\n'+
            '\\usepackage{mdframed}\n'+
            '\\usepackage{hyperref}\n'+
            '\\usepackage[utf8]{inputenc}\n'+
            '\\usepackage[english]{babel}\n'+
            '\\usepackage[a4paper, total={6in, 8in}]{geometry}\n'+
            '\\usepackage{import}\n'
            )

header = '\\begin{document}\n'

#for item in packages:
#    maintex.write((item+'\n'))

maintex.write(preamble)
maintex.write(header)

reddit = Auth.CreateReddit()

for link, key in zip(links,lists):
    print('Parsing file: ',link) 
    submission = reddit.submission(url=link)
    comments = submission.comments
    submission.comments.replace_more(limit=0)
    sub_id = submission.id_from_url(link)
    Parse.Parse_submissionSub(submission, os.getcwd(), sub_id, key)
    #fhand.close()
    maintex.write('\\import{./}{'+sub_id+'.tex}\n')
    
print ('Finished parsing everything')
maintex.write('\\end{document}')
maintex.close()