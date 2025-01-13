import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Typography,
  Paper,
} from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Visualizer = styled(Paper)(({ theme }) => ({
  width: '100%',
  height: '100px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(2),
  backgroundColor: theme.palette.grey[100],
}));

const RecordHistory = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcribedText, setTranscribedText] = useState('');
  const [processedData, setProcessedData] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const { currentUser } = useAuth();

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  const processRecording = async () => {
    if (!audioBlob) return;

    setIsProcessing(true);
    const formData = new FormData();
    formData.append('audio_file', audioBlob);

    try {
      const response = await api.post('/transcription/process-audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setTranscribedText(response.data.transcription);
      setProcessedData(response.data.medical_info);
    } catch (error) {
      console.error('Error processing audio:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const renderProcessedData = () => {
    if (!processedData) return null;

    return (
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Demographics
              </Typography>
              <Typography>Age: {processedData.demographics?.age}</Typography>
              <Typography>Gender: {processedData.demographics?.gender}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Factors
              </Typography>
              {processedData.risk_factors?.map((factor, index) => (
                <Typography key={index}>• {factor}</Typography>
              ))}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Family History
              </Typography>
              {processedData.family_history?.map((item, index) => (
                <Typography key={index}>• {item}</Typography>
              ))}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Surgical History
              </Typography>
              {processedData.surgical_history?.map((item, index) => (
                <Typography key={index}>• {item}</Typography>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Record Clinical History
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Visualizer>
            {isRecording ? (
              <Typography color="primary">Recording in progress...</Typography>
            ) : (
              <Typography color="textSecondary">
                Press the microphone button to start recording
              </Typography>
            )}
          </Visualizer>
          
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Button
              variant="contained"
              color={isRecording ? 'secondary' : 'primary'}
              startIcon={isRecording ? <StopIcon /> : <MicIcon />}
              onClick={isRecording ? stopRecording : startRecording}
            >
              {isRecording ? 'Stop Recording' : 'Start Recording'}
            </Button>
            
            {audioBlob && !isRecording && (
              <Button
                variant="contained"
                color="primary"
                startIcon={isProcessing ? <CircularProgress size={20} /> : <SaveIcon />}
                onClick={processRecording}
                disabled={isProcessing}
              >
                Process Recording
              </Button>
            )}
          </Box>
        </Grid>

        {transcribedText && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Transcribed Text
                </Typography>
                <Typography>{transcribedText}</Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        {processedData && (
          <Grid item xs={12}>
            {renderProcessedData()}
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default RecordHistory;
