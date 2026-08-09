import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navigation from './components/Navigation';

import Login from './pages/Login';
import Register from './pages/Register';

import DoctorDashboard from './pages/doctor/DoctorDashboard';
import CreatePrescription from './pages/doctor/CreatePrescription';
import PrescriptionsList from './pages/doctor/PrescriptionsList';

import NurseDashboard from './pages/nurse/NurseDashboard';
import MedicinesList from './pages/nurse/MedicinesList';
import CreateMedicine from './pages/nurse/CreateMedicine';

import AdminDashboard from './pages/admin/AdminDashboard';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            <Route
              path="/doctor/*"
              element={
                <ProtectedRoute allowedRoles={['doctor']}>
                  <Navigation />
                  <Routes>
                    <Route path="dashboard" element={<DoctorDashboard />} />
                    <Route path="prescriptions" element={<PrescriptionsList />} />
                    <Route path="prescriptions/create" element={<CreatePrescription />} />
                  </Routes>
                </ProtectedRoute>
              }
            />

            <Route
              path="/nurse/*"
              element={
                <ProtectedRoute allowedRoles={['nurse']}>
                  <Navigation />
                  <Routes>
                    <Route path="dashboard" element={<NurseDashboard />} />
                    <Route path="medicines" element={<MedicinesList />} />
                    <Route path="medicines/create" element={<CreateMedicine />} />
                  </Routes>
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin/*"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <Navigation />
                  <Routes>
                    <Route path="dashboard" element={<AdminDashboard />} />
                  </Routes>
                </ProtectedRoute>
              }
            />

            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>

          <ToastContainer
            position="top-right"
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;