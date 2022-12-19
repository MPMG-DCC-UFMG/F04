# MPMG - Extração de Backbone e Caracterização

A ferramenta de extração de backbone e caracterização é composta por três diferentes módulos, sendo eles: (i) recuperação de informação do banco de dados; (ii) extração de backbone e clusterização das comunidades; (iii) caracterização das comunidades encontradas. O fluoxgrama do módulo segue a seguinte lógica: primeiramente, os tuítes são recuperados do banco de dados do MPMG e salvos em um arquivo .csv intermediário. Após essa etapa, o módulo de extração de backbone é disparado, montando o grafo de co-retweets dos tweets recuperados, seguido pela extração do backbone Threshold-NB e, por fim, aplicando o algoritmo de Louvain para encontrar as comunidades em cada backbone. Por fim, o módulo de caracterização é chamado, a fim de extrair as informações mais relevantes de cada encontrada na última etapa do modulo (ii). 

As informações de parametrização de cada um dos módulos está descrita abaixo.

## Requisitos e pré-configurações
-------------------------------------------------
Primeiramente, é importante salientar que todos os módulos estão encapsulados num docker container, e para executar as ferramentas é necessário instalá-lo através do seguinte comando:
```
sudo docker build . -t f04_backbone
```

Considerando a complexidade de parametrizações e montagem de volumes para a execução dos módulos no Docker, foram criados três arquivos .sh que automatizam o processo de execução das aplicações, sendo necessário o usuário fornecer apenas poucos parâmetros em cada módulo. Dessa forma, antes de executar, é necessário conceder permissão de executável para todos os arquivos, que pode ser feito através do seguinte comando:

```
chmod +x *.sh
```

## Módulo I: Recuperando os Tweets do Banco de Dados
----------------------------------------------------

### Informações do banco de dados

O repositório acompanha, por padrão, um arquivo '.env' que conecta ao banco de dados do MPMG, que possui as seguintes configurações:
```shell
DB_USERNAME="f04"
DB_PASSWORD="example" 
DB_NAME="f04" 
DB_HOST="dbstore-gsi-des01.gsi.mpmg.mp.br:58200"
```
Entretanto, caso necessário, altere-o e insira as informações necessárias para conectar à aplicação no banco de dados. Caso essa alteração seja feita, é necessário executar o seguinte comando:

```shell
docker-compose up --build --force-recreate -d
```

Além disso, o módulo puxa as configurações referentes ao 'db_retrieval' no arquivo de configurações, que compreende as datas iniciais e finais e um campo que pode delimitar o número máximo de tweets que serão recuperados. Por padrão, o campo têm o campo 'null', o que indica que a aplicação recuperará todos os tweets cabíveis no intervalo fornecido. Contudo, o campo pode receber um número que limitará o retrieval de tweets.

Para executar esse módulo, basta modificar o arquivo de configuração, caso necessário, e executar o seguinte comando:

```shell
./db_retrieval.sh
```
Por padrão, o programa gerará um csv na pasta 'data/', contendo as informações dos tweets para ser utilizado no próximo módulo.

## Módulo II: Extração de Backbone
---------------------------------------------------
Para executar o módulo de extração do backbone, basta indicar o .csv que contém os tweets que serão utilizados para montar o grafo, extrair o backbone e encontrar as comunidades. Tendo em vista a complexidade de montar os volumes, passar os arquivos e executar a parametrização do código dentro do docker, foi montado um shell script que automatiza grande parte do processo. Por padrão, a saída estará na pasta /output/backbone_files/ a partir do diretório raiz, e é possível alterar parâmetros de configuração no arquivo /configuration/configuration.json. 

Assim, basta executar o shell script passando junto o caminho do arquivo de dados. Um exemplo de execução seria:

```shell
./backbone_extraction.sh data/Data_pre_processsed_Level_2.csv
```

Após a execução do código dentro do docker, na pasta '/output/backbone_files/' estarão os arquivos intermediários e finais que resultaram do processo. Tendo isso em vista, os principais arquivos gerados são: o .pkl que representa as comunidades extraídas, o MPMG_graph.edgelist representa o grafo montado e o Threshold_NB.edgelist representa o backbone extraído. Com essas saídas, é possível chamar o próximo módulo de Caracterização das comunidades


## Módulo III: Caracterização das Comunidades
---------------------------------------------------
Por fim, tendo achado as comunidades de usuários, podemos executar a última parte a fim de extrair as principais informações acerca de cada uma. Para isso, basta executar o shell 'community_classification' e passar dois argumentos: (I) o arquivo de tweets que foi utilizado para extrair as comunidades e (II) o .PKL das comunidades encontrado na etapa anterior. A ferramenta, por padrão, lê as informações do arquivo de configuração encontrado na pasta '/configuration/'. Caso se deseje alterar o local do arquivo, é necessário realizar as modificações indicadas no arquivo community_classification.sh. Entretanto, é aconselhável que se utilize a configuração padrçao.

Um exemplo de execução seria:

```
./community_classification.sh data/Data_pre_processsed_Level_2.csv /output/backbone_files/MPMG_communities.pkl
```

As saídas serão disponibilizadas, por padrão, na pasta '/output/community_output/', onde será gerada uma pasta por comunidade, que contém as principais hashtags, mentions, keywords, número de usuários, wordcloud, dentre outros.


### Datasets Disponibilizados:
------------------------------

Utilizar o git LFS para puxá-los.
Instalar o git LFS a partir do link: 

https://git-lfs.github.com/

Executar o comando: 

```
git lfs pull
```

