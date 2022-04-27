import pandas as pd

class WeightFileProcessor():
    # Get the file
    # Only Excel file available at the moment.
    def get_file(self, filename):
        f_extension = filename.split('.')[-1]
        if f_extension in ["xlsx"]:
            data_df = self.read_excel_text(filename)
        elif f_extension in ["csv"]:
            data_df = self.read_csv_text(filename)
        else:
            print("Unknown Filename Extension")
        print("Read successfully")
        return data_df

    # read the excel file and clean nan/empty value
    def read_excel_text(self, filename):
        data_df = pd.read_excel(filename)
        #data_df = data_df.dropna().reset_index(drop=True)
        data_df = data_df.dropna()
        return data_df

    # read the csv file and clean nan/empty value
    def read_csv_text(self, filename):
        data_df = pd.read_csv(filename)
        #data_df = data_df.dropna().reset_index(drop=True)
        return data_df