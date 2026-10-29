
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Load complaint dataset
data = pd.read_csv("complaints.csv")

# Clean dataset
data = data.dropna(subset=["complaint", "department"])
data["complaint"] = data["complaint"].astype(str).str.strip()
data["department"] = data["department"].astype(str).str.strip()

data = data[
    (data["complaint"] != "") &
    (data["department"] != "")
]

X = data["complaint"]
y = data["department"]

print("Total complaints:", len(data))
print("Total departments:", y.nunique())

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

# Create the machine learning pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("classifier", LogisticRegression(max_iter=2000))
])

# Train the model
model.fit(X_train, y_train)

# Evaluate the model
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions) * 100

print("\nModel Accuracy:", round(accuracy, 2), "%")
print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

# Save the trained model
joblib.dump(model, "complaint_model.joblib")

# Save actual evaluation accuracy
metrics = {
    "accuracy": round(accuracy, 2),
    "total_complaints": len(data),
    "total_departments": int(y.nunique()),
    "test_examples": len(y_test)
}

joblib.dump(metrics, "model_metrics.joblib")

print("\nModel saved as complaint_model.joblib")
print("Metrics saved as model_metrics.joblib")

# Test one sample complaint
sample = ["My internet connection is not working"]

print("\nSample complaint:", sample[0])
print("Recommended department:", model.predict(sample)[0])
