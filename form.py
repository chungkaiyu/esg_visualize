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
    form = CustomForm()
    if form.validate_on_submit():
        session['text'] = form.text.data
        session['analytics'] = form.analytics.data
        session['annualReport'] = form.annualReport.data
        print('In')
        return redirect(url_for('test'))
    # return render_template('form.html', form=form)
    return render_template('form.html')


@app.route('/test')
def test():
    print('Hello')
    return render_template('test.html')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        # if 'in_usr_doc' in request.files:
        #     try:
        #         filename = usr_doc.save(request.files['in_usr_doc'])
        #         print(filename)
        #         file_url = usr_doc.url(filename)
        #         print(file_url)
        #         # return "Oh no, we didn't finish this route."
        #         # return '<script>alert("Upload done!");window.location.href ="./form";</script>'
        #         redirect(url_for('alert', success='True'))
        #         time.sleep(5)
        #         return '<script>window.location.href ="./form";</script>'
        #     except:
        #         # return '<script>alert("We only accept the file type with document or .txt");window.location.href ="./form";</script>'
        #         time.sleep(5)
        #         redirect(url_for('alert', success='False'))
        #         return '<script>window.location.href ="./form";</script>'
        # text = request.form['text']
        # text = re.sub(u"\\<.*?\\>", "", text)
        # text = json.dumps(text.split(' '))
        session['kernel_option'] = request.form['flexRadioDefault']
        session['report_selector'] = request.form['report-selector']
        dp = DocProcessor()
        file_path = os.getcwd() + '/static/input'
        text = dp.get_file_text(str(file_path + '/Test9-2019-IntelCSR-Report.pdf'))
        #session['text'] = text
        return redirect(url_for('present2'))
    return '<script>alert("We didn\'t design Get request.");window.location.href ="./form";</script>'

@app.route('/present2')
def present2():
    
    report = session['report_selector'].split('.')[0]
    report_path = './static/tmp/' + report + '.txt'
    text = open(report_path, 'r', encoding='utf-8').read().split()
    report_kp_path = './static/tmp/' + report + '_key_phrase.txt'
    data = open(report_kp_path, 'r', encoding='utf-8').read()
    #file = open('./key_phrase.txt', 'r', encoding='utf-8')
    #data = file.read()
    return render_template('present.html', text = text, radio = session['kernel_option'], data=json.loads(data))

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

@app.route('/alert')
def alert():
    success = session['data']
    if success:
        return "Upload done！"
    else:
        return "We only accept the file type with document or txt."

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