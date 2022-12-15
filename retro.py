#!/usr/bin/env python

# upstream
import environ
from influxdb_client import InfluxDBClient
from pymindergas import Mindergas

@environ.config(prefix='MG')
class MyConf:
    api_token = environ.var()
    influxdb_bucket = environ.var(name="INFLUXDB_V2_BUCKET")

conf = MyConf.from_environ()

idb = InfluxDBClient.from_env_properties()
query_api = idb.query_api()
q = f"""
from(bucket: "{conf.influxdb_bucket}")
  |> range(start: 2022-05-15T00:00:00Z, stop: 2022-12-15T20:00:00Z)
  |> filter(fn: (r) => r["_measurement"] == "heat" and r["_field"] == "energy")
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: true)
  |> yield(name: "mean")
"""

mg = Mindergas()

result = query_api.query(query=q)
for table in result:
    for record in table.records:
        if record.get_value() is not None:
            reading = '%.3f' % (record.get_value() / 1000000000)
            date = record.get_time().ctime() + " UTC"
            if record.get_value() < 600000000000:
                print(date, reading)
                if not mg.postReading(conf.api_token, reading, date):
                    continue
