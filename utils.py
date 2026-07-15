"""
Utility functions for the Spam Detection application.
Provides risk assessment, explanation generation, and response formatting.
"""


def get_risk_level(spam_probability):
    """
    Determine risk level and associated color based on spam probability.

    Args:
        spam_probability (float): Probability of the message being spam (0.0 to 1.0).

    Returns:
        tuple: (risk_level_string, hex_color_string)
    """
    if spam_probability >= 0.8:
        return ('Critical', '#ff1744')
    elif spam_probability >= 0.6:
        return ('High', '#ff5722')
    elif spam_probability >= 0.4:
        return ('Medium', '#ff9800')
    elif spam_probability >= 0.2:
        return ('Low', '#4caf50')
    else:
        return ('Safe', '#00c853')


def generate_explanation(prediction, confidence, features, preprocessed_data):
    """
    Generate a human-readable explanation of why the message was classified.

    Args:
        prediction (str): 'Spam' or 'Ham'.
        confidence (float): Confidence percentage.
        features (dict): Extracted features from FeatureExtractor.
        preprocessed_data (dict): Output from TextPreprocessor.preprocess().

    Returns:
        str: Detailed explanation paragraph.
    """
    nlp_stats = preprocessed_data.get('nlp_stats', {})
    detected_entities = preprocessed_data.get('detected_entities', {})
    detected_threats = features.get('detected_threats', [])
    suspicious_words = features.get('suspicious_words', [])
    urgency_score = features.get('urgency_score', 0)
    financial_score = features.get('financial_score', 0)
    phishing_score = features.get('phishing_score', 0)

    if prediction == 'Spam':
        explanation = (
            f"This message has been classified as SPAM with {confidence:.1f}% confidence. "
        )

        reasons = []

        if detected_threats:
            threat_names = [t.replace('_', ' ').title() for t in detected_threats]
            reasons.append(
                f"it matches known threat patterns including: {', '.join(threat_names)}"
            )

        if suspicious_words:
            top_words = suspicious_words[:5]
            reasons.append(
                f"it contains suspicious keywords such as: {', '.join(top_words)}"
            )

        if urgency_score > 0.1:
            reasons.append(
                "it uses urgency-inducing language designed to pressure quick action"
            )

        if financial_score > 0.1:
            reasons.append(
                "it contains financial incentives or monetary references typical of scams"
            )

        if phishing_score > 0.1:
            reasons.append(
                "it contains phishing indicators attempting to steal credentials or personal data"
            )

        if nlp_stats.get('urls_found', 0) > 0:
            reasons.append(
                f"it contains {nlp_stats['urls_found']} suspicious hyperlink(s)"
            )

        if nlp_stats.get('emails_found', 0) > 0:
            reasons.append(
                f"it contains {nlp_stats['emails_found']} embedded email address(es)"
            )

        if nlp_stats.get('uppercase_ratio', 0) > 0.3:
            reasons.append(
                "it uses excessive uppercase text, a common spam tactic"
            )

        if detected_entities.get('crypto_wallets', []):
            reasons.append(
                "it contains cryptocurrency wallet addresses"
            )

        if reasons:
            explanation += "Specifically, " + "; ".join(reasons) + "."
        else:
            explanation += (
                "The overall pattern of the message matches characteristics "
                "commonly associated with spam or fraudulent messages."
            )

        explanation += (
            " Exercise caution and avoid clicking any links or sharing personal information."
        )

    else:
        explanation = (
            f"This message has been classified as HAM (legitimate) with {confidence:.1f}% confidence. "
        )

        explanation += "The message appears to be a legitimate, conversational communication. "

        safe_reasons = []

        if urgency_score <= 0.1:
            safe_reasons.append("no urgency-inducing language was detected")

        if financial_score <= 0.1:
            safe_reasons.append("no suspicious financial incentives were found")

        if phishing_score <= 0.1:
            safe_reasons.append("no phishing indicators were identified")

        if not detected_threats:
            safe_reasons.append("it does not match any known threat categories")

        if nlp_stats.get('urls_found', 0) == 0:
            safe_reasons.append("no suspicious hyperlinks were found")

        if safe_reasons:
            explanation += "Specifically, " + "; ".join(safe_reasons) + "."
        else:
            explanation += (
                "The message content and structure are consistent with normal communication."
            )

    return explanation


def generate_reasoning(features, preprocessed_data):
    """
    Generate a list of reasoning strings explaining the classification.

    Args:
        features (dict): Extracted features from FeatureExtractor.
        preprocessed_data (dict): Output from TextPreprocessor.preprocess().

    Returns:
        list: List of human-readable reasoning strings.
    """
    reasoning = []
    nlp_stats = preprocessed_data.get('nlp_stats', {})
    detected_entities = preprocessed_data.get('detected_entities', {})
    detected_threats = features.get('detected_threats', [])

    if features.get('urgency_score', 0) > 0.1:
        reasoning.append('Contains urgency language')

    if features.get('financial_score', 0) > 0.1:
        reasoning.append('Contains financial incentives')

    if features.get('phishing_score', 0) > 0.1:
        reasoning.append('Contains phishing indicators')

    if nlp_stats.get('urls_found', 0) > 0:
        reasoning.append('Contains suspicious hyperlinks')

    if nlp_stats.get('emails_found', 0) > 0:
        reasoning.append('Contains email addresses')

    if nlp_stats.get('phones_found', 0) > 0:
        reasoning.append('Contains phone numbers')

    if nlp_stats.get('currency_symbols', 0) > 0:
        reasoning.append('Contains currency references')

    if 'crypto_scam' in detected_threats:
        reasoning.append('Contains crypto-related content')

    if nlp_stats.get('uppercase_ratio', 0) > 0.3:
        reasoning.append('High uppercase usage suggests shouting')

    # If no spam indicators found, it's likely ham
    if not reasoning:
        reasoning.append('Message appears legitimate and conversational')

    return reasoning


def format_response(prediction, confidence, spam_probability, risk_level,
                    risk_color, reasoning, explanation, highlighted_words,
                    nlp_stats, detected_entities, text_stats, detected_threats):
    """
    Format the complete API response dictionary.

    Args:
        prediction (str): 'Spam' or 'Ham'.
        confidence (float): Confidence percentage.
        spam_probability (float): Raw spam probability (0.0 to 1.0).
        risk_level (str): Risk level string.
        risk_color (str): Hex color for risk level.
        reasoning (list): List of reasoning strings.
        explanation (str): Human-readable explanation.
        highlighted_words (list): Suspicious words from original text.
        nlp_stats (dict): NLP statistics.
        detected_entities (dict): Detected entities (urls, emails, etc.).
        text_stats (dict): Text statistics.
        detected_threats (list): List of detected threat categories.

    Returns:
        dict: Complete formatted API response.
    """
    return {
        'prediction': prediction,
        'confidence': round(confidence, 2),
        'spam_probability': round(spam_probability, 4),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'reasoning': reasoning,
        'explanation': explanation,
        'highlighted_words': highlighted_words,
        'nlp_stats': nlp_stats,
        'detected_entities': detected_entities,
        'text_stats': text_stats,
        'detected_threats': detected_threats
    }
