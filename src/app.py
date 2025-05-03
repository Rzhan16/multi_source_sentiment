import os
from flask import Flask, render_template, request, jsonify, url_for
from dotenv import load_dotenv
from pathlib import Path
from whitenoise import WhiteNoise

load_dotenv()

from models.unified_sentiment import get_unified_sentiment
from visualization.sentiment_plotter import SentimentPlotter

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    static_url_path="/static",
)
# Let Gunicorn serve static files directly
app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(os.path.dirname(__file__), "..", "static"))

plotter = SentimentPlotter()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        symbol = request.form.get("stock_symbol", "").upper()
        unified = get_unified_sentiment(symbol)
        plot_url = None

        daily   = unified["daily_sentiment"]
        history = unified["stock_history"]

        if unified.get("success") and hasattr(daily, "empty") and not daily.empty:
            static_dir = Path(__file__).resolve().parent.parent / "static"
            static_dir.mkdir(exist_ok=True)

            plot_path = static_dir / f"{symbol}_trend.png"
            fig = plotter.plot_sentiment_trend(
                unified["daily_sentiment"],
                unified["stock_history"],
                title=f"{symbol} Sentiment vs Price",
                daily_counts = unified["daily_counts"],
                rolling_mean = unified["rolling_mean"],
                ci_lower     = unified["ci_lower"],
                ci_upper     = unified["ci_upper"],
            )
            plotter.save_plot(fig, plot_path)
            plot_url = url_for("static", filename=f"{symbol}_trend.png")

        return jsonify({
            "stock_symbol": symbol,
            "sentiment": {
                "success"          : unified["success"],
                "average_sentiment": unified["average_sentiment"],
                "trend"            : unified["trend"],
                "sources"          : unified["sources"],
                "post_count"       : unified["post_count"],
            },
            "stock_data": {
                "success": True,
                "data": {
                    "current_price": unified["current_price"],
                    "currency"     : unified["currency"],
                },
            },
            "plot_url": plot_url,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # For development; in production run via gunicorn
    app.run(debug=True)
