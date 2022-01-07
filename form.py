from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DateTimeField, RadioField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from esg_evaluator import *

from flask import Flask, request, session, render_template, redirect, url_for
from flask_uploads import UploadSet, TEXT, DOCUMENTS, configure_uploads
from pathlib import Path
from werkzeug.utils import secure_filename
import os
import re
import json
import time
import bubble_plot
import pandas as pd

from esg_evaluator import util

download_path = (Path.cwd() / 'static/input')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'development'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOADED_DEF_DEST'] = download_path

usr_doc = UploadSet(name='def', extensions=TEXT + DOCUMENTS + tuple(['pdf']))
configure_uploads(app, usr_doc)


class CustomForm(FlaskForm):
    text = TextAreaField(
        'Text we could visualize the extracted key issues and provide explanation issues.', validators=[DataRequired()])
    analytics = RadioField('Analysis Kernel Option', choices=[(
        'wordLv', 'Word-level'), ('sentLv', 'Sentence-level')], default='wordLv')
    annualReport = SelectField('Annual report', choices=[('Material2020', 'Applied Material 2020'), (
        'Material2019', 'Applied Material 2019'), ('Material2018', 'Applied Material 2018')])
    submit = SubmitField("Submit")


@app.errorhandler(413)
def request_entity_too_large(error):
    return '<script>alert("File to large!");window.location.href ="./form";</script>', 413


@app.route('/form', methods=['GET', 'POST'])
def form():
    # print('Entering')
    # form = CustomForm()
    # if form.validate_on_submit():
    #     session['text'] = form.text.data
    #     session['analytics'] = form.analytics.data
    #     session['annualReport'] = form.annualReport.data
    #     print('In')
    #     return redirect(url_for('test'))
    # return render_template('form.html', form=form)
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
        if option == "table":
            session['kernel_option'] = request.form['flexRadioDefault']
            session['report_selector'] = request.form['report-selector']
            redirect(url_for('getPercentage'))
            return redirect(url_for('keyissue'))
        elif option == "report":
            session['kernel_option'] = request.form['flexRadioDefault']
            session['report_selector'] = request.form['report-selector']
            return redirect(url_for('present2'))
        elif option == "text":
            session['kernel_option'] = request.form['flexRadioDefault']
            session['report_selector'] = request.form['report-selector']
            text = request.form['text']
            text = re.sub(u"\\<.*?\\>", "", text)
            text = json.dumps(text.split(' '))
            session['text'] = text
            return redirect(url_for('present2'))
        else:  # "bubblePlot"
            report = request.form['report-selector']
            res = {'E': [[]], 'S': [[]], 'G': [[]]}
            if report != None:
                BUBBLE = bubble_plot.bubble_plot()
                E, S, G = BUBBLE.bubble_weight_multi(report)
                res['E'] = E
                res['S'] = S
                res['G'] = G
            data = json.dumps(res)
            session['data'] = data
            redirect(url_for('updateESG'))
            return redirect(url_for('plot'))
    return '<script>alert("We didn\'t design Get request.");window.location.href ="./form";</script>'


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if 'in_usr_doc' in request.files:
        session['modal'] = "show"
        try:
            filename = usr_doc.save(request.files['in_usr_doc'])
            file_url = usr_doc.url(filename)
            session['msg'] = "Upload Done"
            return redirect(url_for('form'))
        except:
            session['msg'] = "We only accept the file type with document or txt."
            return redirect(url_for('form'))
    else:
        session['msg'] = "Please choose a qualified file."
        return redirect(url_for('form'))


@app.route('/present2')
def present2():
    report = session['report_selector'].split('.')[0]
    report_path = './static/tmp/' + report + '.txt'
    report_kp_path = './static/tmp/' + report + '_key_phrase.txt'
    f = open(report_kp_path, 'r', encoding='utf-8').read()
    data = json.loads(f)
    esg_count = {'Environment': 0, 'Social': 0, 'Governance': 0}
    if session['option'] == "report":
        text = open(report_path, 'r', encoding='utf-8').read().split()
        report_csv_path = './static/tmp/' + report + '.csv'
        report_csv = pd.read_csv(report_csv_path).groupby('Pillar').sum()
        for key in esg_count.keys():
            esg_count[key] = int(report_csv.loc[key].Count)
        esg_count = util.cal_esg_ratio(esg_count)
    else:  # "text"
        text = session['text']
        text = json.loads(text)
        esg_count = util.count_esg_ratio(text, data)

    return render_template('present.html', text=text, data=data, esg_count=esg_count)


@app.route('/present/<action>/<text>')
def present(text, action):
    file = open('./key_phrase.txt', 'r', encoding='utf-8')
    data = file.read()
    return render_template('present.html', text=text.split(' '), action=action, data=json.loads(data))


@app.route('/showReports')
def showReports():
    path = './static/tmp/'
    fullname = os.listdir(path)
    files = list()
    for i in fullname:
        if i[:-4] not in files and 'key_phrase' not in i:
            files.append(i[:-4])
    res = {'files': files}
    session['modal'] = "hide"
    return res

# 氣泡圖繪製相關 (plot.html)
@app.route('/plot')
def plot():
    return render_template('plot.html')

@app.route('/updateESG')
def updateESG():
    data = session['data']
    return data

# Key issue table (key_issue.html)
@app.route('/keyissue')
def keyissue():
    return render_template('key_issue.html')

@app.route('/getPercentage')
def getPercentage():
    report = session['report_selector'].split('.')[0]
    report_csv_path = './static/tmp/' + report + '.csv'
    data = pd.read_csv(report_csv_path)
    res = {'E': {}, 'S': {}, 'G': {}}
    for _ in set(list(data['Pillar'])):
        rows = data.loc[data['Pillar'] == _]
        row_dict = dict(zip(rows.Key_issue, rows.Percentage))
        res[_[0]] = row_dict
    return res


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
