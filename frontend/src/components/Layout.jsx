// frontend/src/components/Layout.jsx

import React from 'react';

function Layout({ children }) {
  // Removed the card layout to apply the dark theme to the whole page
  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8 md:py-16">
        <main>{children}</main>
      </div>
    </div>
  );
}

export default Layout;