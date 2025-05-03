import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class SentimentPlotter:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.figsize = (12, 8)

    def plot_sentiment_trend(
        self,
        sentiment_data,
        stock_data=None,
        title="Sentiment Analysis",
        daily_counts=None,
        rolling_mean=None,
        ci_lower=None,
        ci_upper=None
    ):
        fig, ax1 = plt.subplots(figsize=self.figsize)

        # 1) plot volume bars (behind)
        if daily_counts is not None and not daily_counts.empty:
            ax1.bar(
                daily_counts.index,
                daily_counts.values,
                alpha=0.2,
                label='Post Count'
            )

        # 2) plot raw daily sentiment
        if hasattr(sentiment_data, 'empty') and not sentiment_data.empty:
            ax1.plot(
                sentiment_data.index,
                sentiment_data.values,
                linestyle=':',
                label='Daily Sentiment'
            )

        # 3) plot rolling mean
        if rolling_mean is not None and hasattr(rolling_mean, 'empty') and not rolling_mean.empty:
            ax1.plot(
                rolling_mean.index,
                rolling_mean.values,
                color='blue',
                label='Smoothed (5-day MA)'
            )

        # 4) shade CI
        if ci_lower is not None and ci_upper is not None:
            ax1.fill_between(
                ci_lower.index,
                ci_lower.values,
                ci_upper.values,
                color='grey',
                alpha=0.3,
                label='±1 σ CI'
            )

        ax1.set_ylabel('Sentiment Score')
        ax1.tick_params(axis='y')

        # 5) plot stock price on secondary axis
        if stock_data is not None and not stock_data.empty:
            ax2 = ax1.twinx()
            ax2.plot(
                stock_data.index,
                stock_data['Close'],
                color='tab:red',
                label='Stock Price'
            )
            ax2.set_ylabel('Stock Price')
            ax2.tick_params(axis='y')

        plt.title(title)
        ax1.legend(loc='upper left')
        if stock_data is not None and not stock_data.empty:
            ax2.legend(loc='upper right')
        fig.tight_layout()
        return fig

    def save_plot(self, fig, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        fig.savefig(filename)
        plt.close(fig)
