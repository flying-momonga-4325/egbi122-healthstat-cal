import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path


class ChartManager:
    def __init__(
        self, cal_file="data/cal_rec.csv", personal_file="data/personal_info.csv"
    ):
        self.cal_file = cal_file
        self.personal_file = personal_file

    def build_last_7_days_chart(self, user="default"):
        # Load CSVs
        cal_df = (
            pd.read_csv(self.cal_file, parse_dates=["time"])
            if Path(self.cal_file).exists()
            else pd.DataFrame()
        )
        personal_df = (
            pd.read_csv(self.personal_file, parse_dates=["time"])
            if Path(self.personal_file).exists()
            else pd.DataFrame()
        )

        today = datetime.today().date()
        date_range = pd.date_range(end=today, periods=7).date

        # Filter by user
        cal_df = (
            cal_df[cal_df["name"] == user]
            if not cal_df.empty
            else pd.DataFrame(columns=["time", "food", "cal"])
        )
        personal_df = (
            personal_df[personal_df["name"] == user]
            if not personal_df.empty
            else pd.DataFrame(columns=["time", "tdee"])
        )

        # Process food intake
        if not cal_df.empty:
            cal_df["date"] = cal_df["time"].dt.date
            food_summary = cal_df.groupby(["date", "food"])["cal"].sum().reset_index()
            food_pivot = food_summary.pivot(
                index="date", columns="food", values="cal"
            ).fillna(0)
        else:
            food_pivot = pd.DataFrame(index=date_range)

        food_pivot = food_pivot.reindex(date_range, fill_value=0)
        total_intake = food_pivot.sum(axis=1)

        # Process TDEE
        if not personal_df.empty:
            personal_df["date"] = personal_df["time"].dt.date
            tdee_series = personal_df.groupby("date")["tdee"].last()
            tdee_series = tdee_series.reindex(date_range).ffill().fillna(0)
        else:
            tdee_series = pd.Series([0] * 7, index=date_range)

        # Build figure
        fig = go.Figure()
        colors = px.colors.qualitative.Plotly

        # Stacked bar for food
        for i, food_name in enumerate(food_pivot.columns):
            fig.add_trace(
                go.Bar(
                    x=date_range,
                    y=food_pivot[food_name],
                    name=food_name,
                    marker_color=colors[i % len(colors)],
                    hovertemplate="%{y} kcal of " + food_name + "<extra></extra>",
                )
            )

        tdee_colors = [
            "green" if tdee_series[d] >= total_intake[d] else "red" for d in date_range
        ]

        # Line for TDEE
        fig.add_trace(
            go.Scatter(
                x=date_range,
                y=tdee_series,
                mode="lines+markers",
                name="TDEE",
                line=dict(color="gray", width=2),  # optional line connecting points
                marker=dict(size=10, color=tdee_colors, symbol="circle"),
                hovertemplate="TDEE: %{y} kcal<extra></extra>",
            )
        )

        fig.update_layout(
            barmode="stack",
            title=f"Last 7 Days: TDEE vs Food Intake ({user})",
            xaxis_title="Date",
            yaxis_title="Calories",
            legend_title="Foods / TDEE",
            template="plotly_white",
            xaxis=dict(tickformat="%Y-%m-%d"),
        )

        return fig
