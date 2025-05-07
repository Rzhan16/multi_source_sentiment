import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from pathlib import Path
from whitenoise import WhiteNoise
import plotly.graph_objs as go

# ─── Load env & custom modules ───
load_dotenv()
from models.unified_sentiment import get_unified_sentiment
from models.fundamentals       import FundamentalsFetcher

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
    static_url_path='/static'
)
# serve static with WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(os.path.dirname(__file__), '..', 'static'))

fund_fetcher = FundamentalsFetcher()

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # ── inputs ─────────────────────────────────────────────────────
        sym             = request.form.get("stock_symbol", "").upper()
        window          = int(request.form.get("window", 5))
        include_twitter = request.form.get("twitter", "false") == "true"

        # ── data gathering ────────────────────────────────────────────
        unified      = get_unified_sentiment(sym, window, include_twitter)
        fundamentals = {
            "pe" : unified["pe"],
            "eps": unified["eps"]
        }

        # correlation: sentiment (t) vs return (t+1)
        hist    = unified["stock_history"]
        returns = hist["Close"].pct_change().shift(-1)
        corr    = float(unified["daily_sentiment"].corr(returns) or 0)

        # ── build Plotly chart (unchanged) ────────────────────────────
        # ... [chart‑building code] ...
        chart_json = fig.to_json()

        # ── API response ─────────────────────────────────────────────
        return jsonify({
            "fundamentals": fundamentals,
            "sentiment": {
                "average_sentiment": unified["average_sentiment"],
                "trend"            : unified["trend"],
                "corr"             : corr,
                "sources"          : unified["sources"]
            },
            "chart_json": chart_json
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
