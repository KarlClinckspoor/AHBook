# -*- coding: utf-8 -*-
import pylatex

def Parse_Forest (replies, fhand):
    if (replies == []):
        return
    for comment in replies:
        WriteBody(comment, fhand)
        #PrintDepth(comment)
        Parse_Forest(comment.replies, fhand)

def Parse_submission(submission, destination_dir, sub_id):
    destination_filename = sub_id+'.tex'
    destination_filepath = os.path.join(destination_dir,destination_filename)

    if os.path.isfile(destination_filepath):
        print(sub_id, 'was previously parsed')
        return
    try:
        fhand = open(destination_filepath, 'w', encoding='utf-8')
    except IOError:
        print('File already exists or ', IOError)
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
