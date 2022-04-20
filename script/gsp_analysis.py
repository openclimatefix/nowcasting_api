import pandas as pd
from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.models.base import Base_Forecast
from nowcasting_datamodel.read.read_gsp import get_gsp_yield
from nowcasting_datamodel.models.gsp import GSPYield
from datetime import datetime
import plotly.graph_objects as go
import boto3
import json

client = boto3.client("secretsmanager")
response = client.get_secret_value(
    SecretId="development/rds/forecast/",
)
secret = json.loads(response["SecretString"])
""" We have used a ssh tunnel to 'localhost' """
db_url = f'postgresql://{secret["username"]}:{secret["password"]}@localhost:{secret["port"]}/{secret["dbname"]}'

connection = DatabaseConnection(url=db_url, base=Base_Forecast, echo=True)


session = connection.get_session()

in_day = get_gsp_yield(
    session=session, gsp_ids=[0], start_datetime_utc=datetime(2022, 4, 19), regime="in-day"
)
day_after = get_gsp_yield(
    session=session, gsp_ids=[0], start_datetime_utc=datetime(2022, 4, 19), regime="day-after"
)

in_day = pd.DataFrame([i.__dict__ for i in in_day])
day_after = pd.DataFrame([i.__dict__ for i in day_after])


in_day = in_day[["datetime_utc", "solar_generation_kw"]]
day_after = day_after[["datetime_utc", "solar_generation_kw"]]
in_day.set_index("datetime_utc", inplace=True)
day_after.set_index("datetime_utc", inplace=True)
in_day["solar_generation_kw"] = in_day["solar_generation_kw"].astype(float)
day_after["solar_generation_kw"] = day_after["solar_generation_kw"].astype(float)


gsp = day_after.join(in_day, lsuffix="_day_after", rsuffix="_in_day")

mae = (
    (gsp["solar_generation_kw_in_day"] - gsp["solar_generation_kw_day_after"]).abs().mean()
    / 10 ** 6
).round(2)
me = (
    (gsp["solar_generation_kw_in_day"] - gsp["solar_generation_kw_day_after"]).mean() / 10 ** 6
).round(2)
rmse = (
    (
        ((gsp["solar_generation_kw_in_day"] - gsp["solar_generation_kw_day_after"]) ** 2).mean()
        ** 0.5
    )
    / 10 ** 6
).round(2)

trace_in_day = go.Scatter(
    x=gsp.index,
    y=gsp["solar_generation_kw_in_day"] / 10 ** 6,
    line=dict(width=4, dash="dot"),
    name="in-day",
)
trace_day_after = go.Scatter(
    x=gsp.index,
    y=gsp["solar_generation_kw_day_after"] / 10 ** 6,
    line=dict(width=4),
    name="day-after",
)


fig = go.Figure(data=[trace_in_day, trace_day_after])
fig.update_layout(
    title=f"Compare GSP 'in-day' and 'after-day'. {mae=} {me=} {rmse=} [GW]",
    xaxis_title="Time",
    yaxis_title="Solar generation [GW]",
)


fig.show(renderer="browser")
