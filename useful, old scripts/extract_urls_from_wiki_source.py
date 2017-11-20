import re
import os

currentdir = os.getcwd()
to_parsedir = os.path.join(currentdir,'Wiki\\to_parse')
destination_dir = os.path.join(currentdir,('Posts\\links')) #+ nome do arquivo, tipo wwii, etc
list_of_files = list()
for files in os.listdir(to_parsedir):
    if files.endswith(".txt"):
        list_of_files.append(files)

#tempcount = 0

for item in list_of_files:
    item=item.rstrip()
    if len(item)==0:
        continue
    print('Parsing...',item,end='')

    to_parse_file_path = os.path.join(to_parsedir,item)
    f_to_parse = open(to_parse_file_path,'r', encoding='utf-8')

    try:
        destination_file_path = os.path.join(destination_dir,(item[:-4]+'_parsed.txt'))
        f_destination = open(destination_file_path,'w', encoding='utf-8')
    except EnvironmentError:
        print('File already exists or', EnvironmentError)
    wholefile = f_to_parse.read()
    allmatches = re.findall('(http\S*comments\S*)[)]',wholefile)
    for match in allmatches:
        match = match + '\n'
        f_destination.write(match)

    print('...done')
    f_to_parse.close()
    f_destination.close()
    '''
    tempcount += 1
    if tempcount >= 3:
        print('Quitting temporarily')
        break
    '''
