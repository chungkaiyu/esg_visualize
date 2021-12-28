from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, DateTimeField,
                     RadioField, SelectField,
                     TextAreaField, SubmitField)
from wtforms.validators import DataRequired


from flask import Flask, request, session, render_template, redirect, url_for
from flask_uploads import UploadSet, TEXT, DOCUMENTS, configure_uploads
from werkzeug.utils import secure_filename
import os
import re
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'development'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOADED_DEF_DEST'] = os.getcwd() + '\\static\\input\\'

usr_doc = UploadSet(name='def', extensions=TEXT + DOCUMENTS + tuple(['pdf']))
configure_uploads(app, usr_doc)


class CustomForm(FlaskForm):
    text = StringField('Please enter your text!', validators=[
        DataRequired()])
    analytics = RadioField('Analysis Kernel Option', choices=[(
        'wordLv', 'Word-level'), ('sentLv', 'Sentence-level')])
    annualReport = SelectField('Annual report', choices=[('Material2020', 'Applied Material 2020'), (
        'Material2019', 'Applied Material 2019'), ('Material2018', 'Applied Material 2018')])
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
    form = CustomForm()
    if form.validate_on_submit():
        session['text'] = form.text.data
        session['analytics'] = form.analytics.data
        session['annualReport'] = form.annualReport.data
        print('In')
        return redirect(url_for('test'))
    return render_template('form.html', form=form)


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
                return '<script>alert("Upload done!");window.location.href ="./form";</script>'
            except:
                return '<script>alert("We only accept the file type with document or .txt");window.location.href ="./form";</script>'
        text = request.form['text']
        text = re.sub(u"\\<.*?\\>", "", text)
        text = json.dumps(text.split(' '))
        return redirect(url_for('present', text=text, action="post"))
    return '<script>alert("We didn\'t design Get request.");window.location.href ="./form";</script>'


@app.route('/present/<action>/<text>')
def present(text, action):
    file = open('./key_phrase.txt', 'r', encoding='utf-8')
    data = file.read()
    return render_template('present.html', text=json.loads(text), action=action, data=json.loads(data))


if __name__ == '__main__':
    app.run(debug=True)
