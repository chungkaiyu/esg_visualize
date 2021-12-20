from flask import Flask, request, render_template, redirect, url_for
from flask_uploads import UploadSet, TEXT, DOCUMENTS, configure_uploads
import json
import re

app = Flask(__name__)

app.config['SECRET_KEY'] = 'development'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOADED_DEF_DEST'] = r'C:\Users\Kazuyahoo\Documents\GitHub\esg_visualize\static\input'
app.config['UPLOADED_DEF_URL'] = '\\static\\input\\'

usr_doc = UploadSet(name='def', extensions= TEXT + DOCUMENTS)
configure_uploads(app, usr_doc)

@app.route('/form')
def formPage():
    return render_template('form.html')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST' and 'in_usr_doc' in request.files:
        filename = usr_doc.save(request.files['in_usr_doc'])
        print(filename)
        file_url = usr_doc.url(filename)
        print(file_url)
        return "Hello world!"
    if request.method == 'POST':
        text = request.form['text']
        text = re.sub(u"\\<.*?\\>", "", text)
        text = json.dumps(text.split(' '))
        return redirect(url_for('present', text=text, action="post"))

    # else:
    #     text = request.args.get('text')
    #     #print("get : user => ", user)
    #     return redirect(url_for('present', text=text, action="get"))


@app.route('/present/<action>/<text>')
def present(text, action):
    file = open('./key_phrase.txt', 'r', encoding='utf-8')
    data = file.read()
    return render_template('present.html', text=json.loads(text), action=action, data=json.loads(data))


if __name__ == '__main__':
    app.run()
