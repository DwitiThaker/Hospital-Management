import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { staffAPI } from '../../services/api';
import { toast } from 'react-toastify';
import { Users, UserPlus, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalDoctors: 0,
    totalNurses: 0,
    activeStaff: 0,
  });
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [doctorsRes, nursesRes] = await Promise.all([
        staffAPI.getAllDoctors(),
        staffAPI.getAllNurses(),
      ]);

      setDoctors(doctorsRes.data);

      const activeDoctors = doctorsRes.data.filter(d => d.is_active).length;
      const activeNurses = nursesRes.data.filter(n => n.is_active).length;

      setStats({
        totalDoctors: doctorsRes.data.length,
        totalNurses: nursesRes.data.length,
        activeStaff: activeDoctors + activeNurses,
      });
    } catch (error) {
      toast.error('Failed to fetch staff data');
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
            Welcome back, {user?.username}
          </h1>
          <p className="text-gray-600 mt-2">Manage hospital staff and operations</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            icon={Users}
            title="Total Doctors"
            value={stats.totalDoctors}
            color="text-blue-600"
            bgColor="bg-blue-50"
          />
          <StatCard
            icon={Users}
            title="Total Nurses"
            value={stats.totalNurses}
            color="text-green-600"
            bgColor="bg-green-50"
          />
          <StatCard
            icon={Activity}
            title="Active Staff"
            value={stats.activeStaff}
            color="text-purple-600"
            bgColor="bg-purple-50"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link
                to="/admin/doctors/create"
                className="flex items-center justify-between p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition"
              >
                <div className="flex items-center">
                  <UserPlus className="w-5 h-5 text-blue-600 mr-3" />
                  <span className="font-medium text-gray-800">Add New Doctor</span>
                </div>
              </Link>
              <Link
                to="/admin/nurses/create"
                className="flex items-center justify-between p-4 bg-green-50 rounded-lg hover:bg-green-100 transition"
              >
                <div className="flex items-center">
                  <UserPlus className="w-5 h-5 text-green-600 mr-3" />
                  <span className="font-medium text-gray-800">Add New Nurse</span>
                </div>
              </Link>
              <Link
                to="/admin/doctors"
                className="flex items-center justify-between p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition"
              >
                <div className="flex items-center">
                  <Users className="w-5 h-5 text-purple-600 mr-3" />
                  <span className="font-medium text-gray-800">Manage Doctors</span>
                </div>
              </Link>
              <Link
                to="/admin/nurses"
                className="flex items-center justify-between p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition"
              >
                <div className="flex items-center">
                  <Users className="w-5 h-5 text-orange-600 mr-3" />
                  <span className="font-medium text-gray-800">Manage Nurses</span>
                </div>
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Doctors</h2>
            <div className="space-y-3">
              {doctors.slice(0, 5).map((doctor) => (
                <div
                  key={doctor._id || doctor.email}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-800">{doctor.username}</p>
                    <p className="text-sm text-gray-600">{doctor.email}</p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      doctor.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {doctor.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))}
              {doctors.length === 0 && (
                <p className="text-gray-500 text-center py-8">No doctors registered yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;