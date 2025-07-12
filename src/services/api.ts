import axios, { AxiosResponse } from 'axios';
import Cookies from 'js-cookie';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  ProcessResumeRequest,
  ProcessResumeResponse,
  User,
  ApiError
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      Cookies.remove('auth_token');
      Cookies.remove('refresh_token');
      window.location.href = '/signin';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    // Mock authentication for demo - replace with real API call
    // await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
    
    // // Mock validation
    // if (credentials.email === 'demo@example.com' && credentials.password === 'password') {
    //   const mockResponse: AuthResponse = {
    //     user: {
    //       id: 'demo-user-id',
    //       email: credentials.email,
    //       firstName: 'Demo',
    //       lastName: 'User',
    //       company: 'Demo Company',
    //       role: 'HR Manager',
    //       createdAt: new Date().toISOString()
    //     },
    //     token: 'mock-jwt-token',
    //     refreshToken: 'mock-refresh-token'
    //   };
      
    //   // Store tokens in cookies
    //   Cookies.set('auth_token', mockResponse.token, { expires: 7 });
    //   Cookies.set('refresh_token', mockResponse.refreshToken, { expires: 30 });
      
    //   return mockResponse;
    // } else {
    //   throw new Error('Invalid credentials. Use demo@example.com / password for demo.');
    // }
    
    // Real API call (commented out for demo)
    const response: AxiosResponse<AuthResponse> = await api.post('/auth/login', credentials);
    Cookies.set('auth_token', response.data.token, { expires: 7 });
    Cookies.set('refresh_token', response.data.refreshToken, { expires: 30 });
    return response.data;
  },

  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    // Mock registration for demo - replace with real API call
    // await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay
    
    // const mockResponse: AuthResponse = {
    //   user: {
    //     id: 'new-user-id',
    //     email: userData.email,
    //     firstName: userData.firstName,
    //     lastName: userData.lastName,
    //     company: userData.company,
    //     role: 'HR Professional',
    //     createdAt: new Date().toISOString()
    //   },
    //   token: 'mock-jwt-token',
    //   refreshToken: 'mock-refresh-token'
    // };
    
    // // Store tokens in cookies
    // Cookies.set('auth_token', mockResponse.token, { expires: 7 });
    // Cookies.set('refresh_token', mockResponse.refreshToken, { expires: 30 });
    
    // return mockResponse;
    
    // Real API call (commented out for demo)
    const response: AxiosResponse<AuthResponse> = await api.post('/auth/register', userData);
    Cookies.set('auth_token', response.data.token, { expires: 7 });
    Cookies.set('refresh_token', response.data.refreshToken, { expires: 30 });
    return response.data;
  },

  logout: async (): Promise<void> => {
    // Mock logout for demo
    // await new Promise(resolve => setTimeout(resolve, 500));
    // Cookies.remove('auth_token');
    // Cookies.remove('refresh_token');
    
    // Real API call (commented out for demo)
    try {
      await api.post('/auth/logout');
    } finally {
      Cookies.remove('auth_token');
      Cookies.remove('refresh_token');
    }
  },

  getCurrentUser: async (): Promise<User> => {
    // Mock get current user for demo
    // await new Promise(resolve => setTimeout(resolve, 500));
    
    // const token = Cookies.get('auth_token');
    // if (!token) {
    //   throw new Error('No authentication token');
    // }
    
    // return {
    //   id: 'demo-user-id',
    //   email: 'demo@example.com',
    //   firstName: 'Demo',
    //   lastName: 'User',
    //   company: 'Demo Company',
    //   role: 'HR Manager',
    //   createdAt: new Date().toISOString()
    // };
    
    // Real API call (commented out for demo)
    const response: AxiosResponse<User> = await api.get('/auth/me');
    return response.data;
  },

  refreshToken: async (): Promise<AuthResponse> => {
    const refreshToken = Cookies.get('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    // Mock refresh token for demo
    // await new Promise(resolve => setTimeout(resolve, 500));
    
    // const mockResponse: AuthResponse = {
    //   user: {
    //     id: 'demo-user-id',
    //     email: 'demo@example.com',
    //     firstName: 'Demo',
    //     lastName: 'User',
    //     company: 'Demo Company',
    //     role: 'HR Manager',
    //     createdAt: new Date().toISOString()
    //   },
    //   token: 'new-mock-jwt-token',
    //   refreshToken: 'new-mock-refresh-token'
    // };

    // Cookies.set('auth_token', mockResponse.token, { expires: 7 });
    // Cookies.set('refresh_token', mockResponse.refreshToken, { expires: 30 });

    // return mockResponse;
    
    // Real API call (commented out for demo)
    const response: AxiosResponse<AuthResponse> = await api.post('/auth/refresh', {
      refreshToken
    });
    Cookies.set('auth_token', response.data.token, { expires: 7 });
    Cookies.set('refresh_token', response.data.refreshToken, { expires: 30 });
    return response.data;
  }
};

// Resume processing API calls
export const resumeAPI = {
  processResumes: async (data: ProcessResumeRequest): Promise<ProcessResumeResponse> => {
    const formData = new FormData();
    formData.append('jobDescription', data.jobDescription);
    
    data.files.forEach((file, index) => {
      formData.append(`resumes`, file);
    });

    const response: AxiosResponse<ProcessResumeResponse> = await api.post('/resumes/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  getJobHistory: async (): Promise<any[]> => {
    const response: AxiosResponse<any[]> = await api.get('/resumes/history');
    return response.data;
  },

  getJobDetails: async (jobId: string): Promise<ProcessResumeResponse> => {
    const response: AxiosResponse<ProcessResumeResponse> = await api.get(`/resumes/job/${jobId}`);
    return response.data;
  }
};

// Utility functions
export const isAuthenticated = (): boolean => {
  return !!Cookies.get('auth_token');
};

export const getAuthToken = (): string | undefined => {
  return Cookies.get('auth_token');
};

export const handleApiError = (error: any): ApiError => {
  if (error.response?.data) {
    return error.response.data;
  }
  
  return {
    message: error.message || 'An unexpected error occurred',
    code: 'UNKNOWN_ERROR'
  };
};

export default api;