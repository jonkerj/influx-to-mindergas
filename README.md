This thing submits readings from InfluxDB2 to [mindergas](https://www.mindergas.nl).
I collect readings from my district heating meter using [PyNuts](https://github.com/jonkerj/pynuts).
This script (`oneshot.py`) runs from a `CronJob` on my Kubernetes cluster, but you can run it from regular cron as well.
It needs a couple of env vars:

* `INFLUX_V2_URL` URL to your InfluxDB2
* `INFLUX_V2_TOKEN` Token to access Influxdb
* `INFLUX_V2_BUCKET` bucket to query
* `MG_API_TOKEN` token for mindergas' API

# oneshot

It basically performs this query:

```
from(bucket: "YOUR_BUCKET")
  |> range(start: -2h, stop: -0s)
  |> filter(fn: (r) => r["_measurement"] == "heat" and r["_field"] == "energy")
  |> last()
  ```

In other words: last measurement `heat`, field `energy` from the last 2 hours.

It divides the result by 1000000000 (PyNuts stores canonically in Joules; mindergas requires GJ) and submits, honouring time zon and exits

# retro

It does the same, except that it loops over every reading. I used this to retro-submit my readings.