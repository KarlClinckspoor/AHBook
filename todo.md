---
author: Karl
---

# Workplan

Things to do:

* Write a preamble/introduction for the book

* Do some statistics about the users.
* Check well if the forbidden character escaping function is working correctly. Should change the symbols to:
    \* \$ \% \^{} \& \_ \{ \} \~{} \textbackslash
    -- Update. Change it to this, failed catastrophically. Recheck again, especially \textbackslash.


* \pagestyle{headings}
* Em book, usar \frontmatter, \mainmatter
* usar fancyheaders

Assembly:
* todo: adicionar uma opção para trocar imports por inputs, e aí muda o preambulo (fica nulo) e nao tem begin e end
* document.
* todo: Estudar direito se ele tá conseguindo pegar, de fato, os comentários na sequência desejada.
* Fazer isso utilizando um debug com uma função para retornar somente key. Aí, verifica se as keys estão em ordem
* numérica. Senão, fica tudo alterado.
* todo: Verificar se ele está conseguindo realmente checar até o root. Será que dá para fazer um diagrama? Vai ser um bom
* exercício.

Database
* todo: reajustar TODOS os posts, colocando uma coluna com o shortlink.
* todo: reajustar a função de criação de post, colocando o shortlink na criação.
* todo: renomear as colunas das postagens para algo um pouco mais padronizado. Pensar bem. Verificar se o SQLite permite
* alterar nome de colunas (provavelmente permite). todo: refazer então todas as funções em nomedas colunas certas.

Latex
* todo: verificar se há uma maneira de se checar a sintaxe LaTeX após juntar os arquivos e depois escrever num log
* o que aconteceu de errado.
* todo: verificar as funções de "ajuste" de LaTeX e etc. Talvez rodar algo para procurar em todos os arquivos
*       com uma expressão regular e aí ele tenta mostrar qual que é a melhor maneira.
* todo: verificar o \textbar, ele não está saindo direito nos arquivos
* todo: verificar o pacote bidi, mover ele pro lugar que ele insiste em ficar.
* todo: ficar mexendo no preamble para decidir a melhor fonte e tudo mais. Talvez algo mais amigável.
* todo: decidir, de vez, se vai estar no formato de book ou de article. Ajustar as funções de acordo.


Estatística:
* todo: verificar se SQLite tem um tipo de função MAX, aí ele retorna somente as postagens com o maior comprimento.
* todo: FAzer estatísticas com o comprimento de postagens e o número de votos. Terei que normalizar pelo número de votos
*       da postagem específica. (%?).
* todo: verificar melhor

Importância média:
Separar os AMAs das outras postagens


=======================O que deve constar no preamble=========================

		
Todos:
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

Para tirar o excesso no cabeçado de cada section, em books, colocar \renewcommand{\sectionmark}[1]{}



------------------
How to use the languages
Arabic, Hindi, sanskrit, greek, thai
\begin{Arabic}
\end{Arabic}
\begin{hindi}
\end{hindi}
\begin{sanskrit}
\end{sanskrit}
\begin{greek}
\end{greek}
\begin{thai}
\end{thai}

Chinese:
(nothing)

Japanese:
{\japanesefont ...}
Korean:
{\koreanfont ...}
----------------
Example:
\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{english}
\setotherlanguages{arabic,hindi,sanskrit,greek,thai} %% or other languages
\setmainfont[Ligatures=TeX]{Noto Serif}
\setsansfont[Ligatures=TeX]{Noto Sans}
\setmonofont{Noto Mono}
\newfontfamily\arabicfont[Script=Arabic]{Noto Naskh Arabic}
\newfontfamily\devanagarifont[Script=Devanagari]{Noto Serif Devanagari}
\newfontfamily\greekfont[Script=Greek]{GFS Artemisia}
\newfontfamily\thaifont[Script=Thai]{Noto Serif Thai}

\usepackage[space]{xeCJK}
\setCJKmainfont{Noto Sans CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans CJK SC}
\newCJKfontfamily\japanesefont{IPAexMincho}
\newCJKfontfamily\koreanfont{Baekmuk Batang}

-------------------------------



