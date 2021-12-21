from flask import Flask, request, render_template, redirect, url_for

import json
import re

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


@app.errorhandler(413)
def request_entity_too_large(error):
    return '<script>alert("File to large!");window.location.href ="./form";</script>', 413


usr_doc = UploadSet(name='def', extensions=TEXT + DOCUMENTS + tuple(['pdf']))
configure_uploads(app, usr_doc)


@app.errorhandler(413)
def request_entity_too_large(error):
    return '<script>alert("File to large!");window.location.href ="./form";</script>', 413


@app.route('/form')
def formPage():
    return render_template('form.html')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        if 'in_usr_doc' in request.files:
            try:
                filename = usr_doc.save(request.files['in_usr_doc'])
                print(filename)
                file_url = usr_doc.url(filename)
                print(file_url)
                return "Oh no, we didn't finish this route."
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
