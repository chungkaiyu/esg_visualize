import pandas as pd
import numpy as np
import os
from esg_evaluator import *
class bubble_plot:
    def __init__(self) -> None:
        pass
    def is_csv_exist(self,filename):
        tmp_dir='static/tmp/weight/'
        if os.path.isfile(tmp_dir+filename.split('.')[0]+'.csv'):
            return True
        return False
    def produce_csv(self,filename):
        tmp_dir='static/tmp/'
        input_dir='static/input/'
        dp = DocProcessor()
        print(filename, end=' => ')
        text = dp.get_file_text(input_dir+filename)
        btm = BERT_model(text)
        df = btm.get_issue_keywords(kp_list=True)
        weight = btm.get_key_issue_weight(df)
        file_name = filename.split(".")[0]
        weight.to_csv(tmp_dir+file_name+".csv")
    def produce_plot_weight(self,filename,num=3,label=''):
        tmp_dir='static/tmp/'
        sort_name='Percentage'
        file_name=tmp_dir+filename.split('.')[0]+'.csv'
        E,S,G = list(),list(),list()
        df = pd.DataFrame()
        tmp = pd.read_csv(file_name)
        tmp = tmp.sort_values(sort_name,ascending=False).groupby('Pillar').head(num)
        df = pd.concat([df,tmp],axis=0,ignore_index=True)
        MinMaxScaler=df['MinMaxScaler'].to_list()
        Year=label
        Weight=df['Weight'].to_list()
        Pillar=df['Pillar'].to_list()
        Key_issue=df['Key_issue'].to_list()
        for i in range(len(MinMaxScaler)):
            tmp=[Year,MinMaxScaler[i],Weight[i],Key_issue[i]]
            if Pillar[i]=='Environment':
                E.append(tmp)
            elif Pillar[i]=='Social':
                S.append(tmp)
            else:
                G.append(tmp)
        return E, S, G
    def bubble_weight_single(self,filename,label,num=3):
        if not self.is_csv_exist(filename):
            self.produce_csv(filename)
        return self.produce_plot_weight(filename,num,label=label)
    def getcompanyfiles(self,comapny_name):
        tmp_dir='static/tmp/'
        files=list()
        for filename in os.listdir(tmp_dir):
            if comapny_name in filename and '.csv' in filename:
                files.append(filename)
        return files
    def get_year(self,name):
        for i in range(len(name)-3):
            if name[i:i+4].isdigit() and int(name[i:i+4]) > 2000:
                return name[i:i+4]
        return ''
    def bubble_weight_multi(self,comapny_name,num=3):
        files=self.getcompanyfiles(comapny_name)
        E, S, G = list(),list(),list()
        for filename in files:
            #year=filename.split('-')[1]
            year=self.get_year(filename.split('.')[0])
            tmp_E,tmp_S,tmp_G = self.bubble_weight_single(filename,label=year)
            E+=tmp_E
            S+=tmp_S
            G+=tmp_G
        return E,S,G
    def bubble_compare_with_applied(self,file_name,num=3):
        year='2020'
        files=[tmp_dict[file_name]+'.csv']
        tmp_dir='static/tmp/'
        for f in os.listdir(tmp_dir):
            if 'Applied' in f and '.csv' in f and year in f:
                files.append(f)
        print(files)
        E, S, G = list(),list(),list()
        for filename in files:
            # company_name=filename.split('-')[2].split('(')[0]
            company_name=filename
            tmp_E,tmp_S,tmp_G = self.bubble_weight_single(filename,label=company_name+'-'+year)
            E+=tmp_E
            S+=tmp_S
            G+=tmp_G
        return E,S,G
    #這個上面的都是舊算法，但是先不刪，確定不會用到再拿掉
    def produce_plot_weight_for_wieght3(self,filename,num=3,label=''):
        sort_name='Weight'
        file_name=f'static/tmp/weight/{filename}.csv'
        df = pd.DataFrame()
        tmp = pd.read_csv(file_name)
        tmp = tmp.sort_values(sort_name,ascending=False)
        df = pd.concat([df,tmp],axis=0,ignore_index=True)
        Count=df['Count'].to_list()
        Weight=df['Weight'].to_list()
        Pillar=df['Pillar'].to_list()
        Similarity=df['Similarity'].to_list()
        Key_issue=df['Key_issue'].to_list()
        Doc_word=df['Doc_word'].to_list()
        E, S, G = list(), list(), list()
        for i in range(len(Weight)):
            tmp=[Weight[i],Similarity[i],Count[i],Key_issue[i],Pillar[i],Doc_word[i]]
            if Pillar[i]=='Environment':
                E.append(tmp)
            elif Pillar[i]=='Social':
                S.append(tmp)
            else:
                G.append(tmp)
        return E,S,G
    def produce_plot_weight_compare_with_applied_w3(self,filename,num=3,label=''):
        sort_name='Weight'
        year, _, report_type = filename.split('-')
        applied_type = report_type if report_type in ['Annual', 'Sustainability', '10K'] else 'Sustainability'
        files=[f'static/tmp/weight/{filename}.csv',f'static/tmp/weight/{year}-Applied-{applied_type}.csv']
        company_weight = [[],[]]
        for j in range(len(files)):
            df = pd.DataFrame()
            file_name=files[j]     
            tmp = pd.read_csv(file_name)
            tmp = tmp.sort_values(sort_name,ascending=False).head(num*3)
            df = pd.concat([df,tmp],axis=0,ignore_index=True)
            Count=df['Count'].to_list()
            Weight=df['Weight'].to_list()
            Pillar=df['Pillar'].to_list()
            Similarity=df['Similarity'].to_list()
            Key_issue=df['Key_issue'].to_list()
            Doc_word=df['Doc_word'].to_list()
            for i in range(len(Weight)):
                tmp=[Weight[i],Similarity[i],Count[i],Key_issue[i],Pillar[i],Doc_word[i]]
                company_weight[j].append(tmp)
        return company_weight[0],company_weight[1],filename