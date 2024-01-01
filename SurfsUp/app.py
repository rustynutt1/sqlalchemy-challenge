# Import necessary libraries
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################

# Create an engine to connect to the database
engine = create_engine("sqlite:////Users/ryannuttall/Documents/GitHub/sqlalchemy-challenge/Resources/hawaii.sqlite")

# Reflect the database into a model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Perform your precipitation analysis here
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    one_year_delta = recent_date - dt.timedelta(days=365)

    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_delta).all()

    precipitation_dict = dict(precipitation_data)
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query and return a JSON list of stations
    stations_list = session.query(Station.station).all()
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Perform your temperature observation analysis here
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()[0]
    one_year_ago_tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= one_year_delta).all()

    tobs_df = pd.DataFrame(one_year_ago_tobs, columns=['Date', 'Temperature'])
    tobs_list = tobs_df.to_dict(orient='records')

    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temperature_stats(start, end=None):
    # Perform your temperature statistics analysis here
    if end:
        temp_stats = session.query(func.min(Measurement.tobs).label('TMIN'),
                                   func.avg(Measurement.tobs).label('TAVG'),
                                   func.max(Measurement.tobs).label('TMAX')).\
            filter(Measurement.date >= start, Measurement.date <= end).all()
    else:
        temp_stats = session.query(func.min(Measurement.tobs).label('TMIN'),
                                   func.avg(Measurement.tobs).label('TAVG'),
                                   func.max(Measurement.tobs).label('TMAX')).\
            filter(Measurement.date >= start).all()

    return jsonify(temp_stats)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
