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
