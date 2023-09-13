import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def clean_data(df):
    # Remove the duplicate header row
    df = df.drop(0)
    # Fill missing values with 0
    df.fillna("0", inplace=True)
    # Convert string numbers in month columns to float by removing commas
    month_columns = df.columns[3:]
    for column in month_columns:
        df[column] = df[column].str.replace(",", "").astype(float)
    return df


def monthly_revenue_trend(df):
    df["Profit Center Prefix"] = df["Profit Center"].str[:2]
    month_columns = df.columns[3:]
    grouped_revenue = (
        df[df["Item"] == "Revenue"]
        .groupby(["Profit Center Prefix"])[month_columns]
        .sum(numeric_only=True)
        .abs()
        .transpose()
    )
    fig = go.Figure()
    for prefix in grouped_revenue.columns:
        fig.add_trace(
            go.Scatter(
                x=grouped_revenue.index,
                y=grouped_revenue[prefix],
                mode="lines+markers",
                name=prefix,
            )
        )

    fig.update_layout(
        title="Monthly Revenue Trend by Profit Center Prefix",
        xaxis_title="Month",
        yaxis_title="Revenue",
    )
    return fig


def monthly_expense_breakdown(df):
    expenses_df = df[df["Item"] != "Revenue"]
    month_columns = df.columns[3:]
    grouped_expenses = expenses_df.groupby("Item")[month_columns].sum()
    fig = px.bar(
        grouped_expenses.transpose(),
        x=grouped_expenses.transpose().index,
        y=grouped_expenses.columns,
        height=600,
        title="Monthly Expense Breakdown by Type",
        labels={"x": "Month", "y": "Expense Amount"},
        template="plotly_dark",
    )
    return fig


def total_revenue_vs_expenses(df):
    print(df.head())
    month_columns = df.columns[3:]

    # Calculate total revenue and total expenses for each month
    total_revenue = (
        df[df["Item"] == "Revenue"][month_columns].sum(numeric_only=True).abs()
    )
    total_expenses = (
        df[df["Item"] != "Revenue"][month_columns].sum(numeric_only=True).abs()
    )

    # Print the heads of total_revenue and total_expenses to inspect
    print(total_revenue.head())
    print(total_expenses.head())

    # Create a new DataFrame for easy plotting
    comparison_df = pd.DataFrame(
        {"Total Revenue": total_revenue, "Total Expenses": total_expenses}
    )
    fig = px.bar(
        comparison_df,
        x=comparison_df.index,
        y=["Total Revenue", "Total Expenses"],
        title="Total Revenue vs. Total Expenses Month over Month",
        labels={"x": "Month", "y": "Amount"},
        template="plotly_dark",
    )
    return fig


def monthly_net_profit_loss(df):
    month_columns = df.columns[3:]
    # Convert revenue values to positive
    df.loc[df["Item"] == "Revenue", month_columns] = df.loc[
        df["Item"] == "Revenue", month_columns
    ]
    # Step 3: Calculate the profit for each month
    profit = (
        df[df["Item"] == "Revenue"][month_columns].sum(numeric_only=True).abs()
        - df[df["Item"] != "Revenue"][month_columns].sum(numeric_only=True).abs()
    )
    # Convert profit to DataFrame for easier plotting
    profit_df = profit.reset_index()
    profit_df.columns = ["Month", "Profit"]
    fig = px.line(
        profit_df,
        x="Month",
        y="Profit",
        title="Month over Month Profit",
        labels={"x": "Month", "y": "Profit"},
        template="plotly_dark",
    )
    return fig
