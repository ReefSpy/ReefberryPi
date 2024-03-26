from influxdb_client import InfluxDBClient, BucketRetentionRules, TaskCreateRequest
from influxdb_client.client.write_api import SYNCHRONOUS


INFLUXDB_PROBE_BUCKET_1HR = "reefberrypi_probe_1hr"
INFLUXDB_PROBE_BUCKET_1DY = "reefberrypi_probe_1dy"
INFLUXDB_PROBE_BUCKET_1WK = "reefberrypi_probe_1wk"
INFLUXDB_PROBE_BUCKET_1MO = "reefberrypi_probe_1mo"
INFLUXDB_PROBE_BUCKET_3MO = "reefberrypi_probe_3mo"
INFLUXDB_PROBE_BUCKET_1YR = "reefberrypi_probe_1yr"

INFLUXDB_OUTLET_BUCKET_1HR = "reefberrypi_outlet_1hr"
INFLUXDB_OUTLET_BUCKET_1DY = "reefberrypi_outlet_1dy"
INFLUXDB_OUTLET_BUCKET_1WK = "reefberrypi_outlet_1wk"
INFLUXDB_OUTLET_BUCKET_1MO = "reefberrypi_outlet_1mo"
INFLUXDB_OUTLET_BUCKET_3MO = "reefberrypi_outlet_3mo"
INFLUXDB_OUTLET_BUCKET_1YR = "reefberrypi_outlet_1yr"

INFLUXDB_RET_1HR = 3600
INFLUXDB_RET_1DY = 86400
INFLUXDB_RET_1WK = 604800
INFLUXDB_RET_1MO = 2592000
INFLUXDB_RET_3MO = 7776000
INFLUXDB_RET_1YR = 31536000




# initialize InfluxDB
def InitInfluxDB(app_prefs, logger):
    # connect to InfluxDB
    Influx_client = InfluxDBClient(
        url=app_prefs.influxdb_host, token=app_prefs.influxdb_token, org=app_prefs.influxdb_org)
    logger.info("Connected to InfluxDB at: " + Influx_client.url)
    logger.info("InfluxDB organization: " + Influx_client.org)
    
    #######################################
    # probe buckets
    #######################################
    # initial 1 hour bucket
    checkIfBucketExists(
        Influx_client, app_prefs.influxdb_org, INFLUXDB_PROBE_BUCKET_1HR, INFLUXDB_RET_1HR, logger)
    # 1 day bucket
    checkIfBucketExists(
        Influx_client, app_prefs.influxdb_org, INFLUXDB_PROBE_BUCKET_1DY, INFLUXDB_RET_1DY, logger)
    # 1 week bucket
    checkIfBucketExists(
        Influx_client, app_prefs.influxdb_org, INFLUXDB_PROBE_BUCKET_1WK, INFLUXDB_RET_1WK, logger)
    # 1 month bucket
    checkIfBucketExists(
        Influx_client, app_prefs.influxdb_org, INFLUXDB_PROBE_BUCKET_1MO, INFLUXDB_RET_1MO, logger)
    # 3 month bucket
    checkIfBucketExists(
       Influx_client, app_prefs.influxdb_org, INFLUXDB_PROBE_BUCKET_3MO, INFLUXDB_RET_3MO, logger)
    # 1 year bucket
    # defs_Influx.checkIfBucketExists(Influx_client, INFLUXDB_ORG, INFLUXDB_PROBE_BUCKET_1YR, INFLUXDB_RET_1YR, logger)

    ########################################
    # outlet buckets
    ########################################
    # initial 1 hour bucket
    # checkIfBucketExists(
    #     Influx_client, app_prefs.influxdb_org, INFLUXDB_OUTLET_BUCKET_1HR, INFLUXDB_RET_1HR, logger)
    # # 1 day bucket
    # checkIfBucketExists(
    #     Influx_client, app_prefs.influxdb_org, INFLUXDB_OUTLET_BUCKET_1DY, INFLUXDB_RET_1DY, logger)
    # # 1 week bucket
    # checkIfBucketExists(
    #     Influx_client, app_prefs.influxdb_org, INFLUXDB_OUTLET_BUCKET_1WK, INFLUXDB_RET_1WK, logger)
    # # 1 month bucket
    # checkIfBucketExists(
    #     Influx_client, app_prefs.influxdb_org, INFLUXDB_OUTLET_BUCKET_1MO, INFLUXDB_RET_1MO, logger)
    # 3 month bucket
    checkIfBucketExists(
       Influx_client, app_prefs.influxdb_org, INFLUXDB_OUTLET_BUCKET_3MO, INFLUXDB_RET_3MO, logger)
    # 1 year bucket
    # defs_Influx.checkIfBucketExists(Influx_client, INFLUXDB_ORG, INFLUXDB_OUTLET_BUCKET_1YR, INFLUXDB_RET_1YR, logger)


    # check if Influx Tasks are present and create task if not
    # probe tasks first
    if not checkIfInfluxTaskExists(Influx_client, "downsample_for_1dy"):
        logger.error("InfluxDB task not found!")
        createInfluxTasks(Influx_client, "downsample_for_1dy", INFLUXDB_PROBE_BUCKET_1HR,
                                      INFLUXDB_PROBE_BUCKET_1DY, '5m', '5m', app_prefs.influxdb_org, logger)
    if not checkIfInfluxTaskExists(Influx_client, "downsample_for_1wk"):
        logger.error("InfluxDB task not found!")
        createInfluxTasks(Influx_client, "downsample_for_1wk", INFLUXDB_PROBE_BUCKET_1DY,
                                      INFLUXDB_PROBE_BUCKET_1WK, '10m', '10m', app_prefs.influxdb_org, logger)
    if not checkIfInfluxTaskExists(Influx_client, "downsample_for_1mo"):
        logger.error("InfluxDB task not found!")
        createInfluxTasks(Influx_client, "downsample_for_1mo", INFLUXDB_PROBE_BUCKET_1WK,
                                      INFLUXDB_PROBE_BUCKET_1MO, '15m', '15m', app_prefs.influxdb_org, logger)
    if not checkIfInfluxTaskExists(Influx_client, "downsample_for_3mo"):
        logger.error("InfluxDB task not found!")
        createInfluxTasks(Influx_client, "downsample_for_3mo", INFLUXDB_PROBE_BUCKET_1MO,
                                      INFLUXDB_PROBE_BUCKET_3MO, '30m', '30m', app_prefs.influxdb_org, logger)
    # # outlet tasks next
    # if not checkIfInfluxTaskExists(Influx_client, "downsample_outlet_for_1dy"):
    #     logger.error("InfluxDB task not found!")
    #     createInfluxTasks(Influx_client, "downsample_outlet_for_1dy", INFLUXDB_OUTLET_BUCKET_1HR,
    #                                   INFLUXDB_OUTLET_BUCKET_1DY, '5m', '5m', app_prefs.influxdb_org, logger)
    # if not checkIfInfluxTaskExists(Influx_client, "downsample_outlet_for_1wk"):
    #     logger.error("InfluxDB task not found!")
    #     createInfluxTasks(Influx_client, "downsample_outlet_for_1wk", INFLUXDB_OUTLET_BUCKET_1DY,
    #                                   INFLUXDB_OUTLET_BUCKET_1WK, '10m', '10m', app_prefs.influxdb_org, logger)
    # if not checkIfInfluxTaskExists(Influx_client, "downsample_outlet_for_1mo"):
    #     logger.error("InfluxDB task not found!")
    #     createInfluxTasks(Influx_client, "downsample_outlet_for_1mo", INFLUXDB_OUTLET_BUCKET_1WK,
    #                                   INFLUXDB_OUTLET_BUCKET_1MO, '15m', '15m', app_prefs.influxdb_org, logger)
    # if not checkIfInfluxTaskExists(Influx_client, "downsample_outlet_for_3mo"):
    #     logger.error("InfluxDB task not found!")
    #     createInfluxTasks(Influx_client, "downsample_outlet_for_3mo", INFLUXDB_OUTLET_BUCKET_1MO,
    #                                   INFLUXDB_OUTLET_BUCKET_3MO, '30m', '30m', app_prefs.influxdb_org, logger)

    return Influx_client


def checkIfBucketExists(Influx_client, org, bucket_name, expiration_seconds, logger):
    buckets_api = Influx_client.buckets_api()
    # check if we have a bucket created already
    buckets = buckets_api.find_buckets().buckets
    bucketexists = False
    for bucket in buckets:
        if bucket.name == bucket_name:
            logger.info("Found bucket: " + bucket_name)
            bucketexists = True
            break
        else:
            bucketexists = False

    if not bucketexists:
        logger.error("InfluxDB bucket not found! Attempting to create bucket: " + bucket_name)
        # create initial raw data bucket with expiration of 1 hour
        createInfluxBucket(bucket_name, expiration_seconds, org, buckets_api, "Reefberry Pi raw data bucket", logger)


def createInfluxBucket(bucket_name, retention_time, organization, buckets_api, description, logger):
    #logger.error("InfluxDB bucket not found! Attempting to create bucket...")
    try:
        # Create Bucket with retention policy and name it
        retention_rules = BucketRetentionRules(
            type="expire", every_seconds=retention_time)
        created_bucket = buckets_api.create_bucket(bucket_name=bucket_name,
                                                    retention_rules=retention_rules,
                                                    org=organization,
                                                    description=description)

        logger.info(created_bucket)
        logger.info("InfluxDB bucket created: " + bucket_name)
    except:
        logger.error("Error creating InfluxDB bucket: " + bucket_name)


def createInfluxTasks(client, task_name, from_bucket, to_bucket, run_every, aggregate_time, org, logger):
    logger.info("Attempting to create task: " + task_name)
    tasks_api = client.tasks_api()
    # run_every as time interval in minutes ex:  15m
    # aggregate as time interval in minutes to average.  Ex:  5m
    flux = \
        '''
    option task = {{
     name: "{task_name}",
      every: {run_every}
    }}
  
    from(bucket: "{from_bucket}") 
      |> range(start: -task.every) 
      |> aggregateWindow(every: {aggregate_time}, fn: mean) 
      |> to(bucket: "{to_bucket}", org: "{org}")
  '''.format(task_name=task_name, from_bucket=from_bucket, to_bucket=to_bucket, org=org, run_every=run_every, aggregate_time=aggregate_time)

    task_request = TaskCreateRequest(flux=flux, org=org, description="Task Description", status="active")
    task = tasks_api.create_task(task_create_request=task_request)
    logger.info(task)
    logger.info("Created InfluxDB task: " + task_name)
 
def checkIfInfluxTaskExists(client, task_name):
    tasks_api = client.tasks_api()
    tasklist = tasks_api.find_tasks(name=task_name)

    # print(tasklist)
    for task in tasklist:
        if task.name == task_name:
            return True
    
    return False
