import dash
from dash import dcc, html, Input, Output
import requests
import plotly.graph_objects as go
import os

API_KEY = os.getenv("API_KEY")

app = dash.Dash(__name__)
server = app.server

# =======================
# 🔹 DATA KOTA AUTOCOMPLETE
# =======================
city_list = [
    "Jakarta", "Surabaya", "Bandung", "Medan", "Makassar",
    "Semarang", "Yogyakarta", "Surakarta", "Malang",
    "Denpasar", "Padang", "Palembang", "Balikpapan",
    "Pontianak", "Banjarmasin", "Manado"
]

# =======================
# 🔹 GET WEATHER
# =======================
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()

    if res.get("cod") != 200:
        return None

    return {
        "temp": res["main"]["temp"],
        "desc": res["weather"][0]["description"],
        "icon": res["weather"][0]["icon"],
        "lat": res["coord"]["lat"],
        "lon": res["coord"]["lon"],
        "city": res["name"]
    }

# =======================
# 🔹 GET FORECAST
# =======================
def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()

    if res.get("cod") != "200":
        return None

    temps, times, icons = [], [], []

    for i in range(0, len(res["list"]), 8):  # per hari
        item = res["list"][i]
        temps.append(item["main"]["temp"])
        times.append(item["dt_txt"])
        icons.append(item["weather"][0]["icon"])

    return temps, times, icons

# =======================
# 🔹 ICON CUACA
# =======================
def icon_url(icon):
    return f"http://openweathermap.org/img/wn/{icon}@2x.png"

# =======================
# 🔹 LAYOUT
# =======================
app.layout = html.Div([
    html.H1("⛅ Smart Weather Dash", style={
        "textAlign": "center",
        "color": "white"
    }),

    html.Div([
        dcc.Input(
            id="search",
            type="text",
            placeholder="Cari kota...",
            style={
                "width": "280px",
                "padding": "10px",
                "borderRadius": "10px",
                "border": "none",
                "textAlign": "center"
            }
        ),

        html.Div(id="suggestions", style={
            "background": "white",
            "width": "280px",
            "margin": "auto",
            "borderRadius": "10px"
        })

    ], style={"textAlign": "center"}),

    html.Div(id="content", style={"marginTop": "30px"})

], style={
    "background": "#0b1f3a",
    "minHeight": "100vh",
    "padding": "20px"
})

# =======================
# 🔹 AUTOCOMPLETE
# =======================
@app.callback(
    Output("suggestions", "children"),
    Input("search", "value")
)
def suggest_city(value):
    if not value:
        return []

    matches = [c for c in city_list if value.lower() in c.lower()]

    return [
        html.Div(c, style={
            "padding": "8px",
            "cursor": "pointer"
        })
        for c in matches[:5]
    ]

# =======================
# 🔹 MAIN DASHBOARD
# =======================
@app.callback(
    Output("content", "children"),
    Input("search", "value")
)
def update_dashboard(city):

    if not city:
        return html.H3("🌍 Cari kota dulu...", style={"color": "white", "textAlign": "center"})

    weather = get_weather(city)
    forecast = get_forecast(city)

    if not weather or not forecast:
        return html.H3("❌ Kota tidak ditemukan", style={"color": "red"})

    temps, times, icons = forecast

    # =======================
    # 📈 GRAFIK
    # =======================
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=temps,
        mode="lines",
        line=dict(shape="spline", width=4),
        fill="tozeroy"
    ))

    fig.update_layout(
        plot_bgcolor="#1f2c44",
        paper_bgcolor="#1f2c44",
        font=dict(color="white"),
        height=350,
        margin=dict(l=20, r=20, t=20, b=80)
    )

    # =======================
    # 🗺️ MAP (FIX STABLE)
    # =======================
    map_fig = go.Figure()

    map_fig.add_trace(go.Scattermapbox(
        lat=[weather["lat"]],
        lon=[weather["lon"]],
        mode='markers',
        marker=dict(size=12),
        text=weather["city"]
    ))

    map_fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=weather["lat"], lon=weather["lon"]),
            zoom=5
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        height=300
    )

    # =======================
    # 🌤️ ICON ROW
    # =======================
    icon_row = html.Div([
        html.Div([
            html.Img(src=icon_url(ic), style={"height": "40px"}),
            html.Div(times[i][5:10])
        ], style={"textAlign": "center", "flex": "1"})
        for i, ic in enumerate(icons)
    ], style={"display": "flex"})

    # =======================
    # 📦 UI
    # =======================
    return html.Div([

        # LEFT
        html.Div([
            html.H2(weather["city"], style={"color": "white"}),
            html.H3("Today's Weather", style={"color": "white"}),
            html.H1(f"{weather['temp']}°C", style={"color": "white"}),
            html.P(weather["desc"], style={"color": "white"}),
            html.Img(src=icon_url(weather["icon"]))
        ], style={
            "background": "#1f2c44",
            "padding": "20px",
            "borderRadius": "15px",
            "width": "30%"
        }),

        # RIGHT
        html.Div([
            dcc.Graph(figure=fig),
            icon_row,
            html.H4("📍 Location Map", style={"color": "white"}),
            dcc.Graph(figure=map_fig)
        ], style={
            "background": "#1f2c44",
            "padding": "20px",
            "borderRadius": "15px",
            "width": "65%"
        })

    ], style={
        "display": "flex",
        "justifyContent": "space-between"
    })


# =======================
# 🔹 RUN
# =======================
if __name__ == "__main__":
    app.run(debug=False)
