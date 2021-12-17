import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import pickle
import os
from werkzeug.exceptions import BadRequest, NotFound

DIR_ROOT = os.getcwd()
MODEL_FILENAME = DIR_ROOT + '/model.pkl'
DB_FINAL_RATINGS = DIR_ROOT + '/db-final-ratings.csv'
DB_BOOKS = DIR_ROOT + '/db-books.csv'

books_pivot = ''
books = ''

app = Flask(__name__)

@app.errorhandler(BadRequest)
def forbidden(e):
    return jsonify({ 'message': e.description }), 400

@app.errorhandler(NotFound)
def forbidden(e):
    return jsonify({ 'message': 'Resource not found' }), 404

def load_model():
    return pickle.load(open(MODEL_FILENAME, "rb"))

def load_books():
    global books
    books = pd.read_csv(DB_FINAL_RATINGS, encoding='utf-8')


def load_pivot_data():
    print(' * Loaded Pivot Data!')

    global books_pivot

    # Processando Final Rating
    final_rating = pd.read_csv(DB_FINAL_RATINGS, encoding='utf-8')
    final_rating = final_rating[final_rating['number_of_ratings'] >= 50]

    # Removendo dados dupicados
    final_rating.drop_duplicates(['user_id','title'], inplace=True)

    # Pivot
    books_pivot = final_rating.pivot_table(columns='user_id', index='ISBN', values="rating")
    books_pivot.fillna(0, inplace=True)

    
    
@app.route('/')
def home():    
    return 'Recommender System'

def get_books_ratings():
    

@app.route('/recommender/<string:isbn>')
def predict(isbn):
    
    global books_pivot

    if not isbn:
        raise BadRequest('Invalid ISBN')

    # Get Model
    model = load_model()
    d, s = model.kneighbors(books_pivot.loc[isbn].values.reshape(1, -1))    

    # Array de sugestões
    for i in range(len(s)):
        books_arr = books_pivot.index[s[i]]

    # Get Livros apartir do ISBN
    books_list = books[books['ISBN'].isin(books_arr)].drop_duplicates(['ISBN'])
    books_resp = []
    for i, r in books_list.iterrows():
        b = {
            'isbn': r['ISBN'],
            'title': r['title'],
            'author': r['author'],
            'year': r['year'],
            'publisher': r['publisher']
        }
        books_resp.append(b)
        
    return jsonify(books_resp)

if __name__ == '__main__':
    load_books()
    load_pivot_data()    
    app.run(debug=True, port=3000, host="0.0.0.0")

# Fim