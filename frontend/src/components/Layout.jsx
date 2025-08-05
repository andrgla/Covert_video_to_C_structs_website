// src/components/Layout.jsx

import React from 'react';

function Layout({ children }) {
  return (
    <div className="bg-gray-100 text-gray-800 min-h-screen">
      <div className="container mx-auto px-4 py-8 md:py-16">
        <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-lg overflow-hidden">
          <main>{children}</main>
          <footer className="text-center py-4 bg-gray-50 border-t border-gray-200">
            <p className="text-sm text-gray-500">Created by Andrea</p>
          </footer>
        </div>
      </div>
    </div>
  );
}

export default Layout;