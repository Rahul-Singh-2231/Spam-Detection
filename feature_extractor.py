"""
Feature Extraction and Threat Detection Module for Spam Detection.
Analyzes text for suspicious patterns, urgency, financial bait, phishing, and known scam categories.
"""


class FeatureExtractor:
    """Extracts spam-related features and detects threat categories from text."""

    def __init__(self):
        """Initialize keyword dictionaries for threat categories."""
        self.URGENCY_WORDS = [
            'urgent', 'immediately', 'act now', 'hurry', 'limited time',
            'expires', 'deadline', 'asap', "don't miss", 'last chance',
            'now', 'today only', 'quick'
        ]

        self.FINANCIAL_WORDS = [
            'prize', 'winner', 'won', 'cash', 'money', 'free', 'bonus',
            'reward', 'claim', 'million', 'dollar', 'bank', 'account',
            'credit', 'invest', 'profit', 'income', 'earn', 'guaranteed'
        ]

        self.PHISHING_WORDS = [
            'click', 'link', 'verify', 'confirm', 'update', 'suspend',
            'unauthorized', 'security', 'password', 'login', 'credentials',
            'ssn', 'social security'
        ]

        self.ACTION_WORDS = [
            'call', 'text', 'reply', 'send', 'contact', 'visit',
            'subscribe', 'register', 'sign up', 'download', 'install'
        ]

        self.THREAT_CATEGORIES = {
            'lottery_scam': [
                'lottery', 'jackpot', 'sweepstakes', 'raffle', 'draw',
                'prize', 'winner', 'won', 'selected', 'lucky'
            ],
            'banking_fraud': [
                'bank', 'account', 'transaction', 'suspicious activity',
                'verify', 'blocked', 'unauthorized', 'atm', 'debit',
                'credit card'
            ],
            'otp_fraud': [
                'otp', 'one time password', 'verification code', 'pin',
                'security code', 'authenticate'
            ],
            'crypto_scam': [
                'bitcoin', 'crypto', 'ethereum', 'blockchain', 'wallet',
                'nft', 'token', 'mining', 'btc', 'eth', 'airdrop'
            ],
            'investment_scam': [
                'invest', 'stock', 'trading', 'forex', 'return', 'profit',
                'guaranteed', 'portfolio', 'mutual fund', 'scheme'
            ],
            'job_scam': [
                'job', 'hiring', 'work from home', 'salary', 'vacancy',
                'recruitment', 'career', 'position', 'apply', 'resume',
                'offer letter'
            ],
            'delivery_scam': [
                'delivery', 'package', 'shipment', 'tracking', 'courier',
                'parcel', 'order', 'shipping', 'dispatch', 'customs'
            ],
            'govt_impersonation': [
                'government', 'irs', 'tax', 'refund', 'social security',
                'medicare', 'federal', 'department', 'official', 'authority'
            ],
            'tech_support_scam': [
                'virus', 'malware', 'infected', 'hacked', 'computer',
                'tech support', 'microsoft', 'apple', 'windows', 'firewall'
            ]
        }

    def extract_features(self, text, preprocessed_data):
        """
        Extract all spam-detection features from the text.

        Args:
            text (str): Original input text.
            preprocessed_data (dict): Output from TextPreprocessor.preprocess().

        Returns:
            dict: Complete feature set including scores, threats, and statistics.
        """
        text_lower = text.lower()

        # Text statistics
        char_count = len(text)
        words = text.split()
        word_count = len(words)
        try:
            from nltk.tokenize import sent_tokenize
            sentence_count = len(sent_tokenize(text))
        except Exception:
            sentence_count = len(text.split('.'))

        word_lengths = [len(w) for w in words if w.strip()]
        avg_word_length = (
            round(sum(word_lengths) / len(word_lengths), 2)
            if word_lengths else 0.0
        )

        alpha_chars = [c for c in text if c.isalpha()]
        uppercase_ratio = (
            sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
            if alpha_chars else 0.0
        )

        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_char_ratio = (
            round(special_chars / len(text), 4) if len(text) > 0 else 0.0
        )

        text_stats = {
            'character_count': char_count,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'uppercase_ratio': round(uppercase_ratio, 4),
            'special_char_ratio': special_char_ratio
        }

        # Find suspicious words across all categories
        all_suspicious_words = set()
        for word_list in [self.URGENCY_WORDS, self.FINANCIAL_WORDS,
                          self.PHISHING_WORDS, self.ACTION_WORDS]:
            matched = self._find_matching_words(text_lower, word_list)
            all_suspicious_words.update(matched)

        # Calculate category scores
        urgency_matched = self._find_matching_words(text_lower, self.URGENCY_WORDS)
        financial_matched = self._find_matching_words(text_lower, self.FINANCIAL_WORDS)
        phishing_matched = self._find_matching_words(text_lower, self.PHISHING_WORDS)
        action_matched = self._find_matching_words(text_lower, self.ACTION_WORDS)

        urgency_score = self._calculate_score(urgency_matched, self.URGENCY_WORDS)
        financial_score = self._calculate_score(financial_matched, self.FINANCIAL_WORDS)
        phishing_score = self._calculate_score(phishing_matched, self.PHISHING_WORDS)
        action_score = self._calculate_score(action_matched, self.ACTION_WORDS)

        # Detect threats
        detected_threats, threat_details = self._detect_threats(text_lower)

        # Calculate overall suspicion score (weighted average)
        overall_suspicion_score = (
            urgency_score * 0.25 +
            financial_score * 0.30 +
            phishing_score * 0.30 +
            action_score * 0.15
        )

        return {
            'text_stats': text_stats,
            'suspicious_words': list(all_suspicious_words),
            'urgency_score': round(urgency_score, 4),
            'financial_score': round(financial_score, 4),
            'phishing_score': round(phishing_score, 4),
            'action_score': round(action_score, 4),
            'detected_threats': detected_threats,
            'threat_details': threat_details,
            'overall_suspicion_score': round(overall_suspicion_score, 4)
        }

    def _find_matching_words(self, text, word_list):
        """
        Find which words from a list appear in the text as whole words/phrases.

        Args:
            text (str): Text to search in (should be lowercase).
            word_list (list): List of keywords to search for.

        Returns:
            list: List of matched keywords found in text.
        """
        import re
        matched = []
        for word in word_list:
            # Use word boundaries to avoid matching substrings in larger words
            pattern = rf'\b{re.escape(word)}\b'
            if re.search(pattern, text):
                matched.append(word)
        return matched

    def _calculate_score(self, matched, total_keywords):
        """
        Calculate a 0-1 score based on matched keywords.

        Args:
            matched (list): List of matched keywords.
            total_keywords (list): Complete list of keywords for the category.

        Returns:
            float: Score between 0.0 and 1.0.
        """
        if not total_keywords:
            return 0.0
        return min(len(matched) / len(total_keywords), 1.0)

    def _detect_threats(self, text):
        """
        Check text against all threat categories.

        Args:
            text (str): Lowercase text to analyze.

        Returns:
            tuple: (list of detected threat category names,
                     dict mapping category to matched keywords)
        """
        detected_threats = []
        threat_details = {}

        for category, keywords in self.THREAT_CATEGORIES.items():
            matched = self._find_matching_words(text, keywords)
            if matched:
                detected_threats.append(category)
                threat_details[category] = matched

        return detected_threats, threat_details

    def get_highlighted_words(self, text, preprocessed_data):
        """
        Return list of suspicious words found in the original text,
        preserving case for display.

        Args:
            text (str): Original input text.
            preprocessed_data (dict): Output from TextPreprocessor.preprocess().

        Returns:
            list: Suspicious words found in the original text with preserved case.
        """
        text_lower = text.lower()
        words_in_text = text.split()
        highlighted = []

        # Collect all suspicious keywords
        all_keywords = set()
        for word_list in [self.URGENCY_WORDS, self.FINANCIAL_WORDS,
                          self.PHISHING_WORDS, self.ACTION_WORDS]:
            all_keywords.update(word_list)

        for category_keywords in self.THREAT_CATEGORIES.values():
            all_keywords.update(category_keywords)

        # Find original-case words that match suspicious keywords
        for word in words_in_text:
            clean_word = word.strip('.,!?;:()[]{}"\'-').lower()
            if clean_word in all_keywords and word not in highlighted:
                highlighted.append(word)

        # Also check multi-word phrases
        for keyword in all_keywords:
            if ' ' in keyword and keyword in text_lower:
                # Find the original case version
                start_idx = text_lower.find(keyword)
                if start_idx != -1:
                    original_phrase = text[start_idx:start_idx + len(keyword)]
                    if original_phrase not in highlighted:
                        highlighted.append(original_phrase)

        return highlighted
