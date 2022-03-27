#--------------------------------Imports---------------------------------------------------

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

#--------------------------------Read Data From CSV----------------------------------------

df = pd.read_csv(r"assets/intro_bees.csv")

#--------------------------------Create App------------------------------------------------

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#--------------------------------Set up the HTML visuals-----------------------------------
app.layout = html.Div([

    dbc.Row([
        dbc.Col(html.Div(html.Img(src=r"assets/logo.png",  style={'height':'50px'})), md=3, className="text-center mt-3 mx-0"),
        dbc.Col(html.Div(html.H1("Factors Affecting Bees in USA")), md=6, className="text-center mt-3 mx-0")
    ]),

    dbc.Row([
        dbc.Col(html.Div(
            dcc.Dropdown(
                id="select_year",
                options=[{"label": str(year), "value": year} for year in df['Year'].unique()],
                multi=False,
                value=df['Year'].unique()[0],
                )), md=6, className="mt-3"),
        dbc.Col(html.Div(
            dcc.Dropdown(
                id="select_affected_by",
                options=[{"label": affect, "value": affect} for affect in df['Affected by'].unique()],
                multi=True,
                value=df['Affected by'].unique()[0],
                )), md=6, className="mt-3"),
                 ], className="d-flex justify-content-center mx-0"),       

    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id="bee_map", figure={})), md=6),
        dbc.Col(html.Div(dcc.Graph(id="bee_bar", figure={})), md=6)
    ]),
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id="bee_line", figure={})), md=6),
        dbc.Col(html.Div(dcc.Graph(id="bee_pie_chart", figure={})), md=6)
    ])
])

#-----------------------------------callback - executes when interacting with controls--------------------------

@app.callback(
    [Output(component_id="bee_map", component_property="figure"),
     Output(component_id="bee_bar", component_property="figure"),
     Output(component_id="bee_line", component_property="figure"),
     Output(component_id="bee_pie_chart", component_property="figure")],
     [Input(component_id="select_year", component_property="value"),
     Input(component_id="select_affected_by", component_property="value")]
)
def update_graph(year_option, affected_by_option):
    
    affected_by_option = [affected_by_option] if type(affected_by_option) is str else affected_by_option
    
    df_year_affected_by = df[(df['Year'] == year_option) & (df['Affected by'].isin(affected_by_option))]

    year = "" if len(df_year_affected_by)==0 else  df_year_affected_by.Year.unique()[0]
    
    fig_map = px.choropleth(
        data_frame=df_year_affected_by.groupby(by=['State', 'state_code']).agg({'Pct of Colonies Impacted':'mean'}).reset_index(),
        locationmode="USA-states",
        locations="state_code",
        scope="usa",
        color="Pct of Colonies Impacted",
        hover_data=['State', 'Pct of Colonies Impacted'],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={"Pct of Colonies Impacted": "% of Bee Colonies"},
        title="% of Colonies Impacted VS State {year}".format(year=year)
    )
    
    df_lineC = df[(df['Affected by'].isin(affected_by_option))]
  
    fig_bar = px.bar(
        data_frame=df_year_affected_by.groupby(by=['State', 'state_code']).agg({'Pct of Colonies Impacted':'mean'}).reset_index(), 
        x="State", 
        y="Pct of Colonies Impacted", 
        title="% of Colonies Impacted in each state",
        labels={"Pct of Colonies Impacted": "% of Bee Colonies"}
    )
    fig_bar.update_layout(xaxis={'categoryorder':'total descending'})
    
    fig_line = px.line(
        data_frame=df_lineC.groupby(by=['Year','State']).agg({'Pct of Colonies Impacted':'mean'}).reset_index(), 
        x="Year", 
        y="Pct of Colonies Impacted", 
        title="% of Colonies Impacted VS State",
        labels={"Pct of Colonies Impacted": "% of Bee Colonies"},
        color="State"
    )  
    fig_line.update_xaxes(type="category")
    
    
    fig_pie = px.pie(
        data_frame=df_year_affected_by.groupby(by=['State', 'state_code']).agg({'Pct of Colonies Impacted':'mean'}).reset_index(),
        values="Pct of Colonies Impacted",
        names="State",
        hole=0.3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label+value')
    
    return fig_map, fig_bar, fig_line, fig_pie
 

#-------------------------------Run Server----------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)