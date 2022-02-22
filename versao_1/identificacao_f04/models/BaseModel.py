from imblearn.over_sampling import SMOTE
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_curve, auc, confusion_matrix
import itertools
from sklearn.naive_bayes import MultinomialNB
from scipy import interp
from sklearn.model_selection import GridSearchCV
from itertools import cycle
from scipy.interpolate import UnivariateSpline
import os
import json
import sklearn
import pandas as pd
import csv
import numpy as np
import gc
from sklearn.preprocessing import label_binarize

from utils.text_processor import TextProcessor

import matplotlib.pyplot as plt


class BaseModel:
    def __init__(self,  embeddings_index, word_embed_dim=300, max_seq_length=50, num_folds=10,
                 num_classes=2, dataset_config='dataset_config.json', folds_folder=None,
                 plots_folder=None, seed=42, text_column='text', label_column='label', name='BaseModel'):
        self.embeddings_index = embeddings_index
        self.word_embed_dim = word_embed_dim
        self.max_seq_length = max_seq_length
        self.num_folds = num_folds
        self.num_classes = num_classes
        self.dataset_config = dataset_config
        self.folds_folder = folds_folder
        self.plots_folder = plots_folder
        self.pad_sequences = True
        self.seed = seed
        self.text_column = text_column
        self.label_column = label_column
        self.FILE_CACHE = {}
        self.name = name

        if not os.path.exists(self.plots_folder + self.model_name):
            os.makedirs(self.plots_folder + self.model_name + '/csv')
            os.makedirs(self.plots_folder + self.model_name + '/model')

    @property
    def model_name(self):
        return str(self.name)

    def build_model(self):
        pass

    def _run(self, folds):
        pass

    def equalize_classes(self, predictor, response):
        """
        Equalize classes in training data for better representation.
        https://en.wikipedia.org/wiki/Oversampling_and_undersampling_in_data_analysis#SMOTE
        """
        return SMOTE().fit_resample(predictor, response)

    def train_model(self):
        if not os.path.exists(self.dataset_config):
            raise Exception(
                'Path [%s] to dataset config does not exist!' % (self.dataset_config))

        folds = None

        with open(self.dataset_config) as f:
            folds = json.load(f)

        for fold in folds['ads']:
            self._run(fold)

    def get_embedding_matrix(self):
        embedding_matrix = np.random.random(
            (len(self.vocab) + 1, self.word_embed_dim))
        for word, i in self.vocab.items():
            try:
                embedding_vector = self.embeddings_index[word]
            except:
                print(word)
                pass

            if embedding_vector is not None:
                # words not found in embedding index will be all-zeros.
                if len(embedding_matrix[i]) != len(embedding_vector):
                    print("could not broadcast input array from shape", str(len(embedding_matrix[i])),
                          "into shape", str(len(embedding_vector)
                                            ), " Please make sure your"
                          " EMBEDDING_DIM is equal to embedding_vector file ,GloVe,")
                    exit(1)

                embedding_matrix[i] = embedding_vector

        return embedding_matrix

    def preprocessing(self, files, sep=';', randomize=True):
        data = None
        Y = None
        self.vocab = None
        tp = TextProcessor()

        if '_'.join(files) in self.FILE_CACHE:
            print('[ >> ] Get documents from Cache...')
            print('[ >> ] ', '_'.join(files))
            data = self.FILE_CACHE['_'.join(files)]['data']
            Y = self.FILE_CACHE['_'.join(files)]['Y']
            self.vocab = self.FILE_CACHE['_'.join(files)]['vocab']
        else:
            self.FILE_CACHE['_'.join(files)] = {}

            print('[ >> ] Generate documents...')

            X, Y = self.generate_documents(
                self.folds_folder, files, sep=sep)

            print('X and Y', len(X), len(Y))

            print('[ >> ] Cleaning documents...')
            # clean the text
            X = tp.text_process(X, text_only=True, remove_accent=False)
            print('X', len(X))

            print('[ >> ] Selecting documents...')

            # search word in word2vec
            X, Y = self.select_texts(X, Y)
            print('X and Y', len(X), len(Y))

            print('[ >> ] Generate vocabulary...')
            self.vocab = self.gen_vocab()

            print('[ >> ] Generate sequence...')
            X, Y = self.gen_sequence(X, Y)
            print('X and Y', len(X), len(Y))

            if self.pad_sequences:
                print('[ >> ] Pad documents...')
                data = pad_sequences(X, maxlen=self.max_seq_length)
            else:
                data = X

            print('X', len(X))

            Y = np.array(Y)

            self.FILE_CACHE['_'.join(files)]['data'] = data
            self.FILE_CACHE['_'.join(files)]['Y'] = Y
            self.FILE_CACHE['_'.join(files)]['vocab'] = self.vocab

        print('[ >> ] Shuffle documents...')
        if not len(Y):
            Y = [1] * data.shape[0]
        if randomize:
            data, Y = sklearn.utils.shuffle(data, Y)
            print('X and Y', len(data), len(Y))

        return data, Y

    def select_texts(self, texts, y):
        # selects the texts as in embedding method
        # Processing
        text_return = []

        for i, text in enumerate(texts):
            _emb = 0
            text = [] if text is None else text
            for w in text:
                # Check if embeeding there is in embedding model
                if w in self.embeddings_index:
                    _emb += 1
            # if _emb:   # Not a blank text
            text_return.append(text)

        print('texts selected:', len(text_return))

        return text_return, y

    def gen_vocab(self):
        vocab = dict([(k, v.index)
                     for k, v in self.embeddings_index.vocab.items()])
        vocab['UNK'] = len(vocab) + 1

        return vocab

    def gen_sequence(self, texts, tx_class):
        y_map = dict()

        if len(tx_class):
            for i, v in enumerate(sorted(set(tx_class))):
                y_map[v] = i

        print(y_map)
        X, y = [], []

        for i, text in enumerate(texts):
            seq = []

            for word in text:
                seq.append(self.vocab.get(word, self.vocab['UNK']))

            X.append(seq)

            if len(tx_class):
                y.append(y_map[tx_class[i]])

        return X, y

    def generate_documents(self, folds_root_path, folds, sep=';'):
        X = []
        Y = []

        if type(folds) is list:
            for fold in folds:

                print('loading %s' % folds_root_path + fold)

                df = pd.read_csv(folds_root_path + fold,
                                 sep=sep, quoting=csv.QUOTE_MINIMAL)

                print('[ > ] SHAPE', df.shape)

                for i, row in df.iterrows():
                    row[self.text_column] = row[self.text_column] if type(
                        row[self.text_column]) is str else ''

                    X.append(row[self.text_column])  # annotations or ad_text

                    if self.label_column not in row:
                        continue

                    if row[self.label_column] == 0:
                        Y.append('non-politics')
                    else:
                        Y.append('politics')
        else:
            print('loading %s' % folds_root_path + folds)

            df = pd.read_csv(folds_root_path + folds, sep=sep,
                             quoting=csv.QUOTE_MINIMAL)

            print('[ > ] SHAPE', df.shape)

            for i, row in df.iterrows():
                row[self.text_column] = row[self.text_column] if type(
                    row[self.text_column]) is str else ''

                X.append(row[self.text_column])

                if self.label_column not in row:
                    continue

                if row[self.label_column] == 0:
                    Y.append('non-politics')
                else:
                    Y.append('politics')

        return X, Y

    def classification_full_report(self, report={}, filename=None):
        print('Saving %s' % (filename))

        print(report)

        include_headers = False

        if not os.path.exists(filename):
            include_headers = True

        with open(filename, 'a', encoding="utf-8") as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';')

            if include_headers:
                spamwriter.writerow(report.keys())

            spamwriter.writerow(report.values())

    def save_confusion_matrix(self, y_true, y_pred, filename):
        with open(filename, 'a') as csvfile:
            print(confusion_matrix(y_true, y_pred))
            matrix = confusion_matrix(y_true, y_pred)
            merged = list(itertools.chain.from_iterable(matrix))

            spamwriter = csv.writer(csvfile, delimiter=';',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(merged)

    def generate_roc_curve(self, X, y_true, model, image_file='roc_curve.png', fold=1, label=None, randomize=False):
        label = self.model_name

        if randomize:
            cv = StratifiedKFold(n_splits=self.num_folds, shuffle=True,
                                 random_state=self.seed)
        else:
            cv = StratifiedKFold(n_splits=self.num_folds,
                                 shuffle=False, random_state=None)

        plt.figure(figsize=(8, 6))

        tprs = []
        thresholds_array = []
        aucs = []

        mean_fpr = np.linspace(0, 1, 100)

        i = 0

        for _, test in cv.split(X, y_true):

            x_test = np.array([X[i] for i in test])

            y_test = np.array([y_true[i] for i in test])

            y_probas = list()

            if isinstance(model, GridSearchCV) or isinstance(model, MultinomialNB):
                y__ = model.predict_proba(x_test)
            else:
                x_test = [x_test for _ in range(len(model.input))]
                y__ = model.predict(x_test)

            for y in y__:

                y_probas.append(y[1])

            # Compute ROC curve and area the curve
            fpr, tpr, thresholds = roc_curve(y_test, y_probas)
            thresholds_array.append(thresholds)
            tprs.append(interp(mean_fpr, fpr, tpr))
            tprs[-1][0] = 0.0
            roc_auc = auc(fpr, tpr)
            aucs.append(roc_auc)
            plt.plot(fpr, tpr, lw=1, alpha=0.3,
                     label='ROC fold %d (AUC = %0.2f)' % (i, roc_auc))

            i += 1

        plt.plot([0, 1], [0, 1], linestyle='--', lw=2,
                 color='r', label='Luck', alpha=.8)

        mean_tpr = np.mean(tprs, axis=0)

        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        std_auc = np.std(aucs)

        plt.plot(mean_fpr, mean_tpr, color='b', label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (
            mean_auc, std_auc), lw=2, alpha=.8)

        self.save_roc_curve(mean_fpr, mean_tpr, fold, label,
                            filename=self.plots_folder + self.model_name + '/csv/%s_auc.csv' % (self.model_name))

        std_tpr = np.std(tprs, axis=0)

        tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
        tprs_lower = np.maximum(mean_tpr - std_tpr, 0)

        plt.fill_between(mean_fpr, tprs_lower, tprs_upper,
                         color='grey', alpha=.2, label=r'$\pm$ 1 std. dev.')
        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend(loc="lower right")
        plt.title('ROC Curve')

        plt.savefig(image_file)
        plt.clf()

        # precision, recall, thresholds = precision_recall_curve(y_test, y_probas)

        # # calculate average precision score
        # ap = average_precision_score(y_test, y_probas)
        # print('ap=%.3f' % ap)
        # # plot no skill
        # plt.plot([0, 1], [0.5, 0.5], linestyle='--')
        # # plot the precision-recall curve for the model
        # thresholds = np.insert(thresholds, 0, 0.0)
        # plt.plot(thresholds, precision, marker='.')
        # # show the plot
        # plt.savefig(image_file + 'precision_recall_curve.png')
        # plt.clf()

        return mean_auc, std_auc

    def generate_roc_curve_by_class(self, X, y_true, model, image_file='roc_curve_by_class.png', fold=1, label=None):

        # Plot linewidth.
        lw = 2

        # Compute ROC curve and ROC area for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        y_probas = []
        if isinstance(model, GridSearchCV):
            y__ = model.predict_proba(X)
        elif isinstance(model, MultinomialNB):
            y__ = model.predict(X)
        else:
            X = [X for _ in range(len(model.input))]
            y__ = model.predict(X)

        for y in y__:

            y_probas.append(y)
        y_probas = np.array(y_probas)

        y_test = np.zeros(y_probas.shape)
        for i, k in enumerate(y_true):
            if k == 1:
                y_test[i, 1] = 1
            else:
                y_test[i, 0] = 1

        print(y_test.shape, y_probas.shape)
        for i in range(self.num_classes):
            fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_probas[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = roc_curve(
            y_test.ravel(), y_probas.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        # Compute macro-average ROC curve and ROC area

        # First aggregate all false positive rates
        all_fpr = np.unique(np.concatenate(
            [fpr[i] for i in range(self.num_classes)]))

        # Then interpolate all ROC curves at this points
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(self.num_classes):
            mean_tpr += interp(all_fpr, fpr[i], tpr[i])

        # Finally average it and compute AUC
        mean_tpr /= self.num_classes

        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

        # Plot all ROC curves
        plt.figure(1)
        plt.plot(fpr["micro"], tpr["micro"],
                 label='micro-average ROC curve (area = {0:0.4f})'
                 ''.format(roc_auc["micro"]),
                 color='deeppink', linestyle=':', linewidth=4)

        plt.plot(fpr["macro"], tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.4f})'
                 ''.format(roc_auc["macro"]),
                 color='navy', linestyle=':', linewidth=4)

        colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
        for i, color in zip(range(self.num_classes), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=lw,
                     label='ROC curve of class {0} (area = {1:0.4f})'
                     ''.format(i, roc_auc[i]))

        plt.plot([0, 1], [0, 1], 'k--', lw=lw)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(
            'Some extension of Receiver operating characteristic to multi-class')
        plt.legend(loc="lower right")
        plt.savefig(image_file)
        plt.clf()

        # Zoom in view of the upper left corner.
        plt.figure(2)
        plt.xlim(0, 0.2)
        plt.ylim(0.8, 1)
        plt.plot(fpr["micro"], tpr["micro"],
                 label='micro-average ROC curve (area = {0:0.4f})'
                 ''.format(roc_auc["micro"]),
                 color='deeppink', linestyle=':', linewidth=4)

        plt.plot(fpr["macro"], tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.4f})'
                 ''.format(roc_auc["macro"]),
                 color='navy', linestyle=':', linewidth=4)

        colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
        for i, color in zip(range(self.num_classes), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=lw,
                     label='ROC curve of class {0} (area = {1:0.4f})'
                     ''.format(i, roc_auc[i]))

        plt.plot([0, 1], [0, 1], 'k--', lw=lw)
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(
            'Some extension of Receiver operating characteristic to multi-class')
        plt.legend(loc="lower right")
        plt.savefig(image_file.replace('_class', '_class_zoom'))
        plt.clf()

    def save_roc_curve(self, mean_fpr, mean_tpr, fold, label, filename='{}_roc_curve_data.csv', thresholds=None):
        filename = filename.format(self.model_name)

        mean_tpr = np.append(mean_tpr, [fold, label])
        mean_fpr = np.append(mean_fpr, [fold, label])

        with open(filename, 'a') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(mean_fpr)
            spamwriter.writerow(mean_tpr)
            if thresholds:
                spamwriter.writerow(thresholds)

    def plot_pdf(self, y_pred, y_test, name=None, smooth=500, filename='{}_pdf.pdf'):
        positives = y_pred[y_test == 1]
        negatives = y_pred[y_test == 0]
        N = positives.shape[0]
        n = N//smooth
        s = positives
        p, x = np.histogram(s, bins=n)  # bin it into n = N//10 bins
        x = x[:-1] + (x[1] - x[0])/2   # convert bin edges to centers
        f = UnivariateSpline(x, p, s=n)
        plt.plot(x, f(x))

        N = negatives.shape[0]
        n = N//smooth
        s = negatives
        p, x = np.histogram(s, bins=n)  # bin it into n = N//10 bins
        x = x[:-1] + (x[1] - x[0])/2   # convert bin edges to centers
        f = UnivariateSpline(x, p, s=n)
        plt.plot(x, f(x))
        plt.xlim([0.0, 1.0])
        plt.xlabel('density')
        plt.ylabel('density')
        plt.title('PDF-{}'.format(name))
        plt.savefig(filename.format(self.model_name))
