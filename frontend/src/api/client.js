import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || (
  typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '5174')
    ? 'http://localhost:8000/api'
    : '/api'
);

const api = axios.create({ baseURL });

export const getTransactions = () => api.get('/transactions').then(res => res.data);
export const getTransaction = (id) => api.get(`/transactions/${id}`).then(res => res.data);
export const reviewTransaction = (id, data) => api.patch(`/transactions/${id}/review`, data).then(res => res.data);
export const getStats = () => api.get('/stats').then(res => res.data);
export const startSimulator = () => api.post('/simulate/start').then(res => res.data);
export const stopSimulator = () => api.post('/simulate/stop').then(res => res.data);
export const getSimulatorStatus = () => api.get('/simulate/status').then(res => res.data);
