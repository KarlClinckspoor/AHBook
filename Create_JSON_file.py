import json
import praw
import Authentication as Auth

reddit = Auth.CreateReddit()
fhand = open('wiki_antiquity_parsed.txt', 'r', encoding='utf-8')

links = []
keys = []
subsections = []
weird = []

for line in fhand:
    line = line.rstrip()
    if line.startswith('#'):
        subsections.append(line)
        continue
    if len(line.split(' ')) == 2:
        link, key = line.split(' ')  # Ugly
        links.append(link)
        keys.append(key)
        continue
    if len(line.split(' ')) != 2:
        weird.append(line)
        continue

filedict = {}
counter = 1
for link, key in zip(links, keys):
    sub = reddit.submission(url=link)
    tempdict = {'title':sub.title,
                'url': link,
                'keys': key,
                'main author': sub.comments[key].author.name,
                'authors': [sub.comments[k].author.name for k in key],
                'AMA?': ' AMA ' in sub.title,
                'Non-latin?': False,
                'Points': sub.score,
                # 'Subsection': subsection
                }  # length: only the number of top level comments.
    filedict['Submission ' + str(counter)] = tempdict
    counter += 1

fdest = open('wiki_antiquity_parsed.json', 'w', encoding='utf8')
json.dump(filedict, fdest)
fhand.close()
fdest.close()

import pprint
pp = pprint.PrettyPrinter().pprint
pp(filedict)

"""
	* Criar um script que cria um banco de dados utilizando todas as postagens, sem distinção (todas a nível 0), com
	  os seguintes dados.
	        Código da postagem:
	            Título
	            Seção (Africa, Antiquity, Modern, etc)
	            Autor (selecionar usando o primeiro, ou o mais longo, comentário)
	            Autores adicionais (dos outros comentários selecionados)
	            Limites
	            Tipo (AMA, Normal)
	            Contém Caracteres Diferentes? Chines, Japonês, Coreano, Árabe
	            Pontuação
	            Prefácio no Wiki (Para colocar as seções)
"""