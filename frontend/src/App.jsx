// src/App.jsx - The Router

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import VideosPage from './pages/VideosPage';
import Layout from './components/Layout'; // We'll create this next

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/videos" element={<VideosPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;