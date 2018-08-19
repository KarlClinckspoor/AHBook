# encoding=utf8


import os
from SubmissionProcessing import *
from Database import fetch_database_posts, fetch_submission_comments
import pypandoc


def parse_submission_whole(submission, destination_dir, sub_id):
    """Initially used to go through a submission and write ALL the comments from it. Requires an internet connection
    as it pulls data directly from reddit."""

    destination_filename = sub_id + '.tex'

    if not os.path.isdir(destination_dir):
        os.mkdir(destination_dir)  # todo: check if this creates recursively
    destination_filepath = os.path.join(destination_dir, destination_filename)

    '''
    destination_filepath = os.path.join(destination_dir,destination_filename)
    if not os.path.isfile(destination_filepath):
        try:
            fhand = open(destination_filepath, 'w', encoding='utf-8')
        except IOError:
            print('File already exists or ', IOError)
    '''
    fhand = open(destination_filepath, 'w', encoding='utf-8')
    comments = submission.comments
    submission.comments.replace_more(limit=0)

    write_header(submission.authorname, submission.selftext, submission.title, submission.shortlink, fhand)
    for comment in comments:
        write_body(comment, fhand)
        walk_forest(comment.replies, fhand)
    print('Finished parsing everything from file', sub_id)
    fhand.close()
    return


def parse_submission_limited(submission, destination_dir, submission_id, limitation):
    """Creates a file that has the same name as the submission id, begins by adding the preamble and header and then\
     goes through every comment in the limitation list, which contains the codes for each interesting comment.
     This list consists of a sequence of numbers that are added after the submission URL in the text file."""

    destination_filename = submission_id + '.tex'
    if not os.path.isdir(destination_dir):
        os.mkdir(destination_dir)
    destination_filepath = os.path.join(destination_dir, destination_filename)
    fhand = open(destination_filepath, 'w', encoding='utf-8')

    comments = submission.comments
    submission.comments.replace_more(limit=0)  # only important for long threads, but is useful nonetheless.

    write_header(submission.author.name, submission.selftext,
                 submission.title, submission.shortlink, fhand)

    global comment_identifier
    comment_identifier = 0  # This is for use in the limited comment tree parse, to only select the comments of interest.
    global parsed_comments
    parsed_comments = []  # This is to prevent duplicates from being created.

    walk_forest_paths(comments, fhand, limitation)

    fhand.write('\\clearpage\\end{document}')

    print('Finished parsing everything from file', submission_id)
    fhand.close()


# todo: achar onde que ele colocou {[}deleted{]}

def parse_submission_db(dest_dir='./assembly', dest_file='main.tex', str_post_filters={},
                        str_comm_filters={}, num_comm_filters={}, reddit=''):
    """Utilizes an offline database with the desired comments. Must provide a list of the desired themes
    and a dict with the desired limitations to be imposed, such as depth <= 10, score > 0, length > 500"""
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    dest_filepath = os.path.join(dest_dir, dest_file)
    maintex = open(dest_filepath, 'w', encoding='utf8')

    maintex.write(get_preamble())
    maintex.write('\n\\begin{document}\n\\normalem\n\\tableofcontents\n\\clearpage\n')
    maintex.write('\n\n')

    data = fetch_database_posts(requirements=str_post_filters,
                                 items=['post_fullname', 'theme', 'section', 'subsection',
                                        'rel_comment_folder', 'post_title', 'poster_username', 'url'])
    posts = [i[0] for i in data]
    themes = [i[1] for i in data]
    sections = [i[2] for i in data]
    subsections = [i[3] for i in data]
    relpaths = [i[4].replace('\\', r'/') for i in data]  # Created the db in windows, using it in Linux ATM
    titles = [i[5] for i in data]
    usernames = [i[6] for i in data]
    urls = [i[7] for i in data]  # all of the same length
    # todo: adicionar shortlinks aos urls, ou fazer uma conversão aqui por enquanto. Também, remover a newline

    curr_theme = themes[0]
    curr_section = sections[0]
    curr_subsection = subsections[0]

    for i, post in enumerate(posts):

        print('Assembling {0}: {1} of {2}'.format(post, i + 1, len(posts)))
        if i == 0:
            maintex.write('\n\n\\part{' + curr_theme + '}\n')
            if sections[0] == '':
                maintex.write('\n\n\\chapter{' + curr_theme + '}\n')
        # todo: fazer ele escrever o tema diferente. Tem que ter um primeiro chapter, senão não faz sentido.
        if curr_theme != themes[i]:  # todo: garantir ordenação da maneira que vem nos arquivos originais .txt
            curr_theme = themes[i]
            maintex.write('\n\n\\part{' + curr_theme + '}\n') # todo: ter a flexibilidade de modificar isso para ser
                                                              # part ou chapter, ou que seja

        if curr_section != sections[i]:
            curr_section = sections[i]
            maintex.write('\n\n\\chapter{' + curr_section + '}\n')

        if curr_subsection != subsections[i]:
            curr_subsection = subsections[i]
            maintex.write('\n\n\\section{' + curr_subsection + '}\n')

        #maintex.write('\n\\import{./}{{0}}.tex}\n'.format(post))
        maintex.write('\n\\import{./}{' + post + '.tex}\n')
        maintex.write('\\setcounter{footnote}{1}\n')

        subtex = open(os.path.join(dest_dir, post + '.tex'), 'w', encoding='utf8')

        selftext_path = os.path.join(relpaths[i], 'selftext.txt')
        selftext = open(selftext_path).read()

        sub = reddit.submission(url=urls[i])
        shortlink = sub.shortlink
        #write_header(usernames[i], selftext, titles[i], urls[i], subtex)
        write_header(usernames[i], selftext, titles[i], shortlink, subtex)

        #comm_contents = fetch_submission_comments(post_fullname=post, num_filters={'depth': '<8', 'length': '>1500'},
        #                                       items=['filepath', 'author', 'author_flair', 'depth'])
        comm_contents = fetch_submission_comments(post_fullname=post,
                                                  num_filters=num_comm_filters,
                                                  str_filters=str_comm_filters,
                                                  items=['filepath', 'author', 'author_flair', 'depth'])

        comm_paths = [i[0].replace('\\', r'/') for i in comm_contents]
        comm_authors = [i[1] for i in comm_contents]
        comm_flairs = [i[2] for i in comm_contents]
        comm_depths = [i[3] for i in comm_contents]

        for i, cpath in enumerate(comm_paths):
            body = open(cpath, 'r').read()
            write_body(body, comm_authors[i], comm_flairs[i], comm_depths[i], subtex)

        subtex.write('\n\n\\end{document}\n')
        subtex.close()
        # Create a .tex file of the post and write the preamble
        # Initialize the 'curr' variables
        # Write the appropriate section in the main tex file
        # Import the file into the main tex file and reset the footnote counter to 1
        # Fetch the database with that posts comments
        # Opt: Check if the comments have been processed before
        # Get the desired comments paths with specific rules
        # Get the comment .txt files from the filesystem
        # Clean up the comments
        # Opt: Save the cleaned up comments
        # Convert each comment into LaTeX
        # Clean up the LaTeX comments
        # Opt: Save the LaTeX comments
        # Write the comments into the post specific .tex file
        # Write \end{document} in the .tex file
        #

    #
    #

    maintex.write('\n\n')
    maintex.write(r'\end{document}')
    maintex.close()
    # Create a
    # for post in posts:
    #    select the desired comments, get the author, author flair, depth, id
    #    clean up the text files before conversion
    #    convert the text files
    #    clean up the conversion
    #