# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 18:44:52 2017

@author: Karl
"""

import Parsing_submission as Parse
import Authentication as Auth
import os
import praw
from praw.models import MoreComments
import glob


def Summary_comm_tree (comments, fhand):
    if (comments == []):
        return

    for comment in comments:
        global key
        key += 1
        
        depth = comment.depth
        score = comment.score
        try:
            authorname = comment.author.name
        except:
            authorname = 'deleted'
        comment_length = len(comment.body)
        
        #summ_content = '#'*depth + ' '+authorname+' '+str(comment_length)
        summ_content = '%s %d %s %d %d\n' % ('#'*depth, key, authorname, score, comment_length)
        fhand.write(summ_content)
        Summary_comm_tree(comment.replies, fhand)

def Summary_comm_tree_lim (comments, fhand, selection):
    if comments == []:
        return
    global key
    key += 1
    for comment in comments:
        if key not in selection:
            continue
        
        depth = comment.depth
        score = comment.score
        try:
            authorname = comment.author.name
        except:
            authorname = 'deleted'
        comment_length = len(comment.body)
        
        #summ_content = '#'*depth + ' '+authorname+' '+str(comment_length)
        summ_content = '%s %d %s %d %d\n' % ('#'*depth, key, authorname, score, comment_length)
        fhand.write(summ_content)
        Summary_comm_tree_lim(comment.replies, fhand, selection)

#%%
''' #Whole file
current_dir = os.getcwd()
submission_links_location = os.path.join(current_dir,'Posts\\links')
africa_links = os.path.join(submission_links_location,'wiki_africa_parsed.txt')

links = open(africa_links,'r')
'''

''' #Specific links
url1 = 'https://www.reddit.com/r/AskHistorians/comments/2ba2ah/i_have_read_that_the_colonization_of_zimbabwe/cj3azuc'
url2 = 'https://www.reddit.com/r/AskHistorians/comments/20ctpz/how_many_genocides_were_committed_by_europeans_in/cg2tzct'
url3 = 'https://www.reddit.com/r/AskHistorians/comments/21fotl/what_was_an_englishman_doing_in_zimbabwe_1632/cgcmmeh?context=3'
url4 = 'https://www.reddit.com/r/AskHistorians/comments/35xps1/how_were_christian_missionaries_treated_by_the/crab5ic?context=3'
url5 = 'https://www.reddit.com/r/AskHistorians/comments/35bew8/what_was_life_like_for_former_slaves_sent_to/creib9g?context=3'

links = [url1,url2,url3,url4,url5]
lists = [[1],[1,2],[1,2,3,4,5],[1],[1]]
'''
'''
file_links = open('wiki_africa_parsed.txt','r')

links = []
lists = []

for link in file_links:
    link = link.rstrip()
    url, limits = link.split(' ')
    limits = limits.split(',')
    links.append(url)
    lists.append(list(map(int,limits)))
'''
#%% Criar resumos completos com comentários com keys

links = open('wiki_antiquity_parsed_2.txt','r')
link_summaries = open('antiquity_summary_full_keys.txt','w',encoding='utf-8')

link_summaries.write('--------------Antiquity-----------\n\n')

reddit = Auth.CreateReddit()

for link in links:
    link = link.rstrip()
    submission = reddit.submission(url=link)
    comments = submission.comments
    submission.comments.replace_more(limit=0)
    
    sub_id = submission.id_from_url(link)
    sub_title = submission.title
    
    text_to_write = link + '\n' + sub_id + ' ' + sub_title + '\n\n'
    
    link_summaries.write(text_to_write)
    key = 0
    Summary_comm_tree(comments, link_summaries)
    
    link_summaries.write('----\n\n')

    
link_summaries.close()

"""
#%% Criar resumos usando keys como limites
for link, lst in zip(links,lists):
    link = link.rstrip()
    submission = reddit.submission(url=link)
    comments = submission.comments
    submission.comments.replace_more(limit=0)
    
    sub_id = submission.id_from_url(link)
    sub_title = submission.title
    
    text_to_write = link + '\n' + sub_id + ' ' + sub_title + '\n\n'
    
    link_summaries.write(text_to_write)
    key = 0
    Summary_comm_tree_lim(comments, link_summaries, lst)
    
    link_summaries.write('----\n\n')

    
link_summaries.close()
"""