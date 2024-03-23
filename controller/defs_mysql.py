# import mysql.connector
import cls_Preferences
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import select
from sqlalchemy import insert
from sqlalchemy import and_
from sqlalchemy_utils import database_exists, create_database


# using sql alchemy
def initMySQL_ex(app_prefs, logger):
    try:
        logger.info("Attempting connection to MySQL database.")
        # create the engine
        sqlengine = create_engine("mysql+pymysql://" + app_prefs.mysql_user + ":" + app_prefs.mysql_password + "@" + app_prefs.mysql_host + ":" + app_prefs.mysql_port + "/" + app_prefs.mysql_database + "?charset=utf8mb4")
        #logger.debug("mysql+pymysql://" + app_prefs.mysql_user + ":" + app_prefs.mysql_password + "@" + app_prefs.mysql_host + ":" + app_prefs.mysql_port + "/" + app_prefs.mysql_database + "?charset=utf8mb4")
        if not database_exists(sqlengine.url):
            app_prefs.logger.warning("Database not found, creating database...")
            createDB(app_prefs, sqlengine)
       
        logger.info("Verifying database tables...")
        verifyDs18b20Table(app_prefs, sqlengine)
        verifyDashOrderTable(app_prefs, sqlengine)
        verifyProbesTable(app_prefs, sqlengine)

        logger.info("Succesfully connected to MySQL database.")
        return sqlengine
    except Exception as e:
        logger.error("Can not connect to MySQL database! " + str(e))
        exit()

def verifyDs18b20Table(app_prefs, sqlengine):
    app_prefs.logger.info("Verifying table: ds18b20")

    metadata_obj = MetaData()
    ds18b20_table = Table("ds18b20", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    probeids = ["temp_probe_1",
                    "temp_probe_2",
                    "temp_probe_3",
                    "temp_probe_4"]

    for probe in probeids:
        stmt = select(ds18b20_table).where(ds18b20_table.c.appuid == app_prefs.appuid).where(ds18b20_table.c.probeid == probe)
        results = conn.execute(stmt)
        conn.commit()

        if results.rowcount == 0:
            app_prefs.logger.warn ("Probe: [" + probe  + "] not found! Creating entry.")

            stmt = insert(ds18b20_table).values(appuid = app_prefs.appuid, 
                                                    probeid = probe,)
            
            conn.execute(stmt)
            conn.commit()

def verifyDashOrderTable(app_prefs, sqlengine):
    app_prefs.logger.info("Verifying table: dashorder")

    metadata_obj = MetaData()
    dash_table = Table("dashorder", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    widgetids = ["temp_probe_1",
                    "temp_probe_2",
                    "temp_probe_3",
                    "temp_probe_4",
                    "DHT-T",
                    "DHT-H",
                    "mcp3008_ch0",
                    "mcp3008_ch1",
                    "mcp3008_ch2",
                    "mcp3008_ch3",
                    "mcp3008_ch4",
                    "mcp3008_ch5",
                    "mcp3008_ch6",
                    "mcp3008_ch7",
                    "int_outlet_1",
                    "int_outlet_2",
                    "int_outlet_3",
                    "int_outlet_4",
                    "int_outlet_5",
                    "int_outlet_6",
                    "int_outlet_7",
                    "int_outlet_8",
                    "feed"]

    for widget in widgetids:
        stmt = select(dash_table).where(dash_table.c.appuid == app_prefs.appuid).where(dash_table.c.widgetid == widget)
        results = conn.execute(stmt)
        conn.commit()

        if results.rowcount == 0:
            app_prefs.logger.warn ("Probe: [" + widget  + "] not found! Creating entry.")

            stmt = insert(dash_table).values(appuid = app_prefs.appuid, 
                                                    widgetid = widget, column = "1", order = "1")
            
            conn.execute(stmt)
            conn.commit()

def verifyProbesTable(app_prefs, sqlengine):
    app_prefs.logger.info("Verifying table: probes")

    metadata_obj = MetaData()
    probes_table = Table("probes", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    probeids = ["temp_probe_1",
                    "temp_probe_2",
                    "temp_probe_3",
                    "temp_probe_4",
                    "DHT-T",
                    "DHT-H",
                    "mcp3008_ch0",
                    "mcp3008_ch1",
                    "mcp3008_ch2",
                    "mcp3008_ch3",
                    "mcp3008_ch4",
                    "mcp3008_ch5",
                    "mcp3008_ch6",
                    "mcp3008_ch7"]

    tempprobes = ["temp_probe_1",
                    "temp_probe_2",
                    "temp_probe_3",
                    "temp_probe_4"]
    
    # first, do the ds18b20 temperature probes
    for probe in tempprobes:
        stmt = select(probes_table).where(probes_table.c.appuid == app_prefs.appuid).where(probes_table.c.probeid == probe)
        results = conn.execute(stmt)
        conn.commit()

        if results.rowcount == 0:
            app_prefs.logger.warn ("Probe: [" + probe  + "] not found! Creating entry.")

            stmt = insert(probes_table).values(appuid = app_prefs.appuid, 
                                                    probeid = probe, probetype = "ds18b20", sensortype = "temperature", enabled = "false", name=probe)
            
            conn.execute(stmt)
            conn.commit()
    # next do the DHT22 Temperature and Humidity probe
    dhtprobes = ["DHT-T",
                    "DHT-H",]
    
    for probe in dhtprobes:
        stmt = select(probes_table).where(probes_table.c.appuid == app_prefs.appuid).where(probes_table.c.probeid == probe)
        results = conn.execute(stmt)
        conn.commit()

        if results.rowcount == 0:
            app_prefs.logger.warn ("Probe: [" + probe  + "] not found! Creating entry.")
            
            if probe == "DHT-T":
                stmt = insert(probes_table).values(appuid = app_prefs.appuid, 
                                                        probeid = probe, probetype = "dht", sensortype = "temperature", enabled = "false", name=probe)
            elif probe == "DHT-H":
                 stmt = insert(probes_table).values(appuid = app_prefs.appuid, 
                                                        probeid = probe, probetype = "dht", sensortype = "humidity", enabled = "false", name=probe)
            conn.execute(stmt)
            conn.commit()
    # next do the mcp3008 analog probes
    mcp3008probes = [
        "mcp3008_ch0",
        "mcp3008_ch1",
        "mcp3008_ch2",
        "mcp3008_ch3",
        "mcp3008_ch4",
        "mcp3008_ch5",
        "mcp3008_ch6",
        "mcp3008_ch7"]
    
    for probe in mcp3008probes:
        stmt = select(probes_table).where(probes_table.c.appuid == app_prefs.appuid).where(probes_table.c.probeid == probe)
        results = conn.execute(stmt)
        conn.commit()

        if results.rowcount == 0:
            app_prefs.logger.warn ("Probe: [" + probe  + "] not found! Creating entry.")

            stmt = insert(probes_table).values(appuid = app_prefs.appuid, 
                                                    probeid = probe, probetype = "analog", sensortype = "ph", enabled = "false", name=probe)
            
            conn.execute(stmt)
            conn.commit()

def createDB(app_prefs, sqlengine):
    try:
        
        create_database(sqlengine.url)
        metadata_obj = MetaData()
        
        app_prefs.logger.warning("Creating table dashorder")
        dashorder_table = Table("dashorder",
                                metadata_obj,
                                Column("id", Integer, nullable=False, autoincrement=True, primary_key=True, unique=True),
                                Column("appuid", String(45), nullable=False, primary_key=True),
                                Column("widgetid", String(45), unique=True),
                                Column("column", Integer),
                                Column("order", Integer),
                                )

        app_prefs.logger.warning ("Creating table ds18b20" )
        ds18b20_table = Table("ds18b20",
                            metadata_obj,
                            Column("id", Integer, nullable=False, autoincrement=True, primary_key=True),
                            Column("appuid", String(45), nullable=False, primary_key=True),
                            Column("probeid", String(45), nullable=False, primary_key=True),
                            Column("serialnum", String(45) )
                            )
        
        app_prefs.logger.warning ("Creating table global" )
        global_table = Table("global",
                            metadata_obj,
                            Column("appuid", String(45), nullable=False, primary_key=True),
                            Column("tempscale", String(12), default="C", comment="C or F"),
                            Column("feed_a_time", String(45), default="60") ,
                            Column("feed_b_time", String(45), default="60") ,
                            Column("feed_c_time", String(45), default="60") ,
                            Column("feed_d_time", String(45), default="60") ,
                            Column("dht_enable", String(45), default="False") ,
                            )

        app_prefs.logger.warning ("Creating table mcp3008" )
        mcp3008_table = Table("mcp3008",
                            metadata_obj,
                            Column("id", Integer, nullable=False, autoincrement=True, primary_key=True),
                            Column("appuid", String(45), nullable=False, primary_key=True),
                            Column("chid", String(45), nullable=False, primary_key=True),
                            Column("probeid", String(45), nullable=False, primary_key=True),
                            Column("ph_low", String(45), nullable=False),
                            Column("ph_med", String(45), nullable=False),
                            Column("ph_high", String(45), nullable=False),
                            Column("numsamples", String(45), nullable=False),
                            Column("sigma", String(45), nullable=False),
                            )
        
        app_prefs.logger.warning ("Creating table outlets" )
        outlets_table = Table("outlets",
                            metadata_obj,
                            Column("appuid", String(45), nullable=False, primary_key=True),
                            Column("outletid", String(45), nullable=False, primary_key=True),
                            Column("button_state", String(45), nullable=False),
                            Column("outletname", String(45), nullable=False),
                            Column("control_type", String(45), nullable=False),
                            Column("always_state", String(45), nullable=False),
                            Column("enable_log", String(45), nullable=False),
                            Column("heater_probe", String(45), nullable=False),
                            Column("heater_on", String(45), nullable=False),
                            Column("heater_off", String(45), nullable=False),
                            Column("light_on", String(45), nullable=False),
                            Column("light_off", String(45), nullable=False),
                            Column("return_enable_feed_a", String(45), nullable=False),
                            Column("return_feed_delay_a", String(45), nullable=False),
                            Column("return_enable_feed_b", String(45), nullable=False),
                            Column("return_feed_delay_b", String(45), nullable=False),
                            Column("return_enable_feed_c", String(45), nullable=False),
                            Column("return_feed_delay_c", String(45), nullable=False),
                            Column("return_enable_feed_d", String(45), nullable=False),
                            Column("return_feed_delay_d", String(45), nullable=False),
                            Column("skimmer_enable_feed_a", String(45), nullable=False),
                            Column("skimmer_feed_delay_a", String(45), nullable=False),
                            Column("skimmer_enable_feed_b", String(45), nullable=False),
                            Column("skimmer_feed_delay_b", String(45), nullable=False),
                            Column("skimmer_enable_feed_c", String(45), nullable=False),
                            Column("skimmer_feed_delay_c", String(45), nullable=False),
                            Column("skimmer_enable_feed_d", String(45), nullable=False),
                            Column("skimmer_feed_delay_d", String(45), nullable=False),
                            Column("ph_probe", String(45), nullable=False),
                            Column("ph_high", String(45), nullable=False),
                            Column("ph_low", String(45), nullable=False),
                            Column("ph_onwhen", String(45), nullable=False),
                            Column("enabled", String(45), nullable=False),
                            )
        
        app_prefs.logger.warning ("Creating table probes" )
        probes_table = Table("probes",
                            metadata_obj,
                            Column("idprobes", Integer, nullable=False, autoincrement=True, primary_key=True),
                            Column("probeid", String(45), nullable=False, primary_key=True),
                            Column("name", String(45), nullable=False),
                            Column("appuid", String(45), nullable=False),
                            Column("probetype", String(45), nullable=False),
                            Column("sensortype", String(45), nullable=False),
                            Column("enabled", String(45), nullable=False),
                            )

        metadata_obj.create_all(sqlengine)

    except:
        app_prefs.logger.error("Error creating database database! " + str(e))
        


def readTempProbes_ex_orig(sqlengine, appPrefs, logger):
    logger.info("Reading temperature probe data from database...")
    
    appPrefs.tempProbeDict.clear()
    ########
    # build table object from table in DB
    metadata_obj = MetaData()
    ds18b20_table = Table("probes", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(ds18b20_table).where(ds18b20_table.c.appuid == appPrefs.appuid).where(ds18b20_table.c.probetype=="ds18b20")
    row_headers = conn.execute(stmt).keys()
    print(row_headers)
    myresult = conn.execute(stmt)
    conn.commit()

    json_data = []
    for result in myresult:
        json_data.append(dict(zip(row_headers, result)))
        
    logger.info(json_data)

    for k in json_data:
            probe = cls_Preferences.tempProbeClass()
            probe.probeid = k["probeid"]
            probe.name = k["name"]
            appPrefs.tempProbeDict[probe.probeid] = probe
            logger.info("read temperature probe from db: probeid = " +
                        probe.probeid + ", probename = " + probe.name)

def readTempProbes_ex(sqlengine, appPrefs, logger):
    logger.info("Reading temperature probe data from database...")
    
    appPrefs.tempProbeDict.clear()
    ########
    # build table object from table in DB
    metadata = MetaData()
    probe_table = Table('probes', metadata, autoload_with=sqlengine)
    ds18b20_table = Table('ds18b20', metadata, autoload_with=sqlengine)
    

    conn = sqlengine.connect()

    stmt = select(probe_table.c.probeid, 
                        probe_table.c.appuid,
                        probe_table.c.name,
                        probe_table.c.sensortype,
                        probe_table.c.probetype,
                        probe_table.c.enabled,
                        ds18b20_table.c.serialnum,
                        ).select_from(probe_table.outerjoin(ds18b20_table, probe_table.c.probeid == ds18b20_table.c.probeid)) \
                        .where(probe_table.c.probeid == ds18b20_table.c.probeid, probe_table.c.appuid == ds18b20_table.c.appuid, probe_table.c.enabled == "true")


    results = conn.execute(stmt).fetchall()

    row_headers = conn.execute(stmt).keys()
    json_data = []

    for result in results:
        json_data.append(dict(zip(row_headers, result)))

    print(json_data)

    for k in json_data:
        probe = cls_Preferences.tempProbeClass()
        probe.probeid = k["probeid"]
        probe.name = k["name"]
        probe.serialnum = k["serialnum"]
        appPrefs.tempProbeDict[probe.probeid] = probe
        appPrefs.logger.info("read temperature probe from db: probeid = " +
                    probe.probeid + ", probename = " + probe.name + ", serialnum = " + probe.serialnum)



def readDHTSensor_ex (sqlengine, appPrefs, logger):
    logger.info("Reading DHT sensor data from database...")

    appPrefs.dhtDict.clear()

    # build table object from table in DB
    metadata_obj = MetaData()
    # dht_table = Table("dht", metadata_obj, autoload_with=sqlengine)
    dht_table = Table("probes", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(dht_table).where(dht_table.c.appuid == appPrefs.appuid).where(dht_table.c.probetype == "dht")
    results = conn.execute(stmt)
    conn.commit()
    
    for row in results:    
        dhtsensor = cls_Preferences.dhtSensorClass()
        logger.info(row)
        dhtsensor.name = row.name
        dhtsensor.probeid = row.probeid
        dhtsensor.sensortype = row.sensortype
        appPrefs.dhtDict[row.probeid] = dhtsensor
        logger.info("read dht sensor information from db: Temperature Probe Name = " +
                    dhtsensor.name + ", SensorType = " + dhtsensor.sensortype)


def readGlobalPrefs_ex(sqlengine, appPrefs, logger):    
    logger.info("Reading global prefs from database...")
    # build table object from table in DB
    metadata_obj = MetaData()
    global_table = Table("global", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(global_table).where(global_table.c.appuid == appPrefs.appuid)
    results = conn.execute(stmt)
    conn.commit()
 
    if results.rowcount == 0:
        logger.warn ("Global Prefs not found! Creating entry.")
        appPrefs.temperaturescale = "C"
        appPrefs.feed_a_time = "60"
        appPrefs.feed_b_time = "60"
        appPrefs.feed_c_time = "60"
        appPrefs.feed_d_time = "60"
        appPrefs.dht_enable = "false"

        stmt = insert(global_table).values(appuid = appPrefs.appuid, 
                                                    tempscale = appPrefs.temperaturescale,
                                                    feed_a_time = appPrefs.feed_a_time,
                                                    feed_b_time = appPrefs.feed_b_time,
                                                    feed_c_time = appPrefs.feed_c_time,
                                                    feed_d_time = appPrefs.feed_d_time,
                                                    dht_enable = appPrefs.dht_enable
                                                    )
        results = conn.execute(stmt)
        conn.commit()

    stmt = select(global_table).where(global_table.c.appuid == appPrefs.appuid)
    results = conn.execute(stmt)
    conn.commit()

    for row in results:
        appPrefs.temperaturescale = row.tempscale
        appPrefs.appuid = row.appuid
        appPrefs.feed_a_time = row.feed_a_time
        appPrefs.feed_b_time = row.feed_b_time
        appPrefs.feed_c_time = row.feed_c_time
        appPrefs.feed_d_time = row.feed_d_time
        appPrefs.dht_enable = row.dht_enable

    logger.info("Using temperature scale: " + appPrefs.temperaturescale)
    logger.info("Read Feed Mode A: " + appPrefs.feed_a_time)  
    logger.info("Read Feed Mode B: " + appPrefs.feed_b_time)
    logger.info("Read Feed Mode C: " + appPrefs.feed_c_time)
    logger.info("Read Feed Mode D: " + appPrefs.feed_d_time)     
    logger.info("DHT Sensor Enabled: " + appPrefs.dht_enable)           

def readOutletPrefs_ex(sqlengine, appPrefs, logger):
    try:
        logger.info("Reading outlet prefs from database...")
        appPrefs.outletDict.clear()

        # build table object from table in DB
        metadata_obj = MetaData()
        outlets_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

        conn = sqlengine.connect()
        # we support 8 outlets on the internal bus of the Pi
        intbus = ["int_outlet_1",
                "int_outlet_2",
                "int_outlet_3",
                "int_outlet_4",
                "int_outlet_5",
                "int_outlet_6",
                "int_outlet_7",
                "int_outlet_8"]
        ##########################
        # get all outlets at once
        ##########################
        # stmt = select(outlets_table).where(outlets_table.c.appuid == appPrefs.appuid)
        # results = conn.execute(stmt)
        # conn.commit()

        # for row in results:
        #     logger.debug(row.outletid)

        ##########################
        for intoutlet in intbus:
            outlet = cls_Preferences.outletPrefs()
            stmt = select(outlets_table).where(outlets_table.c.appuid == appPrefs.appuid).where(outlets_table.c.outletid == intoutlet)
            results = conn.execute(stmt)
            conn.commit()

            
            if results.rowcount == 0:
                logger.warn ("Outlet: [" + intoutlet  + "] not found! Creating entry.")
                
                outlet.ischanged = "False"
                outlet.outletid = intoutlet
                outlet.outletname = "Unnamed"
                outlet.control_type = "Always"
                outlet.always_state = "OFF"
                outlet.enable_log = "False"
                outlet.heater_probe = ""
                outlet.heater_on = "25.0"
                outlet.heater_off = "25.5"
                outlet.button_state = "OFF"
                outlet.light_on = "08:00"
                outlet.light_off = "17:00"
                outlet.return_enable_feed_a = "False"
                outlet.return_feed_delay_a = "0"
                outlet.return_enable_feed_b = "False"
                outlet.return_feed_delay_b = "0"
                outlet.return_enable_feed_c = "False"
                outlet.return_feed_delay_c = "0"
                outlet.return_enable_feed_d = "False"
                outlet.return_feed_delay_d = "0"
                outlet.skimmer_enable_feed_a = "False"
                outlet.skimmer_feed_delay_a = "0"
                outlet.skimmer_enable_feed_b = "False"
                outlet.skimmer_feed_delay_b = "0"
                outlet.skimmer_enable_feed_c = "False"
                outlet.skimmer_feed_delay_c = "0"
                outlet.skimmer_enable_feed_d = "False"
                outlet.skimmer_feed_delay_d = "0"
                outlet.ph_probe = "mcp3008_ch0"
                outlet.ph_high = "8.0"
                outlet.ph_low = "7.9"
                outlet.ph_onwhen = "HIGH"
                outlet.enabled = "true"

                stmt = insert(outlets_table).values(appuid = appPrefs.appuid, 
                                                    outletid = intoutlet,
                                                    button_state = "OFF",
                                                    outletname = outlet.outletname,
                                                    control_type = outlet.control_type,
                                                    always_state = outlet.always_state,
                                                    enable_log = outlet.enable_log,
                                                    heater_probe = outlet.heater_probe,
                                                    heater_on = outlet.heater_on,
                                                    heater_off = outlet.heater_off,
                                                    light_on = outlet.light_on,
                                                    light_off = outlet.light_off,
                                                    return_enable_feed_a = outlet.return_enable_feed_a,
                                                    return_feed_delay_a = outlet.return_feed_delay_a,
                                                    return_enable_feed_b = outlet.return_enable_feed_b,
                                                    return_feed_delay_b = outlet.return_feed_delay_b,
                                                    return_enable_feed_c = outlet.return_enable_feed_c,
                                                    return_feed_delay_c = outlet.return_feed_delay_c,
                                                    return_enable_feed_d = outlet.return_enable_feed_d,
                                                    return_feed_delay_d = outlet.return_feed_delay_d,
                                                    skimmer_enable_feed_a = outlet.skimmer_enable_feed_a,
                                                    skimmer_feed_delay_a = outlet.skimmer_feed_delay_a,
                                                    skimmer_enable_feed_b = outlet.skimmer_enable_feed_b,
                                                    skimmer_feed_delay_b = outlet.skimmer_feed_delay_b,
                                                    skimmer_enable_feed_c = outlet.skimmer_enable_feed_c,
                                                    skimmer_feed_delay_c = outlet.skimmer_feed_delay_c,
                                                    skimmer_enable_feed_d = outlet.skimmer_enable_feed_d,
                                                    skimmer_feed_delay_d = outlet.skimmer_feed_delay_d,
                                                    ph_probe = outlet.ph_probe,
                                                    ph_high = outlet.ph_high,
                                                    ph_low = outlet.ph_low,
                                                    ph_onwhen = outlet.ph_onwhen,
                                                    enabled = outlet.enabled)
            else:
 
                for row in results:
                    outlet.ischanged = "False"
                    outlet.outletid = intoutlet
                    outlet.outletname = row.outletname
                    outlet.control_type = row.control_type
                    outlet.always_state = row.always_state
                    outlet.enable_log = row.enable_log
                    outlet.heater_probe = row.heater_probe
                    outlet.heater_on = row.heater_on
                    outlet.heater_off = row.heater_off
                    outlet.button_state = row.button_state
                    outlet.light_on = row.light_on
                    outlet.light_off = row.light_off
                    outlet.return_enable_feed_a = row.return_enable_feed_a
                    outlet.return_feed_delay_a = row.return_feed_delay_a
                    outlet.return_enable_feed_b = row.return_enable_feed_b
                    outlet.return_feed_delay_b = row.return_feed_delay_b
                    outlet.return_enable_feed_c = row.return_enable_feed_c
                    outlet.return_feed_delay_c = row.return_feed_delay_c
                    outlet.return_enable_feed_d = row.return_enable_feed_d
                    outlet.return_feed_delay_d = row.return_feed_delay_d
                    outlet.skimmer_enable_feed_a = row.skimmer_enable_feed_a
                    outlet.skimmer_feed_delay_a = row.skimmer_feed_delay_a
                    outlet.skimmer_enable_feed_b = row.skimmer_enable_feed_b
                    outlet.skimmer_feed_delay_b = row.skimmer_feed_delay_b
                    outlet.skimmer_enable_feed_c = row.skimmer_enable_feed_c
                    outlet.skimmer_feed_delay_c = row.skimmer_feed_delay_c
                    outlet.skimmer_enable_feed_d = row.skimmer_enable_feed_d
                    outlet.skimmer_feed_delay_d = row.skimmer_feed_delay_d
                    outlet.ph_probe = row.ph_probe
                    outlet.ph_high = row.ph_high
                    outlet.ph_low = row.ph_low
                    outlet.ph_onwhen = row.ph_onwhen
                    outlet.outletstatus = "Loading..."
                    outlet.enabled = row.enabled
               
                

            conn.execute(stmt)
            conn.commit()
            
            if row.enabled.lower() == "true":
                logger.info(row)
            appPrefs.outletDict[intoutlet] = outlet
            #print(intoutlet)
            #for row in results:
                
                #print(row.appuid + " " + row.outletid + " " + row.outletname) 
                #logger.info("[" + row.appuid + " " + row.outletid + "] " + row.outletname + " = " + row.button_state)
                
    except Exception as e:
        logger.error("Error reading outlets. " + str(e) )

    #return appPrefs


def readMCP3008Prefs_ex(sqlengine, appPrefs, logger):
    try:
        logger.info("Reading MCP3008 prefs from database...")
        appPrefs.mcp3008Dict.clear()

        # build table object from table in DB
        metadata_obj = MetaData()

        mcp3008_table = Table("mcp3008", metadata_obj, autoload_with=sqlengine)
        probe_table = Table("probes", metadata_obj, autoload_with=sqlengine)

        conn = sqlengine.connect()
        # we support 8 outlets on the internal bus of the Pi
        channels = ["0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7"]
        ##########################################################
        # populate the mcp3008 table if a channel is missing
        ##########################################################
        for ch in channels:
            newchannel = cls_Preferences.analogChannelClass()
            stmt = select(mcp3008_table).where(mcp3008_table.c.appuid == appPrefs.appuid).where(mcp3008_table.c.chid == ch)
            results = conn.execute(stmt)
            conn.commit()
            
            if results.rowcount == 0:
                logger.warn ("Analog Channel: [" + ch  + "] not found! Creating entry.")
                
                newchannel.ch_num = ch
                newchannel.ch_probeid = "mcp3008_ch" + str(ch)
                newchannel.ch_ph_low = "900"
                newchannel.ch_ph_med = "700"
                newchannel.ch_ph_high = "600"
                newchannel.ch_dvlist = []
                newchannel.ch_numsamples = "10"
                newchannel.ch_sigma = "1"
                newchannel.LastLogTime = 0

                stmt = insert(mcp3008_table).values(appuid = appPrefs.appuid, 
                                                    chid = ch,
                                                    probeid = newchannel.ch_probeid,
                                                    ph_low = newchannel.ch_ph_low,
                                                    ph_med = newchannel.ch_ph_med,
                                                    ph_high = newchannel.ch_ph_high,
                                                    numsamples = newchannel.ch_numsamples,
                                                    sigma = newchannel.ch_sigma)
                conn.execute(stmt)
                conn.commit()

        for ch in channels:
            channel = cls_Preferences.analogChannelClass()

            stmt = select(probe_table.c.probeid, 
                        probe_table.c.appuid,
                        probe_table.c.name,
                        probe_table.c.sensortype,
                        probe_table.c.probetype,
                        probe_table.c.enabled,
                        mcp3008_table.c.chid,
                        mcp3008_table.c.ph_low,
                        mcp3008_table.c.ph_med,
                        mcp3008_table.c.ph_high,
                        mcp3008_table.c.numsamples,
                        mcp3008_table.c.sigma,
                        ).select_from(probe_table.outerjoin(mcp3008_table, probe_table.c.probeid == mcp3008_table.c.probeid)) \
                        .where(probe_table.c.probeid == mcp3008_table.c.probeid, probe_table.c.appuid == mcp3008_table.c.appuid, mcp3008_table.c.chid == ch, probe_table.c.enabled == "true")
            
            
            results = conn.execute(stmt)
            conn.commit()
            
            for row in results:
                #logger.info(row)
                channel.ch_num = ch
                channel.ch_probeid = row.probeid
                channel.ch_name = row.name
                channel.ch_type = row.sensortype
                channel.ch_ph_low = row.ph_low
                channel.ch_ph_med = row.ph_med
                channel.ch_ph_high = row.ph_high
                channel.ch_dvlist = []
                channel.ch_enabled = row.enabled
                channel.ch_numsamples = row.numsamples
                channel.ch_sigma = row.sigma
                channel.LastLogTime = 0

                appPrefs.mcp3008Dict[ch] = channel
                
    except Exception as e:
        logger.error("Error reading analog probes. " + str(e) )


    