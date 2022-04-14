import requests
import pandas as pd
from nowcasting_datamodel.models.gsp import GSPYield
import plotly.graph_objects as go

url = 'SET_THIS'

# In day
r = requests.get(
    f"{url}/v0/GB/solar/gsp/truth/one_gsp/0/?regime=in-day"
)
d = r.json()

gsp_yield_in_day = [GSPYield(**i) for i in d]
gsp_yield_in_day = pd.DataFrame([o.__dict__ for o in gsp_yield_in_day])

# day after
r = requests.get(
    f"{url}/v0/GB/solar/gsp/truth/one_gsp/0/?regime=day-after"
)
d = r.json()

gsp_yield_day_after = [GSPYield(**i) for i in d]
gsp_yield_day_after = pd.DataFrame([o.__dict__ for o in gsp_yield_day_after])


trace_in_day = go.Scatter(
    x=gsp_yield_in_day["datetime_utc"],
    y=gsp_yield_in_day["solar_generation_kw"] / 10 * 6,
    line=dict(width=4, dash="dot"),
    name="in-day",
)
trace_day_after = go.Scatter(
    x=gsp_yield_day_after["datetime_utc"],
    y=gsp_yield_day_after["solar_generation_kw"] / 10 * 6,
    line=dict(width=4),
    name="day-after",
)


fig = go.Figure(data=[trace_in_day, trace_day_after])
fig.update_layout(
    title="Compare GSP 'in-day' and 'after-day'",
    xaxis_title="Time",
    yaxis_title="Solar generation [GW]",
)


fig.show(renderer="browser")
