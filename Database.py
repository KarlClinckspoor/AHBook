# encoding=utf8

import sqlite3
import Authentication
import regex as re
import os
import prettyprinter as pp
import glob
import sys
import time
import logging

# todo: add logging to all the functions

# Creating a log file and a logger
logging.basicConfig(filename='log', level='DEBUG', style='{')
logger = logging.getLogger('database')

class Database:

    sleep_time = 1  # seconds to wait between requests to the server

    def __init__(self, dbase='database.sqlite', print_after_fetching=True, verbose=True):
        """Connects to the database file. If not exists, creates one."""
        self.conn = sqlite3.connect(dbase)
        self.c = self.conn.cursor()
        logger.debug('Successfully connected to the database')

        self.print_after_fetching = print_after_fetching
        self.verbose = verbose

    def close(self):
        """Closes the connections. If changes are not commited, they will be lost!"""
        self.c.close()
        self.conn.close()

    def commit(self):
        """Commits the changes to the database"""
        self.conn.commit()

    ####################################################################################################################
    # Getting info from tables
    ####################################################################################################################

    def fetch_print(self):
        """Fetches the results of the last query and returns them"""
        content = self.c.fetchall()
        if self.print_after_fetching:
            pp.pprint(content)
        return content

    def describe_table(self, table):
        """Shows the headers of a table"""
        self.c.execute(rf'PRAGMA table_info({table})')
        return self.fetch_print()
        # Instead of always getting the cursor contents and printing/returning them, this function is called to reduce
        # writing the same code often

    def show_all_tables(self):
        """Shows all the table names from the database"""
        self.c.execute(r'SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
        return self.fetch_print()

    def show_all_items_on_table(self, table):
        self.c.execute(rf'SELECT * FROM {table}')
        return self.fetch_print()

    def get_unique_themes(self):
        self.c.execute('SELECT DISTINCT theme FROM posts')
        themes = [i[0] for i in self.c.fetchall()]
        return themes

    def get_unique_subreddits(self):
        self.c.execute('SELECT DISTINCT subreddit FROM posts')
        subreddits = [i[0] for i in self.c.fetchall()]
        return subreddits

    def get_post_items(self, requirements, items):
        """Searches through the database for the entries that satisfy requirements and returns the items desired.
        Example:
            get_database_posts({'subreddit':'AskHistorians', 'theme':'antiquity'}, items=['url'])
            Fetches all the posts of the subreddit 'Askhistorians' that have been tagged with the 'antiquity' theme, and
            returns their url.

        Available fields:
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id TEXT,
        post_fullname TEXT,
        post_title TEXT,
        url TEXT,
        subreddit TEXT,
        theme TEXT,
        section TEXT,
        subsection TEXT,
        username TEXT,
        author_flair TEXT,
        comment_folder TEXT,
        rel_comment_folder TEXT
        selftext_path TEXT,
        """
        selects = ','.join(items)
        wheres = ' AND '.join([f"{key}={val}" for key, val in zip(requirements.keys(), requirements.values())])
        statement = f'SELECT {selects} FROM posts WHERE {wheres}'
        logger.debug(statement)
        if self.verbose:
            print(statement)
        self.c.execute(statement)
        return self.fetch_print()

    # todo: get be
    def get_submission_comments(self, post_fullname, items, numerical_filters=None, str_filters=None, fill_list=True,
                                orderby='key'):
        """Fetches information in items of the selected post matching the set of numerical and string filters, which
        must be dictionaries.

        fill_list selects, in addition to the filtered comments, every single comment from that point down to the root,
        in order to create a narrative.

        orderby sorts the results according to what you requested. Often, ordered by 'key', the numerical identifier
        of the comment in that specific tree, starting at 1 for the topmost, best comment, and going up for each child.

        Example:
            get_submission_comments('t3_11l66t', ['filepath'], numerical_filters={'depth':'<=10'}): gets only the field
                'filepath' of the comments with a depth less than or equal to 10 from the post t3_11l66t
            get_submission_comments('t3_17r7u6', ['*'], numerical_filters={'depth':'<=10', 'length':'>=500'}):
                gets all the fields of the submission t3_17r7u6 that have a depth of less than 10 but with more
                than 500 characters in their comment body.

        Available fields to fetch:
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key INTEGER,
        score INTEGER,
        parent_id TEXT,
        name TEXT,
        fullname TEXT,
        depth INTEGER,
        length INTEGER,
        author TEXT,
        author_flair TEXT,
        filepath TEXT
        """

        selects = ','.join(items)

        if not numerical_filters and not str_filters:
            statement = rf'SELECT {selects} FROM {post_fullname}'
            fill_list = False  # Will select everything after all
        else:
            if numerical_filters:
                numerical_wheres = ' AND '.join([f'{key}{val}' for key, val in numerical_filters.values()])
            if str_filters:
                str_wheres = ' AND '.join([f"{key}='{val}'" for key, val in str_filters.values()])
            if numerical_filters and str_filters:
                wheres = numerical_wheres + ' AND ' + str_wheres
            elif numerical_wheres:
                wheres = numerical_wheres
            elif str_filters:
                wheres = str_wheres

            statement = f'SELECT {selects} FROM {post_fullname} WHERE {wheres}'

        if orderby:
            statement += f' ORDER BY {orderby}'

        self.c.execute(statement)
        comments = self.c.fetchall()

        if fill_list:
            # Finding root
            self.c.execute(f'SELECT DISTINCT parent_id FROM {post_fullname} WHERE depth=0')
            root = self.c.fetchall[0][0]
            # Finding the keys of the posts selected
            self.c.execute(f'SELECT key FROM {post_fullname} WHERE {wheres}')
            selected_keys = [x[0] for x in self.c.fetchall()]

            filler_keys = []
            for key in selected_keys:
                self.get_to_root(root, key, post_fullname)

            all_keys = selected_keys + filler_keys
            all_keys = list(set(all_keys))
            all_keys.sort()  # Places them in order they appear in the post

            comments_with_fillers = []

            for key in all_keys:
                self.c.execute(rf'SELECT {selects} FROM {post_fullname} WHERE key={key}')
                comments_with_fillers.append(self.c.fetchall()[0])  # todo: figure out exactly with [0] is needed

            # comments += filler_comments  # todo: check if it is necessary to do this, seeing as all keys have been
            # iterated through

            comments = list(set(comments_with_fillers))
        return comments

    ####################################################################################################################
    # Table deletion
    ####################################################################################################################
    def _delete_posts_table(self):
        """Used when debugging to check if the posts table is correctly populated"""
        self.c.execute(r'DROP TABLE posts')

    def _delete_all_submissions(self):
        """Deletes all the submission tables"""
        self.c.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
        tables = self.c.fetchall()
        tables = [i[0] for i in tables][2:]  # remove posts and sqlite_sequence
        print(tables)
        for table in tables:
            self.c.execute('DROP TABLE {0}'.format(table))

    def _recreate_posts_table(self):
        self._delete_posts_table()
        self.create_posts_table()

    ####################################################################################################################
    # Table creation
    ####################################################################################################################

    def create_posts_table(self):
        """The posts table contains information about the differents posts/submissions present in the database.
        It is the primary table, which contains information about everything else."""
        self.c.execute(r'''CREATE TABLE IF NOT EXISTS posts 
            (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            post_id TEXT, 
            post_fullname TEXT,
            post_title TEXT,
            url TEXT, 
            subreddit TEXT,
            theme TEXT,
            section TEXT,
            subsection TEXT,
            username TEXT,
            author_flair TEXT,
            comment_folder TEXT,
            rel_comment_folder TEXT
            selftext_path TEXT,
            );''')

    def create_submission_table(self, submission):
        """Adds a table to the database with the information from a submission, such as author, flair, and the selftext
        content (as a path to a local txt file)"""
        self.c.execute(rf"""CREATE TABLE IF NOT EXISTS {submission} 
                (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key INTEGER,
                score INTEGER,
                parent_id TEXT,
                name TEXT,
                fullname TEXT,
                depth INTEGER,
                length INTEGER,
                author TEXT,
                author_flair TEXT,
                filepath TEXT
                );""")

    ####################################################################################################################
    # Table filling
    ####################################################################################################################

    def populate_posts_table(self, reddit, filename='wiki*.txt'):
        """From a filename (or generic filename with wildcards), gets the submission links from the file and then
        adds the submissions to the posts table of the database. Requires a praw reddit object."""
        re_subreddit_finder = re.compile(r'\/r\/(\w+)\/')  # To find the subreddit name
        files = glob.glob(filename)

        # Gets the posts already parsed so no duplicates are present
        parsed_posts = [i[0] for i in self.c.fetchall()]

        for file in files:
            section = ''  # Necessary in case these values are not found during normal parsing
            subsection = ''
            theme = file.split('_')[1]
            with open(file, 'r', encoding='utf8') as fhand:
                for line in fhand:
                    if len(line) <= 2:  # No content
                        continue
                    elif line.startswith('###') and not line.startswith('####'):  # Found a section
                        section = line.replace('#', '').strip()
                        subsection = ''  # Resets the subsection
                        continue
                    elif line.startswith('####'):  # Found a subsection
                        subsection = line.replace('#', '').strip()

                    if self.verbose:
                        print(f'Processing line: {line}', end='')

                    post = reddit.submission(url=line.strip())
                    if post.fullname in parsed_posts:
                        if self.verbose:
                            print(' --- Already Parsed. Skipping')
                        continue

                    self.create_post_dir(post)

                    # Gathering post information to add to the table
                    post_id = post.id
                    post_fullname = post.fullname
                    url = line.strip()
                    subreddit = re_subreddit_finder.findall(line)[0]
                    comment_folder = os.path.relpath(os.path.join(os.getcwd(), 'comments', post_fullname))
                    rel_comment_path = os.path.relpath(comment_folder)
                    try:
                        author = post.author.name
                    except AttributeError:
                        author='[deleted]'  # todo: log
                    try:
                        author_flair = post.author_flair_text
                    except AttributeError:
                        author_flair = ''
                    title = post.title
                    selftext_path = os.path.join(os.getcwd(), 'comments', post_fullname, 'selftext.txt')
                    self.write_selftext(post, selftext_path)  # Saves the selftext as markdown

                    # Get information into a list to insert it into the database
                    items = [(post_id, post_fullname, title, url, subreddit, theme, section, subsection, author,
                              author_flair, comment_folder, rel_comment_path, selftext_path)]

                    self.c.executemany(
                        r"""INSERT INTO posts (post_id, post_fullname, post_title, url, subreddit, theme, section,
                        subsection, username, author_flair, comment_folder, rel_comment_folder) VALUES
                        (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        items
                    )
            time.sleep(self.sleep_time)  # After parsing a file, wait in order to not overstay my welcome in the server

    def populate_submission_table(self, submission):
        """Receives a praw submission/post instance then creates and populates a table with data from the submission"""
        # global key
        # global key_attributions
        self.create_submission_table(submission)
        submission.comments.replace_more(limit=0)  # Ignores comments that are too deep

        # Every comment in a submission will receive a key. These keys are, in a way, legacy code, but they also work
        # to identify the comments starting from 1 with the first best comment, then its first best reply, and so on.
        # The key attributions correlates comment ids to keys, making conversion between the two trivial
        # These are declared here because the attribute_keys function is recursive
        key_attributions = self._attribute_keys(submission.comments)  # Fills in key attributions

        comments = submission.comments.list()
        fullname = submission.fullname

        for comment in comments:
            # Creating the data to go into the table
            # Creates file at the correct path using the comment id as its name
            relpath = os.path.relpath(os.path.join(os.getcwd(), 'comments', fullname, comment.id + '.txt'))
            try:
                authorname = comment.author.name
            except AttributeError:
                authorname = '[deleted]'  # todo: check if an empty string would be better
            try:
                authorflair = comment.author_flair_text
            except AttributeError:
                authorflair = ''
            score = comment.score
            parent_id = comment.parent_id
            name = comment.name
            _id = comment.id
            depth = comment.depth
            size = len(comment.body)

            items = [(key_attributions[comment.id], score, parent_id, name, _id, depth, size, authorname, authorflair,
                      relpath)]

            self.c.executemany(
                rf"""INSET INTO {fullname} 
                (key, score, parent_id, name, fullname, depth, length, author, author_flair, filepath)""", items
            )

            self.extract_save_comment_contents(relpath, comment)

    def create_submission_tables_from_db(self, reddit):
        """Goes through all the submissions and checks if they have already been added to the database. If not, adds them"""
        self.c.execute('SELECT DISTINCT theme FROM posts')
        themes = [i[0] for i in self.c.fetchall()]
        urllist = []

        for theme in themes:  # todo: how relevant is this?
            self.c.execute(rf'SELECT url FROM posts WHERE theme="{theme}"')
            urllist.extend([i[0].rstrip() for i in self.c.fetchall()])

        self.c.execute(r'SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
        parsed_submissions = [i[0] for i in self.c.fetchall()] # selects irrelevant tables, but doesn't matter

        for url in urllist:
            if self.verbose:
                print(f'Parsing {url}', end='')
                submission = reddit.submission(url=url)

                if not submission.fullname in parsed_submissions:
                    self.populate_submission_table(submission)
                    if self.verbose:
                        print(' --- Done.')
                else:
                    if self.verbose:
                        print(' --- Already added.')
        time.sleep(self.sleep_time)

    ####################################################################################################################
    # File manipulation
    ####################################################################################################################
    # todo: check these functions
    def write_selftext(self, post, path):
        with open(path, 'w', encoding='utf8') as fhand:
            fhand.write(post.selftext)
        return

    def create_post_dir(self, post):
        path = os.path.join(os.getcwd(), 'comments', post.fullname)
        # print('Path: ', path)
        if not os.path.isdir(path):
            os.mkdir(path)
        elif self.verbose:
            print('Path already exists:', path)

    def extract_save_comment_contents(self, path, comment):
        with open(path, 'w', encoding='utf8') as fhand:
            fhand.write(comment.body)
        return

    ####################################################################################################################
    # Walking through submission comment tree
    ####################################################################################################################

    # todo: test this to check if it has the same behavior as the other function
    @staticmethod
    def _attribute_keys(comments):
        key = 0
        key_attributions = {}

        def recursive(comments):
            nonlocal key
            nonlocal key_attributions

            if comments == []:  # No child comments
                return
            key += 1
            for comment in comments:
                key_attributions[comment.id] = key
                recursive(comment.replies)

        for comment in comments:
            recursive(comment)

        return key_attributions

    # todo: test this function and compare it with the other
    def _get_to_root(self, root, key, post):
        """Starts from any comment with depth>= 0 and selects all its parent comments until it reaches root"""
        filler_keys = []

        def recursive(root, parent_key):
            self.c.execute(rf'SELECT parent_id FROM {post} WHERE key={parent_key}')
            parent_id = self.c.fetchall()[0][0]
            parent_key = self._get_key_from_name(parent_id, post)  # Finds new parent

            nonlocal filler_keys

            if parent_id == root:
                if self.verbose:
                    print(f'Terminou, parent={parent_id}, root={root}')
                return
            elif parent_id != root:
                filler_keys.append(parent_key)
                recursive(root, parent_key)

        recursive(root, key)
        return filler_keys

    def _get_key_from_name(self, name, post):
        """Gets the field 'key' for a specific comment"""
        self.c.execute(f'SELECT key FROM {post} WHERE name="{name}"')
        response = self.c.fetchall()
        if response:
            return response[0][0]
        else:
            return response

############# POPULATE TABLE FUNCTIONS ##################
# def populate_posts_table(c, reddit):
#     subreddit_finder = re.compile(r'/r/(\w+)/')
#     files = glob.glob('wiki*.txt')
#     c.execute('SELECT post_fullname FROM posts')
#     parsed_posts = c.fetchall()
#     parsed_posts = [i[0] for i in parsed_posts]
#     for file in files:
#         section = ''
#         subsection = ''
#         theme = file.split('_')[1]
#         with open(file, 'r', encoding='utf8') as fhand:
#             for line in fhand:
#                 if len(line) <= 2:
#                     continue
#                 if line.startswith('###') and not line.startswith('####'):
#                     section = line.replace('#', '').rstrip().lstrip()
#                     subsection = ''  # resets subsection
#                     continue
#                 elif line.startswith('####'):
#                     subsection = line.replace('#', '').rstrip().lstrip()
#                     continue
#
#                 print('Processing {0}'.format(line), end='')
#                 sub = reddit.submission(url=line.rstrip())
#
#                 if sub.fullname in parsed_posts:
#                     print(' --- Already Parsed. Skipping')
#                     continue
#
#                 create_submission_dir(sub)
#
#                 sub_id = sub.id
#                 post_fullname = sub.fullname
#                 url = line.rstrip()
#                 subreddit = subreddit_finder.findall(line)[0]
#                 #theme = theme
#                 comment_folder = os.path.relpath(os.path.join(os.getcwd(), 'comments', sub.fullname))
#                 rel_comment_path = os.path.relpath(comment_folder)
#
#                 try:
#                     author = sub.author.name
#                 except AttributeError:
#                     author='[deleted]'
#
#                 try:
#                     author_flair = sub.author_flair_text
#                 except AttributeError:
#                     author_flair = ''
#
#                 title = sub.title
#                 selftext_path = os.path.join(os.getcwd(), 'comments', sub.fullname, 'selftext.txt')
#                 write_selftext(sub, selftext_path)
#
#                 items = [(sub_id, post_fullname, url, subreddit, theme, section, subsection, comment_folder,
#                           author, title, selftext_path, author_flair, rel_comment_path)]
#                 c.executemany(
#                     r'INSERT INTO posts (post_id, post_fullname, url, subreddit, theme, section, subsection,'
#                     r'comment_folder, poster_username, post_title, selftext_path, '
#                     r'author_flair, rel_comment_folder) '
#                     r'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
#                     items)
#         time.sleep(1)
#
#
# def populate_submission_table(c, sub):
#     global key
#     global key_attributions
#
#     create_submission_table(c, sub)
#
#     sub.comments.replace_more(limit=0)
#     key = 0
#     key_attributions = {}
#     attribute_keys(sub.comments)
#     comments = sub.comments.list()
#     fullname = sub.fullname
#
#     #print(key_attributions)
#
#     for comment in comments:
#         path = os.path.relpath(os.path.join(os.getcwd(), 'comments', sub.fullname, comment.id + '.txt'))
#         items = [(key_attributions[comment.id], *extract_comment_information(comment), path)]
#         # = (key, score, parent_id, name, id, depth, length, author_name, author_flair_text)
#         insert_comment(c, items, fullname)  # inserts comment data into db
#         extract_save_comment_contents(path, comment)  # saves .txt files
#
#
#
# # long example post: t3_17r7u6
# def fetch_submission_comments(post_fullname='t3_11l66t', num_filters= {'depth': '<=10'}, items=['filepath'],
#                               str_filters={}, fill_list=True, orderby='key'):
#     """Fetches select information about the comments from a submission that match the set of filters provided.
#
#     * fill_list selects, in addition to the comments selected by the filters, every single comment starting
#     from each specific comment and going to root. That is, it creates an understandable "narrative" of comments.
#
#     * orderby adds a parameter to the sqlite query to sort the results according to something.
#
#     Table name: post_fullname
#
#       'id INTEGER PRIMARY KEY AUTOINCREMENT,'
#       'key INTEGER,'
#       'score INTEGER,'
#       'parent_id TEXT,'
#       'name TEXT,'
#       'fullname TEXT,'
#       'depth INTEGER,'
#       'length INTEGER,'
#       'author TEXT,'
#       'author_flair TEXT,'
#       'filepath TEXT);'.format(sub.fullname))
#
#     """
#     conn, c = connect_to_database()
#
#     selects = ','.join(items)
#
#     if selects == '':
#         selects = '*'
#
#     if num_filters == {} and str_filters == {}:  # todo: adicionar str_filters nessa comparação.
#         statement = 'SELECT {0} FROM {1}'.format(selects, post_fullname)
#         fill_list = False
#     else:
#         #wheres = ' AND '.join(["{0}='{1}'".format(fil_key, fil_val) for fil_key, fil_val
#         #               in zip(str_filters.keys(), str_filters.values())])
#
#         if num_filters != {}:
#             num_wheres = ' AND '.join(["{0}{1}".format(fil_key, fil_val) for fil_key, fil_val in
#                                zip(num_filters.keys(), num_filters.values())])
#         if str_filters != {}:
#             str_wheres = ' AND '.join(["{0}='{1}'".format(fil_key, fil_val) for fil_key, fil_val in
#                                    zip(str_filters.keys(), str_filters.values())])
#
#         if num_filters != {} and str_filters != {}:
#             wheres = num_wheres + ' AND ' + str_wheres
#         elif num_filters != {}:
#             wheres = num_wheres
#         elif str_filters != {}:
#             wheres = str_wheres
#
#         statement = 'SELECT {0} FROM {1} WHERE {2}'.format(selects, post_fullname, wheres)
#
#     if orderby:
#         statement = statement + ' ORDER BY {0}'.format(orderby)
#
#     c.execute(statement)
#     comments = c.fetchall()
#     #comments = [i[0] for i in c.fetchall()]
#
#     if fill_list:
#         # Finding root
#         c.execute('SELECT DISTINCT parent_id FROM {0} WHERE depth = 0'.format(post_fullname))
#         root = c.fetchall()[0][0]
#         # Finding the keys of the posts selected
#         c.execute('SELECT key FROM {0} WHERE {1}'.format(post_fullname, wheres))
#         good_keys = [x[0] for x in c.fetchall()]
#
#         global filler_keys
#         filler_keys = []
#
#         for key in good_keys:
#             get_to_root(root, key, post_fullname, c)
#
#         all_keys = good_keys + filler_keys
#         all_keys = list(set(all_keys))
#         all_keys.sort()
#
#         filler_comments = []
#
#         for key in all_keys:
#             c.execute('SELECT {0} FROM {1} WHERE key={2}'.format(selects, post_fullname, key))
#             #filler_comments.append(c.fetchall()[0][0])
#             filler_comments.append(c.fetchall()[0])  # todo: figure out exactly with [0] is needed
#
#         comments = comments + filler_comments
#         comments = list(set(comments))
#
#     conn.close()
#     return comments
#
#
# def get_to_root(root, key, post, c):
#     """Starts from any comment whose depth >= 0 and selects all its parent comments until it reaches root."""
#     c.execute('SELECT parent_id FROM {0} WHERE key={1}'.format(post, key))
#     response = c.fetchall()
#     parent_id = response[0][0]
#     parent_key = get_key_from_name(parent_id, post, c)
#
#     global filler_keys
#
#     if parent_id == root:
#         #print('Terminou, parent=', parent_id, 'root', root)
#         return
#     elif parent_id != root:
#         filler_keys.append(parent_key)
#         get_to_root(root, parent_key, post, c)
#
#
# def get_key_from_name(name, post, c):
#     """Using a database cursor c, gets the field "key" for a specific comment."""
#     c.execute('SELECT key FROM {0} WHERE name="{1}"'.format(post, name))
#     response = c.fetchall()
#     if response == []:
#         return response
#     else:
#         return response[0][0]
#
# # reddit = Authentication.CreateReddit()
