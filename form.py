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
print(download_path)
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


class MyForm(FlaskForm):
    name = StringField('你的名字', validators=[DataRequired()])
    agreed = BooleanField('同意加入這個組織？')
    gender = RadioField('請輸入性別', choices=[('M', '男生'), ('F', '女生')])
    hobby = SelectField(
        '你的興趣', choices=[('sports', '運動'), ('travel', '旅遊'), ('movie', '電影')])
    others = TextAreaField()
    submit = SubmitField("確認")


@app.errorhandler(413)
def request_entity_too_large(error):
    return '<script>alert("File to large!");window.location.href ="./form";</script>', 413


@app.route('/form', methods=['GET', 'POST'])
def formPage():
    print('Entering')
    # form = MyForm()
    # if form.validate_on_submit():
    #         session['name'] = form.name.data
    #         session['agreed'] = form.agreed.data
    #         session['gender'] = form.gender.data
    #         session['hobby'] = form.hobby.data
    #         session['others'] = form.others.data
    #         print('In')
    #         return redirect(url_for('test'))
    # form = CustomForm()
    # if form.validate_on_submit():
    #     session['text'] = form.text.data
    #     session['analytics'] = form.analytics.data
    #     session['annualReport'] = form.annualReport.data
    #     print('In')
    #     return redirect(url_for('test'))
    return render_template('form.html')


@app.route('/test')
def test():
    print('Hello')
    return render_template('test.html')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        if 'in_usr_doc' in request.files:
            try:
                filename = usr_doc.save(request.files['in_usr_doc'])
                print(filename)
                file_url = usr_doc.url(filename)
                print(file_url)
                # return "Oh no, we didn't finish this route."
                # return '<script>alert("Upload done!");window.location.href ="./form";</script>'
                redirect(url_for('alert', success='True'))
                time.sleep(5)
                return '<script>window.location.href ="./form";</script>'
            except:
                # return '<script>alert("We only accept the file type with document or .txt");window.location.href ="./form";</script>'
                time.sleep(5)
                redirect(url_for('alert', success='False'))
                return '<script>window.location.href ="./form";</script>'
        text = request.form['text']
        text = re.sub(u"\\<.*?\\>", "", text)
        text = json.dumps(text.split(' '))
        return redirect(url_for('present', text=text, action="post"))
    return '<script>alert("We didn\'t design Get request.");window.location.href ="./form";</script>'


@app.route('/present/<action>/<text>')
def present(text, action):
    file_path = os.getcwd() + '/static/input'
    #print(file_path)
    dp = DocProcessor()
    text = dp.get_file_text(str(file_path + '/Test9-2019-IntelCSR-Report.pdf'))
    file = open('./key_phrase.txt', 'r', encoding='utf-8')
    data = file.read()
    return render_template('present.html', text=text, action=action, data=json.loads(data))

@app.route('/showReports')
def showReports():
    path = './static/input/'
    files = os.listdir(path)
    res = {'files':files}
    return res

@app.route('/alert/<success>')
def alert(success):
    if success=='True':
        return "Upload done！"
    else:
        return "We only accept the file type with document or txt."

#氣泡圖繪製相關(plot.html)
@app.route('/check', methods=['POST','GET'])
def check():
    filename=request.args.get("company")
    OUT=open('templates/plot.html','r',encoding='utf-8').read()
    op='<select name="company">'
    for i in list(sorted(os.listdir('static\input'))):
        if(filename == i):
            op+='<option value="'+i+'"selected>'+i+'</option>'
        else:
            op+='<option value="'+i+'">'+i+'</option>'
    op+='</select>'
    OUT=OUT.replace('<!--replace-->', op)
    if filename != None:
        BUBBLE=bubble_plot.bubble_plot()
        E, S, G = BUBBLE.bubble_weight(filename)
        OUT=OUT.replace('const E=[[]];', 'const E='+str(E)+';')
        OUT=OUT.replace('const S=[[]];', 'const S='+str(S)+';')
        OUT=OUT.replace('const G=[[]];', 'const G='+str(G)+';')
    return OUT

@app.route('/submit_in_plot_html', methods=['POST', 'GET'])
def submit_in_plot_html():
    if request.method == 'POST':
        if 'in_usr_doc' in request.files:
            try:
                filename = usr_doc.save(request.files['in_usr_doc'])
                print(filename)
                file_url = usr_doc.url(filename)
                print(file_url)
                return '<script>alert("Upload done!");window.location.href ="./";</script>'
            except:
                return '<script>alert("We only accept the file type with document or .txt");window.location.href ="./";</script>'
        text = request.form['text']
        text = re.sub(u"\\<.*?\\>", "", text)
        text = json.dumps(text.split(' '))
        return redirect(url_for('present', text=text, action="post"))
    return '<script>alert("We didn\'t design Get request.");window.location.href ="./";</script>'

@app.route('/echarts.min.js', methods=['POST','GET'])
def upload():
    return render_template('/echarts.min.js')

@app.route('/')
def into_plot_html():
    OUT=open('templates/plot.html','r',encoding='utf-8').read()
    op='<select name="company">'
    for i in list(sorted(os.listdir('static\input'))):
        if('.DS_' in i):
            op+='<option>'+'請選擇公司名稱'+'</option>'
        else:
            op+='<option value="'+i+'">'+i+'</option>'
    op+='</select>'
    return OUT.replace('<!--replace-->', op)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)