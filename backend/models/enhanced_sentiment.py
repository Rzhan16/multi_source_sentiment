import re, pandas as pd, nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('vader_lexicon', quiet=True)

class EnhancedSentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.stop_words = set(stopwords.words('english'))
        self.quality_threshold = 0.5

    # ---------- helpers ----------
    def preprocess_text(self, txt: str) -> str:
        txt = re.sub(r'[^a-zA-Z\s]', '', str(txt).lower())
        tokens = [w for w in word_tokenize(txt) if w not in self.stop_words]
        return ' '.join(tokens)

    def calculate_quality_score(self, row):
        score  = 0.3 if len(row['text']) > 100 else 0
        score += 0.3 if row['score'] > 10   else 0
        score += abs(self.sia.polarity_scores(row['text'])['compound']) * 0.4
        return score

    def filter_low_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        df['quality_score'] = df.apply(self.calculate_quality_score, axis=1)
        return df[df.quality_score > self.quality_threshold]

    # ---------- sentiment ----------
    def score(self, txt: str) -> float:
        if not txt:
            return 0
        base = self.sia.polarity_scores(txt)['compound'] * 0.7
        bonus  = (len(txt) / 1000) * 0.1
        bonus += 0.1 if '!' in txt else 0
        bonus -= 0.1 if '?' in txt else 0
        return base + bonus
