from flask import Flask, request, render_template, redirect, url_for
import json
import re

app = Flask(__name__)


@app.route('/form')
def formPage():
    return render_template('tinymce.html')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        text = request.form['text']
        text = re.sub(u"\\<.*?\\>", "", text)
        print(text)
        text = json.dumps(text.split(' '))
        print(text)
        #print("post : user => ", text)
        return redirect(url_for('present', text=text, action="post"))
    else:
        text = request.args.get('text')
        #print("get : user => ", user)
        return redirect(url_for('present', text=text, action="get"))


@app.route('/present/<action>/<text>')
def present(text, action):
    file = open('./key_phrase.txt', 'r', encoding='utf-8')
    data = file.read()
    return render_template('present.html', text=json.loads(text), action=action, data=json.loads(data))


if __name__ == '__main__':
    app.run()
