import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report

vectorizer = TfidfVectorizer()
classifier = SVC()

def train_model():
    df = pd.read_csv('C:\\Users\\prajw\\OneDrive\\Desktop\\mental_health_tracker\\data\\emotion_dataset.csv')
    X_vectorized = vectorizer.fit_transform(df['text'])
    X_train, X_test, y_train, y_test = train_test_split(X_vectorized, df['emotion'], test_size=0.2, random_state=42)
    
    # Hyperparameter tuning with Grid Search
    param_grid = {'kernel': ['linear', 'rbf', 'poly'], 'C': [0.1, 1, 10, 100]}
    grid_search = GridSearchCV(classifier, param_grid, cv=5, scoring='f1_weighted')
    grid_search.fit(X_train, y_train)
    
    # Save the best estimator as a global variable
    global best_classifier
    best_classifier = grid_search.best_estimator_
    
    predictions = best_classifier.predict(X_test)
    
    print("Model training complete")
    print("Best Parameters:", grid_search.best_params_)
    print(classification_report(y_test, predictions))

def predict(emotion_text):
    emotion_vectorized = vectorizer.transform([emotion_text])
    emotion_prediction = best_classifier.predict(emotion_vectorized)[0]
    print(f"Text: {emotion_text}, Prediction: {emotion_prediction}")  # Debugging info
    return emotion_prediction

# Train the model initially
train_model()

