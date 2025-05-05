import os
import plotly.graph_objs as go
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from pathlib import Path
from whitenoise import WhiteNoise

load_dotenv()

from models.unified_sentiment     import get_unified_sentiment
from visualization.plotly_plotter import PlotlyPlotter

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    static_url_path="/static",
)
app.wsgi_app = WhiteNoise(
    app.wsgi_app,
    root=os.path.join(os.path.dirname(__file__), "..", "static")
)

plotly = PlotlyPlotter()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # ── Read inputs ──
        sym = request.form.get("stock_symbol", "").upper()
        window = int(request.form.get("window", 5))
        include_twitter = request.form.get("twitter", "false") == "true"

        # ── Get unified sentiment & stock data ──
        unified = get_unified_sentiment(sym, window, include_twitter)

        # ── Fundamentals ──
        fundamentals = {
            "pe": unified.get("pe"),
            "eps": unified.get("eps")
        }

        # ── Compute correlation ──
        hist = unified["stock_history"]
        returns = hist["Close"].pct_change().shift(-1)
        daily = unified["daily_sentiment"]
        corr = float(daily.corr(returns) or 0)

        # ── Build Plotly figure ──
        fig = go.Figure()

        # volume bars
        fig.add_trace(go.Bar(
            x=unified["daily_counts"].index,
            y=unified["daily_counts"].values,
            marker_opacity=0.2,
            name="Post Count",
            yaxis="y1"
        ))

        # raw daily sentiment
        fig.add_trace(go.Scatter(
            x=daily.index, y=daily.values,
            mode="lines+markers",
            line=dict(dash="dot"),
            name="Daily Sentiment",
            yaxis="y1"
        ))

        # smoothed rolling mean
        fig.add_trace(go.Scatter(
            x=unified["rolling_mean"].index,
            y=unified["rolling_mean"].values,
            name=f"{window}-day MA",
            yaxis="y1"
        ))

        # CI ribbon
        fig.add_trace(go.Scatter(
            x=unified["ci_upper"].index,
            y=unified["ci_upper"].values,
            fill=None, mode="lines",
            line_color="lightgrey",
            showlegend=False,
            yaxis="y1"
        ))
        fig.add_trace(go.Scatter(
            x=unified["ci_lower"].index,
            y=unified["ci_lower"].values,
            fill="tonexty", mode="lines",
            line_color="lightgrey",
            name="±1σ CI",
            yaxis="y1"
        ))

        # stock price
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist["Close"],
            name="Stock Price",
            yaxis="y2"
        ))

        # layout
        fig.update_layout(
            xaxis=dict(domain=[0, 1]),
            yaxis=dict(title="Sentiment Score"),
            yaxis2=dict(
                title="Stock Price",
                overlaying="y",
                side="right"
            ),
            legend=dict(orientation="h", x=0, y=1.1),
            margin=dict(t=50, b=50)
        )

        chart_json = fig.to_json()

        return jsonify({
            "fundamentals": fundamentals,
            "sentiment": {
                "average_sentiment": unified["average_sentiment"],
                "trend": unified["trend"],
                "corr": corr
            },
            "chart_json": chart_json
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # For development only; in prod use Gunicorn
    app.run(debug=True)
