from sqlalchemy import create_engine, MetaData, Table, select, and_

# Assuming you have already set up your SQLAlchemy engine
#engine = create_engine('your_database_connection_string')


APPUID = "QV3BIZZV"

# create the engine
engine = create_engine("mysql+pymysql://root:raspberry@192.168.4.217:3306/reefberrypi?charset=utf8mb4")

metadata = MetaData()

# Define the tables
probe_table = Table('probes', metadata, autoload_with=engine)
mcp3008_table = Table('mcp3008', metadata, autoload_with=engine)

channels = ["0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7"]

# Create the query
#for ch in channels:
ch = 1
stmt = select(probe_table.c.probeid, 
                        probe_table.c.appuid,
                        probe_table.c.name,
                        probe_table.c.sensortype,
                        probe_table.c.probetype,
                        mcp3008_table.c.chid,
                        mcp3008_table.c.enabled,
                        mcp3008_table.c.type,
                        mcp3008_table.c.ph_low,
                        mcp3008_table.c.ph_med,
                        mcp3008_table.c.ph_high,
                        mcp3008_table.c.numsamples,
                        mcp3008_table.c.sigma,
                        ).select_from(probe_table.outerjoin(mcp3008_table, probe_table.c.probeid == mcp3008_table.c.probeid)) \
                        .where(probe_table.c.probeid == mcp3008_table.c.probeid, probe_table.c.appuid == mcp3008_table.c.appuid, mcp3008_table.c.chid == ch)


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
