import React from "react";
import Paper from "@material-ui/core/Paper";
import Tabs from "@material-ui/core/Tabs";
import Tab from "@material-ui/core/Tab";

const styles = {
  Paper: {
    backgroundColor: "#D9DBE0",
    padding: 0,
    marginTop: 0,
    marginBottom: 1,
    marginRight: 0
  }
};

export default props => (
  <Paper style={styles.Paper}>
    <Tabs value={0} indicatorColor="primary" textColor="primary" centered>
      <Tab label="Dashboard" />
      <Tab label="Graphs" />
      <Tab label="Settings" />
      <Tab label="About" />
    </Tabs>
  </Paper>
);
