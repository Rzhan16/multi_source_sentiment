import os
from flask import Flask, render_template, request, jsonify, url_for
from dotenv import load_dotenv
from pathlib import Path

from models.unified_sentiment import get_unified_sentiment
from models.stock_data import StockDataFetcher
from visualization.sentiment_plotter import SentimentPlotter

load_dotenv()

app = Flask(__name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
    static_url_path='/static'
)

stocks = StockDataFetcher()
plotter = SentimentPlotter()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    symbol = request.form.get('stock_symbol', '').upper()
    sentiment_res = get_unified_sentiment(symbol)
    stock_res = stocks.get_stock_data(symbol)

    plot_url = None
    if sentiment_res.get('success'):
        static_dir = Path(__file__).resolve().parent.parent / 'static'
        static_dir.mkdir(exist_ok=True)
        plot_path = static_dir / f'{symbol}_trend.png'
        plotter.trend(symbol, plot_path)
        plot_url = url_for('static', filename=f'{symbol}_trend.png')

    return jsonify({
        'stock_symbol': symbol,
        'sentiment': sentiment_res,
        'stock_data': stock_res,
        'plot_url': plot_url
    })

if __name__ == '__main__':
    app.run(debug=True)
