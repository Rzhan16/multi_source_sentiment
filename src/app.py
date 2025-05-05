import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from pathlib import Path
from whitenoise import WhiteNoise

load_dotenv()

from models.unified_sentiment        import get_unified_sentiment
from visualization.plotly_plotter    import PlotlyPlotter

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    static_url_path="/static",
)
app.wsgi_app = WhiteNoise(app.wsgi_app,
                          root=os.path.join(os.path.dirname(__file__), "..", "static"))

plotly = PlotlyPlotter()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        symbol = request.form.get("stock_symbol", "").upper()
        # Get all our time series, counts, CI, price, fundamentals…
        data = get_unified_sentiment(symbol)

        # Build a Plotly Figure
        fig = plotly.build_chart(
            daily            = data["daily_sentiment"],
            rolling_mean     = data["rolling_mean"],
            ci_lower         = data["ci_lower"],
            ci_upper         = data["ci_upper"],
            volume           = data["daily_counts"],
            price_df         = data["stock_history"],
            earnings_dates   = data["fundamentals"]["earnings_dates"],
            symbol           = symbol
        )
        chart_json = fig.to_json()

        return jsonify({
            "stock_symbol": symbol,
            "sentiment": {
                "success"          : data["success"],
                "average_sentiment": data["average_sentiment"],
                "trend"            : data["trend"],
                "sources"          : data["sources"],
                "post_count"       : data["post_count"],
                # optionally return correlation if you compute it
                "corr"             : data.get("corr", None)
            },
            "stock_data": {
                "success": True,
                "data": {
                    "current_price": data["current_price"],
                    "currency"     : data["currency"],
                },
            },
            "fundamentals": data["fundamentals"],
            "chart_json": chart_json
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # for local dev
    app.run(debug=True)
