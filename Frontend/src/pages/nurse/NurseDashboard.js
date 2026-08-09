import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { medicineAPI } from '../../services/api';
import { toast } from 'react-toastify';
import { Pill, Plus, Package, AlertCircle, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

const NurseDashboard = () => {
  const { user } = useAuth();
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalMedicines: 0,
    lowStock: 0,
    categories: 0,
  });

  useEffect(() => {
    fetchMedicines();
  }, []);

  const fetchMedicines = async () => {
    try {
      const response = await medicineAPI.getAll();
      setMedicines(response.data);
      
      const lowStockCount = response.data.filter(m => m.quantity < 50).length;
      const uniqueCategories = new Set(response.data.map(m => m.category)).size;
      
      setStats({
        totalMedicines: response.data.length,
        lowStock: lowStockCount,
        categories: uniqueCategories,
      });
    } catch (error) {
      toast.error('Failed to fetch medicines');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, color, bgColor, alert }) => (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 font-medium">{title}</p>
          <p className="text-3xl font-bold text-gray-800 mt-2">{value}</p>
          {alert && (
            <p className="text-xs text-red-600 mt-1 flex items-center">
              <AlertCircle className="w-3 h-3 mr-1" />
              Needs attention
            </p>
          )}
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
          <p className="text-gray-600 mt-2">Manage medicine inventory and supplies</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            icon={Pill}
            title="Total Medicines"
            value={stats.totalMedicines}
            color="text-blue-600"
            bgColor="bg-blue-50"
          />
          <StatCard
            icon={AlertCircle}
            title="Low Stock Items"
            value={stats.lowStock}
            color="text-red-600"
            bgColor="bg-red-50"
            alert={stats.lowStock > 0}
          />
          <StatCard
            icon={Package}
            title="Categories"
            value={stats.categories}
            color="text-green-600"
            bgColor="bg-green-50"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link
                to="/nurse/medicines/create"
                className="flex items-center justify-between p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition"
              >
                <div className="flex items-center">
                  <Plus className="w-5 h-5 text-blue-600 mr-3" />
                  <span className="font-medium text-gray-800">Add New Medicine</span>
                </div>
              </Link>
              <Link
                to="/nurse/medicines"
                className="flex items-center justify-between p-4 bg-green-50 rounded-lg hover:bg-green-100 transition"
              >
                <div className="flex items-center">
                  <Pill className="w-5 h-5 text-green-600 mr-3" />
                  <span className="font-medium text-gray-800">View All Medicines</span>
                </div>
              </Link>
              <Link
                to="/nurse/settings"
                className="flex items-center justify-between p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition"
              >
                <div className="flex items-center">
                  <TrendingUp className="w-5 h-5 text-purple-600 mr-3" />
                  <span className="font-medium text-gray-800">Account Settings</span>
                </div>
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Low Stock Alert</h2>
            <div className="space-y-3">
              {medicines
                .filter(m => m.quantity < 50)
                .slice(0, 5)
                .map((medicine) => (
                  <div
                    key={medicine._id}
                    className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-100"
                  >
                    <div>
                      <p className="font-medium text-gray-800">{medicine.name}</p>
                      <p className="text-sm text-red-600">Stock: {medicine.quantity} units</p>
                    </div>
                    <Link
                      to={`/nurse/medicines/edit/${medicine._id}`}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      Update
                    </Link>
                  </div>
                ))}
              {medicines.filter(m => m.quantity < 50).length === 0 && (
                <p className="text-gray-500 text-center py-8">All medicines well stocked</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NurseDashboard;