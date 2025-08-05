// frontend/src/pages/VideosPage.jsx

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function VideosPage() {
  const [videos, setVideos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch the list of videos from the backend API
    const fetchVideos = async () => {
      try {
        // The Vite proxy will forward this request to your Python server
        const response = await fetch('/api/videos');
        if (!response.ok) {
          throw new Error('Failed to fetch videos from the server.');
        }
        const data = await response.json();
        setVideos(data); // Store the fetched videos in state
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchVideos();
  }, []); // The empty array means this effect runs once when the component mounts

  return (
    <div className="px-6 py-8 md:px-10">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Generated Animation Videos</h1>
        <p className="text-gray-600 mt-2">View your processed animation videos</p>
        <Link to="/" className="inline-block mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
          ← Back to Generator
        </Link>
      </div>

      {isLoading && <p className="text-center text-gray-500">Loading videos...</p>}
      {error && <p className="text-center text-red-500">Error: {error}</p>}

      {!isLoading && !error && (
        <>
          {videos.length > 0 ? (
            <div className="grid gap-6">
              {videos.map((video) => (
                <div key={video.path} className="border border-gray-200 rounded-lg p-4 md:p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{video.name}</h3>
                      <p className="text-sm text-gray-500">
                        From: {video.folder} | Size: {(video.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <a href={video.path} download className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition">
                      Download
                    </a>
                  </div>
                  
                  {/* The <video> element now correctly sources from the backend */}
                  <video controls preload="metadata" className="w-full max-w-md mx-auto bg-black rounded" style={{ imageRendering: 'pixelated' }}>
                    <source src={video.path} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">🎬</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Videos Generated Yet</h3>
              <p className="text-gray-500 mb-4">Upload a file on the main page to generate your first animation video.</p>
              <Link to="/" className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
                Generate Your First Animation
              </Link>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default VideosPage;