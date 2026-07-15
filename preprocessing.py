"""
NLP Preprocessing Module for Spam Detection
Handles text cleaning, tokenization, entity detection, and lemmatization.
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize


class TextPreprocessor:
    """Complete NLP text preprocessing pipeline for spam detection."""

    def __init__(self):
        """Initialize NLTK resources and download required data."""
        nltk_resources = [
            'punkt',
            'punkt_tab',
            'stopwords',
            'wordnet',
            'omw-1.4',
            'averaged_perceptron_tagger',
            'averaged_perceptron_tagger_eng'
        ]
        for resource in nltk_resources:
            try:
                nltk.download(resource, quiet=True)
            except Exception as e:
                print(f"Warning: Could not download NLTK resource '{resource}': {e}")

        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

        # Storage for detected entities during preprocessing
        self._detected_urls = []
        self._detected_emails = []
        self._detected_phones = []
        self._detected_currency = []
        self._detected_crypto_wallets = []

    def preprocess(self, text):
        """
        Run the full preprocessing pipeline on the input text.

        Args:
            text (str): Raw input text to preprocess.

        Returns:
            dict: Preprocessing results containing cleaned text, tokens,
                  lemmas, NLP stats, and detected entities.
        """
        if not isinstance(text, str):
            text = str(text)

        original_text = text

        # Reset detected entities for this run
        self._detected_urls = []
        self._detected_emails = []
        self._detected_phones = []
        self._detected_currency = []
        self._detected_crypto_wallets = []

        # Count sentences before cleaning
        try:
            sentence_count = len(sent_tokenize(original_text))
        except Exception:
            sentence_count = len(original_text.split('.'))

        # Calculate uppercase ratio on original text
        alpha_chars = [c for c in original_text if c.isalpha()]
        uppercase_ratio = (
            sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
            if alpha_chars else 0.0
        )

        # Run preprocessing pipeline
        text = self._lowercase(text)
        text = self._remove_html_tags(text)
        text = self._remove_urls(text)
        text = self._remove_emails(text)
        text = self._remove_phone_numbers(text)
        self._detect_currency(original_text)
        self._detect_crypto_wallets(original_text)
        text = self._remove_emojis(text)
        text = self._remove_punctuation(text)
        text = self._remove_numbers(text)
        text = self._remove_extra_spaces(text)

        # Tokenize
        tokens = self._tokenize(text)

        # Remove stopwords
        filtered_tokens, stopwords_removed = self._remove_stopwords(tokens)

        # Lemmatize
        lemmas = self._lemmatize(filtered_tokens)

        # Cleaned text from lemmas
        cleaned_text = ' '.join(lemmas)

        # Calculate average word length
        word_lengths = [len(w) for w in lemmas if w.strip()]
        avg_word_length = (
            round(sum(word_lengths) / len(word_lengths), 2)
            if word_lengths else 0.0
        )

        # Build NLP stats
        nlp_stats = {
            'characters': len(original_text),
            'words': len(original_text.split()),
            'sentences': sentence_count,
            'urls_found': len(self._detected_urls),
            'emails_found': len(self._detected_emails),
            'phones_found': len(self._detected_phones),
            'currency_symbols': len(self._detected_currency),
            'stopwords_removed': stopwords_removed,
            'tokens_count': len(filtered_tokens),
            'lemmas_count': len(lemmas),
            'avg_word_length': avg_word_length,
            'uppercase_ratio': round(uppercase_ratio, 4)
        }

        # Build detected entities
        detected_entities = {
            'urls': self._detected_urls,
            'emails': self._detected_emails,
            'phones': self._detected_phones,
            'currency_symbols': self._detected_currency,
            'crypto_wallets': self._detected_crypto_wallets
        }

        return {
            'original_text': original_text,
            'cleaned_text': cleaned_text,
            'tokens': filtered_tokens,
            'lemmas': lemmas,
            'nlp_stats': nlp_stats,
            'detected_entities': detected_entities
        }

    def _lowercase(self, text):
        """Convert text to lowercase."""
        return text.lower()

    def _remove_html_tags(self, text):
        """Remove HTML tags using regex."""
        return re.sub(r'<[^>]+>', '', text)

    def _remove_urls(self, text):
        """Detect and remove URLs, storing them in detected list."""
        url_pattern = r'https?://\S+|www\.\S+'
        self._detected_urls = re.findall(url_pattern, text)
        return re.sub(url_pattern, ' ', text)

    def _remove_emails(self, text):
        """Detect and remove email addresses, storing them in detected list."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self._detected_emails = re.findall(email_pattern, text)
        return re.sub(email_pattern, ' ', text)

    def _remove_phone_numbers(self, text):
        """Detect and remove phone numbers, storing them in detected list."""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
        self._detected_phones = re.findall(phone_pattern, text)
        # Clean up phone matches (they may be tuples from groups)
        self._detected_phones = [
            p if isinstance(p, str) else ''.join(p)
            for p in self._detected_phones
        ]
        return re.sub(phone_pattern, ' ', text)

    def _detect_currency(self, text):
        """Detect currency symbols and amounts in the text."""
        currency_pattern = r'[\$£€¥₹₿]\s*[\d,]+\.?\d*'
        matches = re.findall(currency_pattern, text)
        # Also detect standalone currency symbols
        symbol_pattern = r'[\$£€¥₹₿]'
        symbols = re.findall(symbol_pattern, text)
        self._detected_currency = matches if matches else symbols

    def _detect_crypto_wallets(self, text):
        """Detect cryptocurrency wallet address patterns."""
        crypto_patterns = [
            r'0x[a-fA-F0-9]{40}',           # Ethereum addresses
            r'1[a-km-zA-HJ-NP-Z1-9]{25,34}', # Bitcoin legacy addresses
            r'3[a-km-zA-HJ-NP-Z1-9]{25,34}', # Bitcoin P2SH addresses
            r'bc1[a-zA-HJ-NP-Z0-9]{25,90}'   # Bitcoin Bech32 addresses
        ]
        wallets = []
        for pattern in crypto_patterns:
            wallets.extend(re.findall(pattern, text))
        self._detected_crypto_wallets = wallets

    def _remove_emojis(self, text):
        """Remove emoji characters using regex on unicode ranges."""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "\U0001f926-\U0001f937"  # supplemental symbols
            "\U00010000-\U0010ffff"  # supplementary
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"
            "\u3030"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(' ', text)

    def _remove_punctuation(self, text):
        """Remove all punctuation characters."""
        return text.translate(str.maketrans('', '', string.punctuation))

    def _remove_extra_spaces(self, text):
        """Collapse multiple spaces into single space and strip."""
        return re.sub(r'\s+', ' ', text).strip()

    def _remove_numbers(self, text):
        """Replace numbers with NUM token."""
        return re.sub(r'\d+', ' NUM ', text)

    def _tokenize(self, text):
        """Split text into tokens using NLTK word_tokenize."""
        try:
            return word_tokenize(text)
        except Exception:
            return text.split()

    def _remove_stopwords(self, tokens):
        """
        Remove English stopwords from token list.

        Returns:
            tuple: (filtered_tokens, count_of_removed_stopwords)
        """
        filtered = [t for t in tokens if t not in self.stop_words]
        removed_count = len(tokens) - len(filtered)
        return filtered, removed_count

    def _lemmatize(self, tokens):
        """Lemmatize tokens using WordNetLemmatizer."""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
