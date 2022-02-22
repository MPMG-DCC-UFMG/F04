from models.BaseModel import BaseModel
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score, ndcg_score, accuracy_score, recall_score, precision_score, roc_curve, auc
import pickle
import numpy as np
import joblib
import pandas as pd
from utils.helpers import gen_data
import time


class ClassicalModel (BaseModel):
    def __init__(self, *args, **kwargs):
        super(ClassicalModel, self).__init__(*args, **kwargs)
        self.pad_sequences = False

    @property
    def model_name(self):
        if self.name is None:
            raise Exception('The classical model name was not provided')

        return str(self.name)

    def get_model(self, m_type):
        if not m_type:
            raise Exception('ERROR: Please specify a model type!')

        if m_type == 'logistic':
            classifier = LogisticRegression(solver='lbfgs')
        elif m_type == "gradient_boosting":
            classifier = GradientBoostingClassifier()
        elif m_type == "random_forest":
            classifier = RandomForestClassifier()
        elif m_type == "svm":
            classifier = SVC(probability=True)
        elif m_type == "svm_linear":
            classifier = LinearSVC()
        else:
            raise Exception("ERROR: Please specify a correct model")

        return classifier

    def gen_sequence(self, texts, tx_class):
        y_map = dict()
        for i, v in enumerate(sorted(set(tx_class))):
            y_map[v] = i
        print(y_map)

        X, y = [], []
        for i, text in enumerate(texts):
            emb = np.zeros(self.word_embed_dim)
            for word in text:
                try:
                    emb += self.embeddings_index[word]
                except:
                    pass

            if not len(text):
                # only links
                print(i, texts[i])
                continue

            emb /= len(text)
            X.append(emb)
            y.append(y_map[tx_class[i]])

        return X, y

    def get_param_grid(self, m_type):
        param_grid = {
            'random_forest': {
                'bootstrap': [True],
                'max_depth': [80, 90, 100],
                'max_features': [2, 3],
                'min_samples_leaf': [3, 4, 5],
                'min_samples_split': [8, 10, 12],
                'n_estimators': [100, 200, 300]
            },
            'logistic': {'max_iter': [500]},
            'gradient_boosting': {'n_estimators': [16, 32], 'learning_rate': [0.8, 1.0]},
            'xgboost': {'nthread': [4],  # when use hyperthread, xgboost may become slower
                        'objective': ['binary:logistic'],
                        'learning_rate': [0.05],  # so called `eta` value
                        'max_depth': [6],
                        'min_child_weight': [11],
                        'subsample': [0.8],
                        'colsample_bytree': [0.7],
                        'n_estimators': [5],
                        'missing': [-999],
                        'seed': [self.seed]
                        },
            'svm': {'kernel': ['rbf', 'linear'], 'C': [1, 10], 'gamma': [0.001, 0.0001], 'probability': [True, True]}
        }

        return param_grid[m_type]

    def build_model(self):
        skf = StratifiedKFold(n_splits=self.num_folds)
        self.model = GridSearchCV(estimator=self.get_model(
            self.model_name), param_grid=self.get_param_grid(self.model_name), cv=skf, n_jobs=-1, verbose=1)

    def _run(self, folds):
        start_time = time.time()

        X, Y = self.preprocessing(folds['train'])

        self.build_model()
        self.model.fit(X, Y)
        print(self.model_name, self.plots_folder)
        with open(self.plots_folder + "/" + self.model_name + "/gridsearch_" + self.model_name + "_" + folds['label'] + ".pickle", 'wb') as handle:
            pickle.dump(self.model, handle, protocol=pickle.HIGHEST_PROTOCOL)

        X, Y = self.preprocessing(folds['test'])
        predictions = self.model.predict(X)

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

        self.save_confusion_matrix(Y, predictions, self.plots_folder +
                                   '/%s/csv/%s_confusion_matrix_evaluate.csv' % (self.model_name, self.model_name))
        self.generate_roc_curve(X, Y, self.model, image_file=self.plots_folder + '/%s/ROC_%s_%s.png' %
                                (self.model_name, self.model_name, folds['label']), fold=folds['label'], label=folds['label'])
        Y2 = []
        for k in Y:
            Y2.append([1 if k == 0 else 0, k])

        ndcg = ndcg_score(Y2, probas_)

        end_time = time.time()

        report = {
            'step': 1,
            'model_name': self.model_name,
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

        joblib.dump(self.model, self.plots_folder + '%s/model/%s._model.skl' %
                    (self.model_name, folds['label']))

        self.classification_full_report(
            report,
            filename=self.plots_folder +
            '/%s/csv/report_test.csv' % (self.model_name)
        )

        if 'classify' in folds:

            f_classify = self.folds_folder + '/' + folds['classify']
            df_classified = pd.read_csv(f_classify, sep=';')
            data = gen_data(df_classified['text'], self.embeddings_index)
            yhat = self.model.predict_proba(data)
            df_classified['score'] = yhat[:, 1]

            df_classified.to_csv(self.plots_folder +
                                 self.model_name + '/%s_classified.csv' % (folds['label']), index=False, sep=';')
