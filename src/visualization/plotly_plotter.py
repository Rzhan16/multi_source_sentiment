# src/visualization/plotly_plotter.py
import plotly.graph_objs as go

class PlotlyPlotter:
    def build_chart(
        self,
        daily, rolling_mean, ci_lower, ci_upper, volume,
        price_df, earnings_dates, symbol
    ):
        fig = go.Figure()

        # Volume bars
        fig.add_trace(go.Bar(
            x=volume.index, y=volume.values,
            name="Post Count", opacity=0.3, yaxis="y2"
        ))

        # Raw sentiment
        fig.add_trace(go.Scatter(
            x=daily.index, y=daily.values,
            mode="lines", name="Daily Sentiment", line={"dash":"dot"}
        ))

        # Smoothed mean
        fig.add_trace(go.Scatter(
            x=rolling_mean.index, y=rolling_mean.values,
            name="Smoothed (5-day MA)"
        ))

        # CI band
        fig.add_trace(go.Scatter(
            x=ci_upper.index.tolist() + ci_lower.index[::-1].tolist(),
            y=ci_upper.values.tolist() + ci_lower.values[::-1].tolist(),
            fill="toself", fillcolor="rgba(128,128,128,0.2)",
            line={"width":0}, name="±1σ CI"
        ))

        # Price line
        fig.add_trace(go.Scatter(
            x=price_df.index, y=price_df["Close"],
            name=f"{symbol} Price", yaxis="y3", line={"color":"red"}
        ))

        # Earnings vertical lines
        for d in earnings_dates:
            fig.add_vline(x=d, line_dash="dash", line_color="green")

        # Layout
        fig.update_layout(
            title=f"{symbol} Sentiment & Price",
            xaxis=dict(domain=[0,0.8]),
            yaxis=dict(title="Sentiment"),
            yaxis2=dict(title="Volume", overlaying="y", side="right"),
            yaxis3=dict(title="Price", anchor="x", overlaying="y", side="right", position=0.9),
            legend=dict(x=0.82, y=1.1),
            hovermode="x unified"
        )
        return fig
