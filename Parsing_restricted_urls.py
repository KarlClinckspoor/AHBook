import Authentication as Auth
import Parsing_submission_pandoc as Parse
import os
import time
import glob

maintex = open('main.tex', 'w', encoding='utf-8')
preamble_xelatex = open('maintex preamble.dat', 'r').read()
header = ('\n\\begin{document}\n' +
          '\\normalem\n' +
          '\\tableofcontents\n' +
          '\\clearpage\n')

# maintex.write(preamble)
maintex.write(preamble_xelatex)
maintex.write(header)

reddit = Auth.CreateReddit()
files = glob.glob('wiki_africa_parsed2.txt')
#files = glob.glob('*.txt')
counter = 0
for file in files:
    with open(file, 'r') as source:
        # links, limits = [], []
        links, limits, sections, languages = [], [], [], {}

        for line in source:
            if len(line) == 0:
                continue
            if line.startswith('%'):  # comment line
                continue
            if line.startswith('###'):
                temp_section = line.rstrip()
                continue
            link = line.rstrip().split(' ')[0]
            limit = line.rstrip().split(' ')[1]
            try:  
                #print('Trying to unpack line<', line,'>')
                #link, limit, language = line.rstrip().split(' ')
                language = line.rstrip().split(' ')[2]
            except IndexError: # in case there's not enough args.
                #link, limit = line.rstrip().split(' ')
                language = ''
            links.append(link)
            if limit.endswith(','):
                limit = limit[:-1]
            limit = limit.split(',')

            limits.append(list(map(int, limit)))
            languages[link] = language
            try:
                sections.append(temp_section)  # not at all memory efficient, but it works.
            except NameError:
                sections.append('')

    current_section = ''
    for link, limit, section in zip(links, limits, sections):
        print('Parsing link: ', link)
        #if len(languages[link]) >= 2: #not languages[link].isalpha():
        #    print(link, 'has an unsupported language (', languages[link], ') at the moment. Skipping')
        #    continue

        submission = reddit.submission(url=link)
        sub_id = submission.id_from_url(link)
        Parse.Parse_submissionSub(submission, os.getcwd(), sub_id, limit)

        if section != current_section:
            current_section = section
            if section.startswith('###'):# and not section.startswith('####'):
                maintex.write('\\chapter{' + section.strip('#') + '}\n')
            #elif section.startswith('####'):
            #    maintex.write('\\section{' + section.strip('#') + '}\n')
            else:
                pass
        maintex.write('\\import{./}{' + sub_id + '.tex}\n')
        maintex.write('\\setcounter{footnote}{1}\n')
        print('Waiting for 2 seconds.')
        time.sleep(2)
    
    counter += 1
    if counter >= 5:
        break

print('Finished parsing everything')
maintex.write('\\end{document}')
maintex.close()
        
# preamble_xelatex = ('\\documentclass[10pt]{article}\n' +
#                     '\\usepackage[subpreambles=true]{standalone}\n' +
#                     '\\usepackage{mdframed}\n' +
#                     '\\usepackage{fontspec}\n' +
#                     '\\usepackage{polyglossia}\n' +
#                     '\\providecommand{\\tightlist}{\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}\n' +
#                     '\\setmainfont[Ligatures=TeX]{Times New Roman}' +
#                     '\\usepackage{hyperref}\n' +
#                     '\\hypersetup{pdftitle={/r/AskHistorians},colorlinks=false}\n'
#                     )

# preamble = ('\\documentclass[10pt]{article}\n' +
#             '\\usepackage[subpreambles=true]{standalone}\n' +
#             '\\usepackage{mdframed}\n' +
#             '\\usepackage{hyperref}\n' +
#             '\\usepackage[utf8]{inputenc}\n' +
#             '\\usepackage[english]{babel}\n' +
#             '\\usepackage[a4paper, total={6in, 8in}]{geometry}\n' +
#             '\\usepackage{import}\n'
#             )



# for link, limit in zip(links, limits):



