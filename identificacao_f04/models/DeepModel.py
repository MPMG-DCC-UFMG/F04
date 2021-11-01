from tensorflow.keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import make_scorer, f1_score, accuracy_score, recall_score, precision_score, classification_report, precision_recall_fscore_support
from sklearn.metrics import classification_report, roc_curve, auc, accuracy_score, precision_recall_fscore_support, f1_score, accuracy_score, recall_score, precision_score, confusion_matrix
from tensorflow.keras.models import Model
from keras.models import load_model
import pandas as pd

from keras.models import Model
from keras.layers import Input, Dense, Concatenate


import numpy as np
import gc
from models.BaseModel import BaseModel
from sklearn.model_selection import GridSearchCV
from keras.wrappers.scikit_learn import KerasClassifier
import time


class DeepModel (BaseModel):
    def __init__(self, epochs=10, batch_size=32, *args, **kwargs):
        super(DeepModel, self).__init__(*args, **kwargs)

        self.epochs = epochs
        self.batch_size = batch_size

    @property
    def model_name(self):
        return str(self.__class__.__name__)

    def build_model(self):
        pass

    def _run_on_grid_search(self, folds):

        # fix random seed for reproducibility
        np.random.seed(self.seed)
        # load dataset
        X, Y = self.preprocessing(folds['train'])
        # create model
        model = KerasClassifier(build_fn=self.build_model, verbose=1)
        # define the grid search parameters
        batch_size = [64]
        epochs = [5, 10, 15, 20]
        optimizer = ['SGD', 'RMSprop', 'Adagrad',
                     'Adadelta', 'Adam', 'Adamax', 'Nadam']
        param_grid = dict(batch_size=batch_size,
                          epochs=epochs)
        grid = GridSearchCV(
            estimator=model, param_grid=param_grid, n_jobs=-1, cv=self.num_folds)
        grid_result = grid.fit(X, Y)
        # summarize results
        print("Best: %f using %s" %
              (grid_result.best_score_, grid_result.best_params_))
        means = grid_result.cv_results_['mean_test_score']
        stds = grid_result.cv_results_['std_test_score']
        params = grid_result.cv_results_['params']
        for mean, stdev, param in zip(means, stds, params):
            print("%f (%f) with: %r" % (mean, stdev, param))

    def _run(self, folds):

        start_time = time.time()

        folds['label'] = folds['label'].replace(' ', '_')

        kfold = StratifiedKFold(n_splits=self.num_folds,
                                shuffle=True, random_state=self.seed)

        X, Y = self.preprocessing(folds['train'])

        #X, Y = equalize_classes(X, Y)

        assemble_models = []

        fold = 1

        for train, test in kfold.split(X, Y):
            print('[ > ] Generating Ad Text Model [%s]' % (fold))

            self.build_model()

            y_train = Y[train].reshape((len(Y[train]), 1))
            y_test = Y[test].reshape((len(Y[test]), 1))

            y_train = np_utils.to_categorical(
                y_train, num_classes=self.num_classes)
            y_test = np_utils.to_categorical(
                y_test, num_classes=self.num_classes)

            self.print_summary()
            # log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            # tensorboard_callback = tf.keras.callbacks.TensorBoard(
            #     log_dir=log_dir, histogram_freq=1)

            self.train(None, X[train], y_train, X[test], y_test)

            y_pred_proba = self.model.predict(X[test])
            y_pred = np.argmax(y_pred_proba, axis=1)

            print(classification_report(Y[test], y_pred))

            fold += 1

            assemble_models.append(self.model)
            del self.model
            del y_pred
            del y_train
            del y_pred_proba

            gc.collect()

        print('Initializing tests...')

        X, Y = self.preprocessing(folds['test'])

        ensemble_scores = []
        single_scores = []

        precision_weighted = []
        precision_micro = []
        precision_by_class = []
        precision_macro = []

        recall_weighted = []
        recall_micro = []
        recall_by_class = []
        recall_macro = []

        f1_weighted = []
        f1_micro = []
        f1_by_class = []
        f1_macro = []

        accuracy = []

        aucs = []

        print('He have %s models to stack...' % (len(assemble_models)))

        for i in range(1, len(assemble_models)):
            y_true = Y

            ensemble_score = self.evaluate_n_members(assemble_models, i, X, Y)

            y_test = np_utils.to_categorical(Y, num_classes=self.num_classes)
            _, single_score = assemble_models[i -
                                              1].evaluate(X, y_test, verbose=0)

            print('> %d: single=%.3f, ensemble=%.3f' %
                  (i, single_score, ensemble_score))

            ensemble_scores.append(ensemble_score)
            single_scores.append(single_score)

            # y_pred = model.predict_on_batch(X)
            y_pred = assemble_models[i - 1].predict(X)

            fpr, tpr, _ = roc_curve(Y, y_pred[:, 1])
            aucs.append(auc(fpr, tpr))

            y_pred = np.argmax(y_pred, axis=1)

            precision_weighted.append(precision_score(
                y_true, y_pred, average='weighted'))
            precision_micro.append(precision_score(
                y_true, y_pred, average='micro'))
            precision_by_class.append(
                precision_score(y_true, y_pred, average=None))
            precision_macro.append(precision_score(
                y_true, y_pred, average='macro'))

            recall_weighted.append(recall_score(
                y_true, y_pred, average='weighted'))
            recall_micro.append(recall_score(y_true, y_pred, average='micro'))
            recall_by_class.append(recall_score(y_true, y_pred, average=None))
            recall_macro.append(recall_score(y_true, y_pred, average='macro'))

            f1_weighted.append(f1_score(y_true, y_pred, average='weighted'))
            f1_micro.append(f1_score(y_true, y_pred, average='micro'))
            f1_by_class.append(f1_score(y_true, y_pred, average=None))
            f1_macro.append(f1_score(y_true, y_pred, average='macro'))

            accuracy.append(accuracy_score(y_true, y_pred))

            print(confusion_matrix(y_true, y_pred))

            self.save_models(
                assemble_models[i - 1], h5file=self.plots_folder + self.model_name + '/model/' + folds['label'] + '_fold_' + str(i) + ".h5")

        print('Reporting...')

        end_time = time.time()

        report = {
            'run_label': self.model_name,
            'model_name': self.model_name,
            'report_type': 'test',
            'label': folds['label'],

            'accuracy': np.array(accuracy).mean(),
            'accuracy_confidence': np.array(accuracy).std() * 2,
            'precision_weighted': np.array(precision_weighted).mean(),
            'precision_weighted_confidence': np.array(precision_weighted).std() * 2,
            'precision_micro': np.array(precision_micro).mean(),
            'precision_micro_confidence': np.array(precision_micro).std() * 2,
            'precision_by_class_0': np.array(np.array(precision_by_class)[:, 0]).mean(),
            'precision_by_class_1': np.array(np.array(precision_by_class)[:, 1]).mean(),
            'precision_by_class_confidence_0': np.array(np.array(precision_by_class)[:, 0]).std() * 2,
            'precision_by_class_confidence_1': np.array(np.array(precision_by_class)[:, 1]).std() * 2,
            'precision_macro': np.array(precision_macro).mean(),
            'precision_macro_confidence': np.array(precision_macro).std() * 2,

            'recall_weighted': np.array(recall_weighted).mean(),
            'recall_weighted_confidence': np.array(recall_weighted).std() * 2,
            'recall_micro': np.array(recall_micro).mean(),
            'recall_micro_confidence': np.array(recall_micro).std() * 2,
            'recall_by_class_0': np.array(np.array(recall_by_class)[:, 0]).mean(),
            'recall_by_class_1': np.array(np.array(recall_by_class)[:, 1]).mean(),
            'recall_by_class_confidence_0': np.array(np.array(recall_by_class)[:, 0]).std() * 2,
            'recall_by_class_confidence_1': np.array(np.array(recall_by_class)[:, 1]).std() * 2,
            'recall_macro': np.array(recall_macro).mean(),
            'recall_macro_confidence': np.array(recall_macro).std() * 2,

            'f1_weighted': np.array(f1_weighted).mean(),
            'f1_weighted_confidence': np.array(f1_weighted).std() * 2,
            'f1_micro': np.array(f1_micro).mean(),
            'f1_micro_confidence': np.array(f1_micro).std() * 2,
            'f1_by_class_0': np.array(np.array(f1_by_class)[:, 0]).mean(),
            'f1_by_class_1': np.array(np.array(f1_by_class)[:, 1]).mean(),
            'f1_by_class_confidence_0': np.array(np.array(f1_by_class)[:, 0]).std() * 2,
            'f1_by_class_confidence_1': np.array(np.array(f1_by_class)[:, 1]).std() * 2,
            'f1_macro': np.array(f1_macro).mean(),
            'f1_macro_confidence': np.array(f1_macro).std() * 2,
            'auc': np.array(aucs).mean(),
            'auc_confidence': np.array(aucs).std() * 2,
            'run_time': (end_time - start_time)
        }

        print(report)

        # stacked_model = self.define_stacked_model(assemble_models)
        # # fit stacked model on test dataset
        # self.fit_stacked_model(stacked_model, X, Y)

        # # if (folds['label'] == 'Step_1'):
        # #     self.save_models(stacked_model)

        # # make predictions and evaluate
        # yhat = self.predict_stacked_model(stacked_model, X)

        # yhat = np.argmax(yhat, axis=1)
        # acc = accuracy_score(Y, yhat)
        # f1 = f1_score(Y, yhat, average='macro')
        # self.save_confusion_matrix(
        #     Y, yhat, self.plots_folder + self.model_name + '/csv/%s_confusion_matrix_evaluate.csv' % (self.model_name))

        # self.generate_roc_curve(X, Y, stacked_model, image_file=self.plots_folder + self.model_name + '/ROC_%s_%s_fold%s.png' % (
        #     self.model_name, folds['label'], i), fold=i, label=folds['label'])
        # self.generate_roc_curve_by_class(X, Y, stacked_model, image_file=self.plots_folder + self.model_name + '/ROC_%s_%s_class.png' % (
        #     self.model_name, folds['label']), fold=folds['label'], label=folds['label'])
        # print('Stacked Test Accuracy: %.4f' % acc)
        # print('Stacked Test F1: %.4f' % f1)

        # if (folds['label'] == 'Step_1'):
        #     print('Loading validation...')

        #     # We perform a classification of non-labeled ads
        #     if 'classify' in folds:
        #         X, Y = self.preprocessing(
        #             folds['classify'], sep=',', randomize=False)
        #         yhat = self.predict_stacked_model(stacked_model, X)

        #         f_classify = self.folds_folder + '/' + folds['classify']
        #         df_classified = pd.read_csv(f_classify)
        #         df_classified['score'] = yhat[:, 1]

        #         # df_classified.to_csv(self.plots_folder +
        #         #                      self.model_name + '/final_ads.csv', index=False)
        #         for x in X:
        #             print(assemble_models[0].show_word_attention(x))

        self.classification_full_report(
            report,
            filename=self.plots_folder + self.model_name +
            '/csv/report_%s_test.csv' % (self.model_name)
        )

        try:
            del assemble_models  # this is from global space - change this as you need
            del self.model
        except:
            pass

        gc.collect()

    def evaluate_n_members(self, members, n_members, testX, testy):
        # select a subset of members
        subset = members[:n_members]
        # make prediction
        yhat = self.ensemble_predictions(subset, testX)
        # calculate accuracy
        return accuracy_score(testy, yhat)

    def ensemble_predictions(self, members, testX):
        # make predictions
        yhats = [model.predict(testX) for model in members]
        yhats = np.array(yhats)
        # sum across ensemble members
        summed = np.sum(yhats, axis=0)
        # argmax across classes
        result = np.argmax(summed, axis=1)

        return result

    def train(self, checkpoint_path, X_train, y_train, X_test, y_test, optimizer='adam', loss='binary_crossentropy', metric='accuracy', monitor='val_loss'):
        """Train the HAN model.

        Args:
            checkpoint_path: str, the path to save checkpoint file.
            X_train: training dataset.
            y_train: target of training dataset.
            X_test: testing dataset.
            y_test: target of testing dataset.
            optimizer: optimizer for compiling, default is adagrad.
            loss: loss function, default is categorical_crossentropy.
            metric: measurement metric, default is acc (accuracy).
            monitor: monitor of metric to pick up best weights, default is val_loss.
            batch_size: batch size, default is 20.
            epochs: number of epoch, default is 10.
        """

        self.model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=[metric]
        )
        checkpoint = ModelCheckpoint(
            filepath=checkpoint_path,
            monitor=monitor,
            verbose=1, save_best_only=True
        )

        self.model.fit(
            X_train, y_train, batch_size=self.batch_size, epochs=self.epochs,
            validation_data=(X_test, y_test),
            callbacks=[]
        )

    # load models from file
    def load_all_models(self, n_models, model_folder=None):
        all_models = list()
        for i in range(n_models):

            if not model_folder:
                # define filename for this ensemble
                filename = self.plots_folder + \
                    'models/model_' + str(i + 1) + '.h5'
            else:
                filename = model_folder + \
                    'models/model_' + str(i + 1) + '.h5'
            # load model from file
            model = load_model(filename)
            # add to list of members
            all_models.append(model)
            print('>loaded %s' % filename)
        return all_models

    # define stacked model from multiple member input models (Meta learner)
    def define_stacked_model(self, members):
        # update all layers in all models to not be trainable
        for i in range(len(members)):
            model = members[i]
            for layer in model.layers:
                # make not trainable
                layer.trainable = False
                # rename to avoid 'unique layer name' issue
                layer._name = 'ensemble_' + str(i+1) + '_' + layer.name
        # define multi-headed input
        ensemble_visible = [model.input for model in members]
        # concatenate merge output from each model
        ensemble_outputs = [model.output for model in members]
        merge = Concatenate()(ensemble_outputs)
        hidden = Dense(10, activation='relu')(merge)
        output = Dense(2, activation='softmax')(hidden)
        model = Model(inputs=ensemble_visible, outputs=output)
        # plot graph of ensemble
        #plot_model(model, show_shapes=True, to_file='model_graph.png')
        # compile
        model.compile(loss='categorical_crossentropy',
                      optimizer='adam', metrics=['accuracy'])
        return model

    # fit a stacked model
    def fit_stacked_model(self, model, inputX, inputy):
        # prepare input data
        X = [inputX for _ in range(len(model.input))]
        # encode output data
        inputy_enc = np_utils.to_categorical(inputy)
        # fit model
        model.fit(X, inputy_enc, epochs=300, verbose=1)

    # make a prediction with a stacked model
    def predict_stacked_model(self, model, inputX):
        # prepare input data
        X = [inputX for _ in range(len(model.input))]
        # make prediction
        return model.predict(X, verbose=0)

    def save_models(self, model, h5file=''):
        # for i, m in enumerate(assemble_models):
        model.save(h5file)

        np.save(self.plots_folder + self.model_name +
                '/model/vocabulary.npy', self.vocab)

    def print_summary(self):
        print(self.model.summary())
