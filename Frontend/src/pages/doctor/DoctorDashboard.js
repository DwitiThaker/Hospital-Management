import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { prescriptionAPI } from '../../services/api';
import { toast } from 'react-toastify';
import { 
  FileText, 
  Plus, 
  Activity, 
  Users, 
  Calendar,
  TrendingUp 
} from 'lucide-react';
import { Link } from 'react-router-dom';

const DoctorDashboard = () => {
  const { user } = useAuth();
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalPrescriptions: 0,
    todayPrescriptions: 0,
    activePatients: 0,
  });

  useEffect(() => {
    fetchPrescriptions();
  }, []);

  const fetchPrescriptions = async () => {
    try {
      const response = await prescriptionAPI.getAll();
      setPrescriptions(response.data);
      
      const today = new Date().toDateString();
      const todayCount = response.data.filter(p => 
        new Date(p.created_at).toDateString() === today
      ).length;
      
      setStats({
        totalPrescriptions: response.data.length,
        todayPrescriptions: todayCount,
        activePatients: new Set(response.data.map(p => p.patient_name)).size,
      });
    } catch (error) {
      toast.error('Failed to fetch prescriptions');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, color, bgColor }) => (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 font-medium">{title}</p>
          <p className="text-3xl font-bold text-gray-800 mt-2">{value}</p>
        </div>
        <div className={`${bgColor} p-3 rounded-lg`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">
            Welcome back, Dr. {user?.username}
          </h1>
          <p className="text-gray-600 mt-2">Here's what's happening today</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            icon={FileText}
            title="Total Prescriptions"
            value={stats.totalPrescriptions}
            color="text-blue-600"
            bgColor="bg-blue-50"
          />
          <StatCard
            icon={Calendar}
            title="Today's Prescriptions"
            value={stats.todayPrescriptions}
            color="text-green-600"
            bgColor="bg-green-50"
          />
          <StatCard
            icon={Users}
            title="Active Patients"
            value={stats.activePatients}
            color="text-purple-600"
            bgColor="bg-purple-50"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link
                to="/doctor/prescriptions/create"
                className="flex items-center justify-between p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition"
              >
                <div className="flex items-center">
                  <Plus className="w-5 h-5 text-blue-600 mr-3" />
                  <span className="font-medium text-gray-800">Create New Prescription</span>
                </div>
              </Link>
              <Link
                to="/doctor/prescriptions"
                className="flex items-center justify-between p-4 bg-green-50 rounded-lg hover:bg-green-100 transition"
              >
                <div className="flex items-center">
                  <FileText className="w-5 h-5 text-green-600 mr-3" />
                  <span className="font-medium text-gray-800">View All Prescriptions</span>
                </div>
              </Link>
              <Link
                to="/doctor/settings"
                className="flex items-center justify-between p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition"
              >
                <div className="flex items-center">
                  <Activity className="w-5 h-5 text-purple-600 mr-3" />
                  <span className="font-medium text-gray-800">Account Settings</span>
                </div>
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Prescriptions</h2>
            <div className="space-y-3">
              {prescriptions.slice(0, 5).map((prescription) => (
                <div
                  key={prescription._id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-800">{prescription.patient_name}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(prescription.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Link
                    to={`/doctor/prescriptions/${prescription._id}`}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    View
                  </Link>
                </div>
              ))}
              {prescriptions.length === 0 && (
                <p className="text-gray-500 text-center py-8">No prescriptions yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DoctorDashboard;