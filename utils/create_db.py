from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy_utils import database_exists, create_database


sqlengine = create_engine("mysql+pymysql://" +
                          "root" + ":" +
                          "raspberry" + "@" +
                          "40breeder.local" + ":" +
                          "3306" + "/" +
                          "rbtest2" +
                          "?charset=utf8")

print(database_exists(sqlengine.url))

metadata_obj = MetaData()

if not database_exists(sqlengine.url):
    print("Database not found, creating database...")
    create_database(sqlengine.url)

    print("Creating table dashorder")
    dashorder_table = Table("dashorder",
                            metadata_obj,
                            Column("id", Integer, nullable=False, autoincrement=True, primary_key=True, unique=True),
                            Column("appuid", String(45), nullable=False, primary_key=True, unique=True),
                            Column("widgetid", String(45), unique=True),
                            Column("column", String(45)),
                            Column("order", String(45)),
                            )

    print ("Creating table ds18b20" )
    ds18b20_table = Table("ds18b20",
                        metadata_obj,
                        Column("id", Integer, nullable=False, autoincrement=True, primary_key=True),
                        Column("appuid", String(45), nullable=False, primary_key=True),
                        Column("probeid", String(45), nullable=False, primary_key=True),
                        Column("serialnum", String(45) )
                        )
    
    print ("Creating table global" )
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

    print ("Creating table mcp3008" )
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
    
    print ("Creating table outlets" )
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
    
    print ("Creating table probes" )
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





print(database_exists(sqlengine.url))
