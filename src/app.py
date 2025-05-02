from flask import Flask, render_template, request, jsonify
from models.reddit_sentiment import RedditSentimentAnalyzer
from models.stock_data       import StockDataFetcher
from visualization.sentiment_plotter import SentimentPlotter
from dotenv import load_dotenv; load_dotenv()

app = Flask(__name__)
reddit  = RedditSentimentAnalyzer()
stocks  = StockDataFetcher()
plotter = SentimentPlotter()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    symbol = request.form.get('stock_symbol', '').upper()

    reddit_res = reddit.analyze(symbol)
    stock_res  = stocks.get_stock_data(symbol)
    plot_url   = None

    if reddit_res['success']:
        plot_path = f"static/{symbol}_trend.png"
        plotter.trend(reddit.daily_series(), stocks.history(symbol), plot_path)
        plot_url = f"/{plot_path}"

    return jsonify({
        'stock_symbol': symbol,
        'sentiment'   : reddit_res,
        'stock_data'  : stock_res,
        'plot_url'    : plot_url
    })

if __name__ == '__main__':
    app.run(debug=True)
