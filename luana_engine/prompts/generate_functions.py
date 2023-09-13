schedma = """
based on all the code you've written, write a few functions and give it a name according to the purpose and questions asks to it can be reused later, don't execute the function.
{
        "name": "get_current_weather",
        "description": "Get the current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "format": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use. Infer this from the users location.",
                },
            },
            "required": ["location", "format"],
        },
    },
"""
finance_data_functions = """
import plotly
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import json

def load_and_clean_data(file_path):
    # Load the data
    data = pd.read_csv(file_path)

    # Remove duplicate rows
    data = data.drop_duplicates()

    # Fill NaN values with 0
    data = data.fillna(0)

    # Convert string numbers to float and remove commas
    for column in data.columns[3:]:
        data[column] = data[column].replace(',', '', regex=True).astype(float)

    return data

def calculate_revenue(data):
    # Calculate the Total for each month
    total_data = data[data['Item'] == "Revenue"].iloc[:, 3:].sum().abs()

    return total_data

def calculate_expense(data):
    # Calculate the Total for each month
    total_data = data[data['Item'] != "Revenue"].iloc[:, 3:].sum()

    return total_data

def calculate_item(data, item):
    # Calculate the Total for each month
    total_data = data[data['Item'] == item].iloc[:, 3:].sum()

    return total_data

def generate_plot_total_over_time(total_data, title, file_name):
    # Create a line plot of Total over time
    fig = go.Figure(data=go.Scatter(x=total_data.index, y=total_data.values, mode='lines+markers'))

    # Add title and labels
    fig.update_layout(title=title, xaxis_title='Month', yaxis_title=title)

    return fig

def calculate_value_and_delta(total_data):
    # Calculate the value
    value = total_data.sum()

    # Calculate the delta over the last time period in percentage
    delta = (total_data[-1] - total_data[-2]) / total_data[-2] * 100

    # Create a JSON object
    result = json.dumps({'value': value, 'delta': delta})

    return result
"""

city_budget_functions = """
def load_and_preprocess_data(file_path):
    #Loads the data from the given file path and preprocesses it by converting the 'Budget' column to numeric.
    data = pd.read_csv(file_path)
    data['Budget'] = pd.to_numeric(data['Budget'].str.replace(',', ''), errors='coerce')
    return data

def calculate_total_expenditure(data):
    #Calculates the total expenditure over time.
    expenditure_data = data[data['Revenue or Spending'] == 'Spending']
    total_expenditure_over_time = expenditure_data.groupby('Fiscal Year')['Budget'].sum().reset_index()
    return total_expenditure_over_time

def calculate_total_revenue(data):
    #Calculates the total revenue over time.
    revenue_data = data[data['Revenue or Spending'] == 'Revenue']
    total_revenue_over_time = revenue_data.groupby('Fiscal Year')['Budget'].sum().reset_index()
    return total_revenue_over_time

def calculate_budget_surplus_deficit(data):
    #Calculates the yearly budget surplus/deficit over time.
    expenditure_data = data[data['Revenue or Spending'] == 'Spending']
    revenue_data = data[data['Revenue or Spending'] == 'Revenue']
    total_expenditure_over_time = expenditure_data.groupby('Fiscal Year')['Budget'].sum().reset_index()
    total_revenue_over_time = revenue_data.groupby('Fiscal Year')['Budget'].sum().reset_index()
    budget_surplus_deficit = pd.merge(total_expenditure_over_time, total_revenue_over_time, on='Fiscal Year', how='outer', suffixes=('_Expenditure', '_Revenue'))
    budget_surplus_deficit['Surplus/Deficit'] = budget_surplus_deficit['Budget_Revenue'] - budget_surplus_deficit['Budget_Expenditure']
    return budget_surplus_deficit
"""
