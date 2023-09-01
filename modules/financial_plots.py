import pandas as pd
import matplotlib.pyplot as plt


def clean_data(df):
    # Remove the duplicate header row
    df = df.drop(0)
    # Fill missing values with 0
    df.fillna('0', inplace=True)
    # Convert string numbers in month columns to float by removing commas
    month_columns = df.columns[3:]
    for column in month_columns:
        df[column] = df[column].str.replace(',', '').astype(float)
    return df

def monthly_revenue_trend(df):
    """Generate a stacked area chart for monthly revenue trend."""
    df['Profit Center Prefix'] = df['Profit Center'].str[:2]
    month_columns = df.columns[3:]
    # Group by the new prefix and month, then aggregate the revenue
    grouped_revenue = df[df['Item'] == 'Revenue'].groupby(['Profit Center Prefix'])[month_columns].sum().abs().transpose()
    # Plotting the monthly revenue trend for each profit center prefix
    plt.figure(figsize=(14, 8))
    for prefix in grouped_revenue.columns:
        plt.plot(grouped_revenue.index, grouped_revenue[prefix], marker='o', label=prefix)
    plt.title('Monthly Revenue Trend by Profit Center Prefix')
    plt.xlabel('Month')
    plt.ylabel('Revenue')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def monthly_expense_breakdown(df):
    expenses_df = df[df['Item'] != 'Revenue']
    month_columns = df.columns[3:]
    # Group by 'Item' and aggregate expenses for each month
    grouped_expenses = expenses_df.groupby('Item')[month_columns].sum()
    # Plotting a stacked bar chart for the monthly expense breakdown
    plt.figure(figsize=(14, 8))
    grouped_expenses.transpose().plot(kind='bar', stacked=True, figsize=(14,8), colormap='tab20', ax=plt.gca())
    plt.title('Monthly Expense Breakdown by Type')
    plt.xlabel('Month')
    plt.ylabel('Expense Amount')
    plt.grid(axis='y')
    plt.xticks(rotation=45)
    plt.legend(title="Expense Type", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    return plt

def total_revenue_vs_expenses(df):
    print(df.head())
    month_columns = df.columns[3:]

    # Calculate total revenue and total expenses for each month
    total_revenue = df[df['Item'] == 'Revenue'][month_columns].sum(numeric_only=True).abs()
    total_expenses = df[df['Item'] != 'Revenue'][month_columns].sum(numeric_only=True)
    
    # Print the heads of total_revenue and total_expenses to inspect
    print(total_revenue.head())
    print(total_expenses.head())
    
    # Create a new DataFrame for easy plotting
    comparison_df = pd.DataFrame({
        'Total Revenue': total_revenue,
        'Total Expenses': total_expenses
    })
    
    # Print the head of comparison_df to inspect
    print(comparison_df.head())

    # Setting custom colors for the bars
    colors = ['#264653', '#E76F51']  # deep blue for revenue, dark red for expenses

    # Plotting with the custom colormap
    comparison_df.plot(kind='bar', figsize=(12,7), color=colors)

    plt.title('Total Revenue vs. Total Expenses Month over Month')
    plt.xlabel('Month')
    plt.ylabel('Amount')
    plt.grid(axis='y')
    plt.xticks(rotation=45)
    plt.legend(loc="upper left")
    plt.tight_layout()
    return plt


def monthly_net_profit_loss(df):
    month_columns = df.columns[3:]  
    # Convert revenue values to positive
    df.loc[df['Item'] == 'Revenue', month_columns] = df.loc[df['Item'] == 'Revenue', month_columns]
    # Step 3: Calculate the profit for each month
    profit = df[df['Item'] == 'Revenue'][month_columns].sum(numeric_only=True).abs() - df[df['Item'] != 'Revenue'][month_columns].sum(numeric_only=True)
    # Convert profit to DataFrame for easier plotting
    profit_df = profit.reset_index()
    profit_df.columns = ['Month', 'Profit']
    # Step 4: Plotting the month over month profit
    plt.figure(figsize=(10, 6))
    plt.plot(profit_df['Month'], profit_df['Profit'], marker='o', color='b')
    plt.title('Month over Month Profit')
    plt.xlabel('Month')
    plt.ylabel('Profit')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt
