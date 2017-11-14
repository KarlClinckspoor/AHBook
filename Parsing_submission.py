import praw
from praw.models import MoreComments
import os
import time
import json

#%%
def Parse_Forest (replies, fhand):
    if (replies == []):
        return
    for comment in replies:
        WriteBody(comment, fhand)
        #PrintDepth(comment)
        Parse_Forest(comment.replies, fhand)

#%%
def WriteHead (submission, fhand):
    try:
        authorname = submission.author.name
    except:
        authorname = 'deleted'

    header=('('+str(submission.score)+') '+
              submission.title+'\n'+
              'By: '+ authorname+
              '\n\n'+ submission.selftext+'\n\n')
    fhand.write(header)
    return
#%%
def WriteBody (comment, fhand):
    depth = comment.depth
    try:
        authorname = comment.author.name
    except:
        authorname = 'deleted'

    comment_content=(depth*'#'+authorname+' '+
                     str(comment.score)+'\n'+ comment.body)
    fhand.write('\n----------------------------------\n')
    fhand.write(comment_content)
    return
#%%
def PrintDepth(comment):
    print (comment.depth*'#', 'Wrote comment', comment.id, 'with depth', comment.depth)
    return
#%%
def Parse_submission(submission, destination_dir, sub_id):
    #destination_dir = E:\Dropbox\Python\AH\Posts\wiki_africa_parsed
    destination_filename = sub_id+'.txt'
    destination_filepath = os.path.join(destination_dir,destination_filename)
    
    if os.path.isfile(destination_filepath):
        print(sub_id, 'already parsed')
        return
    try:
        fhand = open(destination_filepath, 'w', encoding='utf-8')
    except IOError:
        print('File already exists or ', IOError)
    #fhand = open(destination_filepath, 'w', encoding='utf-8')
    comments = submission.comments
    submission.comments.replace_more(limit=0)
    WriteHead(submission, fhand)
    for comment in comments:
        WriteBody(comment, fhand)
        #PrintDepth(comment)
        Parse_Forest(comment.replies, fhand)
        #print('Finished parsing root comment ', comment.id)
        #time.sleep(2)
    print('Finished parsing everything from file', sub_id)
    fhand.close()