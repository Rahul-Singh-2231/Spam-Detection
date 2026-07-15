"""
Model Training Script for Spam Detection.
Downloads the SMS Spam Collection dataset, preprocesses it, trains multiple
classifiers, and saves the best-performing model.
"""

import os
import io
import zipfile
from datetime import datetime

import pandas as pd
import numpy as np
import joblib
import requests

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    classification_report, accuracy_score,
    precision_score, recall_score, f1_score
)

from preprocessing import TextPreprocessor


def download_dataset():
    """
    Download the SMS Spam Collection dataset if not already present.

    Returns:
        str: Path to the downloaded TSV file.
    """
    dataset_dir = 'dataset'
    dataset_path = os.path.join(dataset_dir, 'SMSSpamCollection.tsv')

    if os.path.exists(dataset_path):
        print(f"Dataset already exists at: {dataset_path}")
        return dataset_path

    os.makedirs(dataset_dir, exist_ok=True)

    url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip'
    print(f"Downloading dataset from: {url}")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    print("Extracting dataset...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Find the SMSSpamCollection file in the archive
        file_list = z.namelist()
        print(f"Files in archive: {file_list}")

        sms_file = None
        for fname in file_list:
            if 'SMSSpamCollection' in fname and not fname.endswith('/'):
                sms_file = fname
                break

        if sms_file is None:
            raise FileNotFoundError(
                "Could not find 'SMSSpamCollection' file in the downloaded archive."
            )

        # Extract and save as TSV
        with z.open(sms_file) as src:
            content = src.read()
            with open(dataset_path, 'wb') as dst:
                dst.write(content)

    print(f"Dataset saved to: {dataset_path}")
    return dataset_path


def load_data(path):
    """
    Load and prepare the SMS Spam Collection dataset.

    Args:
        path (str): Path to the TSV file.

    Returns:
        pd.DataFrame: DataFrame with 'label' (0/1) and 'message' columns.
    """
    print(f"\nLoading dataset from: {path}")
    df = pd.read_csv(
        path, sep='\t', header=None,
        names=['label', 'message'], encoding='latin-1'
    )

    # Map labels: 'spam' -> 1, 'ham' -> 0
    df['label'] = df['label'].map({'spam': 1, 'ham': 0})

    # Print class distribution
    print(f"\nDataset size: {len(df)} messages")
    print(f"Class distribution:")
    print(f"  Ham (0):  {(df['label'] == 0).sum()} ({(df['label'] == 0).mean() * 100:.1f}%)")
    print(f"  Spam (1): {(df['label'] == 1).sum()} ({(df['label'] == 1).mean() * 100:.1f}%)")

    return df


def preprocess_dataset(df):
    """
    Apply NLP preprocessing to all messages in the dataset.

    Args:
        df (pd.DataFrame): DataFrame with 'message' column.

    Returns:
        pd.DataFrame: DataFrame with added 'cleaned_text' column.
    """
    print("\nPreprocessing dataset...")
    preprocessor = TextPreprocessor()

    cleaned_texts = []
    total = len(df)

    for idx, row in df.iterrows():
        result = preprocessor.preprocess(row['message'])
        cleaned_texts.append(result['cleaned_text'])

        # Show progress every 500 messages
        if (idx + 1) % 500 == 0:
            print(f"  Processed {idx + 1}/{total} messages...")

    df['cleaned_text'] = cleaned_texts
    print(f"  Preprocessing complete! {total} messages processed.")

    return df


def train_and_evaluate():
    """
    Main training pipeline: download data, preprocess, train models,
    evaluate, and save the best model.
    """
    print("=" * 60)
    print("  SPAM DETECTION MODEL TRAINING")
    print("=" * 60)

    # Step 1: Download and load dataset
    dataset_path = download_dataset()
    df = load_data(dataset_path)

    # Step 2: Preprocess all messages
    df = preprocess_dataset(df)

    # Step 3: Feature extraction with TF-IDF
    print("\nCreating TF-IDF features...")
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )

    X = vectorizer.fit_transform(df['cleaned_text'])
    y = df['label'].values
    print(f"  Feature matrix shape: {X.shape}")

    # Step 4: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Training set: {X_train.shape[0]} samples")
    print(f"  Test set:     {X_test.shape[0]} samples")

    # Step 5: Train models
    print("\n" + "-" * 60)
    print("  TRAINING MODELS")
    print("-" * 60)

    models = {
        'MultinomialNB': MultinomialNB(alpha=0.1),
        'LogisticRegression': LogisticRegression(
            max_iter=1000, C=1.0, random_state=42
        ),
        'LinearSVC': CalibratedClassifierCV(
            LinearSVC(max_iter=1000, C=1.0, random_state=42),
            cv=5
        )
    }

    results = {}

    for name, model in models.items():
        print(f"\n  Training {name}...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        results[name] = {
            'model': model,
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1': f1
        }

        print(f"    Accuracy:  {acc:.4f}")
        print(f"    Precision: {prec:.4f}")
        print(f"    Recall:    {rec:.4f}")
        print(f"    F1-Score:  {f1:.4f}")

    # Step 6: Print comparison table
    print("\n" + "=" * 60)
    print("  MODEL COMPARISON")
    print("=" * 60)
    print(f"  {'Model':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1-Score':>10}")
    print("  " + "-" * 65)

    for name, metrics in results.items():
        print(
            f"  {name:<25} "
            f"{metrics['accuracy']:>10.4f} "
            f"{metrics['precision']:>10.4f} "
            f"{metrics['recall']:>10.4f} "
            f"{metrics['f1']:>10.4f}"
        )

    # Step 7: Select best model by F1-score
    best_name = max(results, key=lambda k: results[k]['f1'])
    best_metrics = results[best_name]
    best_model = best_metrics['model']

    print(f"\n  BEST MODEL: {best_name} (F1-Score: {best_metrics['f1']:.4f})")
    print("\n  Classification Report:")
    y_pred_best = best_model.predict(X_test)
    print(classification_report(y_test, y_pred_best, target_names=['Ham', 'Spam']))

    # Step 8: Save model, vectorizer, and metadata
    model_dir = 'model'
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, 'spam_model.pkl')
    vectorizer_path = os.path.join(model_dir, 'tfidf_vectorizer.pkl')
    metadata_path = os.path.join(model_dir, 'model_metadata.pkl')

    joblib.dump(best_model, model_path)
    print(f"\n  Model saved to: {model_path}")

    joblib.dump(vectorizer, vectorizer_path)
    print(f"  Vectorizer saved to: {vectorizer_path}")

    metadata = {
        'model_name': best_name,
        'accuracy': best_metrics['accuracy'],
        'precision': best_metrics['precision'],
        'recall': best_metrics['recall'],
        'f1': best_metrics['f1'],
        'training_date': datetime.now().isoformat(),
        'dataset_size': len(df),
        'num_features': X.shape[1]
    }

    joblib.dump(metadata, metadata_path)
    print(f"  Metadata saved to: {metadata_path}")

    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE!")
    print("=" * 60)


if __name__ == '__main__':
    train_and_evaluate()
