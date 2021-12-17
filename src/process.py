import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle
import os

DIR_ROOT = os.getcwd()
DB_BOOK_RATINGS = DIR_ROOT + '/src/data/db-book-ratings.csv'
DB_BOOKS = DIR_ROOT + '/src/data/db-books.csv'
DB_USERS = DIR_ROOT + '/src/data/db-users.csv'
DB_FINAL_RATINGS = DIR_ROOT + '/db-final-ratings.csv'
MODEL_FILENAME = DIR_ROOT + '/model.pkl'

# Databases
books = pd.read_csv(DB_BOOKS, sep=';', encoding="latin-1", error_bad_lines= False)
users = pd.read_csv(DB_USERS, sep=';', encoding="latin-1", error_bad_lines= False)
ratings = pd.read_csv(DB_BOOK_RATINGS, sep=';', encoding="latin-1", error_bad_lines= False)

# Renomeando Colunas
books = books[['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher']]
books.rename(columns = {'Book-Title':'title', 'Book-Author':'author', 'Year-Of-Publication':'year', 'Publisher':'publisher'}, inplace=True)
users.rename(columns = {'User-ID':'user_id', 'Location':'location', 'Age':'age'}, inplace=True)
ratings.rename(columns = {'User-ID':'user_id', 'Book-Rating':'rating'}, inplace=True)

## Decisoes de Dominio ---------------------------------------------------------------------------------------------------

# Livros que tenham mais de 150 avaliações pelos usuários
books_eval = 150 
x = ratings['user_id'].value_counts() > books_eval

y = x[x].index  
print('Total users: ', y.shape)

# Trazendo ratings somente dos usuários q avaliaram mais de 200 livros
ratings = ratings[ratings['user_id'].isin(y)]

# Join de tabelas
rating_with_books = ratings.merge(books, on='ISBN')
rating_with_books.head()

# Quantidade de rating dos livros
number_rating = rating_with_books.groupby('title')['rating'].count().reset_index()

#Renomeando coluna
number_rating.rename(columns= {'rating':'number_of_ratings'}, inplace=True)

# Join de tabela de livros com os Ratings com a tabela de quantidade de ratings por livro
final_rating = rating_with_books.merge(number_rating, on='title')

# Filtrar somente livros que tenham pelo menos 50 avaliações
final_rating = final_rating[final_rating['number_of_ratings'] >= 50]

# Tratando dados duplicados
final_rating.drop_duplicates(['user_id','title'], inplace=True)

# Criado CSV do dataframe Final Ratings
final_rating.to_csv(DB_FINAL_RATINGS, encoding='utf-8', index=False)

# Pivot dataframe Final Ratings
book_pivot = final_rating.pivot_table(columns='user_id', index='ISBN', values="rating")

# Tratando dados 
book_pivot.fillna(0, inplace=True)

## Trainning ---------------------------------------------------------------------------------------------------

book_sparse = csr_matrix(book_pivot)

model = NearestNeighbors(algorithm='brute')
model.fit(book_sparse)

pickle.dump(model, open(MODEL_FILENAME, 'wb'))