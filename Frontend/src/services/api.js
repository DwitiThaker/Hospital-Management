import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (credentials) => api.post('/login', credentials),
  register: (userData) => api.post('/register', userData),
};

// Prescription APIs
export const prescriptionAPI = {
  create: (data) => api.post('/doctor/create_prescription', data),
  getById: (id) => api.get(`/doctor/read_prescription_by_id/${id}`),
  getAll: () => api.get('/doctor/read_all_prescriptions'),
  update: (id, data) => api.put(`/doctor/update_prescription_by_id/${id}`, data),
  delete: (id) => api.delete(`/doctor/delete_prescription_by_id/${id}`),
  getByDoctorId: (doctorId) => api.get(`/fetch_prescriptions_from_doctor_id/${doctorId}`),
};

// Medicine APIs
export const medicineAPI = {
  getAll: () => api.get('/nurse/read_all_medicines'),
  getById: (id) => api.get(`/nurse/read_medicine_by_id/${id}`),
  create: (data) => api.post('/nurse/create_medicine', data),
  update: (id, data) => api.put(`/nurse/update_medicine_by_id/${id}`, data),
  delete: (id) => api.delete(`/nurse/delete_medicine_by_id/${id}`),
};

// Staff Management APIs
export const staffAPI = {
  createDoctor: (data) => api.post('/management/create_doctor', data),
  createNurse: (data) => api.post('/management/create_nurse', data),
  getAllDoctors: () => api.get('/read_all_doctors'),
  getAllNurses: () => api.get('/read_all_nurses'),
  changeDoctorPassword: (data) => api.put('/doctor/change_doctor_password', data),
  changeNursePassword: (data) => api.put('/nurse/change_nurse_password', data),
};

export default api;