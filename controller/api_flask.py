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
from flask_jwt_extended import create_access_token
import bcrypt


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
                           "app_description": AppPrefs.app_description,
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
# api_set_outlet_buttonstate
# change the value of button state
# must specify outlet ID and either ON, OFF, or AUTO
#####################################################################


def api_set_outlet_buttonstate(AppPrefs, sqlengine, outletid, buttonstate, request):
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

# #####################################################################
# # api_set_probe_enable_state
# # set the enable state of the probe
# # must specify ProbeID and true or false
# #####################################################################
# def api_set_probe_enable_state(AppPrefs, sqlengine, probeid, enable, request):
#     AppPrefs.logger.info(request)

#     # build table object from table in DB
#     metadata_obj = MetaData()
#     probe_table = Table("probes", metadata_obj, autoload_with=sqlengine)

#     stmt = (
#         update(probe_table)
#         .where(probe_table.c.probeid == probeid)
#         .where(probe_table.c.appuid == AppPrefs.appuid)
#         .values(enabled=enable)
#     )

#     with sqlengine.connect() as conn:
#         result = conn.execute(stmt)
#         conn.commit()

#     defs_mysql.readTempProbes_ex(sqlengine, AppPrefs, AppPrefs.logger)
#     defs_mysql.readDHTSensor_ex(sqlengine, AppPrefs, AppPrefs.logger)
#     defs_mysql.readMCP3008Prefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

#     response = {}
#     response = jsonify({"msg": 'Updated probe enabled state',
#                         "probeid": probeid,
#                         "enabled": enable,
#                         })

#     response.status_code = 200
#     return response

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

#####################################################################
# api_set_outlet_params_always/<outletid>
# set the paramters for outlet of type: Always
# must specify outletid and deliver payload in json
#####################################################################


def api_set_outlet_params_always(AppPrefs, sqlengine, outletid, request):
    AppPrefs.logger.info(request)

    response = {}
    payload = request.get_json()
    print(payload)
    always_state = payload["always_state"]
    outletname = payload["outletname"]
    control_type = payload["control_type"]

    response = jsonify({"msg": 'Updated outlet data for type: Always',
                        "outletid": outletid,
                        "outletname": outletname,
                        "control_type": control_type,
                        "always_state": always_state,
                        })

    response.status_code = 200

    # build table object from table in DB
    metadata_obj = MetaData()
    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == outletid)
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(outletname=outletname, always_state=always_state, control_type=control_type)
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    return response

#####################################################################
# api_set_outlet_params_heater/<outletid>
# set the paramters for outlet of type: Heater
# must specify outletid and deliver payload in json
#####################################################################


def api_set_outlet_params_heater(AppPrefs, sqlengine, outletid, request):
    AppPrefs.logger.info(request)

    response = {}
    payload = request.get_json()
    print(payload)
    heater_on = payload["heater_on"]
    heater_off = payload["heater_off"]
    heater_probe = payload["heater_probe"]
    outletname = payload["outletname"]
    control_type = payload["control_type"]

    if AppPrefs.temperaturescale == "F":
        heater_on = defs_common.convertFtoC(heater_on)
        heater_off = defs_common.convertFtoC(heater_off)

    response = jsonify({"msg": 'Updated outlet data for type: Heater',
                        "outletid": outletid,
                        "outletname": outletname,
                        "control_type": control_type,
                        "heater_on": heater_on,
                        "heater_off": heater_off,
                        "heater_probe": heater_probe,
                        })

    response.status_code = 200

    # build table object from table in DB
    metadata_obj = MetaData()
    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == outletid)
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(outletname=outletname, heater_on=heater_on, heater_off=heater_off, heater_probe=heater_probe, control_type=control_type)
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    return response

#####################################################################
# api_set_outlet_params_ph/<outletid>
# set the paramters for outlet of type: PH
# must specify outletid and deliver payload in json
#####################################################################


def api_set_outlet_params_ph(AppPrefs, sqlengine, outletid, request):
    AppPrefs.logger.info(request)

    response = {}
    payload = request.get_json()
    ph_low = payload["ph_low"]
    ph_high = payload["ph_high"]
    ph_probe = payload["ph_probe"]
    ph_onwhen = payload["ph_onwhen"]
    outletname = payload["outletname"]
    control_type = payload["control_type"]

    response = jsonify({"msg": 'Updated outlet data for type: PH',
                        "outletid": outletid,
                        "outletname": outletname,
                        "control_type": control_type,
                        "ph_low": ph_low,
                        "ph_high": ph_high,
                        "ph_onwhen": ph_onwhen,
                        "ph_probe": ph_probe,
                        })

    response.status_code = 200

    # build table object from table in DB
    metadata_obj = MetaData()
    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == outletid)
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(outletname=outletname, ph_low=ph_low, ph_high=ph_high, ph_onwhen=ph_onwhen, ph_probe=ph_probe, control_type=control_type)
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    return response

#####################################################################
# api_set_outlet_params_return/<outletid>
# set the paramters for outlet of type: Return
# must specify outletid and deliver payload in json
#####################################################################


def api_set_outlet_params_return(AppPrefs, sqlengine, outletid, request):
    AppPrefs.logger.info(request)

    response = {}
    payload = request.get_json()

    return_enable_feed_a = payload["return_enable_feed_a"]
    return_enable_feed_b = payload["return_enable_feed_b"]
    return_enable_feed_c = payload["return_enable_feed_c"]
    return_enable_feed_d = payload["return_enable_feed_d"]
    return_feed_delay_a = payload["return_feed_delay_a"]
    return_feed_delay_b = payload["return_feed_delay_b"]
    return_feed_delay_c = payload["return_feed_delay_c"]
    return_feed_delay_d = payload["return_feed_delay_d"]
    outletname = payload["outletname"]
    control_type = payload["control_type"]

    response = jsonify({"msg": 'Updated outlet data for type: Return',
                        "outletid": outletid,
                        "outletname": outletname,
                        "control_type": control_type,
                        "return_enable_feed_a": return_enable_feed_a,
                        "return_enable_feed_b": return_enable_feed_b,
                        "return_enable_feed_c": return_enable_feed_c,
                        "return_enable_feed_d": return_enable_feed_d,
                        "return_feed_delay_a": return_feed_delay_a,
                        "return_feed_delay_b": return_feed_delay_b,
                        "return_feed_delay_c": return_feed_delay_c,
                        "return_feed_delay_d": return_feed_delay_d,
                        })

    response.status_code = 200

    # build table object from table in DB
    metadata_obj = MetaData()
    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == outletid)
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(outletname=outletname,
                control_type=control_type,
                return_enable_feed_a=return_enable_feed_a,
                return_enable_feed_b=return_enable_feed_b,
                return_enable_feed_c=return_enable_feed_c,
                return_enable_feed_d=return_enable_feed_d,
                return_feed_delay_a=return_feed_delay_a,
                return_feed_delay_b=return_feed_delay_b,
                return_feed_delay_c=return_feed_delay_c,
                return_feed_delay_d=return_feed_delay_d,
                )
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    return response

#####################################################################
# api_set_outlet_params_skimmer/<outletid>
# set the paramters for outlet of type: Skimmer
# must specify outletid and deliver payload in json
#####################################################################


def api_set_outlet_params_skimmer(AppPrefs, sqlengine, outletid, request):
    AppPrefs.logger.info(request)

    response = {}
    payload = request.get_json()

    skimmer_enable_feed_a = payload["skimmer_enable_feed_a"]
    skimmer_enable_feed_b = payload["skimmer_enable_feed_b"]
    skimmer_enable_feed_c = payload["skimmer_enable_feed_c"]
    skimmer_enable_feed_d = payload["skimmer_enable_feed_d"]
    skimmer_feed_delay_a = payload["skimmer_feed_delay_a"]
    skimmer_feed_delay_b = payload["skimmer_feed_delay_b"]
    skimmer_feed_delay_c = payload["skimmer_feed_delay_c"]
    skimmer_feed_delay_d = payload["skimmer_feed_delay_d"]
    outletname = payload["outletname"]
    control_type = payload["control_type"]

    response = jsonify({"msg": 'Updated outlet data for type: Skimmer',
                        "outletid": outletid,
                        "outletname": outletname,
                        "control_type": control_type,
                        "skimmer_enable_feed_a": skimmer_enable_feed_a,
                        "skimmer_enable_feed_b": skimmer_enable_feed_b,
                        "skimmer_enable_feed_c": skimmer_enable_feed_c,
                        "skimmer_enable_feed_d": skimmer_enable_feed_d,
                        "skimmer_feed_delay_a": skimmer_feed_delay_a,
                        "skimmer_feed_delay_b": skimmer_feed_delay_b,
                        "skimmer_feed_delay_c": skimmer_feed_delay_c,
                        "skimmer_feed_delay_d": skimmer_feed_delay_d,
                        })

    response.status_code = 200

    # build table object from table in DB
    metadata_obj = MetaData()
    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid == outletid)
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(outletname=outletname,
                control_type=control_type,
                skimmer_enable_feed_a=skimmer_enable_feed_a,
                skimmer_enable_feed_b=skimmer_enable_feed_b,
                skimmer_enable_feed_c=skimmer_enable_feed_c,
                skimmer_enable_feed_d=skimmer_enable_feed_d,
                skimmer_feed_delay_a=skimmer_feed_delay_a,
                skimmer_feed_delay_b=skimmer_feed_delay_b,
                skimmer_feed_delay_c=skimmer_feed_delay_c,
                skimmer_feed_delay_d=skimmer_feed_delay_d,
                )
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    return response

#####################################################################
# api_set_global_prefs/
# set the global parameters such as temps scale C or F
# must specify outletid and deliver payload in json
#####################################################################


def api_set_global_prefs(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    response = {}
    payload = request.get_json()
    print(payload)
    tempscale = payload["tempscale"]
    dht_enable = payload["dht_enable"]
    feed_a_time = payload["feed_a_time"]
    feed_b_time = payload["feed_b_time"]
    feed_c_time = payload["feed_c_time"]
    feed_d_time = payload["feed_d_time"]
    description = payload["description"]

    response = jsonify({"msg": 'Updated Global Prefs',
                        "tempscale": tempscale,
                        "dht_enable": dht_enable,
                        "feed_a_time": feed_a_time,
                        "feed_b_time": feed_b_time,
                        "feed_c_time": feed_c_time,
                        "feed_d_time": feed_d_time,
                        "description": description
                        })

    response.status_code = 200

    # build table object from table in DB
    metadata_obj = MetaData()
    global_table = Table("global", metadata_obj, autoload_with=sqlengine)

    stmt = (
        update(global_table)
        .where(global_table.c.appuid == AppPrefs.appuid)
        .values(tempscale=tempscale,
                dht_enable=dht_enable,
                feed_a_time=feed_a_time,
                feed_b_time=feed_b_time,
                feed_c_time=feed_c_time,
                feed_d_time=feed_d_time,
                description=description
                )
    )

    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    defs_mysql.readGlobalPrefs_ex(sqlengine, AppPrefs, AppPrefs.logger)

    return response

#####################################################################
# api_get_current_probe_stats/
# get the stats for the specified probe
# things like last value, probe name, etc....
#####################################################################


def api_get_current_probe_stats(AppPrefs, probeid, request):
    # AppPrefs.logger.info(request)

    response = {}

    if probeid.startswith("temp_probe_"):
        response = jsonify({"msg": 'Current probe stats',
                            "appuid": AppPrefs.appuid,
                            "probename": AppPrefs.tempProbeDict[probeid].name,
                            "probeid": AppPrefs.tempProbeDict[probeid].probeid,
                            "lastValue": AppPrefs.tempProbeDict[probeid].lastTemperature,
                            "sensortype": "temperature",
                            "probetype": "ds18b20",
                            })

        response.status_code = 200

    elif probeid.startswith("DHT"):
        response = jsonify({"msg": 'Current probe stats',
                            "appuid": AppPrefs.appuid,
                            "sensortype": AppPrefs.dhtDict[probeid].sensortype,
                            "probename": AppPrefs.dhtDict[probeid].name,
                            "probeid": AppPrefs.dhtDict[probeid].probeid,
                            "probetype": "DHT",
                            "lastValue": AppPrefs.dhtDict[probeid].lastValue})

        response.status_code = 200

    elif probeid.startswith("mcp3008"):
        response = jsonify({"msg": 'Current probe stats',
                            "appuid": AppPrefs.appuid,
                            "sensortype": AppPrefs.mcp3008Dict[probeid[-1]].ch_type,
                            "probename": AppPrefs.mcp3008Dict[probeid[-1]].ch_name,
                            "probeid": probeid,
                            "probetype": "analog",
                            "lastValue": AppPrefs.mcp3008Dict[probeid[-1]].lastValue})

        response.status_code = 200

    return response

#####################################################################
# api_get_outlet_enable_state
# return list of outlets with their enabled state
#####################################################################


def api_get_outlet_enable_state(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    outletdict = {}
    response = {}

    # build table object from table in DB
    metadata_obj = MetaData()

    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(outlet_table).where(
        outlet_table.c.appuid == AppPrefs.appuid)

    results = conn.execute(stmt)
    conn.commit()

    # loop through each row
    for row in results:
        outletdict[row.outletid] = {"outletname": row.outletname,
                                    "outletid": row.outletid,
                                    "enabled": row.enabled, }

    AppPrefs.logger.debug(outletdict)

    return outletdict

#####################################################################
# api_get_outletchartdata
# return array of chart data with date/time and values
# must specify outletID, and time frame (24hr, 1wk, 1mo, etc...)
#####################################################################


def api_get_outletchartdata(AppPrefs, Influx_client, outletid, timeframe, request):
    AppPrefs.logger.info(request)

    bucket = "reefberrypi_outlet_3mo"

    query_api = Influx_client.query_api()

    query = f'from(bucket: "reefberrypi_outlet_3mo") \
    |> range(start: -{timeframe}) \
    |> filter(fn: (r) => r["_measurement"] == "outlet_state") \
    |> filter(fn: (r) => r["_field"] == "value") \
    |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
    |> filter(fn: (r) => r["outletid"] == "{outletid}") \
    |> yield(name: "last")'

    result = query_api.query(org=AppPrefs.influxdb_org, query=query)

    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_time(), record.get_value()))

    return results

#####################################################################
# api_get_current_outlet_stats/
# get the stats for the specified outlet
# things like last button state, status, etc....
#####################################################################


def api_get_current_outlet_stats(AppPrefs, outletid, request):
    # AppPrefs.logger.info(request)

    response = {}

    # convert temperature values to F if using Fahrenheit
    if AppPrefs.temperaturescale == "F":
        heater_on_x = defs_common.convertCtoF(
            AppPrefs.outletDict[outletid].heater_on)
        heater_off_x = defs_common.convertCtoF(
            AppPrefs.outletDict[outletid].heater_off)
    else:
        heater_on_x = AppPrefs.outletDict[outletid].heater_on
        heater_off_x = AppPrefs.outletDict[outletid].heater_off

    response = jsonify({"msg": 'Current outlet stats',
                        "appuid": AppPrefs.appuid,
                        "outletid": AppPrefs.outletDict[outletid].outletid,
                        "outletname": AppPrefs.outletDict[outletid].outletname,
                        "control_type": AppPrefs.outletDict[outletid].control_type,
                        "outletstatus": AppPrefs.outletDict[outletid].outletstatus,
                        "button_state": AppPrefs.outletDict[outletid].button_state,
                        "heater_on": heater_on_x,
                        "heater_off": heater_off_x,
                        "heater_probe": AppPrefs.outletDict[outletid].heater_probe,
                        "light_on": AppPrefs.outletDict[outletid].light_on,
                        "light_off": AppPrefs.outletDict[outletid].light_off,
                        "always_state": AppPrefs.outletDict[outletid].always_state,
                        "return_enable_feed_a": (AppPrefs.outletDict[outletid].return_enable_feed_a).lower() == "true",
                        "return_enable_feed_b": (AppPrefs.outletDict[outletid].return_enable_feed_b).lower() == "true",
                        "return_enable_feed_c": (AppPrefs.outletDict[outletid].return_enable_feed_c).lower() == "true",
                        "return_enable_feed_d": (AppPrefs.outletDict[outletid].return_enable_feed_d).lower() == "true",
                        "return_feed_delay_a": AppPrefs.outletDict[outletid].return_feed_delay_a,
                        "return_feed_delay_b": AppPrefs.outletDict[outletid].return_feed_delay_b,
                        "return_feed_delay_c": AppPrefs.outletDict[outletid].return_feed_delay_c,
                        "return_feed_delay_d": AppPrefs.outletDict[outletid].return_feed_delay_d,

                        "skimmer_enable_feed_a": (AppPrefs.outletDict[outletid].skimmer_enable_feed_a).lower() == "true",
                        "skimmer_enable_feed_b": (AppPrefs.outletDict[outletid].skimmer_enable_feed_b).lower() == "true",
                        "skimmer_enable_feed_c": (AppPrefs.outletDict[outletid].skimmer_enable_feed_c).lower() == "true",
                        "skimmer_enable_feed_d": (AppPrefs.outletDict[outletid].skimmer_enable_feed_d).lower() == "true",
                        "skimmer_feed_delay_a": AppPrefs.outletDict[outletid].skimmer_feed_delay_a,
                        "skimmer_feed_delay_b": AppPrefs.outletDict[outletid].skimmer_feed_delay_b,
                        "skimmer_feed_delay_c": AppPrefs.outletDict[outletid].skimmer_feed_delay_c,
                        "skimmer_feed_delay_d": AppPrefs.outletDict[outletid].skimmer_feed_delay_d,

                        "ph_probe": AppPrefs.outletDict[outletid].ph_probe,
                        "ph_low": AppPrefs.outletDict[outletid].ph_low,
                        "ph_high": AppPrefs.outletDict[outletid].ph_high,
                        "ph_onwhen": AppPrefs.outletDict[outletid].ph_onwhen,
                        })

    response.status_code = 200

    return response

#####################################################################
# api_get_probe_list
# return list of connected probes
#####################################################################


def api_get_probe_list(AppPrefs, request):
    AppPrefs.logger.info(request)

    probedict = {}

    # loop through each section
    for probe in AppPrefs.tempProbeDict:
        probedict[probe] = {"probetype": "ds18b20",
                            "probeid": AppPrefs.tempProbeDict[probe].probeid,
                            "probename": AppPrefs.tempProbeDict[probe].name,
                            "sensortype": "temperature",
                            "lastValue": AppPrefs.tempProbeDict[probe].lastTemperature}

    if AppPrefs.dht_enable == "true":
        probedict["DHT-T"] = {"sensortype": AppPrefs.dhtDict["DHT-T"].sensortype,
                              "probename": AppPrefs.dhtDict["DHT-T"].name,
                              "probeid": AppPrefs.dhtDict["DHT-T"].probeid,
                              "probetype": "DHT",
                              "lastValue": AppPrefs.dhtDict["DHT-T"].lastValue}
        probedict["DHT-H"] = {"sensortype": AppPrefs.dhtDict["DHT-H"].sensortype,
                              "probename": AppPrefs.dhtDict["DHT-H"].name,
                              "probeid": AppPrefs.dhtDict["DHT-H"].probeid,
                              "probetype": "DHT",
                              "lastValue": AppPrefs.dhtDict["DHT-H"].lastValue}
    for ch in AppPrefs.mcp3008Dict:
        # logger.info(ch)
        probedict["mcp3008_ch" + str(ch)] = {"sensortype": AppPrefs.mcp3008Dict[ch].ch_type,
                                             "probename": AppPrefs.mcp3008Dict[ch].ch_name,
                                             "probeid": "mcp3008_ch" + str(ch),
                                             "probetype": "analog",
                                             "lastValue": AppPrefs.mcp3008Dict[ch].lastValue}

    AppPrefs.logger.debug(probedict)
    return probedict

#####################################################################
# api_get_mcp3008_enable_state
# return list of mcp3008 probes and their enabled state
#####################################################################


def api_get_mcp3008_enable_state(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    probedict = {}
    response = {}

    # build table object from table in DB
    metadata_obj = MetaData()

    probe_table = Table("probes", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(probe_table).where(probe_table.c.appuid == AppPrefs.appuid).where(
        probe_table.c.probetype == "analog")

    results = conn.execute(stmt)
    conn.commit()

    # loop through each row
    for row in results:
        probedict[row.probeid] = {"sensortype": row.sensortype,
                                  "probename": row.name,
                                  "probeid": row.probeid,
                                  "probetype": row.probetype,
                                  "enabled": row.enabled,
                                  "sensortype": row.sensortype}

    AppPrefs.logger.debug(probedict)

    return probedict

#####################################################################
# api_get_token
# return login token
#####################################################################


def api_get_token(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    username = request.json.get("username", None).lower()
    password = request.json.get("password", None)

    response = {}

    # build table object from table in DB
    metadata_obj = MetaData()

    user_table = Table("users", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(user_table).where(user_table.c.appuid == AppPrefs.appuid).where(
        user_table.c.username == username)

    results = conn.execute(stmt)
    conn.commit()

    if results.rowcount == 0:
        AppPrefs.logger.warning("Invalid login attempt!  User: " + username)
        return {"msg": "Wrong username or password"}, 401

    else:
        # loop through each row
        for row in results:
            # dbusername = row.username
            dbhash = row.pwhash

            userPW = password
            userBytes = userPW.encode('utf-8')

            result = bcrypt.checkpw(userBytes, dbhash.encode('utf-8'))

            if result == True:
                AppPrefs.logger.info("Sucessful login.  User: " + username)
                access_token = create_access_token(identity=username)
                response = {"token": access_token}

                return response
            else:
                return {"msg": "Wrong username or password"}, 401

#####################################################################
# api_get_user_list
# return list of users that have access to this instance
#####################################################################


def api_get_user_list(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    response = {}

    # build table object from table in DB
    metadata_obj = MetaData()

    user_table = Table("users", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(user_table).where(user_table.c.appuid == AppPrefs.appuid)

    results = conn.execute(stmt)
    conn.commit()

    userlist = []

    for row in results:
        AppPrefs.logger.info(row.username)
        userlist.append({"username": row.username, "role": row.role})

    response = jsonify({"appuid": AppPrefs.appuid,
                        "userlist": userlist}
                       )
    response.status_code = 200

    return response

#####################################################################
# api_set_add_user
# add new user to have access to this instance
#####################################################################


def api_set_add_user(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    username = request.json.get("username", None).lower()
    password = request.json.get("password", None)

    response = {}

    # build table object from table in DB
    metadata_obj = MetaData()

    user_table = Table("users", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    # before adding, check if username exists
    stmt = select(user_table).where(user_table.c.appuid == AppPrefs.appuid)
    results = conn.execute(stmt)
    conn.commit()
    for row in results:
        if row.username == username:
            response = jsonify({"appuid": AppPrefs.appuid,
                                "msg": "FAIL: User already exists"}
                               )
            response.status_code = 500
            AppPrefs.logger.error("Add user failed.  User already exists in database: " + username)
            return response

    # since user did not exist, lets add to the table

    # create password hash
    # converting password to array of bytes
    bytes = password.encode('utf-8')

    # generating the salt
    salt = bcrypt.gensalt()

    # Hashing the password
    hash = bcrypt.hashpw(bytes, salt)

    stmt = insert(user_table).values(appuid=AppPrefs.appuid,
                                     username=username,
                                     role="administrator",
                                     pwhash=hash
                                     )

    results = conn.execute(stmt)
    conn.commit()

    response = jsonify({"appuid": AppPrefs.appuid,
                        "msg": "SUCCESS"}
                       )
    response.status_code = 200

    return response

#####################################################################
# api_set_remove_user
# delete a user from this instance
#####################################################################


def api_set_remove_user(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    response = {}

    activeuser = request.json.get("activeuser", None)
    targetuser = request.json.get("targetuser", None)

    # return fail if missing parameter
    if activeuser == None or activeuser == "":
        response = jsonify({"appuid": AppPrefs.appuid,
                            "msg": "FAIL: missing parameter activeuser"}
                           )
        response.status_code = 500
        return response
    elif targetuser == None or targetuser == "":
        response = jsonify({"appuid": AppPrefs.appuid,
                            "msg": "FAIL: missing parameter targetuser"}
                           )
        response.status_code = 500
        return response

    # build table object from table in DB
    metadata_obj = MetaData()
    user_table = Table("users", metadata_obj, autoload_with=sqlengine)
    conn = sqlengine.connect()

    # don't let a user delete themself
    if activeuser.lower() == targetuser.lower():
        response = jsonify({"appuid": AppPrefs.appuid,
                            "msg": "FAIL: Users can not remove themselves"}
                           )
        response.status_code = 500
        return response

    # if all the other checks passed, lets remove the user from the table
    # before adding, check if username exists
    stmt = delete(user_table).where(user_table.c.appuid == AppPrefs.appuid).where(
        user_table.c.username == targetuser.lower())
    results = conn.execute(stmt)
    conn.commit()

    response = jsonify({"appuid": AppPrefs.appuid,
                        "msg": "SUCCESS"}
                       )
    response.status_code = 200

    AppPrefs.logger.info("User " + targetuser.lower() +
                         " deleted by " + activeuser.lower())

    return response

#####################################################################
# api_set_change_password
# change a user's password
#####################################################################


def api_set_change_password(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)

    username = request.json.get("username", None).lower()
    oldpassword = request.json.get("oldpassword", None)
    newpassword = request.json.get("newpassword", None)

    response = {}

    # build table object from table in DB
    metadata_obj = MetaData()

    user_table = Table("users", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    stmt = select(user_table).where(user_table.c.appuid == AppPrefs.appuid).where(
        user_table.c.username == username)

    results = conn.execute(stmt)
    conn.commit()

    if results.rowcount == 0:
        AppPrefs.logger.warning("Password change fail.  Invalid login attempt!  User: " + username)
        return {"msg": "Wrong username or password"}, 401

    else:
        # loop through each row
        for row in results:
            # dbusername = row.username
            dbhash = row.pwhash

            userPW = oldpassword
            userBytes = userPW.encode('utf-8')

            result = bcrypt.checkpw(userBytes, dbhash.encode('utf-8'))

            if result == True:
                bytes = newpassword.encode('utf-8')
                # generating the salt
                salt = bcrypt.gensalt()
                # Hashing the password
                hash = bcrypt.hashpw(bytes, salt)

                if newpassword == None or newpassword == "":
                    response = jsonify({"appuid": AppPrefs.appuid,
                                        "msg": "FAIL: password can not be empty"}
                                       )
                    AppPrefs.logger.warning("Password change failed. Password can not be empty")
                    response.status_code = 500
                    return response

                stmt = (
                    update(user_table)
                    .where(user_table.c.appuid == AppPrefs.appuid)
                    .where(user_table.c.username == username)
                    .values(pwhash=hash)
                )
                results = conn.execute(stmt)
                conn.commit()

                AppPrefs.logger.info(
                    "Password changed sucessfully for user: " + username)
                response = jsonify({"msg": "Password changed sucessfully!"})
                response.status_code = 200
                return response
            else:
                AppPrefs.logger.warning("Password change fail.  Incorrect password provided. User = " + username)
                response = jsonify(
                    {"msg": "Request denied.  Check credentials and try again."})
                response.status_code = 401
                return response

#####################################################################
# api_get_analog_cal_stats
# return stats that are used for calibration of an analog probe
# connected to tghe mcp3008 analog to digital converter
#####################################################################


def api_get_analog_cal_stats(AppPrefs, sqlengine, request, channelid):
    AppPrefs.logger.info(request)
    AppPrefs.logger.info("Got calibration request for analog channel: " + channelid)

    response = {}

    response = jsonify({"appuid": AppPrefs.appuid,
                        "channelid": channelid,
                        "meanvalue": AppPrefs.mcp3008Dict[channelid].ch_dvcalFilteredMean,
                        "std_deviation": AppPrefs.mcp3008Dict[channelid].ch_dvcalFilteredSD,
                        "datapoints": AppPrefs.mcp3008Dict[channelid].ch_dvcallist
                       })
    response.status_code = 200

    return response