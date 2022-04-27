import pandas as pd
import matplotlib.pyplot as plt

# 1.Read the weight file. (xlsx only)
# 2.Get the basic statistical description.
# 3.Draw the boxplot

# Format of weight file
# Id | 35 Key issues | Rating | Industry_type

class DataDescription():
    def __init__(self):
        self.data_df = ''
        self.filename = ''

    # TBD
    def plot_boxplot(self, data_df):
        X = data_df.drop(columns=['Id', 'Industry_type', 'Rating'])
        temp_X = X.iloc[:0,18]
        Boxplot = plt.boxplot(temp_X)
        Boxplot.set_xlabel('Feature')
        Boxplot.set_ylabel('Weight')
        Boxplot.get_figure()
        plt.show()

    # Save mean, standard deviation, min and max value to a excel file
    # It just optional.
    def save_data_description(self, data_df, filename):
        feature_name = list(data_df.index)
        mean = []
        std = []
        min = []
        max = []

        for i in range(len(data_df)):
            mean.append(round(data_df.iloc[i]['mean'], 2))
            std.append(round(data_df.iloc[i]['std'], 2))
            min.append(round(data_df.iloc[i]['min'], 2))
            max.append(round(data_df.iloc[i]['max'], 2))

        data_stat = pd.DataFrame({
            'Feature': feature_name,
            'Min': min,
            'Max': max,
            'Mean': mean,
            'Std': std,
        })
        #data_stat.to_excel('data_stat.xlsx')
        data_stat.to_excel(filename + '_data_description.xlsx')

    # View some basic statistical details
    def get_data_description(self, data_df):
        data_description = data_df.describe()
        data_description = data_description.T
        return data_description
