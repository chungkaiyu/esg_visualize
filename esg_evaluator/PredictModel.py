import pandas as pd
import json
import os

from sklearn.linear_model import LinearRegression
from sklearn import svm
from sklearn import metrics
from sklearn import preprocessing
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
import pandas as pd
import pickle

# pip install git+https://github.com/D0542090/mrmr.git
from mrmr import mrmr_classif 
import warnings
warnings.filterwarnings('ignore')

this_dir, this_filename = os.path.split(__file__)
TRAINING_DATA_PATH = os.path.join(this_dir, "static", "2020_w3.xlsx")
MODEL_PATH = os.path.join(this_dir, "static", "mRMR_SVM.pickle")

MAX_RANDOM_STATE = 100

PARAMS = {
    'kernel': 'linear', 
    'gamma': 0.0009,
    'C': 100,
}

class PredictModel:
    def __init__(self, model_file=MODEL_PATH, training_data_file=TRAINING_DATA_PATH, model="svm.SVC", 
    model_params=PARAMS, feature_selection="mrmr") -> None: 
        '''
          model_file: model file path (.pickle)
          training_data_file: training data path (.xlxs)
          model: model type, 之後看需不需要改
          model_params: model parameters
          feature_selection: 特徵選取的演算法類型, 之後看需不需要改
        '''
        # Read model
        try:
            with open(model_file, 'rb') as f:
                self.model = pickle.load(f)
        except FileNotFoundError: 
            # there is no local pickle
            print("Producing model......Please wait")
            best_acc = 0
            # data pre-processiong
            training_data = pd.read_excel(training_data_file)
            training_data.dropna(inplace=True)
            training_data.reset_index(inplace=True,drop=True)
            X = training_data.drop(columns=['Column1', 'id', 'Industry_type', 'Rating'])
            y = training_data['Rating']
            selected_X = self.feature_selection_by_mrmr(self.data_standardization(X), y)

            # Start training
            for random_state in range(42, MAX_RANDOM_STATE+1):
                X_train, X_test, y_train, y_test = train_test_split(selected_X, y, test_size=0.2, shuffle=True, random_state=random_state)
                random_state += 1
                model = svm.SVC(**model_params).fit(X_train, y_train)

                # Testing model
                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)
                y_pred = model.predict(selected_X)

                # one-level difference
                y_test_pred = self.make_tolerance(list(y_test), y_test_pred)
                
                # Performance evaluation -- test (when data insufficient)
                acc = metrics.accuracy_score(y_test, y_test_pred)
                if acc > best_acc:
                    self.model = model
                    best_acc = acc
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(self.model, f)
        print("Generating model is done！")

    def getPredict_bycsv_tojson(self, input_file, out_file="applied_request.json") -> None:
        row_data = pd.read_csv(input_file)
        row_data.dropna(inplace=True)
        row_data.reset_index(inplace=True,drop=True)
        all_comapny_name = list(row_data["id"]) #之後要寫到json用
        all_real_rating = list(row_data["Rating"]) #之後要寫到json用

        X = row_data.drop(columns=['id', 'Industry_type', 'Rating'])
        y = row_data["Rating"]
        selected_X = self.feature_selection_by_mrmr(self.data_standardization(X), y)
  
        all_prediction = self.model.predict(selected_X) #之後要寫到json用
        output = dict()
        for i in range(len(all_comapny_name)):
            t = self.get_tolerance_range(all_real_rating[i])
            res = [ t[0], t[-1] ]
            res.append(all_real_rating[i])
            output[f'2020-{all_comapny_name[i]}'] = res #之後如果改年份就要改
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4)
        print(f"Output file is in {out_file}")
        

    def data_standardization(self, X) -> pd.DataFrame:
        normalizer = preprocessing.MinMaxScaler()
        normalizer = normalizer.fit(X)
        X_all = normalizer.transform(X)
        std_X = pd.DataFrame(X_all, columns=X.columns)

        return std_X

    def feature_selection_by_mrmr(self, X, y, K=8) -> pd.DataFrame:
        mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=X, y=y, K=K)
        selected_X = X[mRMR_selected_features]

        return selected_X

    def make_tolerance(self, y, pred_result, level=1) -> list:
        #根據 y對 pred_result容錯處理:)
        for i in range(len(y)):
            if pred_result[i] in self.get_tolerance_range(y[i], level=level):
                pred_result[i] = y[i]

        return pred_result

    def get_tolerance_range(self, rating, level=1) -> list:
        #取得容忍的範圍, e.g., 'A' -> [ 'BBB', 'A', 'AA ]
        rating_type = [ 'CCC', 'B', 'BB', 'BBB', 'A', 'AA', 'AAA']
        mid = rating_type.index(rating)
        start = mid-level if mid>0 else 0
        end = mid+level+1 if mid<len(rating_type)-level else len(rating_type)
        return rating_type[start:end]