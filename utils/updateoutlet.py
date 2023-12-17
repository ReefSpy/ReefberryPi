from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import insert
from sqlalchemy import update

APPUID = "QV3BIZZV"

# define some custom functions
def OutletNumInput():
    print()
    outletnum = input("Enter Outlet Number (1-8): ")

    if outletnum == "1" or outletnum == "2" or outletnum == "3" or outletnum == "4" or outletnum == "5" or outletnum == "6" or outletnum == "7" or outletnum == "8":
        #print ("OK")
        return True, outletnum
    else:   
        print("*** Invalid entry ***")
        return False, outletnum

def OutletValInput():
    outletval = input("Enter (1: ON, 2: OFF, 3: AUTO): ")
    if outletval == "1" or outletval == "2" or outletval == "3":
        #print ("OK")
        return True, outletval
    else:   
        print("*** Invalid entry ***")
        return False, outletval
    
while True:
    # accept input for outlet num
    retVal = False
    while retVal == False:
        retVal, outletnum = OutletNumInput()

    #print(outletnum)


    # accept input for outlet state
    retVal = False
    while retVal == False:
        retVal, outletval = OutletValInput()

    #print(outletval)

    # format input to text values that will be recorded into DB
    #outletnum = "OUTLET_" + outletnum
    outletnum = "int_outlet_" + outletnum

    if outletval == "1":
        outletval = "ON"
    elif outletval == "2":
        outletval = "OFF"
    elif outletval == "3":
        outletval = "AUTO"

    # output what user entered
    print()
    print ("Outlet: {} Value: {}".format(outletnum, outletval) )

    # create the engine
    #engine = create_engine("mysql+pymysql://root:raspberry@192.168.4.217:3306/sample?charset=utf8mb4")
    engine = create_engine("mysql+pymysql://root:raspberry@argon1.local:3306/reefberrypi?charset=utf8mb4")

    # build table object from table in DB
    metadata_obj = MetaData()
    #some_table = Table("first_table", metadata_obj, autoload_with=engine)
    some_table = Table("outlets", metadata_obj, autoload_with=engine)

    # Insert
    #stmt = insert(some_table).values(param_name="OUTLET_1", value="OFF")

    #update
    # stmt = (
    #     update(some_table)
    #     .where(some_table.c.param_name == outletnum)
    #     .values(value=outletval)
    # )

    stmt = (
        update(some_table)
        .where(some_table.c.outletid == outletnum)
        .where(some_table.c.appuid == APPUID)
        .values(button_state=outletval)
    )
    #print(stmt)

    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # print all rows in the table
    print()
    #stmt = select(some_table).where(some_table.name == "first_table")
    stmt = select(some_table).where(some_table.name == "outlets").where(some_table.c.appuid == APPUID)

    #print(stmt)
    with engine.connect() as conn:
        for row in conn.execute(stmt):
            print(row)

    print()