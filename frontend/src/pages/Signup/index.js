import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Container, Paper, Link, Grid, MenuItem, CircularProgress, Alert, Fade } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../../services/api';

const Signup = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    medical_license_number: '',
    qualifications: '',
    specialty: 'General Practice',
    years_of_experience: '',
    doctor_type: 'resident',
    date_of_birth: '',
    gender: 'male',
    contact_number: '',
    department: '',
    office_location: '',
    graduation_date: ''
  });
  
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field when it's being edited
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Basic validation for required fields
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    if (!formData.confirmPassword) newErrors.confirmPassword = 'Please confirm your password';
    if (!formData.first_name) newErrors.first_name = 'First name is required';
    if (!formData.last_name) newErrors.last_name = 'Last name is required';
    if (!formData.medical_license_number) newErrors.medical_license_number = 'Medical license number is required';
    if (!formData.qualifications) newErrors.qualifications = 'Qualifications are required';
    if (!formData.specialty) newErrors.specialty = 'Specialty is required';
    if (!formData.years_of_experience) newErrors.years_of_experience = 'Years of experience is required';
    if (!formData.doctor_type) newErrors.doctor_type = 'Doctor type is required';
    if (!formData.date_of_birth) newErrors.date_of_birth = 'Date of birth is required';
    if (!formData.gender) newErrors.gender = 'Gender is required';
    if (!formData.contact_number) newErrors.contact_number = 'Contact number is required';
    if (!formData.department) newErrors.department = 'Department is required';
    if (!formData.office_location) newErrors.office_location = 'Office location is required';
    if (!formData.graduation_date) newErrors.graduation_date = 'Graduation date is required';

    // Password confirmation validation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.email && !emailRegex.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    // Password strength validation
    if (formData.password && formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }

    // Medical license number format validation
    const licenseRegex = /^ML\d{6}$/;
    if (formData.medical_license_number && !licenseRegex.test(formData.medical_license_number)) {
      newErrors.medical_license_number = 'Invalid license number format (MLxxxxxx)';
    }

    // Contact number format validation
    const phoneRegex = /^\+?[\d\s-]{10,}$/;
    if (formData.contact_number && !phoneRegex.test(formData.contact_number)) {
      newErrors.contact_number = 'Invalid contact number format';
    }

    // Date validations
    const today = new Date();
    const birthDate = new Date(formData.date_of_birth);
    const gradDate = new Date(formData.graduation_date);

    if (birthDate > today) {
      newErrors.date_of_birth = 'Date of birth cannot be in the future';
    }

    if (gradDate > today && formData.doctor_type === 'consultant') {
      newErrors.graduation_date = 'Graduation date cannot be in the future for consultants';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');
    
    // Validate form
    if (!validateForm()) {
      setSubmitError('Please fix the validation errors');
      return;
    }

    setLoading(true);
    
    try {
      const signupData = {
        ...formData,
        years_of_experience: parseInt(formData.years_of_experience) || 0,
        subspecialty: null,
        emergency_contact: null,
        consultation_hours: null,
        bio: null,
        research_interests: null,
        publications: null,
        certifications: null,
        rotation_schedule: null,
        join_date: new Date().toISOString().split('T')[0]
      };

      // Register the user
      await authAPI.register(signupData);
      setSuccess(true);

      // After successful registration, attempt to log in
      try {
        await authAPI.login({
          username: formData.email,
          password: formData.password,
          grant_type: 'password'
        });
        
        // Show success animation for 1.5 seconds before redirecting
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } catch (loginError) {
        console.error('Auto-login failed:', loginError);
        // If auto-login fails, redirect to login page with success message
        setTimeout(() => {
          navigate('/login', {
            state: { message: 'Registration successful! Please log in with your credentials.' }
          });
        }, 1500);
      }
    } catch (error) {
      setLoading(false);
      console.error('Registration error:', error);
      
      if (error.response?.status === 422) {
        const validationErrors = error.response.data.detail;
        if (Array.isArray(validationErrors)) {
          const newErrors = {};
          validationErrors.forEach(err => {
            const field = err.loc[err.loc.length - 1];
            newErrors[field] = err.msg;
          });
          setErrors(newErrors);
          setSubmitError('Please fix the validation errors');
        } else {
          setSubmitError(error.response.data.detail || 'Invalid data provided');
        }
      } else {
        setSubmitError(error.message || 'Registration failed. Please try again.');
      }
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%', position: 'relative' }}>
          {/* Success Animation */}
          <Fade in={success} timeout={500}>
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                zIndex: 1,
              }}
            >
              <CircularProgress color="success" size={60} />
              <Typography variant="h6" color="success" sx={{ mt: 2 }}>
                Registration Successful!
              </Typography>
            </Box>
          </Fade>

          <Typography component="h1" variant="h5" align="center" gutterBottom>
            Create Doctor Account
          </Typography>

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Grid container spacing={2}>
              {/* Basic Information */}
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                  error={!!errors.email}
                  helperText={errors.email}
                  disabled={loading}
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
                  error={!!errors.first_name}
                  helperText={errors.first_name}
                  disabled={loading}
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
                  error={!!errors.last_name}
                  helperText={errors.last_name}
                  disabled={loading}
                />
              </Grid>

              {/* Professional Information */}
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="medical_license_number"
                  label="Medical License Number"
                  id="medical_license_number"
                  value={formData.medical_license_number}
                  onChange={handleChange}
                  error={!!errors.medical_license_number}
                  helperText={errors.medical_license_number || "Format: MLxxxxxx"}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="qualifications"
                  label="Qualifications"
                  id="qualifications"
                  value={formData.qualifications}
                  onChange={handleChange}
                  error={!!errors.qualifications}
                  helperText={errors.qualifications || "e.g., MD"}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="specialty"
                  label="Specialty"
                  id="specialty"
                  select
                  value={formData.specialty}
                  onChange={handleChange}
                  error={!!errors.specialty}
                  helperText={errors.specialty}
                  disabled={loading}
                >
                  <MenuItem value="General Practice">General Practice</MenuItem>
                  <MenuItem value="Internal Medicine">Internal Medicine</MenuItem>
                  <MenuItem value="Surgery">Surgery</MenuItem>
                  <MenuItem value="Pediatrics">Pediatrics</MenuItem>
                  <MenuItem value="Cardiology">Cardiology</MenuItem>
                  <MenuItem value="Neurology">Neurology</MenuItem>
                  <MenuItem value="Oncology">Oncology</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </TextField>
              </Grid>

              {/* Additional Information */}
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="doctor_type"
                  label="Doctor Type"
                  id="doctor_type"
                  select
                  value={formData.doctor_type}
                  onChange={handleChange}
                  error={!!errors.doctor_type}
                  helperText={errors.doctor_type}
                  disabled={loading}
                >
                  <MenuItem value="resident">Resident</MenuItem>
                  <MenuItem value="consultant">Consultant</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="years_of_experience"
                  label="Years of Experience"
                  id="years_of_experience"
                  type="number"
                  value={formData.years_of_experience}
                  onChange={handleChange}
                  error={!!errors.years_of_experience}
                  helperText={errors.years_of_experience}
                  disabled={loading}
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="date_of_birth"
                  label="Date of Birth"
                  id="date_of_birth"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  error={!!errors.date_of_birth}
                  helperText={errors.date_of_birth}
                  InputLabelProps={{ shrink: true }}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="gender"
                  label="Gender"
                  id="gender"
                  select
                  value={formData.gender}
                  onChange={handleChange}
                  error={!!errors.gender}
                  helperText={errors.gender}
                  disabled={loading}
                >
                  <MenuItem value="male">Male</MenuItem>
                  <MenuItem value="female">Female</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="contact_number"
                  label="Contact Number"
                  id="contact_number"
                  value={formData.contact_number}
                  onChange={handleChange}
                  error={!!errors.contact_number}
                  helperText={errors.contact_number || "Format: +1234567890"}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="department"
                  label="Department"
                  id="department"
                  select
                  value={formData.department}
                  onChange={handleChange}
                  error={!!errors.department}
                  helperText={errors.department}
                  disabled={loading}
                >
                  <MenuItem value="Emergency">Emergency</MenuItem>
                  <MenuItem value="Outpatient">Outpatient</MenuItem>
                  <MenuItem value="Inpatient">Inpatient</MenuItem>
                  <MenuItem value="ICU">ICU</MenuItem>
                  <MenuItem value="Surgery">Surgery</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="office_location"
                  label="Office Location"
                  id="office_location"
                  value={formData.office_location}
                  onChange={handleChange}
                  error={!!errors.office_location}
                  helperText={errors.office_location}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="graduation_date"
                  label="Graduation Date"
                  id="graduation_date"
                  type="date"
                  value={formData.graduation_date}
                  onChange={handleChange}
                  error={!!errors.graduation_date}
                  helperText={errors.graduation_date}
                  InputLabelProps={{ shrink: true }}
                  disabled={loading}
                />
              </Grid>

              {/* Password Fields */}
              <Grid item xs={12}>
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
                  error={!!errors.password}
                  helperText={errors.password || "At least 8 characters"}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12}>
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
                  error={!!errors.confirmPassword}
                  helperText={errors.confirmPassword}
                  disabled={loading}
                />
              </Grid>

              {submitError && (
                <Grid item xs={12}>
                  <Alert severity="error">{submitError}</Alert>
                </Grid>
              )}
              <Grid item xs={12}>
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  color="primary"
                  disabled={loading}
                  sx={{ mt: 3, mb: 2 }}
                >
                  {loading ? (
                    <>
                      <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                      Creating Account...
                    </>
                  ) : (
                    'Create Account'
                  )}
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center' }}>
                  <Link href="/login" variant="body2">
                    Already have an account? Sign in
                  </Link>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Signup;
