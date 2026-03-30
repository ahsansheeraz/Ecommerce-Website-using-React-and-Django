import React from 'react';
import { Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';
import AdminSidebar from '../components/admin/AdminSidebar';
import AdminHeader from '../components/admin/AdminHeader';

const AdminLayout = () => {
  const { sidebarOpen } = useSelector((state) => state.admin);

  return (
    <div className="min-h-screen bg-gray-100">
      <AdminSidebar />
      
      <div className={`transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : 'lg:ml-20'}`}>
        <AdminHeader />
        
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;