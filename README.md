# F04
Identificação e caracterização de padrões associados a fraudes eleitorais em redes sociais online, WhatsApp e Telegram

#### Configuração do ambiente
Versão Python: 3.5 ou superior

```
### Instalar biblioteca spacy para lematização
$ pip install spacy

### Instalar modelo em português para lematizar as palavras
$ python -m spacy download pt_core_news_lg
```

#### Método probabilístico de identificação de propaganda eleitoral antecipada

- calcula score para **textos únicos, arquivos json, lista de json e arquivos de texto simples** e imprime resultado,

- permite a filtragem de documentos entre determinado **período de tempo** para fazer a análise de propaganda antecipada,

- oferece parametrização do algoritmo pelos arquivos **blacklist.txt, palavras_reforco.json e pesos_palavras.json**

```
identificacao_propaganda.py [--texto <TEXTO>] 
                            [--lista <LISTA ENTRE ASPAS>] 
                            [-txt] [--corpus <CAMINHO CORPUS>]
                            [--atributo-texto <NOME ATRIBUTO>] [--atributo-data <NOME ATRIBUTO>] 
                            [--data-min <YYYY-MM-DD>] [--data-max  <YYYY-MM-DD>]
                            [--blacklist-texto <TERMOS BLACKLIST>] [--blacklist-arquivo <CAMINHO ARQUIVO>] 
                            [-explicacao]
```

#### Como identificar progaganda em um texto único
```
identificacao_propaganda.py --texto <TEXTO>
```

#### Como identificar progaganda em um corpus JSON
```
identificacao_propaganda.py --atributo-texto <NOME ATRIBUTO> --atributo-data <NOME ATRIBUTO> --data-min <YYYY-MM-DD> --data-max <YYYY-MM-DD> --corpus <CAMINHO CORPUS>
```

O método requer que o corpus tenha um documento no formato JSON por linha 

#### Como identificar progaganda em uma lista de JSON
```
identificacao_propaganda.py --atributo-texto <NOME ATRIBUTO> --atributo-data <NOME ATRIBUTO> --data-min <YYYY-MM-DD> --data-max <YYYY-MM-DD> --lista <LISTA ENTRE ASPAS>
```

A lista de json deve ser uma lista de dicionários convertida para o formato string. Ou seja, o valor precisa estar entre aspas.

#### Como identificar progaganda em um corpus de texto simples
```
identificacao_propaganda.py -txt --corpus <CAMINHO CORPUS>
```

O método requer que o corpus tenha um texto por linha e que a filtragem por datas tenha sido feita previamente. 

#### Como informar termos adicionais para a blacklist
```
### Passar lista de termos separa por vírgulas e sem espaços
identificacao_propaganda.py --blacklist-texto <TERMOS BLACKLIST> [...]

### Passar caminho do arquivo que contem os termos. Um termo por linha.
identificacao_propaganda.py --blacklist-arquivo <CAMINHO ARQUIVO> [...]
```

#### Para mostrar a explicação dos scores do método 
```
identificacao_propaganda.py -explicacao [...]
```