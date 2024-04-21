let hostname = process.env.REACT_APP_API_HOSTNAME;
let portnum = process.env.REACT_APP_API_PORT_NUM;

export const API_GET_TOKEN = `http://${hostname}:${portnum}/get_token`;
export const API_GET_OUTLET_LIST = `http://${hostname}:${portnum}/get_outlet_list/`;
export const API_SET_OUTLET_BUTTONSTATE = `http://${hostname}:${portnum}/set_outlet_buttonstate/`;
export const API_SET_PROBE_NAME = `http://${hostname}:${portnum}/set_probe_name/`;
export const API_GET_CHART_DATA_1HR = `http://${hostname}:${portnum}/get_chartdata_1hr/`;
export const API_GET_CHART_DATA_24HR = `http://${hostname}:${portnum}/get_chartdata_24hr/`;
export const API_GET_CHART_DATA_1WK = `http://${hostname}:${portnum}/get_chartdata_1wk/`;
export const API_GET_CHART_DATA_1MO = `http://${hostname}:${portnum}/get_chartdata_1mo/`;
export const API_GET_CHART_DATA_3MO = `http://${hostname}:${portnum}/get_chartdata_3mo/`;
export const API_GET_OUTLET_CHART_DATA = `http://${hostname}:${portnum}/get_outletchartdata/`;
export const API_SET_OUTLET_PARAMS_LIGHT = `http://${hostname}:${portnum}/set_outlet_params_light/`;
export const API_SET_OUTLET_PARAMS_ALWAYS = `http://${hostname}:${portnum}/set_outlet_params_always/`;
export const API_SET_OUTLET_PARAMS_HEATER = `http://${hostname}:${portnum}/set_outlet_params_heater/`;
export const API_SET_OUTLET_PARAMS_RETURN = `http://${hostname}:${portnum}/set_outlet_params_return/`;
export const API_SET_OUTLET_PARAMS_SKIMMER = `http://${hostname}:${portnum}/set_outlet_params_skimmer/`;
export const API_SET_OUTLET_PARAMS_PH = `http://${hostname}:${portnum}/set_outlet_params_ph/`;
export const API_GET_GLOBAL_PREFS = `http://${hostname}:${portnum}/get_global_prefs/`;
export const API_SET_GLOBAL_PREFS = `http://${hostname}:${portnum}/set_global_prefs/`;
export const API_GET_CURRENT_PROBE_STATS = `http://${hostname}:${portnum}/get_current_probe_stats/`;
export const API_GET_CURRENT_OUTLET_STATS = `http://${hostname}:${portnum}/get_current_outlet_stats/`;
export const API_GET_PROBE_LIST = `http://${hostname}:${portnum}/get_probe_list/`;
export const API_SET_FEEDMODE = `http://${hostname}:${portnum}/set_feedmode`;
export const API_SET_MCP3008_ENABLE_STATE = `http://${hostname}:${portnum}/set_mcp3008_enable_state`;
export const API_GET_MCP3008_ENABLE_STATE = `http://${hostname}:${portnum}/get_mcp3008_enable_state/`;
export const API_GET_OUTLET_ENABLE_STATE = `http://${hostname}:${portnum}/get_outlet_enable_state/`;
export const API_SET_OUTLET_ENABLE_STATE = `http://${hostname}:${portnum}/set_outlet_enable_state`;
export const API_GET_CONNECTED_TEMP_PROBES = `http://${hostname}:${portnum}/get_connected_temp_probes/`;
export const API_SET_CONNECTED_TEMP_PROBES = `http://${hostname}:${portnum}/set_connected_temp_probes`;
export const API_GET_ASSIGNED_TEMP_PROBES = `http://${hostname}:${portnum}/get_assigned_temp_probes/`;
export const API_SET_COLUMN_WIDGET_ORDER = `http://${hostname}:${portnum}/set_column_widget_order`;
export const API_GET_COLUMN_WIDGET_ORDER = `http://${hostname}:${portnum}/get_column_widget_order/`;
export const API_GET_USER_LIST = `http://${hostname}:${portnum}/get_user_list/`;
export const API_SET_CHANGE_PASSWORD = `http://${hostname}:${portnum}/set_change_password`;
export const API_SET_REMOVE_USER =  `http://${hostname}:${portnum}/set_remove_user`;