import os
from flask import Flask, render_template, request, jsonify, url_for
from dotenv import load_dotenv
from pathlib import Path

# Load secrets from .env
load_dotenv()

# Custom modules
from models.unified_sentiment   import get_unified_sentiment
from visualization.sentiment_plotter import SentimentPlotter

# Flask app config: serve static/ from repo root
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
    static_url_path='/static'
)

plotter = SentimentPlotter()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        symbol = request.form.get('stock_symbol', '').upper()

        # 1) Get all-in-one sentiment + stock info
        unified  = get_unified_sentiment(symbol)
        plot_url = None

        # 2) If we have a time series, generate & save the chart
        if unified.get("success") and not unified["daily_sentiment"].empty:
            static_dir = Path(__file__).resolve().parent.parent / 'static'
            static_dir.mkdir(exist_ok=True)

            plot_path = static_dir / f"{symbol}_trend.png"
            fig = plotter.plot_sentiment_trend(
                unified["daily_sentiment"],
                unified["stock_history"],
                title=f"{symbol} Sentiment vs Price"
            )
            plotter.save_plot(fig, plot_path)

            plot_url = url_for('static', filename=f"{symbol}_trend.png")

        # 3) Return JSON for frontend
        return jsonify({
            "stock_symbol": symbol,
            "sentiment": {
                "average_sentiment": unified["average_sentiment"],
                "trend"            : unified["trend"],
                "sources"          : unified["sources"],
                "post_count"       : unified["post_count"]
            },
            "stock_data": {
                "success": True,
                "data": {
                    "current_price": unified["current_price"],
                    "currency"     : unified["currency"]
                }
            },
            "plot_url": plot_url
        })

    except Exception as e:
        # catch ANY error and return as JSON
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
