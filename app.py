import dash
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from dash import dcc, html
import dash.dash_table as dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# PostgreSQL database connection string using SQLAlchemy
db_url = "postgresql://bumeharaz:nYAifKg7cKo93FwvcxSHDaJmeh0oMFH6@dpg-cummh65svqrc73fi5fc0-a.oregon-postgres.render.com/dbname_dk38"

# Create engine for SQLAlchemy
engine = create_engine(db_url)

# Function to fetch data from PostgreSQL database
def fetch_data(query):
    df = pd.read_sql(query, engine)
    return df

# Fetching data for initial and auto-refresh
def get_initial_data():
    query = """
    SELECT total_registered, visitors, applied_to_job, application, unique_applicant,
           total_companies_jobs_apply, direct_payment_for_job_apply, paid_by_applicants,
           became_pro_user_today, amount_from_today_pro_users, pro_job_seeker_count, total_amount_collected
    FROM public.fair_summary_data
    LIMIT 1;
    """
    return fetch_data(query)

def get_hourly_data():
    query = """
    SELECT intervalstart, opidcount FROM public.opidintervalcounts ORDER BY intervalstart;
    """
    return fetch_data(query)

# Preparing hourly data
def prepare_hourly_data(df):
    df['intervalstart'] = pd.to_datetime(df['intervalstart'])
    df['Hour'] = df['intervalstart'].dt.hour
    hourly_data = df.groupby('Hour')['opidcount'].sum().reset_index()
    return hourly_data

# Preparing the initial data for column-wise display
def prepare_column_data(df):
    columns_to_show = [
        'total_registered', 'visitors', 'applied_to_job', 'application',
        'unique_applicant', 'total_companies_jobs_apply', 'direct_payment_for_job_apply',
        'paid_by_applicants', 'became_pro_user_today', 'amount_from_today_pro_users',
        'pro_job_seeker_count', 'total_amount_collected'
    ]
    last_row = df[columns_to_show].iloc[[-1]]
    column_wise_data = [{'Attribute': col, 'Value': last_row[col].values[0]} for col in last_row.columns]
    return column_wise_data

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the application
app.layout = html.Div([
    # Header with logo and title
    html.Div([
        html.Img(src='https://bdjobs.com/images/bdjobs-chakri-mela-chef-feb-2025.svg',
                 style={'height': '100px', 'float': 'left', 'maxWidth': '100%', 'height': 'auto'}),
        html.H1('HOSPITALITY & CHEF JOB FAIR', style={'textAlign': 'center', 'fontSize': '2vw'})
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),

    # DataTable to display column-wise data
    dash_table.DataTable(
        id='data-table',
        columns=[{"name": col, "id": col} for col in ['Attribute', 'Value']],
        data=[],
        style_table={'height': 'auto', 'width': '60%', 'margin': 'auto'},
        style_cell={'textAlign': 'center', 'fontSize': '16px'},
        style_header={'backgroundColor': '#4F5D75', 'color': 'white'},
        style_data={'backgroundColor': '#2B3B4B', 'color': 'white'}
    ),

    # Div for pie charts
    html.Div([
        dcc.Graph(id='pie-chart-1', style={'width': '33%', 'display': 'inline-block'}),
        dcc.Graph(id='pie-chart-2', style={'width': '33%', 'display': 'inline-block'}),
        dcc.Graph(id='pie-chart-3', style={'width': '33%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'}),

    # Dropdown for plot type selection (5-minute vs Hourly)
    dcc.Dropdown(
        id='plot-type-dropdown',
        options=[{'label': '5-Minute Interval Data', 'value': '5min'}, {'label': 'Hourly Data', 'value': 'hourly'}],
        value='5min',
        style={'width': '50%', 'margin': '0 auto', 'padding': '10px'}
    ),

    # Graph for displaying the selected data
    dcc.Graph(id='interval-graph', style={'height': '60vh'}),

    # Auto-refresh every 30 seconds
    dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0)
])

@app.callback(
    [Output('data-table', 'data'),
     Output('pie-chart-1', 'figure'),
     Output('pie-chart-2', 'figure'),
     Output('pie-chart-3', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_data(n):
    # Fetch the latest data
    df = get_initial_data()
    column_data = prepare_column_data(df)

    # Pie chart 1 - Total Registered vs Visitors
   # Pie chart 1 - Total Registered vs Visitors
    pie_chart_1 = {
        'data': [
            go.Pie(
                labels=['Total Registered', 'Visitors'],
                values=[df['total_registered'].iloc[0], df['visitors'].iloc[0]],
                hole=0.3,
                marker=dict(colors=['#FFA500', '#1E90FF'])  # Orange and Blue colors
            )
        ],
        'layout': go.Layout(
            title='Total Registered vs Visitors',
            showlegend=True,
            height=400,
        )
    }

    # Pie chart 2 - Applied to Job vs Application
    pie_chart_2 = {
        'data': [
            go.Pie(
                labels=['Applied to Job', 'Application'],
                values=[df['applied_to_job'].iloc[0], df['application'].iloc[0]],
                hole=0.3,
                marker=dict(colors=['#FFA500', '#1E90FF'])  # Orange and Blue colors
            )
        ],
        'layout': go.Layout(
            title='Applied to Job vs Application',
            showlegend=True,
            height=400,
        )
    }

    # Pie chart 3 - Unique Applicant vs Pro Job Seeker Count
    pie_chart_3 = {
        'data': [
            go.Pie(
                labels=['Unique Applicant', 'Pro Job Seeker Count'],
                values=[df['unique_applicant'].iloc[0], df['pro_job_seeker_count'].iloc[0]],
                hole=0.3,
                marker=dict(colors=['#FFA500', '#1E90FF'])  # Orange and Blue colors
            )
        ],
        'layout': go.Layout(
            title='Unique Applicants vs Pro Job Seeker Count',
            showlegend=True,
            height=400,
        )
    }


    return column_data, pie_chart_1, pie_chart_2, pie_chart_3


@app.callback(
    Output('interval-graph', 'figure'),
    [Input('plot-type-dropdown', 'value')]
)
def update_graph(plot_type):
    # Fetch the hourly data or 5-minute data
    df = get_hourly_data()
    hourly_data = prepare_hourly_data(df)

    if plot_type == '5min':
        figure = go.Figure(data=[go.Scatter(
            x=df['intervalstart'],
            y=df['opidcount'],
            mode='lines+markers',
            name='OPID Count',
            marker=dict(color='#FF6347', size=10),
            line=dict(color='#FF6347', width=2),
            text=df['opidcount'],
            hoverinfo='x+y+text'
        )])

        # Add value labels on the chart
        for i in range(len(df)):
            figure.add_annotation(
                x=df['intervalstart'][i],
                y=df['opidcount'][i],
                text=str(df['opidcount'][i]),
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-20,
                font=dict(color='#FF6347', size=12)
            )
        
        figure.update_layout(
            title='5-Minute Interval Pro Purchase in Fair Day',
            xaxis_title='Time',
            yaxis_title='OPID Count',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(245, 245, 245, 1)',
            font=dict(family='Arial, sans-serif', color='#333')
        )

    elif plot_type == 'hourly' and not hourly_data.empty:
        figure = go.Figure(data=[go.Bar(
            x=hourly_data['Hour'],
            y=hourly_data['opidcount'],
            name='OPID Count',
            marker=dict(color='#6A5ACD')
        )])

        # Add value labels on the bars
        for i in range(len(hourly_data)):
            figure.add_annotation(
                x=hourly_data['Hour'][i],
                y=hourly_data['opidcount'][i],
                text=str(hourly_data['opidcount'][i]),
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-20,
                font=dict(color='#6A5ACD', size=12)
            )
        
        figure.update_layout(
            title='Hourly Pro Purchase in Fair Day',
            xaxis_title='Hour',
            yaxis_title='OPID Count',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(245, 245, 245, 1)',
            font=dict(family='Arial, sans-serif', color='#333')
        )

    else:
        # In case of no valid data for hourly chart
        figure = go.Figure()
        figure.update_layout(
            title='No Data Available',
            xaxis_title='Time',
            yaxis_title='OPID Count',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(245, 245, 245, 1)',
            font=dict(family='Arial, sans-serif', color='#333')
        )

    return figure

# Fetch data for initial load
df = fetch_data("""
    SELECT intervalstart, opidcount FROM public.opidintervalcounts ORDER BY intervalstart;
""")
hourly_data = prepare_hourly_data(df)
server = app.server
# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
