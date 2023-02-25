from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect = True)

measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    return(
        f"Available Routes: <br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precipitation = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    one_year = session.query(measurement.date, measurement.prcp).filter(measurement.date >= precipitation).all()
    values = {date: prcp for date, prcp in one_year}
    session.close()
    return jsonify(values)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Station.station).all()
    lists = list(np.ravel(station_list))
    session.close()
    return jsonify(lists)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    previous_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    previous_date = dt.datetime.strptime(previous_date, "%Y-%M-%D")
    date_query = dt.date(previous_date.year - 1, previous_date.month, previous_date.day)
    tobs = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == "USC00519281").\
        filter(measurement.date >= date_query).all()

    temp_Observe = []
    for date, tobs in previous_date:
        date_tobs = {}
        date_tobs["date"] = date
        date_tobs["tobs"] = tobs

        temp_Observe.append(date_tobs)
        session.close()
        return jsonify(temp_Observe)


@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    start_date_tobs_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs),
                                            func.max(measurement.tobs)). \
                                            filter(measurement.date >= start).all()
    session.close()
    start_date_tobs_values = []
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    return jsonify(start_date_tobs_values)


@app.route("/api/v1.0/<start>/<end>")
def Start_end_date(start, end):
    session = Session(engine)
    start_end_date_tobs_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    session.close()

    start_end_tobs_date_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date_values.append(start_end_tobs_date_dict)
    return jsonify(start_end_tobs_date_values)


if __name__ == '__main__':
    app.run(debug=True)



