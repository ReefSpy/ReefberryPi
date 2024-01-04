import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

bucket = "reefberrypi_probe_1dy"
org = "reefberrypi"
token = "lZqJh3rEn6y4jDZqgQG19Vck53e2oryHLgHWd3qhoYZbwqGNJlbCkArZsG643ldFrEWPjmxWRdgnrtBnogp0jw=="
# Store the URL of your InfluxDB instance
url="http://argon1.local:8086"


client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

query_api = client.query_api()

query = 'from(bucket: "reefberrypi_probe_1dy") \
  |> range(start: -24h) \
  |> filter(fn: (r) => r["_measurement"] == "temperature_c") \
  |> filter(fn: (r) => r["_field"] == "value") \
  |> filter(fn: (r) => r["appuid"] == "QV3BIZZV") \
  |> filter(fn: (r) => r["probeid"] == "ds18b20_28-0416525f5eff") \
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false) \
  |> yield(name: "mean")'


result = query_api.query(org=org, query=query)

results = []
for table in result:
  for record in table.records:
    results.append((record.get_time(), record.get_value()))

for result in results:
  format_string = '%Y-%m-%d %H:%M:%S'
  date_string = result[0].strftime(format_string)
  print(date_string)
