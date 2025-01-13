import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { clinicalHistoryAPI } from '../../services/api';

const RecordHistory = () => {
  const [histories, setHistories] = useState([]);

  useEffect(() => {
    fetchHistories();
  }, []);

  const fetchHistories = async () => {
    try {
      const response = await clinicalHistoryAPI.getHistories();
      setHistories(response.data);
    } catch (error) {
      console.error('Error fetching histories:', error);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Clinical History Records</Typography>
        <Button variant="contained" color="primary">
          Add Record
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Patient</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {histories.map((history) => (
              <TableRow key={history.id}>
                <TableCell>{history.patient_name}</TableCell>
                <TableCell>{new Date(history.date).toLocaleDateString()}</TableCell>
                <TableCell>{history.description}</TableCell>
                <TableCell>{history.status}</TableCell>
                <TableCell>
                  <IconButton color="primary">
                    <EditIcon />
                  </IconButton>
                  <IconButton color="error">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {histories.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No history records found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default RecordHistory;
