# F04
Identificação e caracterização de padrões associados a fraudes eleitorais em redes sociais online, WhatsApp e Telegram

#### Configuração do ambiente
Python: 3.5 ou superior

```
### Instalar biblioteca numpy para cálculo dos scores
$ pip install numpy

### Instalar biblioteca spacy para lematização
$ pip install spacy

### Instalar modelo em português para lematizar as palavras
$ python -m spacy download pt_core_news_lg
```

#### Método probabilístico de identificação de propaganda eleitoral antecipada

- calcula score para **textos únicos, arquivos json, lista de json e arquivos de texto simples**,

- permite a filtragem de documentos entre determinado **período de tempo** para fazer a análise de propaganda antecipada,

- oferece parametrização do algoritmo pelos arquivos **blacklist.txt, palavras_reforco.json e pesos_palavras.json**

```
identificacao.py  [--texto <TEXTO>] 
                  [--lista <LISTA JSON (DUMP)>] 
                  [-txt][-json]
                  [--arquivo <CAMINHO ARQUIVO>]
                  [--atributo-texto <NOME ATRIBUTO>]
                  [--atributo-data <NOME ATRIBUTO>] 
                  [--data-inicial <DD-MM-YYYY>] 
                  [--data-final <DD-MM-YYYY>]
                  [--blacklist-texto <TERMOS BLACKLIST>] 
                  [--blacklist-arquivo <CAMINHO ARQUIVO>] 
                  [-explicacao]

```

#### Como identificar progaganda em um texto único
```
identificacao.py --texto <TEXTO>
```

#### Como identificar progaganda em um arquivo JSON
```
identificacao.py --atributo-texto <NOME ATRIBUTO> --atributo-data <NOME ATRIBUTO> --data-inicial <DD-MM-YYYY> --data-final <DD-MM-YYYY> --arquivo <CAMINHO ARQUIVO>
```

O método requer que o arquivo tenha um documento no formato JSON por linha 

#### Como identificar progaganda em uma lista de JSON
```
identificacao.py --atributo-texto <NOME ATRIBUTO> --atributo-data <NOME ATRIBUTO> --data-inicial <DD-MM-YYYY> --data-final <DD-MM-YYYY> --lista <LISTA JSON NO FORMATO TEXTO>
```

A lista de json deve ser uma lista de dicionários convertida para o formato string. Ou seja, o valor precisa estar entre aspas.

#### Como identificar progaganda em um arquivo de texto simples
```
identificacao.py -txt --arquivo <CAMINHO ARQUIVO>
```

O método requer que o arquivo tenha um texto por linha e que a filtragem por datas tenha sido feita previamente. 

#### Como informar termos adicionais para a blacklist
```
### Passar lista de termos separa por vírgulas e sem espaços
identificacao.py --blacklist-texto <TERMOS BLACKLIST> [...]

### Passar caminho do arquivo que contem os termos. Um termo por linha.
identificacao.py --blacklist-arquivo <CAMINHO ARQUIVO> [...]
```

#### Para mostrar a explicação dos scores do método 
```
identificacao.py -explicacao [...]
```
