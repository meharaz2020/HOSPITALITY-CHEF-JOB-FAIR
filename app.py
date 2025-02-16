import dash
import pandas as pd
import psycopg2
from dash import dcc, html
import dash.dash_table as dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go  # Import Plotly for graphing

# PostgreSQL database connection details
db_url = "postgresql://bumeharaz:nYAifKg7cKo93FwvcxSHDaJmeh0oMFH6@dpg-cummh65svqrc73fi5fc0-a.oregon-postgres.render.com/dbname_dk38"

# Establish connection to the PostgreSQL database
def get_data_from_db():
    conn = psycopg2.connect(db_url)
    query = """
    SELECT total_registered, visitors, applied_to_job, application, unique_applicant,
           total_companies_jobs_apply, direct_payment_for_job_apply, paid_by_applicants,
           became_pro_user_today, amount_from_today_pro_users, pro_job_seeker_count, total_amount_collected
    FROM public.fair_summary_data
    LIMIT 1;
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fetch the initial data
df = get_data_from_db()

# Strip any extra spaces in column names
df.columns = df.columns.str.strip()

# Clean data (replace NaN values with empty strings)
df = df.fillna("")

# Columns to display
columns_to_show = [
    'total_registered', 'visitors', 'applied_to_job', 'application',
    'unique_applicant', 'total_companies_jobs_apply', 
    'direct_payment_for_job_apply', 'paid_by_applicants', 
    'became_pro_user_today', 'amount_from_today_pro_users', 
    'pro_job_seeker_count', 'total_amount_collected'
]

# Get the last row of the dataframe
last_row = df[columns_to_show].iloc[[-1]]

# Transform data into a column-wise format
column_wise_data = [{'Attribute': col, 'Value': last_row[col].values[0]} for col in last_row.columns]

# Initialize Dash app
app = dash.Dash(__name__)

# Layout with a fixed image header and DataTable to show the column-wise data
app.layout = html.Div([  
    html.Div([  
        # Logo on the left  
        html.Img(src='https://bdjobs.com/images/bdjobs-chakri-mela-chef-feb-2025.svg', 
                 style={'height': '100px', 'float': 'left', 'maxWidth': '100%', 'height': 'auto'}),  
        # Title centered with flexbox and auto margins for centering  
        html.H1('HOSPITALITY & CHEF JOB FAIR', style={'textAlign': 'center', 'margin': '0 auto', 'fontSize': '2vw'}),  
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),  

    # DataTable displaying the data in column-wise format  
    dash_table.DataTable(  
        id='data-table',  
        columns=[{"name": col, "id": col} for col in ['Attribute', 'Value']],  # Two columns: Attribute and Value  
        data=column_wise_data,  # Data in column-wise format  
        style_table={'height': 'auto', 'width': '60%', 'margin': 'auto'},  
        style_cell={'textAlign': 'center', 'fontSize': '16px'},  
        style_header={'backgroundColor': '#4F5D75', 'color': 'white'},  
        style_data={'backgroundColor': '#2B3B4B', 'color': 'white'}  
    ),  

    # Div to hold the 3 pie charts in one row
    html.Div([
        # Pie chart 1 - Total Registered vs Visitors
        dcc.Graph(
            id='pie-chart-1',
            style={'width': '33%', 'display': 'inline-block'},
            figure={
                'data': [
                    go.Pie(
                        labels=['Total Registered', 'Visitors'],
                        values=[df['total_registered'].iloc[0], df['visitors'].iloc[0]],
                        hole=0.3,
                        marker=dict(colors=['#4F5D75', '#2B3B4B'])
                    )
                ],
                'layout': go.Layout(
                    title='Total Registered vs Visitors',
                    showlegend=True,
                    height=400,
                )
            }
        ),

        # Pie chart 2 (You can modify the data/labels accordingly)
        dcc.Graph(
            id='pie-chart-2',
            style={'width': '33%', 'display': 'inline-block'},
            figure={
                'data': [
                    go.Pie(
                        labels=['Applied to Job', 'Application'],
                        values=[df['applied_to_job'].iloc[0], df['application'].iloc[0]],
                        hole=0.3,
                        marker=dict(colors=['#4F5D75', '#2B3B4B'])
                    )
                ],
                'layout': go.Layout(
                    title='Applied to Job vs Application',
                    showlegend=True,
                    height=400,
                )
            }
        ),

        # Pie chart 3 (You can modify the data/labels accordingly)
        dcc.Graph(
            id='pie-chart-3',
            style={'width': '33%', 'display': 'inline-block'},
            figure={
                'data': [
                    go.Pie(
                        labels=['Unique Applicant', 'Pro Job Seeker Count'],
                        values=[df['unique_applicant'].iloc[0], df['pro_job_seeker_count'].iloc[0]],
                        hole=0.3,
                        marker=dict(colors=['#4F5D75', '#2B3B4B'])
                    )
                ],
                'layout': go.Layout(
                    title='Unique Applicants vs Pro Job Seeker Count',
                    showlegend=True,
                    height=400,
                )
            }
        ),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'}),  

    # Auto-refresh every 30 seconds  
    dcc.Interval(  
        id='interval-component',  
        interval=30*1000,  # 30 seconds  
        n_intervals=0  
    )  
])  

# Update table with new data periodically
@app.callback(  
    Output('data-table', 'data'),  
    Output('pie-chart-1', 'figure'),  # Add the pie chart output for chart 1
    Output('pie-chart-2', 'figure'),  # Add the pie chart output for chart 2
    Output('pie-chart-3', 'figure'),  # Add the pie chart output for chart 3
    Input('interval-component', 'n_intervals')  
)  
def update_data(n):  
    new_df = get_data_from_db()  # Fetch fresh data from the database
    
    # Strip spaces and get the last row with specific columns  
    new_df.columns = new_df.columns.str.strip()  

    last_row = new_df[columns_to_show].iloc[[-1]]  # Get the last row of the updated data with selected columns  
   
    # Transform data into a column-wise format  
    column_wise_data = [{'Attribute': col, 'Value': last_row[col].values[0]} for col in last_row.columns]  
    
    # Generate new pie chart data for 3 charts
    pie_chart_1 = {
        'data': [
            go.Pie(
                labels=['Total Registered', 'Visitors'],
                values=[new_df['total_registered'].iloc[0], new_df['visitors'].iloc[0]],
                hole=0.3,
                marker=dict(colors=['#4F5D75', '#2B3B4B'])
            )
        ],
        'layout': go.Layout(
            title='Total Registered vs Visitors',
            showlegend=True,
            height=400,
        )
    }

    pie_chart_2 = {
        'data': [
            go.Pie(
                labels=['Applied to Job', 'Application'],
                values=[new_df['applied_to_job'].iloc[0], new_df['application'].iloc[0]],
                hole=0.3,
                marker=dict(colors=['#4F5D75', '#2B3B4B'])
            )
        ],
        'layout': go.Layout(
            title='Applied to Job vs Application',
            showlegend=True,
            height=400,
        )
    }

    pie_chart_3 = {
        'data': [
            go.Pie(
                labels=['Unique Applicant', 'Pro Job Seeker Count'],
                values=[new_df['unique_applicant'].iloc[0], new_df['pro_job_seeker_count'].iloc[0]],
                hole=0.3,
                marker=dict(colors=['#4F5D75', '#2B3B4B'])
            )
        ],
        'layout': go.Layout(
            title='Unique Applicants vs Pro Job Seeker Count',
            showlegend=True,
            height=400,
        )
    }

    return column_wise_data, pie_chart_1, pie_chart_2, pie_chart_3  # Return both the table data and the updated pie charts

server = app.server

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
