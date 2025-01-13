import React from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import HistoryIcon from '@mui/icons-material/History';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const Dashboard = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={4}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'primary.light',
              color: 'white',
            }}
          >
            <PeopleIcon sx={{ fontSize: 40, mb: 1 }} />
            <Typography variant="h6">Total Patients</Typography>
            <Typography variant="h4">0</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'secondary.light',
              color: 'white',
            }}
          >
            <HistoryIcon sx={{ fontSize: 40, mb: 1 }} />
            <Typography variant="h6">History Records</Typography>
            <Typography variant="h4">0</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'success.light',
              color: 'white',
            }}
          >
            <TrendingUpIcon sx={{ fontSize: 40, mb: 1 }} />
            <Typography variant="h6">Recent Activity</Typography>
            <Typography variant="h4">0</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
