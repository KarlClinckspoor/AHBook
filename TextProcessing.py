import regex as re
import pypandoc

# todo: colocar todas as funções que lidam com texto, inclusive criar headers, preambles, etc, aqui.
# todo: transformar isto em uma classe.

# Characters with special meaning in LaTeX: & % $ # _ { } ~ ^ \
def find_forbidden_chars(string):
    """To be used on markdown strings:
    LaTeX has some problems when trying to write files with these characters, so this script will \
    correctly escape them, before pypandoc conversion."""
    # forbid_char = ['[&]','[%]','[$]','[#]','[_]','[{]','[}]','[~]']

    # easyforbids2 = re.compile(r'&|%|\$|#|_|{|}|~|\^|\\')
    easyforbids = re.compile(r'[&%$#_{}~\^\\]')

    # New definition: \# \$ \% \^{} \& \_ \{ \} \~{} \textbackslash

    #easyforbids = re.compile(r'[#$%&_{}]')
    #add_forbids = re.compile(r'[\^~]')
    #back_forbid = re.compile(r'[\\]')

    pipe = re.compile(r'[|]')
    string = pipe.sub(r"\textbar ", string)

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

def find_naked_hyperlinks(string): # achar formação errada de html ou colocar o link em (link)

    """To be used on markdown strings.
    Looks for naked hyperlinks and wraps them in good markdown syntax.

    What we we will be looking for is the following:

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
    case1 = re.compile(url_pattern4)
    string = case1.sub('[link](\g<1>)', string)

    return string


def fill_empty_href_command(string):
    """To be used on latex strings.
    Sometimes LaTeX will find things with empty strings, {}, and will ignore the URL in place. When this happens,
    the URL is lost. Therefore, it is better to add something, like -link, in that place, so that the URL is
    accessible again. Takes a LaTeX string and returns it with filled curly brackets."""
    href_pattern = r'(\\href{.*?}){}'  # todo: alterar essa pattern para algo menos abrangente.
    substitution = re.compile(href_pattern)
    string = substitution.sub('\g<1>{ - link }', string)

    #href_pattern = r'(\\fnurl{Link}{.*?}){}'
    #substitution = re.compile(href_pattern)
    #string = substitution.sub('\g<1>{ - link }', string)
    return string


def href_to_fnurl(string):
    """To be used on latex strings.
    Changes all the instances of href to fnurl, so that the urls go into the footnotes. Custom command.
    Current syntax of the command, which is the opposite of href:
    \fnurl{text}{url}
    href is:
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


def encapsulate_scripts(string):
    """To be used in latex strings.
    Encapsulates scripts in foreign languages in appropriate tags so that XeLaTeX with foreign language support can
    correctly choose the font for each script.
    Requires the package regex instead of the builtin re in order to match based on unicode ranges."""

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


def title_to_subtitle(string):  # todo: checar o que essa função realmente faz.
    """ To be used on markdown strings. Adds '#' to divisions in markdown strings
     so that the sectioning is kept constant."""
    title = re.compile('\n\n# ')
    sub = re.compile('\n\n## ')

    string = title.sub('\n\n### ', string)
    string = sub.sub('\n\n#### ', string)
    #string = title.sub(r'\')
    return string


def section_to_subsub(string):
    """To be used on latex strings. Changes sections to subsections in a file. This is used to correct pandoc
    conversions on user markdown with "#"
    Sometimes comments get creative and use # to organize the text. This would get translated as \\section,
    but it is better to modify it so that it becomes a subsub section."""
    section = re.compile(r'\\section')
    string = section.sub(r'\\subsubsection', string)
    return string


def section_to_bf(string):
    """Workaround2, not really good"""
    section = re.compile(r'\section{(.*?)}')
    string = section.sub(r'\begin{LARGE}\textbf{\g<0>}\end{LARGE}')
    return string


def get_subpreamble():
    preamble_xelatex = open('subtex preamble.dat', 'r').read()
    return preamble_xelatex


def get_preamble():
    preamble_xelatex = open('Maintex preamble.dat', 'r').read()
    return preamble_xelatex


def write_body(body, authorname, flair, depth, fhand):
    """Writes the comment body into the file, correcting for forbidden characters, finding missing URLs."""
    # print('Debug: Starting to write about comment id', comment.id)
    if authorname == '[removed]':
        authorname = 'removed'  # todo: testar se isso resolver o problema
    authorname = find_forbidden_chars(authorname)  # escapes chars in the username, for LaTeX

    if type(flair) != str:  # In case flair is passed as None or something else
        flair = ''

    flair = find_forbidden_chars(flair)  # escapes chars in the username flair.

    # todo: findstrayhyperlinks is messing with existing hyperlinks. Fix it
    # comment_cleaned = FindStrayHyperlinks(comment.body)
    # comment_cleaned = ChangeTitlestoSubtitles(comment_cleaned)
    comment_cleaned = body
    comment_latex = pypandoc.convert_text(comment_cleaned, 'latex', format='markdown',
                                          extra_args=['--wrap=preserve'], encoding='utf-8')

    # comment_latex = FillEmptyHyperlinksInLaTeX(comment_latex)

    # Adjusts the latex content
    comment_latex = encapsulate_scripts(comment_latex)  # For XeLaTeX language support
    comment_latex = section_to_subsub(comment_latex)  # To stop interfering with the main latex file ordering
    comment_latex = href_to_fnurl(comment_latex)  # Adds links to footnotes

    comment_content = '\\textbf{' + authorname + '} \\emph{' + flair + '}\n\n' + comment_latex

    # shifts text to the right as deeper in the comment chain it goes.
    fhand.write('\\begin{adjustwidth}{' + str(0.5 * depth) + 'cm}{}\n')
    fhand.write(comment_content)
    fhand.write('\\end{adjustwidth}\n')
    return 'Success'


def write_header(authorname, selftext, title, shortlink, fhand):
    """Writes the header of the submission, which contains the preamble,
     the title as a section and the selftext in a frame."""

    # try:
    #    authorname = submission.author.name
    # except:
    #    authorname = 'deleted'

    authorname = find_forbidden_chars(authorname)

    selftext = find_naked_hyperlinks(selftext)
    selftext = find_forbidden_chars(selftext)

    # try:
    #     selftext = submission.selftext
    # except:
    #     selftext = ''

    # selftext = FindForbiddenChars(selftext)

    selftext = pypandoc.convert_text(selftext, 'latex', format='markdown', extra_args=['--wrap=preserve'],
                                     encoding='utf-8')

    selftext = fill_empty_href_command(selftext)
    # todo: debug this
    selftext = href_to_fnurl(selftext)

    title = find_forbidden_chars(title)

    header = '\\subsection{' + title + '}\n\\begin{flushright}By:{' + authorname + '}' \
              ' -- \\fnurl{Link}{' + shortlink + '}\\end{flushright}\n'

    if len(selftext) == 0 or selftext == '[deleted]' or selftext.isspace():
        header = header + '\\hrule\n\\vspace{10pt}\n'
    else:
        header = header + '\\begin{mdframed}\n{' + selftext + '}\n\\end{mdframed}\n'

    fhand.write(get_subpreamble())
    fhand.write(header)

    return 'Success'
