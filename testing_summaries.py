# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 18:44:52 2017

@author: Karl
"""

import Authentication as Auth

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


links = open('antiquity links.txt','r')
link_summaries = open('antiquity_summary_full_keys.txt','w',encoding='utf-8')

link_summaries.write('--------------Antiquity-----------\n\n')

reddit = Auth.CreateReddit()

for link in links:
    if link.startswith('#'):
        continue
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
