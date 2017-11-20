import praw
from praw.models import MoreComments
import Authentication as Rauth

#----------------------------------------------------
def Parse_Forest (replies):
    if (replies == []):
        return
    for comment in replies:
        WriteBody(comment)
        WriteDepth(comment)
        Parse_Forest(comment.replies)

def WriteHead (submission):
    header=('('+str(submission.score)+') '+
              submission.title+'\n'+
              'By: '+ submission.author.name+
              '\n\n'+ submission.selftext+'\n\n')
    fhand.write(header)
    return

def WriteBody (comment):
    depth = comment.depth
    comment_content=(depth*'#'+comment.author.name+' '+
                     str(comment.score)+'\n'+ comment.body)
    fhand.write('\n----------------------------------\n')
    fhand.write(comment_content)
    return

def WriteDepth(comment):
    print (comment.depth*'#', 'Wrote comment', comment.id, 'with depth', comment.depth)
    return

reddit = Rauth.CreateReddit()

fhand = open('first_tree_test.txt', 'w', encoding='utf-8')

submission = reddit.submission(url='https://www.reddit.com/r/AskHistorians/comments/3ayhe8/how_could_a_white_minority_of_south_africans_10/cshenj0')
comments = submission.comments
submission.comments.replace_more(limit=0)

WriteHead(submission)

for comment in comments:
    WriteBody(comment)
    WriteDepth(comment)
    Parse_Forest(comment.replies)
    print('Finished parsing root comment ', comment.id)

print('Finished parsing everything')
fhand.close()
