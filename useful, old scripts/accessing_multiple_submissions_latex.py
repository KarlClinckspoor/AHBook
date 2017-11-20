import Parsing_submission_latex as Parse
import Authentication as Auth
import os
import time

reddit = Auth.CreateReddit()

current_dir = os.getcwd()
submission_links_location = os.path.join(current_dir,'Posts\\links')

list_of_files = list()
for files in os.listdir(submission_links_location):
    list_of_files.append(files) #wiki_africa_parsed, etc

#temp_count = 0
for item in list_of_files:
    print('Parsing file: ',item,end='\n')

    links_filepath = os.path.join(submission_links_location,item)
    destination_dir = os.path.join(current_dir,('Posts\\'+item[:-4]))
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    fhand_to_parse = open(links_filepath,'r', encoding='utf-8')

    for link in fhand_to_parse:
        submission=reddit.submission(url=link)
        sub_id = submission.id_from_url(link) #teste para ver se isso muda em outro caso
        Parse.Parse_submission(submission,destination_dir,sub_id)
        time.sleep(1)

    #Verificar se acessar algo com um contexto específico ou a submissão inteira são diferentes.

        '''
        temp_count+=1
        if temp_count>=1:
            print('Breaking temporarily')
            quit()
        '''
