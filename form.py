from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DateTimeField,RadioField, SelectField,TextAreaField, SubmitField
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

download_path = (Path.cwd() / 'static/input')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'development'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOADED_DEF_DEST'] = download_path

usr_doc = UploadSet(name='def', extensions=TEXT + DOCUMENTS + tuple(['pdf']))
configure_uploads(app, usr_doc)

class CustomForm(FlaskForm):
    text = TextAreaField('Text we could visualize the extracted key issues and provide explanation issues.', validators=[DataRequired()])
    analytics = RadioField('Analysis Kernel Option', choices=[('wordLv','Word-level'),('sentLv','Sentence-level')], default = 'wordLv')
    annualReport = SelectField('Annual report', choices=[('Material2020','Applied Material 2020'),('Material2019','Applied Material 2019'),('Material2018','Applied Material 2018')])
    submit = SubmitField("Submit")

@app.errorhandler(413)
def request_entity_too_large(error):
    return '<script>alert("File to large!");window.location.href ="./form";</script>', 413


@app.route('/form', methods=['GET', 'POST'])
def form():
    print('Entering')
    # form = CustomForm()
    # if form.validate_on_submit():
    #     session['text'] = form.text.data
    #     session['analytics'] = form.analytics.data
    #     session['annualReport'] = form.annualReport.data
    #     print('In')
    #     return redirect(url_for('test'))
    # return render_template('form.html', form=form)
    if session.get('msg') == True:
        return render_template('form.html', msg = session['msg'])
    else:
        return render_template('form.html', msg = "Please choose a qualified file.")


@app.route('/test')
def test():
    print('Hello')
    return render_template('test.html')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        option = request.form['plotRadio']
        session['option'] = option
        if option =="report":
            session['kernel_option'] = request.form['flexRadioDefault']
            session['report_selector'] = request.form['report-selector']
            return redirect(url_for('present2'))
        elif option =="text":
            session['kernel_option'] = request.form['flexRadioDefault']
            session['report_selector'] = request.form['report-selector']
            text = request.form['text']
            text = re.sub(u"\\<.*?\\>", "", text)
            text = json.dumps(text.split(' '))
            session['text'] = text
            return redirect(url_for('present2'))
        else: # "bubblePlot"
            report = request.form['report-selector']
            res = {'E':[[]], 'S':[[]], 'G':[[]]}
            if report != None:
                BUBBLE=bubble_plot.bubble_plot()
                E, S, G = BUBBLE.bubble_weight(report)
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
        try:
            filename = usr_doc.save(request.files['in_usr_doc'])
            file_url = usr_doc.url(filename)
            session['msg'] = "Upload Done"
            return redirect(url_for('form'))
        except:
            session['msg'] = "We only accept the file type with document or txt."
            return redirect(url_for('form'))
    session['msg'] = "Please choose a qualified file."
    return redirect(url_for('form'))

@app.route('/present2')
def present2():    
    report = session['report_selector'].split('.')[0]
    report_path = './static/tmp/' + report + '.txt'
    if session['option']=="report":
        text = open(report_path, 'r', encoding='utf-8').read().split()
    else: # "text"
        text = session['text']
        text = json.loads(text)
    report_kp_path = './static/tmp/' + report + '_key_phrase.txt'
    data = open(report_kp_path, 'r', encoding='utf-8').read()
    report_csv_path = './static/tmp/' + report + '.csv'
    report_csv = pd.read_csv(report_csv_path).groupby('Pillar').sum()
    esg_count = {'Environment':0, 'Social': 0, 'Governance': 0}
    for key in esg_count.keys():
        esg_count[key] = int(report_csv.loc[key].Count)
    print(text)
    return render_template('present.html', text = text, data=json.loads(data), esg_count = esg_count)

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
    res = {'files':files}
    return res

# 氣泡圖繪製相關 (plot.html)
@app.route('/plot')
def plot():
    return render_template('plot.html')

@app.route('/updateESG')
def updateESG():
    data = session['data']
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)