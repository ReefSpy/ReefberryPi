from sqlalchemy import create_engine, MetaData, Table, select, and_


class tempProbeClass():
    name = ""
    probeid = ""
    lastTemperature = ""
    lastLogTime = ""
    serialnum = ""

# Assuming you have already set up your SQLAlchemy engine
#engine = create_engine('your_database_connection_string')


APPUID = "QV3BIZZV"

# create the engine
engine = create_engine("mysql+pymysql://root:raspberry@192.168.4.217:3306/reefberrypi?charset=utf8mb4")

metadata = MetaData()

# Define the tables
probe_table = Table('probes', metadata, autoload_with=engine)
ds18b20_table = Table('ds18b20', metadata, autoload_with=engine)


# Create the query
#for ch in channels:
ch = 1
stmt = select(probe_table.c.probeid, 
                        probe_table.c.appuid,
                        probe_table.c.name,
                        probe_table.c.sensortype,
                        probe_table.c.probetype,
                        probe_table.c.enabled,
                        ds18b20_table.c.serialnum,
                        ).select_from(probe_table.outerjoin(ds18b20_table, probe_table.c.probeid == ds18b20_table.c.probeid)) \
                        .where(probe_table.c.probeid == ds18b20_table.c.probeid, probe_table.c.appuid == ds18b20_table.c.appuid, probe_table.c.enabled == "true")


# query = select([probes]).\
#     select_from(probes.join(mcp3008, and_(
#         probes.c.probeid == mcp3008.c.probeid,
#         probes.c.appuid == mcp3008.c.appuid
#     ))).\
#     where(and_(
#         probes.c.probeid == mcp3008.c.probeid,
#         probes.c.appuid == mcp3008.c.appuid
#     ))

# Execute the query using your SQLAlchemy session
conn = engine.connect()
results = conn.execute(stmt).fetchall()

# Process the results as needed
for row in results:
    # Do something with each row
    print(row)

row_headers = conn.execute(stmt).keys()
json_data = []
tempProbeDict = {}
for result in results:
    json_data.append(dict(zip(row_headers, result)))

print(json_data)

for k in json_data:
            probe = tempProbeClass()
            probe.probeid = k["probeid"]
            probe.name = k["name"]
            probe.serialnum = k["serialnum"]
            tempProbeDict[probe.probeid] = probe
            print("read temperature probe from db: probeid = " +
                        probe.probeid + ", probename = " + probe.name + ", serialnum = " + probe.serialnum)


