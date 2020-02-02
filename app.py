# ---------------------------------------------
# ---------------------------------------------
# Dependencies
import numpy as np
import pandas as pd

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# ---------------------------------------------
# ---------------------------------------------
# Database creation business
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)
# Map and reflect
Base = automap_base()
Base.prepare(engine, reflect=True)
# Refference tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# Calling last 12 months variable
last_twelve_mo = dt.date(2017,8,23)-dt.timedelta(days=365)

# ---------------------------------------------
# ---------------------------------------------
# Create flask app
app = Flask(__name__)

# Flask routes
# # #

# Home
@app.route("/")
def index():
    return (
        f"Isn't this fun?<br/>"
        f"<br>"
        f"Climate App<br/>"
        f"~~~ Nav Options ~~~<br/>"
        f"<br>"
        f"Precipitation data:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br>"
        f"Station ids:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br>"
        f"Temperatures of most recent year on record:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br>"
        f"View max, min, & avg temps of [user entered] start date until most recent recorded date<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"<br>"
        f"Enter a start date & end date to see max, min, avg temps: (page under construction)<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
def precipitation():
    session = Session(engine)

    # Return all dates & precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()

    # Convert tuples to normal list
    all_prcp = list(np.ravel(results))

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
# Return a JSON list of stations from the dataset.
def stations():
    session = Session(engine)

    # Return all stations
    results = session.query(Station.station).all()
    
    session.close()
    
    return jsonify(results)


@app.route("/api/v1.0/tobs")
# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
def tobs():
    session = Session(engine)
    
    # Return all data from the most recent year
    results = session.query(Measurement.date, Measurement.tobs).\
        order_by(Measurement.date.desc()).\
        filter(Measurement.date >= last_twelve_mo).\
        all()
    
    session.close()

    recent_year = []
    for date, tobs in results:
        dates_dict = {}
        dates_dict["date"] = date
        dates_dict["temperature"] = tobs
        recent_year.append(dates_dict)

    return jsonify(recent_year)


@app.route("/api/v1.0/<start_date>")
#   When given the start only, calculate TMIN, TAVG, and TMAX for all dates 
#   greater than and equal to the start date.
#   Return a JSON list of the minimum temperature, the average temperature, 
#   and the max temperature for a given start range.
def reference_table(start_date):
    # Fetch date match supplied by the user. 404 if invalid.
    # # #
    # Data queries
    session = Session(engine)
    # Return all dates and temps
    results = session.query(Measurement.date, Measurement.tobs).all()
    # Query if start date is valid
    if_match = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start_date).\
                    all()
    session.close()

    # Ceate dictionary from "results" query to look up user input
    reference_table = []
    for date, tobs in results:
        ref_dict = {}
        ref_dict["date"] = date
        ref_dict["temperature"] = tobs
        reference_table.append(ref_dict)

    date_real = start_date
    for start_date in reference_table:
        search = start_date["date"]
        if search == date_real:
            return jsonify(if_match)
    return jsonify({"error": "Woah, sorry there! The date isn't working for me. Try Again."}), 404


# # PAGE UNDER CONSTRUCTION
# @app.route("/api/v1.0/<start_date>/<end_date>")
# #   When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
# #   for dates between the start and end date inclusive.
# def reference_table(start_date,end_date):
#     # Fetch date match supplied by the user. 404 if invalid.
#     # # #
#     # Data queries
#     session = Session(engine)
#     # Return all dates and temps
#     results = session.query(Measurement.date, Measurement.tobs).all()
#     # Query if start date is valid
#     if_match = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
#                     filter(Measurement.date >= start_date).\
#                     filter(Measurement.date <= end_date).\
#                     all()
#     session.close()

#     # Ceate dictionary from "results" query to look up user input
#     reference_table = []
#     for date, tobs in results:
#         ref_dict = {}
#         ref_dict["date"] = date
#         ref_dict["temperature"] = tobs
#         reference_table.append(ref_dict)

#     start_real = start_date
#     end_real = end_date
#     for start_date in reference_table:
#         s_search = start_date["date"]
#         e_search = end_date["date"]
#         if s_search == start_real & e_search == end_real:
#             return jsonify(if_match)
#     return jsonify({"error": "Woah, sorry there! Those dates aren't working for me. Try Again."}), 404
# # END PAGE UNDER CONSTRUCTION 

# ---------------------------------------------
# ---------------------------------------------
# App behavior
if __name__ == "__main__":
    app.run(debug=True)