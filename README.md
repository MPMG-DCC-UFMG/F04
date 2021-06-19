# F04
Identificação e caracterização de padrões associados a fraudes eleitorais em redes sociais online, WhatsApp e Telegram

## Configuração do ambiente
Versão Python: 3.5 ou superior

### Bibliotecas utilizadas
spacy (pip install spacy)

### Instalar modelo em português para lematizar as palavras
python -m spacy download pt_core_news_lg

## Instruções de uso

Execute <code>python identificacao_propaganda.py -t \<TEXTO\></code> para avaliar um texto único ou  <code>python identificacao_propaganda.py -c \<CAMINHO PARA O CORPUS\></code> para avaliar os textos de um corpus.




