from sqlalchemy import create_engine, MetaData, Table, select, and_

# Assuming you have already set up your SQLAlchemy engine
#engine = create_engine('your_database_connection_string')


APPUID = "QV3BIZZV"

# create the engine
engine = create_engine("mysql+pymysql://root:raspberry@192.168.4.217:3306/reefberrypi?charset=utf8mb4")

metadata = MetaData()

# Define the tables
probes = Table('probes', metadata, autoload_with=engine)
mcp3008 = Table('mcp3008', metadata, autoload_with=engine)

# Create the query

stmt = select(probes.c.probeid, 
              probes.c.appuid,
              probes.c.name,
              probes.c.sensortype,
              probes.c.probetype,
              mcp3008.c.chid,
              mcp3008.c.enabled,
              mcp3008.c.type,
              mcp3008.c.ph_low,
              mcp3008.c.ph_med,
              mcp3008.c.ph_high,
              mcp3008.c.numsamples,
              mcp3008.c.sigma,

              ).select_from(probes.outerjoin(mcp3008,probes.c.probeid == mcp3008.c.probeid)) \
                  .where(probes.c.probeid == mcp3008.c.probeid, probes.c.appuid == mcp3008.c.appuid)


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
