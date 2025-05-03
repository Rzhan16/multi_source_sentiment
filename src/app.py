import os
from flask import Flask, render_template, request, jsonify, url_for
from dotenv import load_dotenv
from pathlib import Path

# Load secrets
load_dotenv()

# Your unified logic & plotter
from models.unified_sentiment import get_unified_sentiment
from visualization.sentiment_plotter import SentimentPlotter

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
        unified = get_unified_sentiment(symbol)

        # Always fetch the current price & currency from your unified result
        current_price = unified.get("current_price", 0)
        currency      = unified.get("currency", "USD")

        # Build chart if we have a time series
        plot_url = None
        daily = unified.get("daily_sentiment")
        history = unified.get("stock_history")
        if unified.get("success") and hasattr(daily, "empty") and not daily.empty:
            static_dir = Path(__file__).resolve().parent.parent / 'static'
            static_dir.mkdir(exist_ok=True)
            plot_path = static_dir / f"{symbol}_trend.png"

            fig = plotter.plot_sentiment_trend(
                daily,         # pd.Series of sentiment
                history,       # DataFrame from stock_data.history()
                title=f"{symbol} Sentiment vs Price"
            )
            plotter.save_plot(fig, plot_path)
            plot_url = url_for('static', filename=f"{symbol}_trend.png")

        return jsonify({
            "stock_symbol": symbol,
            "sentiment": {
                "success"          : unified.get("success", False),
                "average_sentiment": unified.get("average_sentiment", 0),
                "trend"            : unified.get("trend", "Neutral"),
                "sources"          : unified.get("sources", {}),
                "post_count"       : unified.get("post_count", 0)
            },
            "stock_data": {
                "success": True,
                "data": {
                    "current_price": current_price,
                    "currency"     : currency
                }
            },
            "plot_url": plot_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
