import pandas as pd
import matplotlib.pyplot as plt

def clean_data(data):
    """Cleans the data for plotting."""
    # Removing rows with repeated headers
    cleaned_data = data[data['Profit Center'] != 'Profit center']

    # Converting monetary columns to float
    for column in cleaned_data.columns[3:]:
        cleaned_data[column] = cleaned_data[column].str.replace(',', '').astype(float).abs()
        cleaned_data[column] = pd.to_numeric(cleaned_data[column], errors='coerce')
    return cleaned_data

def monthly_revenue_trend(revenue_data):
    """Generate a stacked area chart for monthly revenue trend."""
    plt.figure(figsize=(14, 8))

    # Prepare data for the stacked area chart
    monthly_data = revenue_data.set_index('Profit Center').iloc[:, 3:].transpose()

    # Plotting
    plt.stackplot(monthly_data.index, monthly_data.values.T, labels=monthly_data.columns, alpha=0.7)
    
    plt.title('Monthly Revenue Trend (Stacked Area)')
    plt.xlabel('Month')
    plt.ylabel('Revenue')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=10)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    return plt

def monthly_expense_breakdown(expense_data):
    expense_aggregated = expense_data.groupby('Item').sum()
    ax = expense_aggregated.T.plot(kind='bar', stacked=True, figsize=(12, 6))
    plt.title('Monthly Expense Breakdown')
    plt.xlabel('Month')
    plt.ylabel('Expense Amount')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    return plt

def total_revenue_vs_expenses(revenue_data, expense_data):
    total_revenue = revenue_data.sum(numeric_only=True)
    total_expenses = expense_data.sum(numeric_only=True)
    total_revenue = total_revenue.iloc[3:].sort_index()
    total_expenses = total_expenses.iloc[3:].sort_index()
    plt.figure(figsize=(12, 6))
    plt.bar(total_revenue.index, total_revenue.values, label='Total Revenue', alpha=0.7)
    plt.figure(figsize=(12, 6))
    plt.bar(total_revenue.index, total_revenue.values, label='Total Revenue', alpha=0.7)
    plt.bar(total_expenses.index, total_expenses.values, label='Total Expenses', alpha=0.7)
    plt.title('Total Revenue vs. Total Expenses')
    plt.xlabel('Month')
    plt.ylabel('Amount')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    return plt

import matplotlib.patches as mpatches

def cost_center_expense_distribution(expense_data):
    """Generate a simple treemap for cost center expense distribution using just matplotlib."""
    plt.figure(figsize=(14, 8))
    
    # Aggregate data
    total_expenses = expense_data.groupby("Cost Center").sum().sum(axis=1)
    total_expenses = total_expenses.sort_values(ascending=False)
    
    # To make the treemap more readable, we'll display top N cost centers and group the rest under 'Others'
    N = 20
    top_N = total_expenses.head(N)
    if len(total_expenses) > N:
        top_N['Others'] = total_expenses[N:].sum()
    
    # Simple treemap plotting using pie chart as an alternative
    patches, texts, autotexts = plt.pie(top_N, labels=None, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab20c.colors)
    plt.title('Cost Center Expense Distribution')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.    

    # Create custom legend
    legend_patches = []
    for i, (label, value) in enumerate(top_N.items()):
        color = plt.cm.tab20c.colors[i % len(plt.cm.tab20c.colors)]
        legend_patches.append(mpatches.Patch(color=color, label=f'{label} - {value:.2f}'))
    plt.legend(handles=legend_patches, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.2), title='Cost Center - Expense')
    
    return plt

def monthly_net_profit_loss(revenue_data, expense_data):
    total_revenue = revenue_data.sum(numeric_only=True)
    total_expenses = expense_data.sum(numeric_only=True)
    net_profit_loss = total_revenue - total_expenses
    plt.figure(figsize=(12, 6))
    net_profit_loss.plot(kind='line', marker='o', color='green' if all(net_profit_loss >= 0) else 'red')
    plt.title('Monthly Net Profit/Loss')
    plt.xlabel('Month')
    plt.ylabel('Net Amount')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.axhline(0, color='black', linewidth=0.7)
    plt.tight_layout()
    return plt
