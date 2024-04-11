import glob
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import insert
import defs_mysql
from flask import jsonify
import time
import defs_common


#####################################################################
# api_get_connected_temp_probes
# return list of ds18b20 temperature probes that are connected to the
# system and showing up in '/sys/bus/w1/devices/'
#####################################################################
def api_get_connected_temp_probes():
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')

    probelist = []

    for d in device_folder:
        probeid = d.split("/")[-1]
        probelist.append(probeid)

    return probelist

#####################################################################
# api_set_connected_temp_probes
# assign the selected ds18b20 probes to Probe ID 1,2,3,4
#####################################################################


def api_set_connected_temp_probes(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    ProbeID1 = str(request.json.get(
        "probeID1", "")).lower()
    ProbeID2 = str(request.json.get(
        "probeID2", "")).lower()
    ProbeID3 = str(request.json.get(
        "probeID3", "")).lower()
    ProbeID4 = str(request.json.get(
        "probeID4", "")).lower()

    probearray = []

    probearray.append({"temp_probe_1": ProbeID1})
    probearray.append({"temp_probe_2": ProbeID2})
    probearray.append({"temp_probe_3": ProbeID3})
    probearray.append({"temp_probe_4": ProbeID4})

    AppPrefs.logger.info(probearray)

    metadata_obj = MetaData()
    ds18b20_table = Table("ds18b20", metadata_obj, autoload_with=sqlengine)
    probe_table = Table("probes", metadata_obj, autoload_with=sqlengine)

    for probe in probearray:
        # AppPrefs.logger.info(probe)
        keys = probe.keys()
        # convert to list to avoid the dreaded not-subscriptable error
        key = list(keys)[0]

        if (probe[key]) != "":
            enabled = "true"
        else:
            enabled = "false"

        stmt = (
            update(ds18b20_table)
            .where(ds18b20_table.c.probeid == key)
            .where(ds18b20_table.c.appuid == AppPrefs.appuid)
            .values(serialnum=probe[key])
        )
        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        stmt = (
            update(probe_table)
            .where(probe_table.c.probeid == key)
            .where(probe_table.c.appuid == AppPrefs.appuid)
            .values(enabled=enabled)
        )
        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

    defs_mysql.readTempProbes_ex(sqlengine, AppPrefs, AppPrefs.logger)

    return

#####################################################################
# api_get_assigned_temp_probes
# return list of ds18b20 temperature probes that that have been
# assigned to Probe IDs
####################################################################


def api_get_assigned_temp_probes(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)
    # build table object from table in DB
    metadata_obj = MetaData()
    ds18b20_table = Table("ds18b20", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(ds18b20_table).where(
        ds18b20_table.c.appuid == AppPrefs.appuid)
    row_headers = conn.execute(stmt).keys()
    AppPrefs.logger.info(row_headers)
    myresult = conn.execute(stmt)
    conn.commit()

    json_data = []

    for row in myresult:
        json_data.append({row.probeid: row.serialnum})

    return json_data

#####################################################################
# api_get_outlet_list
# return list of outlets on the internal bus
#####################################################################


def api_get_outlet_list(AppPrefs, request):
    AppPrefs.logger.info(request)

    outletdict = {}

    # loop through each outlet
    for outlet in AppPrefs.outletDict:
        #           convert temperature values to F if using Fahrenheit
        if AppPrefs.temperaturescale == "F":
            heater_on_x = defs_common.convertCtoF(
                AppPrefs.outletDict[outlet].heater_on)
            heater_off_x = defs_common.convertCtoF(
                AppPrefs.outletDict[outlet].heater_off)
        else:
            heater_on_x = AppPrefs.outletDict[outlet].heater_on
            heater_off_x = AppPrefs.outletDict[outlet].heater_off

        outletdict[outlet] = {"outletid": AppPrefs.outletDict[outlet].outletid,
                              "outletname": AppPrefs.outletDict[outlet].outletname,
                              "control_type": AppPrefs.outletDict[outlet].control_type,
                              "outletstatus": AppPrefs.outletDict[outlet].outletstatus,
                              "button_state": AppPrefs.outletDict[outlet].button_state,
                              "heater_on": heater_on_x,
                              "heater_off": heater_off_x,
                              "heater_probe": AppPrefs.outletDict[outlet].heater_probe,
                              "light_on": AppPrefs.outletDict[outlet].light_on,
                              "light_off": AppPrefs.outletDict[outlet].light_off,
                              "always_state": AppPrefs.outletDict[outlet].always_state,
                              "return_enable_feed_a": (AppPrefs.outletDict[outlet].return_enable_feed_a).lower() == "true",
                              "return_enable_feed_b": (AppPrefs.outletDict[outlet].return_enable_feed_b).lower() == "true",
                              "return_enable_feed_c": (AppPrefs.outletDict[outlet].return_enable_feed_c).lower() == "true",
                              "return_enable_feed_d": (AppPrefs.outletDict[outlet].return_enable_feed_d).lower() == "true",
                              "return_feed_delay_a": AppPrefs.outletDict[outlet].return_feed_delay_a,
                              "return_feed_delay_b": AppPrefs.outletDict[outlet].return_feed_delay_b,
                              "return_feed_delay_c": AppPrefs.outletDict[outlet].return_feed_delay_c,
                              "return_feed_delay_d": AppPrefs.outletDict[outlet].return_feed_delay_d,

                              "skimmer_enable_feed_a": (AppPrefs.outletDict[outlet].skimmer_enable_feed_a).lower() == "true",
                              "skimmer_enable_feed_b": (AppPrefs.outletDict[outlet].skimmer_enable_feed_b).lower() == "true",
                              "skimmer_enable_feed_c": (AppPrefs.outletDict[outlet].skimmer_enable_feed_c).lower() == "true",
                              "skimmer_enable_feed_d": (AppPrefs.outletDict[outlet].skimmer_enable_feed_d).lower() == "true",
                              "skimmer_feed_delay_a": AppPrefs.outletDict[outlet].skimmer_feed_delay_a,
                              "skimmer_feed_delay_b": AppPrefs.outletDict[outlet].skimmer_feed_delay_b,
                              "skimmer_feed_delay_c": AppPrefs.outletDict[outlet].skimmer_feed_delay_c,
                              "skimmer_feed_delay_d": AppPrefs.outletDict[outlet].skimmer_feed_delay_d,

                              "enabled": AppPrefs.outletDict[outlet].enabled,

                              }

    if len(outletdict) < 8:
        return "Error getting list"
    else:
        return outletdict


#####################################################################
# api_get_column_widget_order
# get the widget order of the column tables
#####################################################################


def api_get_column_widget_order(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)
    # build table object from table in DB
    metadata_obj = MetaData()

    dashtable = Table("dashorder", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    # get column 1 order
    stmt = select(dashtable).where(
        dashtable.c.appuid == AppPrefs.appuid).where(dashtable.c.column == 1).order_by(dashtable.c.order)
    row_headers = conn.execute(stmt).keys()
    # AppPrefs.logger.info(row_headers)
    myresult = conn.execute(stmt)
    conn.commit()

    col1_data = []

    for row in myresult:
        col1_data.append(row.widgetid)

    AppPrefs.logger.info("Getting widget order for column 1")
    AppPrefs.logger.info(col1_data)

    # get column 2 order
    stmt = select(dashtable).where(
        dashtable.c.appuid == AppPrefs.appuid).where(dashtable.c.column == 2).order_by(dashtable.c.order)
    row_headers = conn.execute(stmt).keys()
    # AppPrefs.logger.info(row_headers)
    myresult = conn.execute(stmt)
    conn.commit()

    col2_data = []

    for row in myresult:
        col2_data.append(row.widgetid)

    AppPrefs.logger.info("Getting widget order for column 2")
    AppPrefs.logger.info(col2_data)

    # get column 3 order
    stmt = select(dashtable).where(
        dashtable.c.appuid == AppPrefs.appuid).where(dashtable.c.column == 3).order_by(dashtable.c.order)
    row_headers = conn.execute(stmt).keys()
    # AppPrefs.logger.info(row_headers)
    myresult = conn.execute(stmt)
    conn.commit()

    col3_data = []

    for row in myresult:
        col3_data.append(row.widgetid)

    AppPrefs.logger.info("Getting widget order for column 3")
    AppPrefs.logger.info(col3_data)

    return col1_data, col2_data, col3_data

#####################################################################
# api_set_column_widget_order
# save the widget order to the column tables
#####################################################################


def api_set_column_widget_order(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    ColumnItems1 = str(request.json.get(
        "column1", ""))
    ColumnItems2 = str(request.json.get(
        "column2", ""))
    ColumnItems3 = str(request.json.get(
        "column3", ""))

    metadata_obj = MetaData()

    dashtable = Table("dashorder", metadata_obj, autoload_with=sqlengine)

    ColumnItems1 = ColumnItems1.replace("[", "")
    ColumnItems1 = ColumnItems1.replace("]", "")
    ColumnItems1 = ColumnItems1.replace("'", "")
    ColumnItems1 = ColumnItems1.replace(" ", "")

    ColumnItems2 = ColumnItems2.replace("[", "")
    ColumnItems2 = ColumnItems2.replace("]", "")
    ColumnItems2 = ColumnItems2.replace("'", "")
    ColumnItems2 = ColumnItems2.replace(" ", "")

    ColumnItems3 = ColumnItems3.replace("[", "")
    ColumnItems3 = ColumnItems3.replace("]", "")
    ColumnItems3 = ColumnItems3.replace("'", "")
    ColumnItems3 = ColumnItems3.replace(" ", "")

    items1List = ColumnItems1.split(",")
    items2List = ColumnItems2.split(",")
    items3List = ColumnItems3.split(",")

    with sqlengine.connect() as conn:
        if items1List[0] != "":
            AppPrefs.logger.info("Saving Column 1 widget order")
            AppPrefs.logger.info(items1List)
            i = 0
            for widget in items1List:
                i = i + 1
                stmt = (update(dashtable).where(dashtable.c.appuid == AppPrefs.appuid, dashtable.c.widgetid == widget)
                        .values(
                    column=1, order=i))

                result = conn.execute(stmt)

        if items2List[0] != "":
            AppPrefs.logger.info("Saving Column 2 widget order")
            AppPrefs.logger.info(items2List)
            i = 0
            for widget in items2List:
                i = i + 1
                stmt = (update(dashtable).where(dashtable.c.appuid == AppPrefs.appuid, dashtable.c.widgetid == widget)
                        .values(
                    column=2, order=i))

                result = conn.execute(stmt)

        if items3List[0] != "":
            AppPrefs.logger.info("Saving Column 3 widget order")
            AppPrefs.logger.info(items3List)
            i = 0
            for widget in items3List:
                i = i + 1
                stmt = (update(dashtable).where(dashtable.c.appuid == AppPrefs.appuid, dashtable.c.widgetid == widget)
                        .values(
                    column=3, order=i))

                result = conn.execute(stmt)

        conn.commit()

    return

#####################################################################
# api_set_feed_mode
# to start a feed mode.  Must specify Feed mode A, B, C, D or Cancel
#####################################################################


def api_set_feed_mode(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    value = str(request.json.get(
        "feedmode", "CANCEL"))

    AppPrefs.logger.info("Set feed mode: " + value)
    AppPrefs.feed_CurrentMode = value
    AppPrefs.feed_SamplingTimeSeed = int(
        round(time.time()*1000))  # convert time to milliseconds
    AppPrefs.feed_PreviousMode = "CANCEL"

    return value

#####################################################################
# api_get_global_prefs/
# get the global paramters for the controller
# things like temperature scale, version, etc...
#####################################################################


def api_get_global_prefs(AppPrefs, sqlengine, request):
    # AppPrefs.logger.info(request)

    globalprefs = {}

    globalprefs = jsonify({"msg": 'Global preferences delivered',
                           "appuid": AppPrefs.appuid,
                           "tempscale": AppPrefs.temperaturescale,
                           "dht_enable": AppPrefs.dht_enable,
                           "feed_CurrentMode": AppPrefs.feed_CurrentMode,
                           "feed_a_time": AppPrefs.feed_a_time,
                           "feed_b_time": AppPrefs.feed_b_time,
                           "feed_c_time": AppPrefs.feed_c_time,
                           "feed_d_time": AppPrefs.feed_d_time,
                           "controller_version": AppPrefs.controller_version,
                           })

    return globalprefs

#####################################################################
# api_get_chartdata_24hr
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################


def api_get_chartdata_24hr(AppPrefs, Influx_client, probeid, unit, request):
    AppPrefs.logger.info(request)
    if unit == "temperature":
        if AppPrefs.temperaturescale == "F":
            unit = "temperature_f"
        else:
            unit = "temperature_c"

    bucket = "reefberrypi_probe_1dy"

    query_api = Influx_client.query_api()

    query = f'from(bucket: "reefberrypi_probe_1dy") \
    |> range(start: -24h) \
    |> filter(fn: (r) => r["_measurement"] == "{unit}") \
    |> filter(fn: (r) => r["_field"] == "value") \
    |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
    |> filter(fn: (r) => r["probeid"] == "{probeid}") \
    |> aggregateWindow(every: 10m, fn: mean, createEmpty: false) \
    |> yield(name: "mean")'

    result = query_api.query(org=AppPrefs.influxdb_org, query=query)

    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_time(), record.get_value()))

    return results

#####################################################################
# api_get_chartdata_1hr
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################


def api_get_chartdata_1hr(AppPrefs, Influx_client, probeid, unit, request):
    AppPrefs.logger.info(request)

    if unit == "temperature":
        if AppPrefs.temperaturescale == "F":
            unit = "temperature_f"
        else:
            unit = "temperature_c"

    bucket = "reefberrypi_probe_1hr"

    query_api = Influx_client.query_api()

    query = f'from(bucket: "reefberrypi_probe_1hr") \
    |> range(start: -1h) \
    |> filter(fn: (r) => r["_measurement"] == "{unit}") \
    |> filter(fn: (r) => r["_field"] == "value") \
    |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
    |> filter(fn: (r) => r["probeid"] == "{probeid}") \
    |> aggregateWindow(every: 30s, fn: mean, createEmpty: false) \
    |> yield(name: "mean")'

    result = query_api.query(org=AppPrefs.influxdb_org, query=query)

    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_time(), record.get_value()))

    return results

#####################################################################
# api_get_chartdata_1wk
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################


def api_get_chartdata_1wk(AppPrefs, Influx_client, probeid, unit, request):
    AppPrefs.logger.info(request)

    if unit == "temperature":
        if AppPrefs.temperaturescale == "F":
            unit = "temperature_f"
        else:
            unit = "temperature_c"

    bucket = "reefberrypi_probe_1wk"

    query_api = Influx_client.query_api()

    query = f'from(bucket: "reefberrypi_probe_1wk") \
    |> range(start: -7d) \
    |> filter(fn: (r) => r["_measurement"] == "{unit}") \
    |> filter(fn: (r) => r["_field"] == "value") \
    |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
    |> filter(fn: (r) => r["probeid"] == "{probeid}") \
    |> aggregateWindow(every: 15m, fn: mean, createEmpty: false) \
    |> yield(name: "mean")'

    result = query_api.query(org=AppPrefs.influxdb_org, query=query)

    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_time(), record.get_value()))

    return results


#####################################################################
# api_get_chartdata_1mo
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################


def api_get_chartdata_1mo(AppPrefs, Influx_client, probeid, unit, request):
    AppPrefs.logger.info(request)

    if unit == "temperature":
        if AppPrefs.temperaturescale == "F":
            unit = "temperature_f"
        else:
            unit = "temperature_c"

    bucket = "reefberrypi_probe_1wk"

    query_api = Influx_client.query_api()

    query = f'from(bucket: "reefberrypi_probe_1mo") \
    |> range(start: -30d) \
    |> filter(fn: (r) => r["_measurement"] == "{unit}") \
    |> filter(fn: (r) => r["_field"] == "value") \
    |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
    |> filter(fn: (r) => r["probeid"] == "{probeid}") \
    |> aggregateWindow(every: 1h, fn: mean, createEmpty: false) \
    |> yield(name: "mean")'

    result = query_api.query(org=AppPrefs.influxdb_org, query=query)

    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_time(), record.get_value()))

    return results

#####################################################################
# api_put_outlet_buttonstate
# change the value of button state
# must specify outlet ID and either ON, OFF, or AUTO
#####################################################################

def api_put_outlet_buttonstate(AppPrefs, sqlengine, outletid, buttonstate, request):
    AppPrefs.logger.info(request)


    # build table object from table in DB
    metadata_obj = MetaData()

    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == outletid)
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(button_state=buttonstate)
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)
    AppPrefs.outletDict[outletid].button_state = buttonstate
    AppPrefs.outletDict[outletid].outletstatus = buttonstate

    response = {}
    response = jsonify({"msg": 'Set outlet button state',
                        "appuid": AppPrefs.appuid,
                        "outletid": outletid,
                        "buttonstate": buttonstate
                        })

    response.status_code = 200

    return response

#####################################################################
# api_set_probe_name
# set the name of the probe
# must specify ProbeID and Name
#####################################################################
def api_set_probe_name(AppPrefs, sqlengine, probeid, probename, request):
    AppPrefs.logger.info(request)


    # build table object from table in DB
    metadata_obj = MetaData()
    probe_table = Table("probes", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == probeid)
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(name=probename)
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readTempProbes_ex(sqlengine, AppPrefs, AppPrefs.logger)
    defs_mysql.readDHTSensor_ex(sqlengine, AppPrefs, AppPrefs.logger)
    defs_mysql.readMCP3008Prefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    response = {}
    response = jsonify({"msg": 'Updated probe name',
                        "probeid": probeid,
                        "probename": probename,
                        })

    response.status_code = 200
    return response

#####################################################################
# api_set_probe_enable_state
# set the enable state of the probe
# must specify ProbeID and true or false
#####################################################################
def api_set_probe_enable_state(AppPrefs, sqlengine, probeid, enable, request):
    AppPrefs.logger.info(request)

    # build table object from table in DB
    metadata_obj = MetaData()
    probe_table = Table("probes", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == probeid)
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(enabled=enable)
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readTempProbes_ex(sqlengine, AppPrefs, AppPrefs.logger)
    defs_mysql.readDHTSensor_ex(sqlengine, AppPrefs, AppPrefs.logger)
    defs_mysql.readMCP3008Prefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    response = {}
    response = jsonify({"msg": 'Updated probe enabled state',
                        "probeid": probeid,
                        "enabled": enable,
                        })

    response.status_code = 200
    return response

#####################################################################
# api_set_mcp3008_enable_state
# set the enable state of the probe
# must specify ProbeID and true or false
#####################################################################
def api_set_mcp3008_enable_state(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    ch0_enable = str(request.json.get(
        "adc_enable_channel_0", None)).lower()
    ch1_enable = str(request.json.get(
        "adc_enable_channel_1", None)).lower()
    ch2_enable = str(request.json.get(
        "adc_enable_channel_2", None)).lower()
    ch3_enable = str(request.json.get(
        "adc_enable_channel_3", None)).lower()
    ch4_enable = str(request.json.get(
        "adc_enable_channel_4", None)).lower()
    ch5_enable = str(request.json.get(
        "adc_enable_channel_5", None)).lower()
    ch6_enable = str(request.json.get(
        "adc_enable_channel_6", None)).lower()
    ch7_enable = str(request.json.get(
        "adc_enable_channel_7", None)).lower()

    
    # build table object from table in DB
    metadata_obj = MetaData()
    probe_table = Table("probes", metadata_obj, autoload_with=sqlengine)

    # channel 0
    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == "mcp3008_ch0")
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(enabled=ch0_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # channel 1
    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == "mcp3008_ch1")
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(enabled=ch1_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # channel 2
    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == "mcp3008_ch2")
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(enabled=ch2_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # channel 3
    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == "mcp3008_ch3")
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(enabled=ch3_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # channel 4
    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == "mcp3008_ch4")
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(enabled=ch4_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # channel 5
    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == "mcp3008_ch5")
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(enabled=ch5_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # channel 6
    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == "mcp3008_ch6")
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(enabled=ch6_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # channel 7
    stmt = (
        update(probe_table)
        .where(probe_table.c.probeid == "mcp3008_ch7")
        .where(probe_table.c.appuid == AppPrefs.appuid)
        .values(enabled=ch7_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # defs_mysql.readTempProbes_ex(sqlengine, AppPrefs, logger)
    # defs_mysql.readDHTSensor_ex(sqlengine, AppPrefs, logger)
    defs_mysql.readMCP3008Prefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    response = {}
    response = jsonify({"msg": 'Updated mcp3008 enabled state',
                        })

    response.status_code = 200
    return response

#####################################################################
# api_set_outlet_enable_state
# set the enable state of the outlet
# must specify ProbeID and true or false
#####################################################################
def api_set_outlet_enable_state(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    int_outlet_1_enable = str(request.json.get(
        "enable_int_outlet_1", None)).lower()
    int_outlet_2_enable = str(request.json.get(
        "enable_int_outlet_2", None)).lower()
    int_outlet_3_enable = str(request.json.get(
        "enable_int_outlet_3", None)).lower()
    int_outlet_4_enable = str(request.json.get(
        "enable_int_outlet_4", None)).lower()
    int_outlet_5_enable = str(request.json.get(
        "enable_int_outlet_5", None)).lower()
    int_outlet_6_enable = str(request.json.get(
        "enable_int_outlet_6", None)).lower()
    int_outlet_7_enable = str(request.json.get(
        "enable_int_outlet_7", None)).lower()
    int_outlet_8_enable = str(request.json.get(
        "enable_int_outlet_8", None)).lower()

    
    # build table object from table in DB
    metadata_obj = MetaData()
    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    # outlet 1
    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == "int_outlet_1")
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(enabled=int_outlet_1_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # outlet 2
    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == "int_outlet_2")
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(enabled=int_outlet_2_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # outlet 3
    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == "int_outlet_3")
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(enabled=int_outlet_3_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # outlet 4
    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == "int_outlet_4")
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(enabled=int_outlet_4_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # outlet 5
    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == "int_outlet_5")
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(enabled=int_outlet_5_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # outlet 6
    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == "int_outlet_6")
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(enabled=int_outlet_6_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # outlet 7
    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == "int_outlet_7")
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(enabled=int_outlet_7_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    # outlet 8
    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == "int_outlet_8")
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(enabled=int_outlet_8_enable)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    response = {}
    response = jsonify({"msg": 'Updated outlet enabled state',
                        })

    response.status_code = 200
    return response

#####################################################################
# api_set_outlet_params_light/<outletid>
# set the paramters for outlet of type: Light
# must specify outletid and deliver payload in json
#####################################################################
def api_set_outlet_params_light(AppPrefs, sqlengine, outletid, request):
    AppPrefs.logger.info(request)

    response = {}
    payload = request.get_json()
    print(payload)
    light_on = payload["light_on"]
    light_off = payload["light_off"]
    outletname = payload["outletname"]
    control_type = payload["control_type"]

    response = jsonify({"msg": 'Updated outlet data for type: Light',
                        "outletid": outletid,
                        "outletname": outletname,
                        "control_type": control_type,
                        "light_on": light_on,
                        "light_off": light_off,
                        })

    response.status_code = 200

    # build table object from table in DB
    metadata_obj = MetaData()
    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == outletid)
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(outletname=outletname, light_on=light_on, light_off=light_off, control_type=control_type)
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    return response