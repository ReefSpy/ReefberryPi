import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import select
from sqlalchemy import insert


MYSQL_HOST = "192.168.4.217"
MYSQL_USER = "root"
MYSQL_PASSWORD = "raspberry"
MYSQL_DATABASE = "reefberrypi"
MYSQL_PORT = "3306"


class AppPrefences():
    appuid = "QV3BIZZV"
    tempProbeDict = {}

class tempProbeClass():
    name = ""
    probeid = ""
    lastTemperature = ""
    lastLogTime = ""

# using sql alchemy
def initMySQL_ex():
    try:
        # create the engine
        sqlengine = create_engine("mysql+pymysql://" + MYSQL_USER + ":" + MYSQL_PASSWORD + "@" + MYSQL_HOST + ":" + MYSQL_PORT + "/" + MYSQL_DATABASE + "?charset=utf8mb4")
        #logger.debug("mysql+pymysql://" + app_prefs.mysql_user + ":" + app_prefs.mysql_password + "@" + app_prefs.mysql_host + ":" + app_prefs.mysql_port + "/" + app_prefs.mysql_database + "?charset=utf8mb4")
        print("Succesfully connected to MySQL database.")
        return sqlengine
    except Exception as e:
        print("Can not connect to MySQL database! " + str(e))
        exit()


def readTempProbes_ex(sqlengine, appPrefs):
    print("Reading temperature probe data from database...")
    
    appPrefs.tempProbeDict.clear()
    ########
    # build table object from table in DB
    metadata_obj = MetaData()
    ds18b20_table = Table("ds18b20", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(ds18b20_table).where(ds18b20_table.c.appuid == appPrefs.appuid)
    row_headers = conn.execute(stmt).keys()
    print(row_headers)
    myresult = conn.execute(stmt)
    conn.commit()

    json_data = []
    for result in myresult:
        json_data.append(dict(zip(row_headers, result)))
        
    print(json_data)

    for k in json_data:
            probe = tempProbeClass()
            probe.probeid = k["probeid"]
            probe.name = k["name"]
            appPrefs.tempProbeDict[probe.probeid] = probe
            print("read temperature probe from db: probeid = " +
                        probe.probeid + ", probename = " + probe.name)

    #########
    # mycursor = mysqldb.cursor()
    # sql = "SELECT probeid, name, appuid FROM " + mysqldb.database + \
    #     ".ds18b20 WHERE appuid = '" + appPrefs.appuid + "'"
    # #logger.info(sql)
    # mycursor.execute(sql)

    ##############
    # # this will extract row headers
    # row_headers = [x[0] for x in mycursor.description]
    # myresult = mycursor.fetchall()
    # json_data = []
    # mycursor.close()
    # mysqldb.commit()
    # for result in myresult:
    #     json_data.append(dict(zip(row_headers, result)))

    # logger.info(json_data)

    # for k in json_data:
    #     probe = cls_Preferences.tempProbeClass()
    #     probe.probeid = k["probeid"]
    #     probe.name = k["name"]
    #     appPrefs.tempProbeDict[probe.probeid] = probe
    #     logger.info("read temperature probe from db: probeid = " +
    #                 probe.probeid + ", probename = " + probe.name)

    ############################


appPrefs = AppPrefences
sqlengine = initMySQL_ex()
readTempProbes_ex(sqlengine, appPrefs)