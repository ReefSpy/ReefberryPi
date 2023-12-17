from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import select
from datetime import datetime
import time


APPUID = "QV3BIZZV"

# create the engine
engine = create_engine("mysql+pymysql://root:raspberry@192.168.4.217:3306/reefberrypi?charset=utf8mb4")

# build table object from table in DB
metadata_obj = MetaData()
some_table = Table("outlets", metadata_obj, autoload_with=engine)

#stmt = select(some_table).where(some_table.c.param_name == "OUTLET_1")
stmt = select(some_table.c.outletid, some_table.c.appuid, some_table.c.button_state, some_table.c.outletname).where(some_table.c.appuid == APPUID)
# with engine.connect() as conn:
#     for row in conn.execute(stmt):
#         #print(row)
#         print(str(datetime.now()) + " " + row.param_name + " = " + row.value)


while True:
    
    with engine.connect() as conn:
        results = conn.execute(stmt)
        for row in results:
            #print(row)
            print("[" + str(datetime.now()) + "] (" + row.outletid + ") " + row.outletname + " = " + row.button_state)

    time.sleep(1)

