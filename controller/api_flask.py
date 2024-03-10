import glob
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy import insert
import defs_mysql


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
#####################################################################


def api_get_assigned_temp_probes(AppPrefs, sqlengine):
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

    col1_table = Table("dashcol1", metadata_obj, autoload_with=sqlengine)
    col2_table = Table("dashcol2", metadata_obj, autoload_with=sqlengine)
    col3_table = Table("dashcol3", metadata_obj, autoload_with=sqlengine)

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

    # delete existing entries
    # col1
    stmt = (
        delete(col1_table)
        .where(col1_table.c.appuid == AppPrefs.appuid)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    # col2
    stmt = (
        delete(col2_table)
        .where(col2_table.c.appuid == AppPrefs.appuid)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    # col3
    stmt = (
        delete(col3_table)
        .where(col3_table.c.appuid == AppPrefs.appuid)
    )
    with sqlengine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()

    if items1List[0] != "":
        AppPrefs.logger.info(items1List)
        for widget in items1List:
            stmt = (insert(col1_table).values(
                appuid=AppPrefs.appuid, widgetid=widget))
            with sqlengine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()

    if items2List[0] != "":
        AppPrefs.logger.info(items2List)
        for widget in items2List:
            stmt = (insert(col2_table).values(
                appuid=AppPrefs.appuid, widgetid=widget))
            with sqlengine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()

    if items3List[0] != "":
        AppPrefs.logger.info(items3List)
        for widget in items3List:
            stmt = (insert(col3_table).values(
                appuid=AppPrefs.appuid, widgetid=widget))
            with sqlengine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()

    return

#####################################################################
# api_get_column_widget_order
# get the widget order of the column tables
#####################################################################


def api_get_column_widget_order(AppPrefs, sqlengine, request):
    AppPrefs.logger.info(request)
    # build table object from table in DB
    metadata_obj = MetaData()
    col1table = Table("dashcol1", metadata_obj, autoload_with=sqlengine)
    col2table = Table("dashcol2", metadata_obj, autoload_with=sqlengine)
    col3table = Table("dashcol3", metadata_obj, autoload_with=sqlengine)

    conn = sqlengine.connect()

    # get column 1 order
    stmt = select(col1table).where(
        col1table.c.appuid == AppPrefs.appuid)
    row_headers = conn.execute(stmt).keys()
    AppPrefs.logger.info(row_headers)
    myresult = conn.execute(stmt)
    conn.commit()

    col1_data = []

    for row in myresult:
        col1_data.append(row.widgetid)

    # get column 2 order
    stmt = select(col2table).where(
        col2table.c.appuid == AppPrefs.appuid)
    row_headers = conn.execute(stmt).keys()
    AppPrefs.logger.info(row_headers)
    myresult = conn.execute(stmt)
    conn.commit()

    col2_data = []

    for row in myresult:
        col2_data.append(row.widgetid)

    # get column 3 order
    stmt = select(col3table).where(
        col3table.c.appuid == AppPrefs.appuid)
    row_headers = conn.execute(stmt).keys()
    AppPrefs.logger.info(row_headers)
    myresult = conn.execute(stmt)
    conn.commit()

    col3_data = []

    for row in myresult:
        col3_data.append(row.widgetid)

    return col1_data, col2_data, col3_data
