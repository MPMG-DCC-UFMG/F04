# Como executar o crawler de Tweets STANDALONE.

## Criação dos arquivos de Chaves do Twitter

Crie o diretório authentication (se não exisitir) e dentro dele crie um arquivo JSON chamado **Bearer_tokens.json** com o seguinte conteúdo:

```json
{ 

     "access_keys": [
         {
               "consumer_key": "CONSUMER_TOKEN_1",
               "consumer_secret": "CONSUMER_SECRET_1",
               "access_token": "ACCESS_TOKEN_1",
               "access_token_secret": "ACCESS_TOKEN_SECRET_1",
               "bearer_token": "BEARER_TOKEN_1"
          },
          {
               "consumer_key": "CONSUMER_TOKEN_2",
               "consumer_secret": "CONSUMER_SECRET_2",
               "access_token": "ACCESS_TOKEN_2",
               "access_token_secret": "ACCESS_TOKEN_SECRET_2",
               "bearer_token": "BEARER_TOKEN_2"
          }
     ]
}

```

Neste arquivo, é possível informar N Access Keys, pois caso alguma atinja o limite máximo de requisições, a próxima da lista será utilizada.

## Carregar arquivo com os IDS de Tweets para a coleta

- Crie o diretório chamado **data** (se não existir) na raiz da pasta crawler;

- Descompacte o arquivo *All_ids_current.csv.tar.gz* dentro do diretório **data**.

## Informações do banco de dados

Crie um arquivo *.env*  no diretório raiz do crawler e coloque o seguinte conteúdo.

```
DB_USERNAME=f04
DB_PASSWORD=example
DB_HOST=mongodb
DB_NAME=f04
```

Crie um arquivo docker-compose.yaml com o seguinte conteúdo.

```yaml
version: "3.3"
services:
  crawler:
    container_name: f04-crawler
    env_file:
      - ./.env
    build: .
    environment:
      TZ: America/Sao_Paulo
    volumes:
      - ./crawler:/code/
```

For fim, execute o seguinte comando no diretório raiz do crawler:

```shell
docker-compose up --build --force-recreate -d
```
