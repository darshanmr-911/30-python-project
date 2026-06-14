"""
Email Spam Detection using NLP and Machine Learning
Pipeline: Collect data -> Clean text -> Feature extraction -> Train -> Evaluate -> Predict
"""

import os
import re
import string
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "spam.csv"
DATASET_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
)
RANDOM_STATE = 42
TEST_SIZE = 0.2


# ---------------------------------------------------------------------------
# Step 1: Collect Data
# ---------------------------------------------------------------------------
def download_dataset() -> None:
    """Download SMS Spam Collection dataset if not present locally."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if DATA_FILE.exists():
        print(f"Dataset already exists at: {DATA_FILE}")
        return

    print("Downloading spam dataset...")
    zip_path = DATA_DIR / "smsspamcollection.zip"

    urllib.request.urlretrieve(DATASET_URL, zip_path)

    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(DATA_DIR)

    raw_file = DATA_DIR / "SMSSpamCollection"
    if raw_file.exists():
        raw_file.rename(DATA_FILE)

    zip_path.unlink(missing_ok=True)
    print(f"Dataset saved to: {DATA_FILE}")


def load_data() -> pd.DataFrame:
    """Load and return the spam dataset as a DataFrame."""
    download_dataset()

    df = pd.read_csv(
        DATA_FILE,
        sep="\t",
        header=None,
        names=["label", "message"],
        encoding="latin-1",
    )

    df["label"] = df["label"].map({"ham": 0, "spam": 1})
    df.dropna(inplace=True)
    df.drop_duplicates(subset=["message"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f"\nDataset loaded: {len(df)} emails")
    print(f"  Ham (not spam): {(df['label'] == 0).sum()}")
    print(f"  Spam:           {(df['label'] == 1).sum()}")

    return df


# ---------------------------------------------------------------------------
# Step 2: Clean Text (NLP Preprocessing)
# ---------------------------------------------------------------------------
def setup_nltk() -> None:
    """Download required NLTK resources into the project folder."""
    nltk_data_dir = Path(__file__).parent / "nltk_data"
    nltk_data_dir.mkdir(exist_ok=True)
    nltk.data.path.insert(0, str(nltk_data_dir))

    resources = ["stopwords", "punkt", "punkt_tab"]
    for resource in resources:
        try:
            nltk.data.find(
                f"corpora/{resource}" if resource == "stopwords" else f"tokenizers/{resource}"
            )
        except LookupError:
            nltk.download(resource, download_dir=str(nltk_data_dir), quiet=True)


stemmer = PorterStemmer()
stop_words = set()


def clean_text(text: str) -> str:
    """
    NLP text cleaning pipeline:
    - Lowercase
    - Remove URLs, emails, numbers
    - Remove punctuation
    - Tokenize
    - Remove stopwords
    - Stem words
    """
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()

    tokens = nltk.word_tokenize(text)
    tokens = [
        stemmer.stem(word)
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(tokens)


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply NLP cleaning to all messages."""
    print("\nCleaning text with NLP (tokenize, stopwords, stemming)...")
    df = df.copy()
    df["clean_message"] = df["message"].apply(clean_text)
    df = df[df["clean_message"].str.len() > 0]
    df.reset_index(drop=True, inplace=True)
    print(f"Messages after cleaning: {len(df)}")
    return df


# ---------------------------------------------------------------------------
# Step 3: Feature Extraction
# ---------------------------------------------------------------------------
def extract_features(
    train_texts: pd.Series, test_texts: pd.Series
) -> tuple:
    """
    Convert cleaned text to TF-IDF feature vectors.
    TF-IDF captures word importance across documents (better than raw counts).
    """
    print("\nExtracting TF-IDF features...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
    )

    x_train = vectorizer.fit_transform(train_texts)
    x_test = vectorizer.transform(test_texts)

    print(f"Feature matrix shape (train): {x_train.shape}")
    return x_train, x_test, vectorizer


# ---------------------------------------------------------------------------
# Step 4: Train Models
# ---------------------------------------------------------------------------
def get_models() -> dict:
    """Return dictionary of ML classifiers to compare."""
    return {
        "Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "Linear SVM": LinearSVC(random_state=RANDOM_STATE, dual="auto"),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1
        ),
    }


def train_and_evaluate(x_train, x_test, y_train, y_test) -> tuple:
    """Train all models, evaluate, and return the best one."""
    models = get_models()
    results = []
    best_model = None
    best_name = ""
    best_f1 = 0.0

    print("\n" + "=" * 60)
    print("TRAINING & EVALUATION")
    print("=" * 60)

    for name, model in models.items():
        print(f"\n--- {name} ---")
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        cv_scores = cross_val_score(model, x_train, y_train, cv=5, scoring="f1")
        cm = confusion_matrix(y_test, y_pred)

        results.append(
            {
                "Model": name,
                "Accuracy": round(acc, 4),
                "Precision": round(prec, 4),
                "Recall": round(rec, 4),
                "F1-Score": round(f1, 4),
                "CV F1 (mean)": round(cv_scores.mean(), 4),
            }
        )

        print(f"Accuracy:  {acc:.4f}")
        print(f"Precision: {prec:.4f}")
        print(f"Recall:    {rec:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        print(f"5-Fold CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        print(f"Confusion Matrix:\n{cm}")
        print(classification_report(y_test, y_pred, target_names=["Ham", "Spam"]))

        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_name = name

    results_df = pd.DataFrame(results)
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print(results_df.to_string(index=False))
    print(f"\nBest model: {best_name} (F1 = {best_f1:.4f})")

    return best_model, best_name, results_df


# ---------------------------------------------------------------------------
# Step 5: Predict New Emails
# ---------------------------------------------------------------------------
def predict_email(
    text: str, model, vectorizer, show_clean: bool = False
) -> tuple[str, float]:
    """Classify a single email/message as spam or ham."""
    cleaned = clean_text(text)
    if show_clean:
        print(f"Cleaned text: {cleaned[:120]}{'...' if len(cleaned) > 120 else ''}")

    features = vectorizer.transform([cleaned])

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)[0]
        spam_prob = proba[1]
    elif hasattr(model, "decision_function"):
        score = model.decision_function(features)[0]
        spam_prob = 1 / (1 + pow(2.71828, -score))
    else:
        spam_prob = float(model.predict(features)[0])

    prediction = "SPAM" if model.predict(features)[0] == 1 else "NOT SPAM"
    confidence = spam_prob if prediction == "SPAM" else 1 - spam_prob

    return prediction, confidence


def interactive_mode(model, vectorizer) -> None:
    """Let the user test custom emails interactively."""
    print("\n" + "=" * 60)
    print("INTERACTIVE SPAM DETECTOR")
    print("Type an email/message to classify (or 'quit' to exit)")
    print("=" * 60)

    while True:
        user_input = input("\nEnter message: ").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break
        if not user_input:
            print("Please enter a message.")
            continue

        label, confidence = predict_email(user_input, model, vectorizer, show_clean=True)
        print(f"Result: {label}  (confidence: {confidence:.2%})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("EMAIL SPAM DETECTION - NLP + Machine Learning")
    print("=" * 60)

    setup_nltk()
    global stop_words
    stop_words = set(stopwords.words("english"))

    # Step 1: Collect data
    df = load_data()

    # Step 2: Clean text
    df = preprocess_dataframe(df)

    # Split before feature extraction to avoid data leakage
    x = df["clean_message"]
    y = df["label"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # Step 3: Feature extraction
    x_train_vec, x_test_vec, vectorizer = extract_features(x_train, x_test)

    # Step 4 & 5: Train and evaluate
    best_model, best_name, _ = train_and_evaluate(
        x_train_vec, x_test_vec, y_train, y_test
    )

    # Demo predictions on sample messages
    print("\n" + "=" * 60)
    print("SAMPLE PREDICTIONS")
    print("=" * 60)

    samples = [
        "Hey, are we still meeting for lunch tomorrow?",
        "Congratulations! You won $1,000,000. Click here to claim now!",
        "Your package has been delivered. Track at our website.",
        "FREE entry to win a brand new iPhone! Text WIN to 12345",
        "Can you send me the project report by Friday?",
    ]

    for msg in samples:
        label, conf = predict_email(msg, best_model, vectorizer)
        print(f"\nMessage: {msg[:70]}{'...' if len(msg) > 70 else ''}")
        print(f"  -> {label} ({conf:.2%} confidence)")

    # Interactive mode
    choice = input("\nTry your own messages? (y/n): ").strip().lower()
    if choice == "y":
        interactive_mode(best_model, vectorizer)


if __name__ == "__main__":
    main()
