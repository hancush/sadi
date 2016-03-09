import re
import os

from flask import Flask, render_template, request, jsonify, url_for, session
from flask.ext.basicauth import BasicAuth
from flask_weasyprint import HTML, render_pdf
from slacker import Slacker

from classes_web import Parser

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = os.environ['username']
app.config['BASIC_AUTH_PASSWORD'] = os.environ['pass']

basic_auth = BasicAuth(app)

@app.route('/',methods=['GET', 'POST'])
def listen():
    data = request.form
    if data['token'] == os.environ['ap_token']:
        story = re.sub(' ', '_', data['text']) # handle special chars (punctuation, etc.)
        url = 'https://here-sadi.herokuapp.com/{0}_report.pdf'.format(story)
        return jsonify({'response_type': 'ephemeral',
                        'text': ':confetti_ball: Here\'s your PDF: {0} :confetti_ball:'.format(url)})
    else:
        print 'no'
        return jsonify({'response_type': 'ephemeral',
                        'text': 'Girls are cool but your request wasn\'t. :upside_down_face:'})

@app.route('/<story>_report.pdf')
@basic_auth.required
def render_report(story):
    data = Parser(story)
    results = data.receive()
    html = render_template('page.html',
                           story=story,
                           results=results)
    return render_pdf(HTML(string=html))

if __name__ == '__main__':
    app.run(debug=True)