# 🛡️ AI-Powered Spam Detection System

> An intelligent, real-time spam detection web application powered by Machine Learning and Natural Language Processing. Classify messages instantly with detailed threat analysis and confidence scoring.

---

## ✨ Feature Highlights

| Feature | Description |
|---|---|
| 🤖 **Multi-Model ML Pipeline** | Trains Naive Bayes, Logistic Regression & SVM — auto-selects the best performer |
| 🔍 **Advanced NLP Preprocessing** | Tokenization, lemmatization, stopword removal & entity detection |
| 🎯 **Threat Detection Engine** | Identifies 10 categories of spam threats with severity scoring |
| ⚡ **Real-Time Prediction API** | RESTful endpoint with sub-second response times |
| 📊 **Confidence Scoring** | Probability-based confidence percentages for every prediction |
| 🌐 **Modern SPA Frontend** | Responsive single-page application with live results |
| 📦 **Auto Dataset Download** | SMS Spam Collection (UCI) downloaded automatically during training |
| 🔒 **CORS Enabled** | Secure cross-origin resource sharing out of the box |
| 🩺 **Health Check Endpoint** | Built-in service monitoring and status reporting |
| 🚀 **Production Ready** | Gunicorn-compatible with environment variable configuration |

---

## 🏗️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.12+ | Core language |
| Flask | Web framework |
| Flask-CORS | Cross-origin resource sharing |
| Gunicorn | Production WSGI server |

### Machine Learning & NLP
| Technology | Purpose |
|---|---|
| scikit-learn | ML models (Naive Bayes, Logistic Regression, SVM) |
| NLTK | Natural Language Processing pipeline |
| Pandas | Data manipulation & analysis |
| NumPy | Numerical computations |
| Joblib | Model serialization & persistence |

### Frontend
| Technology | Purpose |
|---|---|
| HTML5 | Semantic markup |
| CSS3 | Styling & responsive design |
| Vanilla JavaScript | Client-side logic & API integration |

---

## 📁 Project Structure

```
MP_45/
├── app.py                    # Flask application
├── train_model.py            # Model training script
├── predict.py                # Prediction engine
├── preprocessing.py          # NLP preprocessing pipeline
├── feature_extractor.py      # Feature extraction & threat detection
├── utils.py                  # Utility functions
├── requirements.txt          # Python dependencies
├── README.md                 # Documentation
├── .env.example              # Environment variables template
├── dataset/                  # Training data (auto-downloaded)
│   └── SMSSpamCollection.tsv
├── model/                    # Saved ML artifacts
│   ├── spam_model.pkl
│   └── tfidf_vectorizer.pkl
├── templates/
│   └── index.html            # SPA frontend
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git

### 1. Clone & Navigate

```bash
git clone <repository-url>
cd MP_45
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**Activate the virtual environment:**

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

- **Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('averaged_perceptron_tagger'); nltk.download('averaged_perceptron_tagger_eng')"
```

### 5. Train the Model

```bash
python train_model.py
```

> This will automatically download the SMS Spam Collection dataset, train multiple models, and save the best-performing one to the `model/` directory.

### 6. Run the Application

```bash
python app.py
```

### 7. Open in Browser

Navigate to **[http://localhost:5000](http://localhost:5000)** to access the application.

---

## 📡 API Documentation

### `GET /` — Homepage

Serves the single-page application frontend.

---

### `GET /health` — Health Check

Returns the current status of the service and model readiness.

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-07-14T14:30:00.000Z"
}
```

---

### `POST /predict` — Spam Prediction

Classifies a message as **spam** or **ham** (not spam) with confidence scoring and threat analysis.

**Request:**

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"message": "Congratulations! You have won a $1000 gift card. Click here to claim now!"}'
```

**Request Body:**

```json
{
  "message": "Congratulations! You have won a $1000 gift card. Click here to claim now!"
}
```

**Response:**

```json
{
  "prediction": "spam",
  "confidence": 97.85,
  "threat_analysis": {
    "threats_detected": [
      {
        "category": "Prize/Lottery Scam",
        "severity": "high",
        "matched_keywords": ["congratulations", "won", "claim"]
      },
      {
        "category": "Financial Lure",
        "severity": "medium",
        "matched_keywords": ["$1000", "gift card"]
      }
    ],
    "threat_score": 8.5,
    "risk_level": "high"
  },
  "preprocessing": {
    "original_length": 74,
    "processed_length": 45,
    "entities_detected": {
      "urls": 0,
      "emails": 0,
      "phones": 0,
      "currency": 1
    }
  }
}
```

| Field | Type | Description |
|---|---|---|
| `prediction` | `string` | Classification result: `"spam"` or `"ham"` |
| `confidence` | `float` | Prediction confidence as a percentage (0–100) |
| `threat_analysis` | `object` | Detailed threat categorization and severity |
| `preprocessing` | `object` | NLP preprocessing metadata |

---

## 🧠 NLP Pipeline

The preprocessing pipeline transforms raw text into ML-ready features through the following stages:

```
Raw Message
    │
    ▼
┌─────────────────────┐
│  Entity Detection   │  ← Extracts URLs, emails, phone numbers, currency symbols
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Text Normalization │  ← Lowercasing, HTML tag removal, URL stripping
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Tokenization       │  ← Splits text into individual word tokens
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Stopword Removal   │  ← Filters common English stopwords
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Lemmatization      │  ← Reduces words to base form (e.g., "running" → "run")
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  TF-IDF Vectorizer  │  ← Converts tokens to numerical feature vectors
└─────────┬───────────┘
          │
          ▼
   Feature Vector → ML Model
```

---

## 🚨 Threat Detection Categories

The threat detection engine scans messages for **10 categories** of spam indicators:

| # | Category | Examples | Severity |
|---|---|---|---|
| 1 | **Prize / Lottery Scam** | "you won", "congratulations", "claim your prize" | 🔴 High |
| 2 | **Financial Lure** | "cash bonus", "free money", "credit card" | 🔴 High |
| 3 | **Urgency / Pressure** | "act now", "limited time", "expires today" | 🟡 Medium |
| 4 | **Phishing Attempt** | "verify your account", "confirm identity", "login" | 🔴 High |
| 5 | **Suspicious Links** | Shortened URLs, obfuscated domains | 🔴 High |
| 6 | **Adult Content** | Explicit language and solicitations | 🟡 Medium |
| 7 | **Subscription Trap** | "subscribe", "unsubscribe", "opt out" | 🟢 Low |
| 8 | **Contact Harvesting** | Requests for personal information, emails, phone numbers | 🟡 Medium |
| 9 | **Impersonation** | "from your bank", "customer service", "official notice" | 🔴 High |
| 10 | **Malware / Virus** | "download now", "install", "attachment" | 🔴 High |

Each detected threat contributes to an overall **threat score** (0–10) and **risk level** (low / medium / high).

---

## 📈 Model Training

### Dataset

The system uses the **SMS Spam Collection** dataset from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/sms+spam+collection). It contains **5,574 SMS messages** labeled as either `ham` (legitimate) or `spam`.

- The dataset is **automatically downloaded** during training if not already present.
- Stored at `dataset/SMSSpamCollection.tsv`.

### Training Process

The `train_model.py` script:

1. **Downloads** the SMS Spam Collection dataset (if missing)
2. **Preprocesses** all messages through the NLP pipeline
3. **Extracts features** using TF-IDF vectorization
4. **Trains three models** in parallel:

   | Model | Algorithm | Strengths |
   |---|---|---|
   | Multinomial Naive Bayes | Probabilistic classifier | Fast, works well with text data |
   | Logistic Regression | Linear classifier | Strong baseline, interpretable |
   | Linear SVM | Support Vector Machine | Excellent for high-dimensional text features |

5. **Evaluates** each model using F1 score (weighted) on a held-out test set
6. **Auto-selects** the best-performing model
7. **Saves** the winning model and TF-IDF vectorizer to the `model/` directory

### Output Artifacts

| File | Description |
|---|---|
| `model/spam_model.pkl` | Serialized best-performing classifier |
| `model/tfidf_vectorizer.pkl` | Fitted TF-IDF vectorizer for feature transformation |

---

## 🌍 Deployment

### Production with Gunicorn

For production deployments, use **Gunicorn** as the WSGI server:

```bash
gunicorn app:app -w 4 -b 0.0.0.0:5000
```

| Flag | Description |
|---|---|
| `-w 4` | Number of worker processes (adjust based on CPU cores) |
| `-b 0.0.0.0:5000` | Bind address and port |

**Recommended worker count:** `(2 × CPU cores) + 1`

### Docker (Optional)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('averaged_perceptron_tagger'); nltk.download('averaged_perceptron_tagger_eng')"
RUN python train_model.py
EXPOSE 5000
CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:5000"]
```

---

## ⚙️ Environment Variables

Configure the application using environment variables. Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `FLASK_ENV` | `production` | Environment mode (`development` / `production`) |
| `FLASK_DEBUG` | `0` | Enable debug mode (`0` = off, `1` = on) |
| `PORT` | `5000` | Server port |
| `HOST` | `0.0.0.0` | Server bind address |
| `MODEL_PATH` | `model/spam_model.pkl` | Path to trained model file |
| `VECTORIZER_PATH` | `model/tfidf_vectorizer.pkl` | Path to TF-IDF vectorizer file |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

---

## 📜 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Built with ❤️ using Python, Flask & scikit-learn
</p>
