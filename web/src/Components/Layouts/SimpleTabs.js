import React from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/core/styles";
import AppBar from "@material-ui/core/AppBar";
import Tabs from "@material-ui/core/Tabs";
import Tab from "@material-ui/core/Tab";
import Typography from "@material-ui/core/Typography";
import Box from "@material-ui/core/Box";
import { Dashboard } from "../Dashboard";
import { AboutPage } from "../About/AboutPage";
import Paper from "@material-ui/core/Paper";

const styles = {
  Paper: {
    backgroundColor: "#D9DBE0",
    padding: 0,
    marginTop: 0,
    marginBottom: 1,
    marginRight: 0
  },
  bigIndicator: {
    height: 5,
    backgroundColor: "#D9DBE0"
  }
};

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <Typography
      component="div"
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      <Box p={3}>{children}</Box>
    </Typography>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.any.isRequired,
  value: PropTypes.any.isRequired
};

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    "aria-controls": `simple-tabpanel-${index}`
  };
}

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1,
    backgroundColor: theme.palette.background.paper
  }
}));

export default function SimpleTabs(props) {
  const classes = useStyles();
  const [value, setValue] = React.useState(0);

  function handleChange(event, newValue) {
    setValue(newValue);
  }

  return (
    <div>
      <Paper style={styles.Paper}>
        <Tabs
          value={value}
          onChange={handleChange}
          aria-label="simple tabs example"
          centered
          style={styles.bigIndicator}
        >
          <Tab label="Dashboard" {...a11yProps(0)} />
          <Tab label="Graphs" {...a11yProps(1)} />
          <Tab label="Settings" {...a11yProps(2)} />
          <Tab label="About" {...a11yProps(3)} />
        </Tabs>

        <TabPanel value={value} index={0}>
          <Dashboard
            probes={props.probes}
            probevals={props.probevals}
            outlets={props.outlets}
            feedmode={props.feedmode}
            onOutletWidgetClick={props.onOutletWidgetClick}
            onFeedWidgetClick={props.onFeedWidgetClick}
          />
        </TabPanel>
        <TabPanel value={value} index={1}>
          Graphs
        </TabPanel>
        <TabPanel value={value} index={2}>
          Settings
        </TabPanel>
        <TabPanel value={value} index={3}>
          About
          <AboutPage />
        </TabPanel>
      </Paper>
    </div>
  );
}
