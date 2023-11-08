import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

dotenv_path = join(dirname(_file_), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db=client[DB_NAME]

# client = MongoClient('mongodb+srv://diskarmn:Diska123@cluster0.3lnlkgx.mongodb.net/?retryWrites=true&w=majority')
# db = client.dbsparta_plus_week2



@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []

    for word in words_result:
        definitions = word.get('definitions', [])
        if definitions:
            definition = definitions[0].get('shortdef', [])
            if definition:
                definition = definition[0]
            else:
                definition = "Tidak ada definisi tersedia"
        else:
            definition = "Tidak ada definisi tersedia"

        words.append({
            'word': word['word'],
            'definition': definition,
        })
    msg=request.args.get('msg')
    return render_template('index.html', words=words,msg=msg)


@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = 'e74b8091-20e7-49d2-982c-bb8dcbbd7faf'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()
    if not definitions:
        return redirect(url_for('main',msg=f'could not find the owrd"{keyword}'))
    if type(definitions[0]) is str:
        suggestions=', '.join(definitions)
        return redirect(url_for('main',msg=f'cdid yu mean?"{suggestions}'))
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=request.args.get('status_give', 'new')
    )

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')
    doc = {
        'word': word,
        'definitions': definitions,
        'date':datetime.now().strftime('%Y%m%d')
    }
    db.words.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was saved!!!',
    })

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'the word {word} was deleted'
    })
@app.route('/api/get_exs',methods=['GET'])
def get_exs():
    word=request.args.get('word')
    examples_data=db.examples.find({'word':word})
    examples=[]
    for example in examples_data:
        examples.append({
            'example':example.get('example'),
            'id':str(example.get('_id'))
        })       
    return jsonify({'result':'success',"examples":examples})

@app.route('/api/save_ex',methods=['POST'])
def save_ex():
    word=request.form.get('word')
    example=request.form.get('example')
    doc={
        'word':word,
        'example':example
    }
    db.examples.insert_one(doc)
    return jsonify({'result':'success','msg':f'your example{example} was saved{word}'})

@app.route('/api/delete_ex',methods=['POST'])
def delete_ex():
    id=request.form.get('id')
    word=request.form.get('word')
    db.word.delete_one({"word":word})
    db.examples.delete_one({'word':word})
    return jsonify({'result':'success','msg':f'your word, {word} was deleted'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)