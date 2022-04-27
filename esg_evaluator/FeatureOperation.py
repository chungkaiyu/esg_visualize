import numpy as np
from skrebate import ReliefF
import pandas as pd
from sklearn import metrics, svm
from sklearn import preprocessing
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from numpy import mean
from mrmr import mrmr_classif

import warnings
warnings.filterwarnings('ignore')

# Feature Extraction and Feature Selection will be implemented.

class FeatureOperation():
    '''
    Data Preprocess
    1. Drop the nan value.
    2. Encode rating as number.
    3. Drop the values of Column1, id and Industry_type.
    '''
    def preprocess(self, data_df) -> pd.DataFrame:
        data_df.dropna(inplace=True)
        data_df.reset_index(inplace=True, drop=True)
        data_df["Rating"] = data_df["Rating"].map({"AAA": 1, "AA": 2, "A": 3, "BBB": 4, "BB": 5, "B": 6, "CCC": 7})
        data_df = data_df.drop(columns=['Column1', 'id', 'Industry_type'])
        return data_df

    def extractRating(self, data_df):
        rating = data_df["Rating"]
        return rating

    def extractWeight(self, data_df):
        weight = data_df.drop("Rating", axis=1).values
        return weight
    
    # Under Maintenance
    def extractWeightAndRating(self, data_df):
        fo = FeatureOperation()
        weight = fo.extractWeight(data_df)
        rating = fo.extractRating(data_df)
        return [weight, rating]
    
    '''
    Acquiring feature importance Scores and feature with relief algorithm
    Return the relief score of 35 key issues one by one
    Output Format: Feature sorted with 'relief_score' in ascending order
                   Key Issues | Relief Score
    If relief score > 0.8, it means that the relevance of that key issues is too high.
    If relief score is close to 0, it means that the relevance of key issues to rating is very low.
    '''
    
    # For Step 7 (apple to apple comparison?)
    def reliefResult(self, data_df):
        fo = FeatureOperation()
        weight = fo.extractWeight(data_df)
        rating = fo.extractRating(data_df)
        rating = np.asarray(rating)
        
        clf = ReliefF()
        clf.fit(weight, rating)
        relief_result = pd.DataFrame({'Feature':data_df.drop('Rating', axis=1).columns, 'relief_score': clf.feature_importances_})
        relief_result.sort_values(by=['relief_score'], ascending=False, inplace=True)
        return relief_result
    
    # For Step 5
    def reliefFeature(self, data_df, numFeatures=10):
        fo = FeatureOperation()
        relief_result = fo.reliefResult(data_df)
        relief_features = relief_result['Feature'].tolist()
        return relief_features[:numFeatures]
    
    '''
    Acquiring feature importance Scores with chi-squared formula
    Return the chi-squared result of 35 key issues one by one
    Output Format: Feature(key issues), chi2_score
    
    param
    numFeatures: number of features with highest chi-squared statistics
    '''
    def chi2Result(self, data_df, bestFeatures=10):
        fo = FeatureOperation()
        weight = fo.extractWeight(data_df)
        rating = fo.extractRating(data_df)
        
        chi2Selector = SelectKBest(chi2, k=bestFeatures)
        chi2Selector.fit(weight, rating)
        chi2_result = pd.DataFrame(list(zip(data_df.drop('Rating', axis=1).columns, chi2Selector.scores_)),
                                   columns=['Feature', 'chi2_score'])
        chi2_result.sort_values(by=['chi2_score'], ascending=False, inplace=True)
        return chi2_result
    
    def chi2Feature(self, data_df, bestFeatures=10, numFeatures=10):
        fo = FeatureOperation()
        chi2_result = fo.chi2Result(data_df, numFeatures)
        chi2_features = chi2_result['Feature'].tolist()
        return chi2_features[:numFeatures]
    
    def mRMRFeature(self, data_df, rating, numFeatures):
        X = data_df.drop(columns=['Rating'])
        std_X = self.data_standardization(X)
        mRMR_selected_features, scores = mrmr_classif(X=std_X, y=rating, K=numFeatures)
        return mRMR_selected_features 

    def data_standardization(self, weight):
        normalizer = preprocessing.MinMaxScaler()
        normalizer = normalizer.fit(weight)
        weight_all = normalizer.transform(weight)
        std_weight = pd.DataFrame(weight_all, columns=weight.columns)
        return std_weight

    def convert2Dict(self, feature_number, accuracy, recall, F1, precision):
        temp_dict = {
            'Number of features': feature_number,
            'Accuracy': accuracy,
            'Recall': recall,
            'F1': F1,
            'Precision': precision
        }
        result = pd.DataFrame(temp_dict)
        result.sort_values(by=['Recall', 'F1', 'Precision'], ascending=False, inplace=True)
        return result

    '''
    Classification method: Precision, Recall and F1 are used
    Precision: The part of the data detected by the classifier that is correctly classified (被分类器检测到的数据中分类正确的部分)
    Recall: Positive Class that is classified correctly (正类中被分类正确的部分)
    F1: Reconciled average of accuracy and recall (准确率和召回率的调和平均数)
    
    Param explanation
    rating: AAA->1, AA->2, etc.
    algo: relief, mrmr, chi2 (new feature extraction/selection algorithms maybe used in the future)
    c: Inverse of regularization strength; must be a positive float. Like in support vector machines, smaller values specify stronger regularization.
       We use 10 and 100 (same as colab file)
    result: If you use mRMR, it should be None.  
    
    Notes
    Result are sorted with Recall, F1, Precision because they are more suitable indicators in classification problem.
    recall/f1/precision_macro are used because I think the class imbalance is not exist in the data. 
    If there is class imbalance, used micro instead of macro. 
    '''
    def featureSelectionWithLR(self, weight, rating, algo, result=None):
        std_weight = self.data_standardization(weight)

        PARAMS = [10, 100]

        # We think that rank 20-35 features are not important
        for c in PARAMS:
            feature_number, accuracy, recall, F1, precision = [], [], [], [], []
            for i in range(3, 20):
                if algo == "relief" :
                    #relief_selected_features = list(result['Feature'].iloc[0:i].values)
                    relief_selected_features = list(result)[0:i]
                    selected_features = std_weight[relief_selected_features]
                elif algo == "mRMR":
                    mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=std_weight, y=rating, K=i)
                    selected_features = std_weight[mRMR_selected_features]
                elif algo == "chi2":
                    chi2_selected_features = list(result)[0:i]
                    selected_features = std_weight[chi2_selected_features]

                #model = LogisticRegression(C=c)
                model = LogisticRegression(C=c)

                # cross validation
                # define cross-validation method to use
                cv = LeaveOneOut()

                # use LOOCV to evaluate model
                feature_number.append(i)
                accuracy.append(mean(cross_val_score(model, selected_features, rating, cv=cv, scoring='accuracy')))
                recall.append(mean(cross_val_score(model, selected_features, rating, cv=cv, scoring='recall_macro')))
                F1.append(mean(cross_val_score(model, selected_features, rating, cv=cv, scoring='f1_macro')))
                precision.append(mean(cross_val_score(model, selected_features, rating, cv=cv, scoring='precision_macro')))

            selected_result = self.convert2Dict(feature_number, accuracy, recall, F1, precision)
            print("----------------------")
            print(selected_result)
        #return result
        return None


    def featureSelectionWithSVC(self, weight, rating, algo, result=None):
        std_weight = self.data_standardization(weight)
        '''
        PARAMS = {
            'gamma': [0.0009, 0.001, 0.01],
            'C': [100, 10, 1]
        }
        '''
        gamma = [0.0009, 0.001, 0.01]
        C = [100, 10, 1]

        # We think that rank 21-35 features are not important
        for index in range(len(gamma)):
            feature_number, accuracy, recall, F1, precision = [], [], [], [], []
            for i in range(3, 20):
                if algo == "relief":
                    # relief_selected_features = list(result['Feature'].iloc[0:i].values)
                    relief_selected_features = list(result)[0:i]
                    selected_features = std_weight[relief_selected_features]
                elif algo == "mRMR":
                    mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=std_weight, y=rating, K=i)
                    selected_features = std_weight[mRMR_selected_features]
                elif algo == "chi2":
                    chi2_selected_features = list(result)[0:i]
                    selected_features = std_weight[chi2_selected_features]

                model = svm.SVC(kernel='linear',gamma=gamma[index], C=C[index])

                # cross validation
                # define cross-validation method to use
                cv = LeaveOneOut()

                # use LOOCV to evaluate model
                feature_number.append(i)
                accuracy.append(mean(cross_val_score(model, selected_features, rating, cv=cv, scoring='accuracy')))
                recall.append(mean(cross_val_score(model, selected_features, rating, cv=cv, scoring='recall_macro')))
                F1.append(mean(cross_val_score(model, selected_features, rating, cv=cv, scoring='f1_macro')))
                precision.append(mean(cross_val_score(model, selected_features, rating, cv=cv, scoring='precision_macro')))

            selected_result = self.convert2Dict(feature_number, accuracy, recall, F1, precision)
            print("----------------------")
            print(selected_result)
        return None

    def featureSelectionWithKNN(self, data_df, rating, algo, neighbours, result=None):
        X = data_df.drop(columns=['Rating'])
        std_X = self.data_standardization(X)

        feature_number, accuracy, recall, F1, precision = [], [], [], [], []

        # We think that rank 21-35 features are not important
        for i in range(3, 20):
            if algo == "relief" or algo == "chi2":
                selected_features = list(result['Feature'].iloc[0:i].values)
                selected_X = std_X[selected_features]
            elif algo == "mRMR":
                mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=std_X, y=rating, K=i)
                selected_X = std_X[mRMR_selected_features]

            model = KNeighborsClassifier(n_neighbors = neighbours)

            # cross validation
            # define cross-validation method to use
            cv = LeaveOneOut()

            # use LOOCV to evaluate model
            feature_number.append(i)
            accuracy.append(mean(cross_val_score(model, selected_X, rating, cv=cv, scoring='accuracy')))
            recall.append(mean(cross_val_score(model, selected_X, rating, cv=cv, scoring='recall_macro')))
            F1.append(mean(cross_val_score(model, selected_X, rating, cv=cv, scoring='f1_macro')))
            precision.append(mean(cross_val_score(model, selected_X, rating, cv=cv, scoring='precision_macro')))

        result = self.convert2Dict(feature_number, accuracy, recall, F1, precision)
        return result

    def featureSelectionWithDT(self, data_df, rating, algo, result=None):
        X = data_df.drop(columns=['Rating'])
        std_X = self.data_standardization(X)

        feature_number = []
        accuracy = []
        recall = []
        F1 = []
        precision = []

        # We think that rank 21-35 features are not important
        for i in range(3, 20):
            if algo == "relief" or algo == "chi2":
                selected_features = list(result['Feature'].iloc[0:i].values)
                selected_X = std_X[selected_features]
            elif algo == "mRMR":
                mRMR_selected_features, mRMR_feature_score = mrmr_classif(X=std_X, y=rating, K=i)
                selected_X = std_X[mRMR_selected_features]

            model = DecisionTreeClassifier()

            # cross validation
            # define cross-validation method to use
            cv = LeaveOneOut()

            # use LOOCV to evaluate model
            feature_number.append(i)
            accuracy.append(mean(cross_val_score(model, selected_X, rating, cv=cv, scoring='accuracy')))
            recall.append(mean(cross_val_score(model, selected_X, rating, cv=cv, scoring='recall_macro')))
            F1.append(mean(cross_val_score(model, selected_X, rating, cv=cv, scoring='f1_macro')))
            precision.append(mean(cross_val_score(model, selected_X, rating, cv=cv, scoring='precision_macro')))

        result = self.convert2Dict(feature_number, accuracy, recall, F1, precision)
        return result