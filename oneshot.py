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

query = f"""
from(bucket: "{conf.influxdb_bucket}")
  |> range(start: -2h, stop: -0s)
  |> filter(fn: (r) => r["_measurement"] == "heat" and r["_field"] == "energy")
  |> last()
"""

mg = Mindergas()

result = query_api.query(query=query)
for table in result:
    for record in table.records:
        if record.get_value() is not None:
            reading = '%.3f' % (record.get_value() / 1000000000) # J to GJ
            date = record.get_time().ctime() + " UTC" # 't ding wil perse date uit string parsen, maar lijkt TZ te eten
            print(date, reading)
            if not mg.postReading(conf.api_token, reading, date):
                raise RuntimeError("mindergas was het er niet mee eens")
            break # one submit is enough