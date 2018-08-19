# -*- coding: utf-8 -*-

import pypandoc
#import re
import regex as re


def Parse_Forest(replies, fhand):
    """A recursive function that will go start with a comment and go through all of its replies, and write the \
    contents. It follows the form:
    1 - 1 - 1
        2 - 1
          - 2
        3 - 1
          - 2
          - 3
    2 - 1 ...
    Not used anymore, due to its indiscriminate nature (i.e. gets ALL the comments).
    """
    if (replies == []):
        return
    for comment in replies:
        WriteBody(comment, fhand)
        Parse_Forest(comment.replies, fhand)

        

def ParseForestLimited(comments, fhand, limit_list):
    """Goes through a comment forest but only writes the comments which are in the limit_list.
    Limit_list is a list containing the unique code of the comment, which begins at 1 and goes up for each
    comment on a tree. So the tree:
    1 - 1 - 1
      - 2 - 1
          - 2
      - 3 - 1
          - 2
          - 3
    2 - 1 ...

    has the comment codes:
    1 - 2 - 3
      - 4 - 5
      - 6 - 7
          - 8
          - 9
    10 - 11 ...

    It requires the global variable limit because, by the nature of the recursive function it is tedious to
    keep passing a variable like this, back and forth, so this is a more direct solution.
    Instead of this code, it could be possible to use the comment_id, but it is less human-readable, so manually
    selecting which comments one wants to include would get much more tedious.
    """
    if comments == []: return

    global comment_identifier
    comment_identifier += 1  # limit_list always starts at 1.
    global parsed_comments

    #print('Debug: ParseForesLimited, identifier', comment_identifier)

    # for comment in comments:
    #     if comment_identifier not in limit_list:
    #         continue
    #     WriteBody(comment, fhand)
    #     ParseForestLimited(comment.replies, fhand, limit_list)
    for comment in comments:
        if (comment_identifier in limit_list) and (comment_identifier not in parsed_comments):
            # print('Debug: Comment identifier:', comment_identifier, 'Limit list', limit_list)
            WriteBody(comment, fhand)
            parsed_comments.append(comment_identifier)
            # print('Debug: Parsed', comment_identifier, 'parsed comments: ', parsed_comments)
            # ParseForestLimited(comment.replies, fhand, limit_list)
        ParseForestLimited(comment.replies, fhand, limit_list)



# %%
def WriteHead(submission, fhand):
    """Writes the header of the file. Has been supplanted by WriteHeadSub"""

    try:
        authorname = submission.author.name
    except:
        authorname = 'deleted'
    
    authorname = FindForbiddenChars(authorname)
    
    try:
        selftext = submission.selftext
    except:
        selftext = ''
    
    #selftext = FindForbiddenChars(selftext)
    
    selftext = pypandoc.convert_text(selftext, 'latex', format='markdown', extra_args=['--wrap=preserve'],
                                     encoding='utf-8')
    header = (
              '\\section{' + submission.title+'}\n' +
              '\\begin{flushright}By:' + authorname + '\\end{flushright}\n'
              )
    if len(selftext) == 0 or selftext == '[deleted]':
        header = header + '\\hrule\n\\vspace{10pt}\n'
    else:
        header = header + '\\begin{mdframed}\n' + submission.selftext + '\n\\end{mdframed}\n'
    fhand.write(header)
    return


def WriteHeadSub(submission, fhand):
    """Writes the header for the LaTeX file for a specific submission."""
    try:
        authorname = submission.author.name
    except:
        authorname = 'deleted'
    
    authorname = FindForbiddenChars(authorname) # escapes forbidden characters in the username
    
    try:
        selftext = submission.selftext
    except:
        selftext = ''
    if selftext == '[deleted]':
        selftext = '' # extra precautions in case the text of the submission has been deleted

    selftext = FindStrayHyperlinks(selftext)
    selftext = FindForbiddenChars(selftext)

    selftext = pypandoc.convert_text(selftext, 'latex', format='markdown', extra_args=['--wrap=preserve'],
                                     encoding='utf-8') # needs to use --wrap=preserve to avoid weird extra spaces.

    selftext = FillEmptyHyperlinksInLaTeX(selftext)
    # todo: debug this
    selftext = Change_href_to_fnurl(selftext)

    # todo: test if removing the excess parameters will positively or negatively impact compiling
    preamble_xelatex = open('subtex preamble.dat', 'r').read()


    # preamble = ('\\documentclass[float=false,crop=false]{standalone}\n' +
    #             '\\usepackage[subpreambles=true]{standalone}\n' +
    #             '\\usepackage{mdframed}\n' +
    #             '\\usepackage{hyperref}\n' +
    #             '\\usepackage[utf8]{inputenc}\n' +
    #             '\\usepackage[english]{babel}\n' +
    #             #'\\usepackage[a4paper, total={6in, 8in}]{geometry}\n'+
    #             '\\providecommand{\\tightlist}{\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}' +
    #             '\\usepackage{changepage}' +
    #             '\\begin{document}\n'
    #             )

    title = FindForbiddenChars(submission.title)

    # Added \fnurl, to get the submission URL as a footnote.
    header = (
              '\\section{' + title + '}\n' +
              '\\begin{flushright}By:' + authorname +
              #' \\fnurl{' + submission.shortlink + '}{Link}\\end{flushright}\n'
              ' \\fnurl{Link}{' + submission.shortlink + '}\\end{flushright}\n'
              )
    if selftext.isspace():
        header = header + '\\hrulefill\n\n'
    else:
        header = header + '\\begin{mdframed}\n' + selftext + '\n\\end{mdframed}\n'
    # In case the header contains nothing, place a horizontal ruler. Else, frame it in a pretty box.

    # fhand.write(preamble)
    fhand.write(preamble_xelatex)
    fhand.write(header)
    return


def WriteBody (comment, fhand):
    """Writes the comment body into the file, correcting for forbidden characters, finding missing URLs."""
    #print('Debug: Starting to write about comment id', comment.id)
    depth = comment.depth
    try:
        authorname = comment.author.name
    except:
        authorname = 'deleted'
    
    authorname = FindForbiddenChars(authorname) # escapes chars in the username, for LaTeX
    
    try:
        flair = comment.author_flair_text # username flair is useful for distinguishing specific commenters.
        flair = FindForbiddenChars(flair) # escapes chars in the username flair.
    except:
        flair = ''
    if type(flair)!=str:
        flair = ''
    
    #if comment.body == 'removed' or comment.body == 'deleted': # should not really occur, because it looks ugly
    #    print('Comment has no content')
    #    return

    # todo: findstrayhyperlinks is messing with existing hyperlinks.
    #comment_cleaned = FindStrayHyperlinks(comment.body)
    #comment_cleaned = ChangeTitlestoSubtitles(comment_cleaned)
    comment_cleaned = comment.body
    comment_latex = pypandoc.convert_text(comment_cleaned, 'latex', format='markdown',
                                          extra_args=['--wrap=preserve'], encoding='utf-8')
    #comment_latex = FillEmptyHyperlinksInLaTeX(comment_latex)
    comment_latex = EncapsulateScripts(comment_latex)
    comment_latex = ChangeSectionToSubSub(comment_latex)
    comment_latex = Change_href_to_fnurl(comment_latex)

    #hspace = '\\hspace{'+str((depth*10))+'pt}\n\n'
#    comment_content = (
#                       '\\textbf{'+authorname+'} '+
#                       '\\emph{'+flair+'}\n\n'+
#                       #hspace+
#                       comment_latex
#                       )

    comment_content = (
                       '\\textbf{%s} \\emph{%s}\n\n%s' % (authorname, flair, comment_latex)
                       )
#    if depth == 0:
#        comment_content =  comment_content + '\n\n\\hrulefill\n\n'
    #print(comment_latex)
    fhand.write('\\begin{adjustwidth}{' + str(0.5*depth) + 'cm}{}\n')
    fhand.write(comment_content)
    fhand.write('\\end{adjustwidth}\n')
    #print('Debug: Written comment id', comment.id)
    return


def Parse_submission(submission, destination_dir, sub_id):
    """Initially used to go through a submission and write ALL the comments from it. Requires an internet connection
    as it pulls data directly from reddit."""

    destination_filename = sub_id+'.tex'
    '''
    destination_filepath = os.path.join(destination_dir,destination_filename)
    if not os.path.isfile(destination_filepath):
        try:
            fhand = open(destination_filepath, 'w', encoding='utf-8')
        except IOError:
            print('File already exists or ', IOError)
    '''
    fhand = open(destination_filename,'w',encoding='utf-8')
    comments = submission.comments
    submission.comments.replace_more(limit=0)
    WriteHead(submission, fhand)
    for comment in comments:
        WriteBody(comment, fhand)
        #PrintDepth(comment)
        Parse_Forest(comment.replies, fhand)
        #print('Finished parsing root comment ', comment.id)
        #time.sleep(1)
    print('Finished parsing everything from file', sub_id)
    fhand.close()


def Parse_submissionSub(submission, destination_dir, submission_id, limitation):
    """Creates a file that has the same name as the submission id, begins by adding the preamble and header and then\
     goes through every comment in the limitation list, which contains the codes for each interesting comment.
     This list consists of a sequence of numbers that are added after the submission URL in the text file."""
    destination_filename = submission_id + '.tex'
    #print('Debug: Limits = ', limitation)
    '''
    destination_filepath = os.path.join(destination_dir,destination_filename)
    if not os.path.isfile(destination_filepath):
        try:
            fhand = open(destination_filepath, 'w', encoding='utf-8')
        except IOError:
            print('File already exists or ', IOError)
    '''
    fhand = open(destination_filename, 'w', encoding='utf-8')
    comments = submission.comments
    submission.comments.replace_more(limit=0)  # only important for long threads, but is useful nonetheless.

    WriteHeadSub(submission, fhand)
    
    global comment_identifier
    comment_identifier = 0  # This is for use in the limited comment tree parse, to only select the comments of interest.
    global parsed_comments
    parsed_comments = []  # This is to prevent duplicates from being created.
    #print('Debug: Limitation =', limitation)
    ParseForestLimited(comments, fhand, limitation)

    # This should go through all the comments, not needing to go through a loop for the first comment.
    '''
    for comment in comments:
        WriteBody(comment, fhand)
        #PrintDepth(comment)
        Parse_Forest(comment.replies, fhand)
        #if comment.depth == 0:
            #fhand.write('\n\n\\hrulefill\n\n')
        #print('Finished parsing root comment ', comment.id)
        #time.sleep(1)
    '''
    end = '\\clearpage\\end{document}'
    fhand.write(end)

    print('Finished parsing everything from file', submission_id)
    fhand.close()
