from fileinput import filename
import pandas as pd
import numpy as np
import json
import re
import os
import fitz
class Dominate_page:
    def run(filename='Test10-2020-Microsoft(CSR-Report).pdf'):
        # read pdf
        pdf = fitz.open('find_domate_page/input/'+filename)
        df = pd.read_csv('find_domate_page/key_phrase/'+filename.split('.')[0]+'.csv')
        df=df.to_numpy()
        key_issue={}
        for i in df:
            if i[1] not in key_issue:
                key_issue[i[1]]={'key_phrase':[],'page_percentage':[0]*len(pdf)}
            key_issue[i[1]]['key_phrase'].append([i[3],i[5]])
        # get words of each pages
        page_content=[]
        for i in pdf:
            page_content.append("")
        no = 0
        for page in pdf:
            # use get_text('blocks') instead of get_text('text')
            # each blocks entry is [x0, y0, x1, y1, word, block_id, line_id]
            blocks = page.get_text('blocks')
            blocks = sorted(blocks, key = lambda b: (b[0], b[1]))
            for block_word in blocks:
                if block_word[4].startswith( '<image:'):
                    continue
                elif len( block_word[4].replace('\n','') ) < 10:
                    continue
                page_content[no] += block_word[4]
            no+=1
        # calculate the key issue weight of each page
        for i in range(len(page_content)):
            for issue in key_issue:
                weight=0 # weight= avg(Similarity of Word Use in Key Issue) * len(Similarity of Word Use in Key Issue) = sum(Similarity of Word Use in Key Issue )
                for pharse in key_issue[issue]['key_phrase']:
                    weight+=pharse[1]
                for pharse in key_issue[issue]['key_phrase']:
                    key_issue[issue]['page_percentage'][i] += page_content[i].count(pharse[0])*weight
                    if pharse[0]=='materials':# exclude the influence of 'applied materials' in weight
                        key_issue[issue]['page_percentage'][i] -= page_content[i].count('applied materials')*weight
        # OUTPUT
        # calculate the percentage of each page for key issue weight and get the dominate page for each key issue
        key_issue_dominate_page={}
        for issue in key_issue:
            MAX=0
            max_page=0
            key_phrase=list()
            for i  in key_issue[issue]['key_phrase']:
                key_phrase.append(i[0]) 
            sum=0
            for i in range(len(pdf)):
                sum+=key_issue[issue]['page_percentage'][i]
            for i in range(len(pdf)):
                key_issue[issue]['page_percentage'][i]=key_issue[issue]['page_percentage'][i]/sum*100
            for i in range(len(pdf)):
                if key_issue[issue]['page_percentage'][i]>MAX:
                    MAX = key_issue[issue]['page_percentage'][i]
                    max_page = i
            key_issue_dominate_page[issue]={'max_page':max_page+1,'percetage':MAX,'key_phrase':key_phrase}
            #print(issue+': '+str(max_page+1)+'('+str(round(MAX,3))+'%)'+', key_parse: '+key_phrase)
        return key_issue_dominate_page

key_issue_dominate_page=Dominate_page.run('Test10-2020-Microsoft(CSR-Report).pdf')
print(key_issue_dominate_page)