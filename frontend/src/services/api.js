import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

// Add a request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If the error status is 401 and there is no originalRequest._retry flag,
    // it means the token has expired and we need to refresh it
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await api.post('/auth/refresh', {
          refresh_token: refreshToken,
        });

        const { token } = response.data;
        localStorage.setItem('token', token);

        // Retry the original request with the new token
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      } catch (error) {
        // If refresh token fails, redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (credentials) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);
      formData.append('grant_type', 'password');
      
      console.log('Sending login request with:', {
        username: credentials.username,
        grant_type: 'password'
      });
      
      const response = await axios.post('/auth/token', formData, {
        baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
        },
        withCredentials: false
      });

      console.log('Login response:', response.data);

      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        return response.data;
      } else {
        throw new Error('No access token received');
      }
    } catch (error) {
      console.error('Login API error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else if (error.message === 'Network Error') {
        throw new Error('Unable to connect to the server. Please try again.');
      } else {
        throw new Error('Invalid username or password');
      }
    }
  },
  
  register: async (userData) => {
    try {
      // Transform the data to match the backend schema
      const transformedData = {
        email: userData.email,
        password: userData.password,
        first_name: userData.first_name,
        last_name: userData.last_name,
        medical_license_number: userData.medical_license_number,
        qualifications: userData.qualifications,
        specialty: userData.specialty || "General Practice",
        years_of_experience: parseInt(userData.years_of_experience) || 0,
        doctor_type: userData.doctor_type || "resident",
        date_of_birth: userData.date_of_birth,
        gender: userData.gender || "male",
        contact_number: userData.contact_number,
        department: userData.department,
        office_location: userData.office_location,
        graduation_date: userData.graduation_date,
        // Optional fields
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

      console.log('Sending registration data:', JSON.stringify(transformedData, null, 2));

      const response = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/auth/register`,
        transformedData,
        {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          withCredentials: false
        }
      );

      console.log('Registration response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Registration error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });

      if (error.response?.status === 422) {
        const validationErrors = error.response.data.detail;
        if (Array.isArray(validationErrors)) {
          const errorMessage = validationErrors
            .map(err => `${err.loc[err.loc.length - 1]}: ${err.msg}`)
            .join('\n');
          throw new Error(errorMessage);
        }
      }

      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  },
};

export const patientAPI = {
  getPatients: async () => {
    const response = await api.get('/api/patients');
    return response.data;
  },
  
  getPatient: async (id) => {
    const response = await api.get(`/api/patients/${id}`);
    return response.data;
  },
  
  createPatient: async (data) => {
    const response = await api.post('/api/patients', data);
    return response.data;
  },
  
  updatePatient: async (id, data) => {
    const response = await api.put(`/api/patients/${id}`, data);
    return response.data;
  },
  
  deletePatient: async (id) => {
    const response = await api.delete(`/api/patients/${id}`);
    return response.data;
  },
};

export const clinicalHistoryAPI = {
  getHistories: async (patientId) => {
    const response = await api.get(`/api/clinical-histories/${patientId}`);
    return response.data;
  },
  
  createHistory: async (data) => {
    const response = await api.post('/api/clinical-histories', data);
    return response.data;
  },
  
  updateHistory: async (id, data) => {
    const response = await api.put(`/api/clinical-histories/${id}`, data);
    return response.data;
  },
  
  deleteHistory: async (id) => {
    const response = await api.delete(`/api/clinical-histories/${id}`);
    return response.data;
  },
};

export default api;
