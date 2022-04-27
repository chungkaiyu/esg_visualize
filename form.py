from esg_evaluator import *
import bubble_plot

from flask import Flask, request, session, render_template, redirect, url_for
from flask_uploads import UploadSet, TEXT, DOCUMENTS, configure_uploads
from pathlib import Path
import os
import re
import json
import pandas as pd

# Setting Flask environment
download_path = (Path.cwd() / 'static/input')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'development'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOADED_DEF_DEST'] = download_path

# Upload Setting
usr_doc = UploadSet(name='def', extensions=TEXT + DOCUMENTS + ('PDF', 'pdf'))
configure_uploads(app, usr_doc)

# When an upload file exceeds 16MB


@app.errorhandler(413)
def request_entity_too_large(error):
    session['msg'] = "File to large!"
    session['modal'] = "show"
    return redirect(url_for('form'))


@app.route('/form', methods=['GET', 'POST'])
def form():
    if session.get('msg'):
        if session.get('modal'):
            return render_template('form.html', msg=session['msg'], s=session['modal'])
        else:
            return render_template('form.html', msg=session['msg'], s="hide")
    else:
        return render_template('form.html', msg="Please choose a qualified file.", s="hide")


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        option = request.form['plotRadio']
        session['option'] = option
        session['year'] = request.form['year-selector']
        session['company'] = request.form['company-selector']
        session['type'] = request.form['report-selector']
        print(request.form.get('year-selector'))
        print(request.form.get('company-selector'))
        print(request.form.get('report-selector'))
        report = f'{session["year"]}-{session["company"]}-{session["type"]}'
        if option == "table":
            session['kernel_option'] = request.form['flexRadioDefault']
            redirect(url_for('getPercentage'))
            return redirect(url_for('keyissue'))
        elif option == "report":
            session['kernel_option'] = request.form['flexRadioDefault']
            return redirect(url_for('present'))
        elif option == "text":
            session['kernel_option'] = request.form['flexRadioDefault']
            session['text'] = request.form['text']
            return redirect(url_for('present'))
        else:  # 泡泡圖
            # res = {'E': [[]], 'S': [[]], 'G': [[]]}
            # if report != None:
            #     BUBBLE = bubble_plot.bubble_plot()
            #     if option == "bubblePlot":
            #         E, S, G = BUBBLE.produce_plot_weight_for_wieght3(report)
            #         session['plot_title'] = report
            #     else:
            #         E, S, G = BUBBLE.produce_plot_weight_compare_with_applied_w3(
            #             report)
            #         session['plot_title'] = report+' v.s. '+'Applied'
            #     res['E'] = E
            #     res['S'] = S
            #     res['G'] = G
            # data = json.dumps(res)
            # session['data'] = data
            # redirect(url_for('updateESG'))
            return redirect(url_for('test_plot'))
    return '<script>alert("We didn\'t design Get request.");window.location.href ="./form";</script>'


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if 'in_usr_doc' in request.files:
        session['modal'] = "show"
        try:
            usr_doc.save(request.files['in_usr_doc'])
            session['msg'] = "Upload Done"
            return redirect(url_for('form'))
        except:
            session['msg'] = "We only accept the file type with document or txt."
            return redirect(url_for('form'))
    else:
        session['msg'] = "Please choose a qualified file."
        return redirect(url_for('form'))


@app.route('/present')
def present():
    year = session['year']
    company = session['company']
    report_type = session['type']
    report = f'{year}-{company}-{report_type}'
    report_path = './static/tmp/text/' + report + '.txt'
    if session['kernel_option'] == 'Word-level':
        report_kp_path = './static/tmp/keyphrase_word/' + report + '_keyphrase_word.txt'
    else:
        report_kp_path = './static/tmp/keyphrase_sentence/' + \
            report + '_keyphrse_sentence.txt'  # 下一版名字要改對
    kp_file = open(report_kp_path, 'r', encoding='utf-8').read()
    data = json.loads(kp_file)
    # Msci rating
    rating_file = open('./static/input/applied_request.json',
                       'r', encoding='utf-8').read()
    msci = json.loads(rating_file)
    try:
        msci = msci[report]
    except:
        msci[0] = '?'
        msci[1] = '?'
        msci[2] = '?'

    esg_count = {'Environment': 0, 'Social': 0, 'Governance': 0}
    # Highlighting
    opt = 'word' if session['kernel_option'] == 'Word-level' else 'sentence'
    if session['option'] == "report":
        # 暫存版本
        text = open(report_path, 'r', encoding='utf-8').read()
        text = util.step3_compare(text, data, opt=opt)
        # 直接讀取
        # dp = DocProcessor()
        # text = dp.get_file_text_with_pageNo( filename='./static/input/'+report +'.pdf' )
        ###
        report_csv_path = './static/tmp/weight/' + report + '.csv'
        report_csv = pd.read_csv(report_csv_path).groupby('Pillar').sum()
        for key in esg_count.keys():
            esg_count[key] = float(report_csv.loc[key].Weight)
    else:  # "text"
        text = session['text']
        print(text)
        #text = json.loads(text)
        text = util.step3_compare(text, data, opt=opt)
        esg_count = util.count_esg_ratio(text, data)
        # Predicted rating tmp
        msci[0] = '?'
        msci[1] = '?'
    return render_template('present.html', text=text, data=data, esg_count=esg_count, msci=msci)


@app.route('/showReports')
def showReports():
    path = './static/input/'
    fullname = os.listdir(path)
    fullname = [tmp[:-4] for tmp in os.listdir(path) if tmp.endswith('.pdf')]

    # 舊的 => res = {'files': files(list), 'opt': 'report'}
    c_list = list()
    y_list = list()
    r_list = list()

    for f in fullname:
        y_list.append(f.split("-")[0])
        c_list.append(f.split("-")[1])
        r_list.append(f.split("-")[2])

    all_company = sorted(list(set(c_list)))
    # 依產業分開 TO DO?
    # map = pd.read_excel('./static/tmp/ESG rating.xlsx')
    # c_category = dict()
    # for c in all_company:
    #     subindustry = map.loc[map['Company'] == c,'SubIndustry'].iloc[0]
    #     if subindustry not in c_category.keys():
    #         c_category[subindustry] = list()
    #     c_category[subindustry].append(c)
    # for _ in c_category.values():
    #     sorted( _ )

    # , 'category':c_category }
    return {'files': fullname, 'company': all_company, 'year': sorted(list(set(y_list))), 'type': sorted(list(set(r_list)))}


@app.route('/getReportList', methods=['POST', 'GET'])
def getReportList():
    company = request.form['company']
    year = request.form['year']

    path = './static/input/'
    fullname = os.listdir(path)
    fullname = [tmp[:-4] for tmp in os.listdir(path) if tmp.endswith('.pdf')]

    r_list = list()
    for f in fullname:
        if company in f and year in f:
            r_list.append(f.split("-")[2])

    return {'type': r_list}

# 氣泡圖繪製相關 (plot.html)


@app.route('/plot')
def plot():
    # 這邊的company就是選項上的字
    return render_template('plot.html', plot_title=session['plot_title'])


@app.route('/updateESG')
def updateESG():
    data = session['data']
    return data


@app.route('/keyissue')
def keyissue():
    return render_template('key_issue.html')


@app.route('/getPercentage')
def getPercentage():
    # company = session['company'] #其實company只是選項上的字，例如 2020-ALPHABET-10K
    year = session['year']
    firm = session['company']
    report_type = session['type']
    company = f'{year}-{firm}-{report_type}'
    # python string format => 例如 static/tmp/weight/2020-ALPHABET-10K.csv
    file_name = f"static/tmp/weight/{company}.csv"
    selected = pd.read_csv(file_name)
    # ---------------------------------------------------------------- #
    applied_type = report_type if report_type in [
        'Annual', 'Sustainability', '10K'] else 'Sustainability'
    file_name = f"static/tmp/weight/{year}-Applied-{applied_type}.csv"
    # ---------------------------------------------------------------- #
    applied = pd.read_csv(file_name)
    # e.g., 'E': { 'k_name':[], 's_weight':[], 'a_weight':[] }
    res = {'E': {}, 'S': {}, 'G': {}}
    for _ in set(list(selected['Pillar'])):
        rows = selected.loc[selected['Pillar'] == _]
        res[_[0]]['k_name'] = rows.Key_issue.tolist()
        res[_[0]]['s_weight'] = rows.Weight.tolist()
        rows = applied.loc[applied['Pillar'] == _]
        res[_[0]]['a_weight'] = rows.Weight.tolist()
    res['selected_company'] = company
    return res


@app.route('/test_plot')
def test_plot():
    year = session['year']
    company = session['company']
    report_type = session['type']

    sl = Sentence_Level()
    test_df = sl.industry_weight(
        report_type=report_type, industry_type='Information Technology')
    plot = sl.plot_graph(company_name=company, data=test_df)

    return render_template('test_plot.html', graphJSON=plot)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
