# -*- coding: utf-8 -*-

import pypandoc
#import re
import regex as re

# Characters with special meaning in LaTeX: & % $ # _ { } ~ ^ \
def FindForbiddenChars (string):
    """LaTeX has some problems when trying to write files with these characters, so this script will \
    correctly escape them, before pypandoc conversion."""
    # forbid_char = ['[&]','[%]','[$]','[#]','[_]','[{]','[}]','[~]']

    # easyforbids2 = re.compile(r'&|%|\$|#|_|{|}|~|\^|\\')
    easyforbids = re.compile(r'[&%$#_{}~\^\\]')

    # New definition: \# \$ \% \^{} \& \_ \{ \} \~{} \textbackslash

    #easyforbids = re.compile(r'[#$%&_{}]')
    #add_forbids = re.compile(r'[\^~]')
    #back_forbid = re.compile(r'[\\]')

    pipe = re.compile(r'[|]')
    string = pipe.sub("\\textbar ", string)

    #string = back_forbid.sub(r"\\textbackslash ", string)
    string = easyforbids.sub(r"\\\g<0>", string)
    #string = add_forbids.sub(r"\\\g<0>{}", string)

    return string


# teststring = r'[In our inaugural installment](http://www.reddit.com/r/AskHistorians/comments/zu5si/theory_thursdays_defining_history/), ' \
#              'we opened with a discussion how history should be defined. We followed that with a discussion of the fellow who has been called both ' \
#              'the "father of history" and the "father of lies," ' \
#              '[Herodotus](http://www.reddit.com/r/AskHistorians/comments/1071mf/theory_thursdays_herodotus_and_the_invention_of/). ' \
#              'Most recently, we discussed several other important ' \
#              '[ancient historians](http://www.reddit.com/r/AskHistorians/comments/10jxvc/theory_thursdays_ancient_and_medieval_historians/).'
# URL_no_s = r'http://www.google.com/'
# URL_no_http = r'www.google.com/'
# URL_no_slash = r'www.google.com'
# URL_complete = r'https://www.google.com/'
# URL_long = r'http://www.reddit.com/r/AskHistorians/comments/zu5si/theory_thursdays_defining_history/'
# correctstring = r'[In our inaugural installment](http://www.reddit.com/r/AskHistorians/comments/zu5si/theory_thursdays_defining_history/)'
# tests = [teststring, URL_no_s, URL_no_http, URL_no_slash, URL_complete, correctstring]

def FindStrayHyperlinks (string): # achar formação errada de html ou colocar o link em (link)

    """What we we will be looking for is the following:

    Number 1: More important, naked links. Things such as
        http://www.google.com
        https://www.google.com
        www.google.com
        https://www.google.com./search?q=test&oq=test&aqs=chrome..69i57j69i65j69i61.2512j0j

        The pattern must reflect all of these possibilities and return: [LINK](url)
    Number 2: Erroneous links. Markdown treats [text](url) as the correct way of indicating an URL. So, if [] and ()
              were to be switched, the code would not work properly. For example:
              (www.google.com)[Google] instead of [Google](www.google.com)

              or

              (Google)[www.google.com]
        The pattern must find the incorrect uses and return them correctly. This one is less important.

    At the moment, this function can only find and substitute rogue links that aren't correctly placed.

    Note: This fixed links in Markdown, before conversion.
    """

    # url_pattern = 'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
    # url_pattern = 'https?:\/\/(?P<url>(?P<www>www)\.\S{2,300}\.\w{2,3}\/?(?P<fim>\S{2,300}))'
    # url_pattern2 = '((https?:\/\/)?(www)\.\S{2,100}\.\w{2,3}(\/)?(\S{2,300}(\/)?)?(\/?))'
    # url_pattern3 = '(?<!\]\()((https?:\/\/)?(www)\.\S{2,100}\.\w{2,3}(\/)?(\S{2,300}(\/)?)?(\/?))'

    # Looks for http and switches to https
    find_http_pattern = r'http:\/\/'
    http_to_https_fix = re.compile(find_http_pattern)
    string = http_to_https_fix.sub('https://', string)

    # Looks for www and adds https before it.
    alone_www_fix_pattern = r'(?<!https://)((www)\.\S{2,100}\.\w{2,3}(\/)?(\S{2,300}(\/)?)?(\/?))'
    alone_www_fix = re.compile(alone_www_fix_pattern)
    string = alone_www_fix.sub('https://\g<1>', string)

    # Finds URLs that are alone (that is, not preceded by '](' and adds something to make them parseable by pandoc.
    # Supposedly does not require the ? after https, as there will be no http left.
    url_pattern4 = '(?<!\]\()(https?:\/\/(www)\.\S{2,100}\.\w{2,3}(\/)?(\S{2,300}(\/)?)?(\/?))'
    Case1 = re.compile(url_pattern4)
    string = Case1.sub('[link](\g<1>)', string)

    return string


def FillEmptyHyperlinksInLaTeX(string):
    """Sometimes LaTeX will find things with empty strings, {}, and will ignore the URL in place. When this happens,
    the URL is lost. Therefore, it is better to add something, like -link, in that place, so that the URL is
    accessible again. Takes a LaTeX string and returns it with filled curly brackets."""
    href_pattern = r'(\\href{.*?}){}'
    substitution = re.compile(href_pattern)
    string = substitution.sub('\g<1>{ - link }', string)

    #href_pattern = r'(\\fnurl{Link}{.*?}){}'
    #substitution = re.compile(href_pattern)
    #string = substitution.sub('\g<1>{ - link }', string)
    return string


def Change_href_to_fnurl(string):
    """Changes all the instances of href to fnurl, so that the urls go into the footnotes
    Current syntax of the command:
    \fnurl{text}{url}
    to compare, href is:
    \href{url}{text}
    """

    #string = r'\href{https://en.wikipedia.org/wiki/Ethiopia\#Religion}{30\% Muslim}'
    href_to_fnurl = re.compile(r'\\href{(.*?)}{(.*?)}')
    string = href_to_fnurl.sub(r'\\fnurl{\g<2>}{\g<1>}', string)
    #print(string)

    #string = '\href{https://en.wikipedia.org/wiki/Ethiopia\#Religion}{30\% Muslim}'
    #simple_href_to_fnurl = re.compile(r'href')
    #string = simple_href_to_fnurl.sub(r'fnurl', string)
    #print(string)

    return string


def EncapsulateScripts(string):
    """It is better to encapsulate the words in different scripts for XeLaTeX. It is possible, therefore, to use a
    less comprehensive main font, select which fonts are going to be used for the additional scripts and to avoid
    errors during compilation."""
    # \p{InGreek_and_Coptic}: U+0370–U+03FF
    # \p{InCyrillic}: U+0400–U+04FF
    # \p{InCyrillic_Supplementary}: U+0500–U+052F
    # \p{InHebrew}: U+0590–U+05FF
    # \p{InArabic}: U+0600–U+06FF

    Greek = re.compile('[\p{Greek}]{1,100}')
    Cyrillic = re.compile('[\p{Cyrillic}]{1,100}')
    Hebrew = re.compile('[\p{Hebrew}]{1,100}')
    Arabic = re.compile('[\p{Arabic}]{1,100}')
    Jap1 = re.compile('[\p{Han}\p{Katakana}\p{Hiragana}]{1,100}')
    # Jap2 = re.compile('[\p{Katakana}]{1,100}')
    # Jap3 = re.compile('[\p{Hiragana}]{1,100}')
    Korean = re.compile('[\p{Hangul}]{1,100}')
    # Chinese = re.compile('[\p{Han}]{1,100}')
    HindiSanskrit = re.compile('[\p{Devanagari}]{1,100}')

    string = Greek.sub(r'\\begin{greek}\g<0>\end{greek}', string)
    string = Cyrillic.sub(r'\\begin{russian}\g<0>\end{russian}', string)
    string = Hebrew.sub(r'\\begin{hebrew}\g<0>\end{hebrew}', string)
    string = Arabic.sub(r'\\begin{Arabic}\g<0>\end{Arabic}', string)
    string = Jap1.sub(r'{\japanesefont \g<0>}', string)
    string = Korean.sub(r'{\koreanfont \g<0>}', string)
    string = HindiSanskrit.sub(r'\\begin{sanskrit}\g<0>\end{sanskrit}', string)

    return string


def ChangeTitlestoSubtitles(string):
    """Finds text in latex files with '#' and changes them to '###' to avoid messing with the formatting"""
    title = re.compile('\n\n# ')
    sub = re.compile('\n\n## ')

    #string = title.sub('\n\n### ', string)
    #string = sub.sub('\n\n#### ', string)
    #string = title.sub(r'\')
    return string


def ChangeSectionToSubSub(string):
    """Sometimes comments get creative and use # to organize the text. This would get translated as \\section,
    but it is better to modify it so that it becomes a subsub section."""
    section = re.compile(r'\\section')
    string = section.sub(r'\\subsection', string)
    return string


def ChangeSectionToBF(string):
    """Workaround2, not really good"""
    section = re.compile(r'\section{(.*?)}')
    string = section.sub(r'\begin{LARGE}\textbf{\g<0>}\end{LARGE}')
    return string


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


#%% Not used at the moment, replaced by the limited version
def Parse_submission(submission, destination_dir, sub_id):
    """Initially used to go through a submission and write the comments for it. Deprecated"""
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


#%%
def Parse_submissionSub(submission, destination_dir, submission_id, limitation):
    """Creates a file that contains the submission id, begins by adding the preamble and header and then\
     goes through every comment in the limitation list, which contains the codes for each interesting comment."""
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
