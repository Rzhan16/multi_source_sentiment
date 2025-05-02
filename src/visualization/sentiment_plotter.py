import matplotlib, os
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class SentimentPlotter:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.size=(12,8)

    def trend(self, series, price=None, out_path="static/trend.png"):
        fig, ax1 = plt.subplots(figsize=self.size)
        if series.empty:
            ax1.text(.5,.5,'No data',ha='center',va='center')
        else:
            ax1.plot(series.index, series.values, color='tab:blue')
            ax1.set_ylabel('Sentiment', color='tab:blue')
            ax1.tick_params(axis='y', labelcolor='tab:blue')
            if price is not None and not price.empty:
                ax2 = ax1.twinx()
                ax2.plot(price.index, price.Close, color='tab:red')
                ax2.set_ylabel('Close', color='tab:red')
                ax2.tick_params(axis='y', labelcolor='tab:red')
        fig.tight_layout()
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        fig.savefig(out_path)
        plt.close(fig)
