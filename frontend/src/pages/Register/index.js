import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Container, Paper, Grid, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { authAPI } from '../../services/api';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    medical_license_number: '',
    qualifications: '',
    specialty: '',
    subspecialty: '',
    years_of_experience: '',
    doctor_type: 'resident',
    date_of_birth: '',
    gender: '',
    contact_number: '',
    emergency_contact: '',
    department: '',
    office_location: '',
    graduation_date: ''
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Basic validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    if (!formData.password.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)) {
      setError('Password must contain at least one uppercase letter, one lowercase letter, and one number');
      return;
    }

    if (!formData.contact_number.match(/^\+?[0-9]{10,20}$/)) {
      setError('Contact number must be in the format: +1234567890');
      return;
    }

    if (formData.emergency_contact && !formData.emergency_contact.match(/^\+?[0-9]{10,20}$/)) {
      setError('Emergency contact number must be in the format: +1234567890');
      return;
    }

    if (!formData.medical_license_number || formData.medical_license_number.length < 5) {
      setError('Medical license number must be at least 5 characters long');
      return;
    }

    if (!formData.qualifications || formData.qualifications.length < 2) {
      setError('Qualifications must be at least 2 characters long');
      return;
    }

    if (!formData.specialty) {
      setError('Please select a specialty');
      return;
    }

    if (!formData.years_of_experience || formData.years_of_experience < 0) {
      setError('Years of experience must be a positive number');
      return;
    }

    if (!formData.date_of_birth) {
      setError('Please enter your date of birth');
      return;
    }

    if (!formData.gender) {
      setError('Please select your gender');
      return;
    }

    if (!formData.department) {
      setError('Please enter your department');
      return;
    }

    if (!formData.graduation_date) {
      setError('Please enter your expected graduation date');
      return;
    }

    const birthDate = new Date(formData.date_of_birth);
    if (birthDate > new Date()) {
      setError('Date of birth cannot be in the future');
      return;
    }

    const graduationDate = new Date(formData.graduation_date);
    if (graduationDate <= new Date()) {
      setError('Graduation date must be in the future');
      return;
    }

    try {
      const signupData = {
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        medical_license_number: formData.medical_license_number,
        qualifications: formData.qualifications,
        specialty: formData.specialty,
        subspecialty: formData.subspecialty || null,
        years_of_experience: parseInt(formData.years_of_experience),
        doctor_type: 'resident',
        date_of_birth: formData.date_of_birth,
        gender: formData.gender,
        contact_number: formData.contact_number,
        emergency_contact: formData.emergency_contact || null,
        department: formData.department,
        office_location: formData.office_location || null,
        graduation_date: formData.graduation_date
      };

      // Register the user
      await authAPI.register(signupData);

      // Attempt to log in automatically
      try {
        await authAPI.login({
          username: formData.email,
          password: formData.password
        });
        navigate('/dashboard');
      } catch (loginError) {
        // If automatic login fails, redirect to login page
        navigate('/login', { 
          state: { 
            message: 'Registration successful! Please log in with your credentials.' 
          } 
        });
      }
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.response?.data?.message) {
        setError(err.response.data.message);
      } else if (typeof err.response?.data === 'string') {
        setError(err.response.data);
      } else {
        setError('Registration failed. Please check your information and try again.');
      }
      console.error('Registration error:', err);
    }
  };

  return (
    <Container component="main" maxWidth="md">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center" gutterBottom>
            Create Doctor Account
          </Typography>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="medical_license_number"
                  label="Medical License Number"
                  id="medical_license_number"
                  value={formData.medical_license_number}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="first_name"
                  label="First Name"
                  id="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="last_name"
                  label="Last Name"
                  id="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete="new-password"
                  value={formData.password}
                  onChange={handleChange}
                  helperText="Must contain at least one uppercase letter, one lowercase letter, and one number"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="confirmPassword"
                  label="Confirm Password"
                  type="password"
                  id="confirmPassword"
                  autoComplete="new-password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="qualifications"
                  label="Qualifications"
                  id="qualifications"
                  value={formData.qualifications}
                  onChange={handleChange}
                  helperText="e.g., MD, PhD, FRCS"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel id="specialty-label">Specialty</InputLabel>
                  <Select
                    labelId="specialty-label"
                    id="specialty"
                    name="specialty"
                    value={formData.specialty}
                    onChange={handleChange}
                    label="Specialty"
                  >
                    <MenuItem value="General Practice">General Practice</MenuItem>
                    <MenuItem value="Cardiology">Cardiology</MenuItem>
                    <MenuItem value="Neurology">Neurology</MenuItem>
                    <MenuItem value="Pediatrics">Pediatrics</MenuItem>
                    <MenuItem value="Orthopedics">Orthopedics</MenuItem>
                    <MenuItem value="Psychiatry">Psychiatry</MenuItem>
                    <MenuItem value="Dermatology">Dermatology</MenuItem>
                    <MenuItem value="Oncology">Oncology</MenuItem>
                    <MenuItem value="Emergency Medicine">Emergency Medicine</MenuItem>
                    <MenuItem value="Internal Medicine">Internal Medicine</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  name="subspecialty"
                  label="Subspecialty"
                  id="subspecialty"
                  value={formData.subspecialty}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="years_of_experience"
                  label="Years of Experience"
                  type="number"
                  id="years_of_experience"
                  value={formData.years_of_experience}
                  onChange={handleChange}
                  inputProps={{ min: 0 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="date_of_birth"
                  label="Date of Birth"
                  type="date"
                  id="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel id="gender-label">Gender</InputLabel>
                  <Select
                    labelId="gender-label"
                    id="gender"
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}
                    label="Gender"
                  >
                    <MenuItem value="male">Male</MenuItem>
                    <MenuItem value="female">Female</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="department"
                  label="Department"
                  id="department"
                  value={formData.department}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="contact_number"
                  label="Contact Number"
                  id="contact_number"
                  value={formData.contact_number}
                  onChange={handleChange}
                  helperText="Format: +1234567890"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  name="emergency_contact"
                  label="Emergency Contact"
                  id="emergency_contact"
                  value={formData.emergency_contact}
                  onChange={handleChange}
                  helperText="Format: +1234567890"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  name="office_location"
                  label="Office Location"
                  id="office_location"
                  value={formData.office_location}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  name="graduation_date"
                  label="Expected Graduation Date"
                  type="date"
                  id="graduation_date"
                  value={formData.graduation_date}
                  onChange={handleChange}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
            {error && (
              <Typography color="error" align="center" sx={{ mt: 2 }}>
                {error}
              </Typography>
            )}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              sx={{ mt: 3 }}
            >
              Sign Up
            </Button>
            <Button
              component={RouterLink}
              to="/login"
              fullWidth
              variant="text"
              sx={{ mt: 1 }}
            >
              Already have an account? Sign in
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register;
