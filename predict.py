"""
Prediction Engine for Spam Detection.
Loads the trained model and provides spam/ham predictions with detailed analysis.
"""

import os
import joblib
import numpy as np

from preprocessing import TextPreprocessor
from feature_extractor import FeatureExtractor
from utils import get_risk_level, generate_explanation, generate_reasoning, format_response


class SpamPredictor:
    """Loads the trained spam detection model and provides predictions."""

    def __init__(self):
        """
        Initialize the predictor by loading the trained model, vectorizer,
        and metadata. Also initializes the preprocessor and feature extractor.
        """
        model_dir = 'model'
        model_path = os.path.join(model_dir, 'spam_model.pkl')
        vectorizer_path = os.path.join(model_dir, 'tfidf_vectorizer.pkl')
        metadata_path = os.path.join(model_dir, 'model_metadata.pkl')

        try:
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.metadata = joblib.load(metadata_path)
            print(f"Model loaded: {self.metadata.get('model_name', 'Unknown')}")
            print(f"Model F1-Score: {self.metadata.get('f1', 'N/A')}")
        except FileNotFoundError:
            raise FileNotFoundError(
                "Trained model files not found. Please run 'python train_model.py' "
                "first to train and save the model. Expected files:\n"
                f"  - {model_path}\n"
                f"  - {vectorizer_path}\n"
                f"  - {metadata_path}"
            )

        self.preprocessor = TextPreprocessor()
        self.feature_extractor = FeatureExtractor()

    def predict(self, message):
        """
        Predict whether a message is spam or ham with detailed analysis.

        Args:
            message (str): The text message to classify.

        Returns:
            dict: Complete prediction result with classification, confidence,
                  risk level, reasoning, explanation, and analysis data.

        Raises:
            ValueError: If message is empty or not a string.
        """
        # Validate input
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Message must be a non-empty string.")

        # Step 1: Preprocess
        preprocessed_data = self.preprocessor.preprocess(message)

        # Step 2: Extract features
        features = self.feature_extractor.extract_features(message, preprocessed_data)

        # Step 3: Transform with vectorizer
        text_vector = self.vectorizer.transform([preprocessed_data['cleaned_text']])

        # Step 4: Get prediction
        prediction = self.model.predict(text_vector)[0]

        # Step 5: Get probability
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(text_vector)[0]
            spam_probability = float(proba[1])
            confidence = float(np.max(proba)) * 100
        elif hasattr(self.model, 'decision_function'):
            decision = self.model.decision_function(text_vector)[0]
            # Sigmoid to convert decision function to probability-like score
            spam_probability = float(1 / (1 + np.exp(-decision)))
            confidence = abs(decision) * 100
            confidence = min(confidence, 100.0)
        else:
            spam_probability = 1.0 if prediction == 1 else 0.0
            confidence = 100.0

        # Step 6: Determine prediction label
        prediction_label = 'Spam' if prediction == 1 else 'Ham'

        # Step 7: Get risk level
        risk_level, risk_color = get_risk_level(spam_probability)

        # Step 8: Generate reasoning
        reasoning = generate_reasoning(features, preprocessed_data)

        # Step 9: Generate explanation
        explanation = generate_explanation(
            prediction_label, confidence, features, preprocessed_data
        )

        # Step 10: Get highlighted words
        highlighted_words = self.feature_extractor.get_highlighted_words(
            message, preprocessed_data
        )

        # Step 11: Format and return response
        return format_response(
            prediction=prediction_label,
            confidence=confidence,
            spam_probability=spam_probability,
            risk_level=risk_level,
            risk_color=risk_color,
            reasoning=reasoning,
            explanation=explanation,
            highlighted_words=highlighted_words,
            nlp_stats=preprocessed_data['nlp_stats'],
            detected_entities=preprocessed_data['detected_entities'],
            text_stats=features['text_stats'],
            detected_threats=features['detected_threats']
        )

    def is_model_loaded(self):
        """
        Check if the model and vectorizer are loaded.

        Returns:
            bool: True if both model and vectorizer are loaded.
        """
        return self.model is not None and self.vectorizer is not None

    def get_model_info(self):
        """
        Get metadata about the loaded model.

        Returns:
            dict: Model metadata including name, metrics, and training info.
        """
        return self.metadata if self.metadata else {}
