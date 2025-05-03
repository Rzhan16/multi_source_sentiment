import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class SentimentPlotter:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.figsize = (12, 8)

    def plot_sentiment_trend(self, sentiment_data, stock_data=None, title="Sentiment Analysis"):
        """
        Returns a Matplotlib Figure plotting:
         • sentiment_data (pd.Series) on the left y-axis
         • stock_data['Close'] (pd.DataFrame) on the right y-axis, if provided
        """
        fig, ax1 = plt.subplots(figsize=self.figsize)

        if sentiment_data.empty:
            ax1.text(0.5, 0.5, 'No sentiment data available',
                     ha='center', va='center')
        else:
            ax1.plot(sentiment_data.index, sentiment_data.values, label='Sentiment')
            ax1.set_ylabel('Sentiment Score')
            ax1.tick_params(axis='y')

            if stock_data is not None and not stock_data.empty:
                ax2 = ax1.twinx()
                ax2.plot(stock_data.index, stock_data['Close'], color='tab:red', label='Stock Price')
                ax2.set_ylabel('Stock Price')
                ax2.tick_params(axis='y')

        plt.title(title)
        fig.tight_layout()
        return fig

    def save_plot(self, fig, filename):
        """
        Save a Matplotlib Figure to disk, creating parent dirs if needed.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        fig.savefig(filename)
        plt.close(fig)
