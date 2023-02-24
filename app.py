import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with=engine)

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)
app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    precipitation = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    one_year = session.query(measurement.date, measurement.prcp).filter(measurement.date >= precipitation).all()

    all_prcp = []
    for date, prcp in preci_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    session.close()

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_number = session.query(measurement.station).distinct().count()

    session.close()

    return jsonify(station_number)

@app.route("/api/v1.0/tobs")
def temp_obs():
    session = Session(engine)

  active_stations = session.query(func.min(measurement.tobs),
                                  func.max(measurement.tobs),
                                  func.avg(measurement.tobs)).\
      filter(measurement.station == "USC00519281").order_by*func.min(measurement.tobs).all()

    session.close()

    return jsonify(temp_tobs)



@app.route("/api/v1.0/<start>/<end>")
def st_end_tobs(start, end):
    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%Y%m%d")
    end_date = dt.datetime.strptime(end, "%Y%m%d")

    temp_obs = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)). \
        filter(measurement.date >= start_date). \
        filter(measurement.date <= end_date).all()

    lst_tobs = list(np.ravel(temp_obs))

    session.close()

    return jsonify(lst_tobs)

if __name__ == '__main__':
    app.run(debug=True)