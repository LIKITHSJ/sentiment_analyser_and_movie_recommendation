from flask import Flask, render_template, request
import pandas as pd
import joblib

app = Flask(__name__)
movies = pd.read_csv('filtered_movies_with_split.csv')  

model = joblib.load('sentiment_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

def predict_sentiment(review):
    vectorized_review = vectorizer.transform([review])
    sentiment = model.predict(vectorized_review)[0]
    return "Positive" if sentiment == 1 else "Negative"

def recommend_movies(genre, decade, top_n=5):
    start_year = decade
    end_year = decade + 9
    
    movies['Released_Year'] = pd.to_numeric(movies['Released_Year'], errors='coerce')  

    filtered_movies = movies[
        movies['Genre'].str.contains(genre, case=False, na=False) &
        (movies['Released_Year'] >= start_year) & (movies['Released_Year'] <= end_year) 
    ]
    
    return filtered_movies.nlargest(top_n, 'IMDB_Rating')[['Series_Title', 'IMDB_Rating', 'Released_Year']].to_dict(orient='records')


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    review = request.form['review']
    sentiment = predict_sentiment(review)  
    
    if sentiment == 'Negative':
        return render_template('negative_review.html') 
    
    else:
        return render_template('result.html', review=review, sentiment=sentiment)

@app.route('/preferences')
def preferences():
    return render_template('preferences.html')  

@app.route('/recommend', methods=['POST'])
def recommend():
    genre = request.form['genre']  
    decade = int(request.form['decade']) 
    recommendations = recommend_movies(genre, decade) 
    return render_template('recommend.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
