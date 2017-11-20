# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 19:59:09 2017

@author: Karl
"""
#r'[^]',('['+r'\\'+']')
'''
forbid_char = ['&','%','$','#','_','{','}','~','^',r'\\\\']
forbid_char2 = ['[&]','[%]','[$]','[#]','[_]','[{]','[}]','[~]']

string = 'voracious&llama'
string = 'voracious%llama'
string = 'voracious$llama'
string = 'voracious#llama'
string = 'voracious_llama'
string = 'voracious{llama'
string = 'voracious}llama'
string = 'voracious~llama'
'''
'''
string = 'quente'
for item in forbid_char2:
    print('checking',item,':',end='\n')
    string = re.sub(item,(r'\\'+item[1]),string)
    print(string)
'''
#%%
import re

string='asdlajsdljasldkjlaksjdlkajsdlkjaslkdj\n\nasdlkçaçsldkçalksdçlaksdçlkasdçlaksdasd[the following inscription](http://en.wikipedia.org/wiki/Anthropodermic_bibliopegy#History)asdlkajsdlkjaslkdjalksd\nalsdçlaksdçlkasdçlk\naslçdkaçlskdçlaskd'
string2='asdlajsdljasldkjlaksjdlkajsdlkjaslkdj\n\nasdlkçaçsldkçalksdçlaksdçlkasdçlaksdasd(the following inscription)[http://en.wikipedia.org/wiki/Anthropodermic_bibliopegy#History]asdlkajsdlkjaslkdjalksd\nalsdçlaksdçlkasdçlk\naslçdkaçlskdçlaskd'

url = re.findall('\[.+\]\((.+)\)',string)
text = re.findall('\[(.+)\]\(.+\)',string)
#url2, text2 = re.findall('\[(.+)\)]\((.+)\)',string)

replacement = '\\href{'+url[0]+'}{'+text[0]+'}'
replacement2 = '\\href{%s}{%s}' % (url[0], text[0])
#não ideal, acha só a primeira instância, fazer um loop para pegar todas as instâncias

reworked = re.sub('\[.+\]\(.+\)',replacement,string)
#%% Não está dando certo... continuar depois
forbid_char = r'&%$#_{}~^\\'
string3 = 'vor_ac{iou_s}$lla%ma'
pattern = '['+forbid_char+']'

chars = re.findall(pattern,string3)
newstring3 = string3[:]

for char in chars:
    escaped = r'\\' + char
    newpattern = '['+char+']'
    newstring3 = re.sub(newpattern,escaped,string3,count=1)

print(count)
print(string3)
print(newstring3)
