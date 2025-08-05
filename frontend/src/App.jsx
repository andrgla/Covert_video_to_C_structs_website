// frontend/src/App.jsx

import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import VideosPage from './pages/VideosPage';
import Layout from './components/Layout';

function App() {
  // Lift the result state here, so it persists across page navigation
  const [result, setResult] = useState(null);

  return (
    <Router>
      <Layout>
        <Routes>
          {/* Pass the result state and the function to update it down to HomePage */}
          <Route 
            path="/" 
            element={<HomePage result={result} setResult={setResult} />} 
          />
          <Route path="/videos" element={<VideosPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;