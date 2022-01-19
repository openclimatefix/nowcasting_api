from nowcasting_forecast.database.read import get_latest_forecast


from nowcasting_forecast.database.models import Forecast, ManyForecasts


from sqlalchemy.orm.session import Session


def get_forecasts_from_database(session: Session) -> ManyForecasts:

    # sql almacy objects
    forecasts = [
        get_forecasts_for_a_specific_gsp_from_database(session=session, gsp_id=gsp_id)
        for gsp_id in range(0, 338)
    ]

    # change to pydantic objects
    forecasts = [Forecast.from_orm(forecast) for forecast in forecasts]

    # return as many forecasts
    return ManyForecasts(forecasts=forecasts)


def get_forecasts_for_a_specific_gsp_from_database(session: Session, gsp_id) -> Forecast:

    # get forecast from database
    forecast = get_latest_forecast(session=session, gsp_id=gsp_id)

    return Forecast.from_orm(forecast)


# TODO load fprecast and make national