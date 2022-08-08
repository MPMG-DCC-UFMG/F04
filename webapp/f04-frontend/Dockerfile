# Imagem de Origem
FROM node:16-alpine
# Diretório de trabalho(é onde a aplicação ficará dentro do container).
WORKDIR /app
# Adicionando `/app/node_modules/.bin` para o $PATH
ENV PATH /app/node_modules/.bin:$PATH
# Instalando dependências da aplicação e armazenando em cache.
COPY package.json /app/package.json

RUN npm install -g npm@8.6.0
RUN npm config set legacy-peer-deps true
RUN npm install 
RUN chown -R node /app/node_modules
RUN npm install react-scripts@4.0.3 -g --silent
EXPOSE 3000
# Inicializa a aplicação
CMD ["npm", "start"]