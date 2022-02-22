from models.BaseModel import BaseModel
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, ndcg_score, accuracy_score, confusion_matrix, roc_curve, auc, f1_score, recall_score, precision_score
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import interp
import joblib
import pandas as pd
import time


class NaiveModel(BaseModel):
    def __init__(self, *args, **kwargs):
        super(NaiveModel, self).__init__(*args, **kwargs)
        self.pad_sequences = False

    @property
    def model_name(self):
        return str(self.__class__.__name__)

    def get_vectorizer(self):
        """
        Return a HashingVectorizer, which we're using so that we don't
        need to serialize one.
        """
        return HashingVectorizer(
            alternate_sign=False,
            n_features=500000,
            ngram_range=(1, 3)
        )

    def build_model(self):
        skf = StratifiedKFold(n_splits=self.num_folds)

        self.model = GridSearchCV(
            MultinomialNB(), cv=skf, param_grid={}, return_train_score=True)

    def preprocessing(self, files):
        X, Y = self.generate_documents(
            self.folds_folder, files)

        data = list()

        for i in range(0, len(X)):
            data.append((X[i], 1.0 if Y[i] == 'politics' else 0.0))

        return data

    def _run(self, folds):
        start_time = time.time()

        data = self.preprocessing(folds['train'])
        self.build_model()
        self.train(data)

        X, Y = self.generate_documents(
            self.folds_folder, folds['test'])

        for i in range(0, len(Y)):
            Y[i] = 1.0 if Y[i] == 'politics' else 0.0

        self.generate_roc_curve(X, Y, self.model, image_file=self.plots_folder + '/%s/ROC_%s_%s.png' %
                                (self.model_name, self.model_name, folds['label']), fold=folds['label'], label=folds['label'])

        X = self.get_vectorizer().transform(X)

        predictions = self.model.predict(X)
        self.save_confusion_matrix(Y, predictions, self.plots_folder +
                                   '/%s/csv/confusion_matrix_evaluate.csv' % (self.model_name))

        precision_weighted = precision_score(
            Y, predictions, average='weighted')
        recall_weighted = recall_score(Y, predictions, average='weighted')
        f1_weighted = f1_score(Y, predictions, average='weighted')

        # getting metrics by class
        f1_by_class = f1_score(Y, predictions, average=None)
        recall_by_class = recall_score(Y, predictions, average=None)
        precision_by_class = precision_score(Y, predictions, average=None)

        f1_macro = f1_score(Y, predictions, average='macro')
        recall_macro = recall_score(Y, predictions, average='macro')
        precision_macro = precision_score(Y, predictions, average='macro')

        f1_micro = f1_score(Y, predictions, average='micro')
        recall_micro = recall_score(Y, predictions, average='micro')
        precision_micro = precision_score(Y, predictions, average='micro')

        accuracy = accuracy_score(Y, predictions)

        probas_ = self.model.predict_proba(X)
        fpr, tpr, _ = roc_curve(Y, probas_[:, 1])
        auc_ = auc(fpr, tpr)

        Y2 = []
        for k in Y:
            Y2.append([1 if k == 0 else 0, k])

        ndcg = ndcg_score(Y2, probas_)

        end_time = time.time()

        report = {
            'run_label': 'NB',
            'model_name': 'NB',
            'report_type': 'test',
            'label': folds['label'],
            'accuracy': accuracy,
            'accuracy_confidence': 0,
            'precision_weighted': precision_weighted,
            'precision_weighted_confidence': 0,
            'precision_micro': precision_micro,
            'precision_micro_confidence': 0,
            'precision_by_class_0': precision_by_class[0],
            'precision_by_class_1': precision_by_class[1],
            'precision_by_class_confidence_0': 0,
            'precision_by_class_confidence_1': 0,
            'precision_macro': precision_macro,
            'precision_macro_confidence': 0,

            'recall_weighted': recall_weighted,
            'recall_weighted_confidence': 0,
            'recall_micro': recall_micro,
            'recall_micro_confidence': 0,
            'recall_by_class_0': recall_by_class[0],
            'recall_by_class_1': recall_by_class[1],
            'recall_by_class_confidence_0': 0,
            'recall_by_class_confidence_1': 0,
            'recall_macro': recall_macro,
            'recall_macro_confidence': 0,

            'f1_weighted': f1_weighted,
            'f1_weighted_confidence': 0,
            'f1_micro': f1_micro,
            'f1_micro_confidence': 0,
            'f1_by_class_0': f1_by_class[0],
            'f1_by_class_1': f1_by_class[1],
            'f1_by_class_confidence_0': 0,
            'f1_by_class_confidence_1': 0,
            'f1_macro': f1_macro,
            'f1_macro_confidence': 0,
            'auc': auc_,
            'auc_confidence': 0,
            'ndcg': ndcg,
            'run_time': (end_time - start_time)
        }

        print(report)
        joblib.dump(self.model, self.plots_folder +
                    '/%s/model/naive_%s_ben.skl' % (self.model_name, folds['label']))

        self.classification_full_report(
            report,
            filename=self.plots_folder +
            '/%s/csv/report_test.csv' % (self.model_name)
        )

        if 'classify' in folds:
            X, Y = self.generate_documents(
                self.folds_folder, folds['classify'])
            X = self.get_vectorizer().transform(X)

            yhat = self.model.predict_proba(X)

            f_classify = self.folds_folder + '/' + folds['classify']
            df_classified = pd.read_csv(f_classify, sep=';')
            df_classified['score'] = yhat[:, 1]

            df_classified.to_csv(self.plots_folder +
                                 self.model_name + '/%s_classified.csv' % (folds['label']), index=False, sep=';')

    def train(self, data):
        vectorizer = self.get_vectorizer()
        train, test = train_test_split(
            data, test_size=0.1, random_state=self.seed, shuffle=True)
        x_train, y_train = zip(*train)
        x_test, y_test = zip(*test)
        x_train = vectorizer.transform(x_train)
        x_test = vectorizer.transform(x_test)
        x_train, y_train = self.equalize_classes(x_train, y_train)

        print("final size of training data: %s" % x_train.shape[0])

        self.model.fit(x_train, y_train)

        print("Train report")
        print(classification_report(y_test, self.model.predict(x_test)))

    def generate_roc_curve(self, X, y, model, image_file='roc_curve.png', fold=1, label=None, randomize=False):
        if randomize:
            cv = StratifiedKFold(n_splits=self.num_folds,
                                 shuffle=True, random_state=self.seed)
        else:
            cv = StratifiedKFold(n_splits=self.num_folds,
                                 shuffle=False, random_state=None)
        tprs = []
        aucs = []
        mean_fpr = np.linspace(0, 1, 100)

        i = 0

        for train, test in cv.split(X, y):

            x_test = [X[i] for i in test]
            y_test = np.array([y[i] for i in test])

            x_test = self.get_vectorizer().transform(x_test)
            probas_ = model.predict_proba(x_test)

            # Compute ROC curve and area the curve
            fpr, tpr, thresholds = roc_curve(y_test, probas_[:, 1])
            tprs.append(interp(mean_fpr, fpr, tpr))
            tprs[-1][0] = 0.0
            roc_auc = auc(fpr, tpr)
            aucs.append(roc_auc)
            plt.plot(fpr, tpr, lw=1, alpha=0.3,
                     label='ROC fold %d (AUC = %0.2f)' % (i, roc_auc))

            i += 1

        plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
                 label='Luck', alpha=.8)

        mean_tpr = np.mean(tprs, axis=0)
        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        std_auc = np.std(aucs)
        plt.plot(mean_fpr, mean_tpr, color='b',
                 label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (
                     mean_auc, std_auc),
                 lw=2, alpha=.8)

        self.save_roc_curve(mean_fpr, mean_tpr, fold, label,
                            filename='%s/%s/csv/auc.csv' % (self.plots_folder, self.model_name))

        std_tpr = np.std(tprs, axis=0)
        tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
        tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
        plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                         label=r'$\pm$ 1 std. dev.')

        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')

        plt.title('ROC Curve: Naive Bayes')
        plt.legend(loc="lower right")

        # plt.show()
        plt.savefig(image_file)
        plt.clf()

        return mean_auc, std_auc
