from utils.helpers import gen_data
import gensim
print("Passei 1 em metodo_aprendizado_maquina", flush=True)
from sklearn.feature_extraction.text import HashingVectorizer
print("Passei 2 em metodo_aprendizado_maquina", flush=True)
import joblib
print("Passei 3 em metodo_aprendizado_maquina", flush=True)
from utils.text_processor import TextProcessor
print("Passei 4 em metodo_aprendizado_maquina", flush=True)
from utils.political_classification import PoliticalClassification
print("Passei 5 em metodo_aprendizado_maquina", flush=True)
import os, sys
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
EMBEDDING_DIM = 300

print("Terminei de importar metodo_aprendizado_maquina", flush=True)

class MetodoAprendizadoMaquina:
    def __init__(self, nome_modelo, caminho_arquivo_modelo, caminho_arquivo_npy, caminho_arquivo_word2vec):
        self.__nome_modelo = nome_modelo
        self.__caminho_arquivo_modelo = caminho_arquivo_modelo
        self.__caminho_arquivo_npy = caminho_arquivo_npy
        self.__caminho_arquivo_word2vec = caminho_arquivo_word2vec

    def get_score(self, texto):
        try:
            INPUT_TEXT = texto
            MODEL = self.__nome_modelo
            MODEL_FILE = self.__caminho_arquivo_modelo # Arquivo h5 para CNN e SKL para outros modelos
            NPY_FILE = self.__caminho_arquivo_npy  # Necessário apenas para a CNN ou Modelos de Deep Learning
            WORD2VEC_FILE = self.__caminho_arquivo_word2vec

            tp = TextProcessor()
            texts = [INPUT_TEXT]
            texts = tp.text_process(texts, text_only=True)
            X = [INPUT_TEXT]
            Y = []

            # if MODEL in ['rnn', 'han', 'lstm']:
            #     pc = PoliticalClassification(MODEL_FILE, NPY_FILE, 50)
            #
            #     for text in texts:
            #         Y.append(pc.is_political_prob(' '.join(text)))

            if MODEL == 'naive_bayes':
                model = joblib.load(MODEL_FILE)

                vectorizer = HashingVectorizer(
                    alternate_sign=False,
                    n_features=500000,
                    ngram_range=(1, 3)
                )
                texts = [' '.join(txt) for txt in texts]
                texts = vectorizer.transform(texts)
                for text in texts:
                    prob = model.predict_proba(text)
                    Y.append(prob[0][1])

                pass
            elif MODEL in ['cnn', 'rnn', 'lstm', 'han']:
                pc = PoliticalClassification(MODEL_FILE, NPY_FILE, 50)

                for text in texts:
                    if MODEL == 'han':
                        Y.append(pc.is_political_prob_han(' '.join(text)))
                    else:
                        Y.append(pc.is_political_prob(' '.join(text)))

            elif MODEL in ['svm', 'rforest', 'lregression', 'gboost']:
                word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(WORD2VEC_FILE,
                                                                                 binary=False,
                                                                                 unicode_errors="ignore")
                model = joblib.load(MODEL_FILE)

                data = gen_data(texts, word2vec_model)
                probabilities = model.predict_proba(data)

                Y = probabilities[:, 1]
            else:
                return (None, "Erro: modelo informado é inválido")

            retornos = []
            for i, x in enumerate(X):
                # print('{}'.format(Y[i]))
                retornos.append(Y[i])

            if len(retornos) > 0:
                return (retornos[0], None)
            else:
                return None, "Nenhum score foi gerado para o texto {}".format(INPUT_TEXT)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno,
            #       '\tData e Hora: ',
            #       datetime.now(),
            #       flush=True)
            return (None, e)