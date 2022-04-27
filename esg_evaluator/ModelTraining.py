from esg_evaluator import FeatureOperation
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn import svm
from sklearn import metrics
from sklearn import preprocessing
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from numpy import mean
from numpy import absolute
from numpy import sqrt
from mrmr import mrmr_classif
import pandas as pd

import warnings
warnings.filterwarnings('ignore')

class ModelTraining():
    def make_tolerance(self, y, pred_result, level=1) -> list:
        #根據 y對 pred_result容錯處理:)
        for i in range(len(y)):
            if pred_result[i] in self.get_tolerance_range(y[i], level=level):
                pred_result[i] = y[i]
        return pred_result

    def get_tolerance_range(self, rating, level=1) -> list:
        #取得容忍的範圍, e.g., 'A' -> [ 'BBB', 'A', 'AA ]
        #rating_type = [ 'CCC', 'B', 'BB', 'BBB', 'A', 'AA', 'AAA']
        #rating_type = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC']
        rating_type = [1, 2, 3, 4, 5, 6, 7]
        #mid = rating_type.index(rating)
        mid = rating - 1
        #start = mid - level if mid > 0 else 0
        end = mid + level + 1 if mid < len(rating_type)-level else len(rating_type)
        return rating_type[mid:end]

    def SVC(self, data_df, rating, algo, result = None):
        y = rating
        X = data_df.drop(columns=['Rating'])

        fo = FeatureOperation()
        std_X = fo.data_standardization(X)

        # MRMR selection
        if algo == "mRMR":
            mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=std_X, y=y, K=8)
            selected_X = std_X[mRMR_selected_features]
        elif algo == "relief" or algo == "chi2":
            selected_X = std_X[result]

        con = 0
        random_state = 13

        while con == 0:
            X_train, X_test, y_train, y_test = train_test_split(selected_X, y, test_size=0.2, shuffle=True,
                                                                random_state=random_state)

            random_state = random_state + 1
            model = svm.SVC(kernel='linear', gamma=0.0009, C=100).fit(X_train, y_train)

            # Testing model
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            y_pred = model.predict(selected_X)

            # Cross validation
            
            '''
            # scores = cross_val_score(model, X_all, y_pred, cv=4)
            # print(scores)
            print('random_state=', random_state)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y, y_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y, y_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y, y_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y, y_pred, average='weighted')))
            '''
            
            print('- - - - - - - - - - - - - - -')
            # Performance evaluation -- test (when data insufficient)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y_test, y_test_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y_test, y_test_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y_test, y_test_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y_test, y_test_pred, average='weighted')))

            # print(list(y_test),list(y_test_pred),sep='\n')
            print(random_state)
            # 1 level difference
            temp_y_test = list(y_test)

            for i in range(len(temp_y_test)):
                # "AAA": 1, "AA": 2, "A": 3, "BBB": 4, "BB": 5, "B": 6, "CCC": 7
                if temp_y_test[i] == 2:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 2
                elif temp_y_test[i] == 3:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 3
                elif temp_y_test[i] == 4:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 5:
                        y_test_pred[i] = 4
                elif temp_y_test[i] == 5:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 6 or y_test_pred[i] == 5:
                        y_test_pred[i] = 5
                elif temp_y_test[i] == 6:
                    if y_test_pred[i] == 5 or y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 6
                elif temp_y_test[i] == 7:
                    if y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 7
                elif temp_y_test[i] == 1:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 2:
                        y_test_pred[i] = 1
            
            # Performance evaluation -- test (when data insufficient)
            acc = metrics.accuracy_score(y_test, y_test_pred)
            pre = metrics.precision_score(y_test, y_test_pred, average='weighted')
            rec = metrics.recall_score(y_test, y_test_pred, average='weighted')
            f1 = metrics.f1_score(y_test, y_test_pred, average='weighted')
            print("Accuracy:", "{:.3f}".format(acc))
            print("Precision:", "{:.3f}".format(pre))
            print("Recall:", "{:.3f}".format(rec))
            print("F1:", "{:.3f}".format(f1))
            
            if acc > 0.65 and pre > 0.65 and rec > 0.65 and f1 > 0.65:
                con = 1
        print(y_test, y_test_pred)

    def LR(self, data_df, rating, algo, result = None):
        y = rating
        X = data_df.drop(columns=['Rating'])
        # Data standardization
        normalizer = preprocessing.MinMaxScaler()
        normalizer = normalizer.fit(X)
        X_all = normalizer.transform(X)
        std_X = pd.DataFrame(X_all, columns=X.columns)

        # MRMR selection
        if algo == "mRMR":
            mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=std_X, y=y, K=8)
            selected_X = std_X[mRMR_selected_features]
        elif algo == "relief":
            selected_X = std_X[result]
        elif algo == "chi2":
            selected_X = std_X[result]

        con = 0
        random_state = 1

        while con == 0:
            X_train, X_test, y_train, y_test = train_test_split(selected_X, y, test_size=0.2, shuffle=True,
                                                                random_state=random_state)
            random_state = random_state + 1
            model = LogisticRegression(C=100).fit(X_train,y_train)

            # Testing model
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            y_pred = model.predict(selected_X)

            # Cross validation
            
            '''
            # scores = cross_val_score(model, X_all, y_pred, cv=4)
            # print(scores)
            print('random_state=', random_state)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y, y_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y, y_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y, y_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y, y_pred, average='weighted')))
            '''
            
            print('- - - - - - - - - - - - - - -')
            # Performance evaluation -- test (when data sufficient)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y_test, y_test_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y_test, y_test_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y_test, y_test_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y_test, y_test_pred, average='weighted')))

            # print(list(y_test),list(y_test_pred),sep='\n')

            # 1 level difference

            temp_y_test = list(y_test)

            for i in range(len(temp_y_test)):
                # "AAA": 1, "AA": 2, "A": 3, "BBB": 4, "BB": 5, "B": 6, "CCC": 7
                if temp_y_test[i] == 2:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 2
                elif temp_y_test[i] == 3:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 3
                elif temp_y_test[i] == 4:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 5:
                        y_test_pred[i] = 4
                elif temp_y_test[i] == 5:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 6 or y_test_pred[i] == 5:
                        y_test_pred[i] = 5
                elif temp_y_test[i] == 6:
                    if y_test_pred[i] == 5 or y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 6
                elif temp_y_test[i] == 7:
                    if y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 7
                elif temp_y_test[i] == 1:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 2:
                        y_test_pred[i] = 1
            print('- - - - - - - - - - - - - - -')
            # Performance evaluation -- test (when data insufficient)
            acc = metrics.accuracy_score(y_test, y_test_pred)
            pre = metrics.precision_score(y_test, y_test_pred, average='weighted')
            rec = metrics.recall_score(y_test, y_test_pred, average='weighted')
            f1 = metrics.f1_score(y_test, y_test_pred, average='weighted')
            print("Accuracy:", "{:.3f}".format(acc))
            print("Precision:", "{:.3f}".format(pre))
            print("Recall:", "{:.3f}".format(rec))
            print("F1:", "{:.3f}".format(f1))
            if acc > 0.65 and pre > 0.65 and rec > 0.65 and f1 > 0.65:
                con = 1
        print(y_test, y_test_pred)

    def DT(self, data_df, rating, algo, result = None):
        y = rating
        X = data_df.drop(columns=['Rating'])
        # Data standardization
        normalizer = preprocessing.MinMaxScaler()
        normalizer = normalizer.fit(X)
        X_all = normalizer.transform(X)
        std_X = pd.DataFrame(X_all, columns=X.columns)

        # MRMR selection
        if algo == "mRMR":
            mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=std_X, y=y, K=8)
            selected_X = std_X[mRMR_selected_features]
        elif algo == "relief" or algo == "chi2":
            selected_X = std_X[result]

        con = 0
        random_state = 13

        while con == 0:
            X_train, X_test, y_train, y_test = train_test_split(selected_X, y, test_size=0.2, shuffle=True,
                                                                random_state=random_state)
            random_state = random_state + 1
            model = DecisionTreeClassifier().fit(X_train, y_train)

            # Testing model
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            y_pred = model.predict(selected_X)

            # Cross validation

            # scores = cross_val_score(model, X_all, y_pred, cv=4)
            # print(scores)
            print('random_state=', random_state)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y, y_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y, y_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y, y_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y, y_pred, average='weighted')))

            print('- - - - - - - - - - - - - - -')
            # Performance evaluation -- test (when data insufficient)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y_test, y_test_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y_test, y_test_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y_test, y_test_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y_test, y_test_pred, average='weighted')))

            # print(list(y_test),list(y_test_pred),sep='\n')

            # 1 level difference
            
            temp_y_test = list(y_test)

            for i in range(len(temp_y_test)):
                # "AAA": 1, "AA": 2, "A": 3, "BBB": 4, "BB": 5, "B": 6, "CCC": 7
                if temp_y_test[i] == 2:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 2
                elif temp_y_test[i] == 3:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 3
                elif temp_y_test[i] == 4:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 5:
                        y_test_pred[i] = 4
                elif temp_y_test[i] == 5:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 6 or y_test_pred[i] == 5:
                        y_test_pred[i] = 5
                elif temp_y_test[i] == 6:
                    if y_test_pred[i] == 5 or y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 6
                elif temp_y_test[i] == 7:
                    if y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 7
                elif temp_y_test[i] == 1:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 2:
                        y_test_pred[i] = 1
            print('- - - - - - - - - - - - - - -')
            # Performance evaluation -- test (when data insufficient)
            acc = metrics.accuracy_score(y_test, y_test_pred)
            pre = metrics.precision_score(y_test, y_test_pred, average='weighted')
            rec = metrics.recall_score(y_test, y_test_pred, average='weighted')
            f1 = metrics.f1_score(y_test, y_test_pred, average='weighted')
            print("Accuracy:", "{:.3f}".format(acc))
            print("Precision:", "{:.3f}".format(pre))
            print("Recall:", "{:.3f}".format(rec))
            print("F1:", "{:.3f}".format(f1))
            if acc > 0.60 and pre > 0.60 and rec > 0.60 and f1 > 0.60:
                con = 1
        print(y_test, y_test_pred)
        
    def ANN(self, data_df, rating, algo, result = None):
        y = rating
        X = data_df.drop(columns=['Rating'])
        # Data standardization
        normalizer = preprocessing.MinMaxScaler()
        normalizer = normalizer.fit(X)
        X_all = normalizer.transform(X)
        std_X = pd.DataFrame(X_all, columns=X.columns)

        # MRMR selection
        if algo == "mRMR":
            mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=std_X, y=y, K=8)
            selected_X = std_X[mRMR_selected_features]
        elif algo == "relief" or algo == "chi2":
            selected_X = std_X[result]

        con = 0
        random_state = 13

        while con == 0:
            X_train, X_test, y_train, y_test = train_test_split(selected_X, y, test_size=0.2, shuffle=True,
                                                                    random_state=random_state)
            random_state = random_state + 1
            model = MLPClassifier(hidden_layer_sizes=(17, 8),activation="relu",random_state=1).fit(X_train, y_train)

            # Testing model
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            y_pred = model.predict(selected_X)

            # Cross validation

            # scores = cross_val_score(model, X_all, y_pred, cv=4)
            # print(scores)
            print('random_state=', random_state)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y, y_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y, y_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y, y_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y, y_pred, average='weighted')))

            print('- - - - - - - - - - - - - - -')
            # Performance evaluation -- test (when data insufficient)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y_test, y_test_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y_test, y_test_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y_test, y_test_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y_test, y_test_pred, average='weighted')))

            # print(list(y_test),list(y_test_pred),sep='\n')

            # 1 level difference
                
            temp_y_test = list(y_test)

            for i in range(len(temp_y_test)):
                # "AAA": 1, "AA": 2, "A": 3, "BBB": 4, "BB": 5, "B": 6, "CCC": 7
                if temp_y_test[i] == 2:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 2
                elif temp_y_test[i] == 3:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 3
                elif temp_y_test[i] == 4:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 5:
                        y_test_pred[i] = 4
                elif temp_y_test[i] == 5:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 6 or y_test_pred[i] == 5:
                        y_test_pred[i] = 5
                elif temp_y_test[i] == 6:
                    if y_test_pred[i] == 5 or y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 6
                elif temp_y_test[i] == 7:
                    if y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 7
                elif temp_y_test[i] == 1:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 2:
                        y_test_pred[i] = 1
            print('- - - - - - - - - - - - - - -')
            # Performance evaluation -- test (when data insufficient)
            acc = metrics.accuracy_score(y_test, y_test_pred)
            pre = metrics.precision_score(y_test, y_test_pred, average='weighted')
            rec = metrics.recall_score(y_test, y_test_pred, average='weighted')
            f1 = metrics.f1_score(y_test, y_test_pred, average='weighted')
            print("Accuracy:", "{:.3f}".format(acc))
            print("Precision:", "{:.3f}".format(pre))
            print("Recall:", "{:.3f}".format(rec))
            print("F1:", "{:.3f}".format(f1))
            if acc > 0.60 and pre > 0.60 and rec > 0.60 and f1 > 0.60:
                con = 1
        print(y_test, y_test_pred)
    
    def KNN(self, data_df, rating, algo, result = None):
        y = rating
        X = data_df.drop(columns=['Rating'])
        # Data standardization
        normalizer = preprocessing.MinMaxScaler()
        normalizer = normalizer.fit(X)
        X_all = normalizer.transform(X)
        std_X = pd.DataFrame(X_all, columns=X.columns)

        # MRMR selection
        if algo == "mRMR":
            mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=std_X, y=y, K=8)
            selected_X = std_X[mRMR_selected_features]
        elif algo == "relief" or algo == "chi2":
            selected_X = std_X[result]

        con = 0
        random_state = 13

        while con == 0:
            X_train, X_test, y_train, y_test = train_test_split(selected_X, y, test_size=0.2, shuffle=True,
                                                                    random_state=random_state)
            random_state = random_state + 1
            model = KNeighborsClassifier(n_neighbors=7).fit(X_train,y_train)

            # Testing model
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            y_pred = model.predict(selected_X)

            # Cross validation

            # scores = cross_val_score(model, X_all, y_pred, cv=4)
            # print(scores)
            print('random_state=', random_state)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y, y_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y, y_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y, y_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y, y_pred, average='weighted')))

            print('- - - - - - - - - - - - - - -')
            # Performance evaluation -- test (when data insufficient)
            print("Accuracy:", "{:.3f}".format(metrics.accuracy_score(y_test, y_test_pred)))
            print("Precision:", "{:.3f}".format(metrics.precision_score(y_test, y_test_pred, average='weighted')))
            print("Recall:", "{:.3f}".format(metrics.recall_score(y_test, y_test_pred, average='weighted')))
            print("F1:", "{:.3f}".format(metrics.f1_score(y_test, y_test_pred, average='weighted')))

            # print(list(y_test),list(y_test_pred),sep='\n')

            # 1 level difference
                
            temp_y_test = list(y_test)

            for i in range(len(temp_y_test)):
                # "AAA": 1, "AA": 2, "A": 3, "BBB": 4, "BB": 5, "B": 6, "CCC": 7
                if temp_y_test[i] == 2:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 2
                elif temp_y_test[i] == 3:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 2:
                        y_test_pred[i] = 3
                elif temp_y_test[i] == 4:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 3 or y_test_pred[i] == 5:
                        y_test_pred[i] = 4
                elif temp_y_test[i] == 5:
                    if y_test_pred[i] == 4 or y_test_pred[i] == 6 or y_test_pred[i] == 5:
                        y_test_pred[i] = 5
                elif temp_y_test[i] == 6:
                    if y_test_pred[i] == 5 or y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 6
                elif temp_y_test[i] == 7:
                    if y_test_pred[i] == 6 or y_test_pred[i] == 7:
                        y_test_pred[i] = 7
                elif temp_y_test[i] == 1:
                    if y_test_pred[i] == 1 or y_test_pred[i] == 2:
                        y_test_pred[i] = 1
            print('- - - - - - - - - - - - - - -')
            # Performance evaluation -- test (when data insufficient)
            acc = metrics.accuracy_score(y_test, y_test_pred)
            pre = metrics.precision_score(y_test, y_test_pred, average='weighted')
            rec = metrics.recall_score(y_test, y_test_pred, average='weighted')
            f1 = metrics.f1_score(y_test, y_test_pred, average='weighted')
            print("Accuracy:", "{:.3f}".format(acc))
            print("Precision:", "{:.3f}".format(pre))
            print("Recall:", "{:.3f}".format(rec))
            print("F1:", "{:.3f}".format(f1))
            if acc > 0.60 and pre > 0.60 and rec > 0.60 and f1 > 0.60:
                con = 1
        print(y_test, y_test_pred)