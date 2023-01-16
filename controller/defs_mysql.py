import mysql.connector
import cls_Preferences


def initMySQL(app_prefs, logger):
    try:
        mySQLdb = mysql.connector.connect(
            host=app_prefs.mysql_host,
            user=app_prefs.mysql_user,
            password=app_prefs.mysql_password,
            database=app_prefs.mysql_database
        )

        logger.info("Succesfully connected to MySQL database.")
        return mySQLdb
    except Exception as e:
        logger.error("Can not connect to MySQL database! " + str(e))
        exit()


def readTempProbes(mysqldb, appPrefs, logger):
    logger.info("Reading temperature probe data from database...")

    appPrefs.tempProbeDict.clear()

    mycursor = mysqldb.cursor()
    sql = "SELECT probeid, name, appuid FROM " + mysqldb.database + \
        ".ds18b20 WHERE appuid = '" + appPrefs.appuid + "'"
    #logger.info(sql)
    mycursor.execute(sql)
    # this will extract row headers
    row_headers = [x[0] for x in mycursor.description]
    myresult = mycursor.fetchall()
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


def readGlobalPrefs(mysqldb, appPrefs, logger):
    logger.info("Reading global prefs from database...")

    mycursor = mysqldb.cursor()

    sql = "SELECT tempscale FROM " + mysqldb.database + \
        ".global WHERE appuid = '" + appPrefs.appuid + "'"
    logger.info(sql)
    mycursor.execute(sql)
    myresult = mycursor.fetchone()
    #print(myresult)

    if myresult is not None:
        appPrefs.temperaturescale = myresult[0]
    else:
        #print("error")
        appPrefs.temperaturescale = "C"
        sql = "INSERT into " + mysqldb.database + \
                ".global (appuid, tempscale) values ('" + appPrefs.appuid + "'," + "'" + "C" + "')"
        #print(sql)
        mycursor.execute(sql)
        mysqldb.commit()
        
    logger.info("Using temperature scale: " + appPrefs.temperaturescale)
    
def readOutletPrefs(mysqldb, appPrefs, logger):
    logger.info("Reading outlet prefs from database...")
    appPrefs.outletDict.clear()
    mycursor = mysqldb.cursor(dictionary=True)
    # we support 8 outlets on the internal bus of the Pi
    intbus = ["int_outlet_1",
              "int_outlet_2",
              "int_outlet_3",
              "int_outlet_4",
              "int_outlet_5",
              "int_outlet_6",
              "int_outlet_7",
              "int_outlet_8"]

    for intoutlet in intbus:
        outlet = cls_Preferences.outletPrefs()
        sql = "SELECT * FROM " + mysqldb.database + \
                    ".outlets WHERE appuid = '" + appPrefs.appuid + "'" + " AND outletid = '" + intoutlet + "'"
        
        mycursor.execute(sql)
        myresult = mycursor.fetchone()
        if myresult is None:
            logger.warn("Inserting outlet configuration into database: " + intoutlet)
            
            sql = "INSERT into " + mysqldb.database + \
                '''.outlets (appuid,
                outletid,
                button_state,
                outletname,
                control_type,
                always_state,
                enable_log,
                heater_probe,
                heater_on,
                heater_off,
                light_on,
                light_off,
                return_enable_feed_a,
                return_feed_delay_a,
                return_enable_feed_b,
                return_feed_delay_b,
                return_enable_feed_c,
                return_feed_delay_c,
                return_enable_feed_d,
                return_feed_delay_d,
                skimmer_enable_feed_a,
                skimmer_feed_delay_a,
                skimmer_enable_feed_b,
                skimmer_feed_delay_b,
                skimmer_enable_feed_c,
                skimmer_feed_delay_c,
                skimmer_enable_feed_d,
                skimmer_feed_delay_d,
                ph_probe,
                ph_high,
                ph_low,
                ph_onwhen)''' + "values ('" + appPrefs.appuid + "'," + "'" + intoutlet + "'," + \
                "'OFF'," + \
                "'Unnamed'," + \
                "'Always'," + \
                "'False'," + \
                "'False'," + \
                "''," + \
                "'25.0'," + \
                "'25.5'," + \
                "'08:00'," + \
                "'17:00'," + \
                "'False'," + \
                "'0'," + \
                "'False'," + \
                "'0'," + \
                "'False'," + \
                "'0'," + \
                "'False'," + \
                "'0'," + \
                "'False'," + \
                "'0'," + \
                "'False'," + \
                "'0'," + \
                "'False'," + \
                "'0'," + \
                "'False'," + \
                "'0'," + \
                "'mcp3008_ch1'," + \
                "'8.0'," + \
                "'7.9'," + \
                "'HIGH'" + \
                ")"
            mycursor.execute(sql)
            mysqldb.commit()

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
            outlet.ph_probe = "mcp3008_ch1"
            outlet.ph_high = "8.0"
            outlet.ph_low = "7.9"
            outlet.ph_onwhen = "HIGH"
        else:
            logger.info("Reading outlet configuration: " + intoutlet)
            outlet.outletid = myresult["outletid"]
            outlet.button_state = myresult["button_state"]
            outlet.outletname = myresult["outletname"]
            outlet.control_type = myresult["control_type"]
            outlet.always_state = myresult["always_state"] 
            outlet.enable_log = myresult["enable_log"]
            outlet.heater_probe = myresult["heater_probe"] 
            outlet.heater_on = myresult["heater_on"]
            outlet.heater_off = myresult["heater_off"]
            outlet.light_on = myresult["light_on"]
            outlet.light_off = myresult["light_off"]
            outlet.return_enable_feed_a = myresult["return_enable_feed_a"]
            outlet.return_feed_delay_a = myresult["return_feed_delay_a"]
            outlet.return_enable_feed_b = myresult["return_enable_feed_b"]
            outlet.return_feed_delay_b = myresult["return_feed_delay_b"]
            outlet.return_enable_feed_c = myresult["return_enable_feed_c"]
            outlet.return_feed_delay_c = myresult["return_feed_delay_c"]
            outlet.return_enable_feed_d = myresult["return_enable_feed_d"]
            outlet.return_feed_delay_d = myresult["return_feed_delay_d"]
            outlet.skimmer_enable_feed_a = myresult["skimmer_enable_feed_a"]
            outlet.skimmer_feed_delay_a = myresult["skimmer_feed_delay_a"]
            outlet.skimmer_enable_feed_b = myresult["skimmer_enable_feed_b"]
            outlet.skimmer_feed_delay_b = myresult["skimmer_feed_delay_b"]
            outlet.skimmer_enable_feed_c = myresult["skimmer_enable_feed_c"]
            outlet.skimmer_feed_delay_c = myresult["skimmer_feed_delay_c"]
            outlet.skimmer_enable_feed_d = myresult["skimmer_enable_feed_d"]
            outlet.skimmer_feed_delay_d = myresult["skimmer_feed_delay_d"]
            outlet.ph_probe = myresult["ph_probe"]
            outlet.ph_high = myresult["ph_high"]
            outlet.ph_low = myresult["ph_low"]
            outlet.ph_onwhen = myresult["ph_onwhen"]
            
        appPrefs.outletDict[intoutlet] = outlet
    #print (appPrefs.outletDict["int_outlet_1"].outletname)
    #print (appPrefs.outletDict["int_outlet_7"].outletname)
    #exit()