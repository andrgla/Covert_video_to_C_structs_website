import React from 'react';
import { Link } from 'react-router-dom'; // <-- 1. Import Link

function VideosPage() {
  const videos = []; 

  return (
    <div className="bg-gray-100 text-gray-800">
        <div className="container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className="px-6 py-8">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-gray-900">Generated Animation Videos</h1>
                        <p className="text-gray-600 mt-2">View your processed animation videos</p>
                        {/* 2. Changed <a> to <Link> */}
                        <Link to="/" className="inline-block mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
                            ← Back to Generator
                        </Link>
                    </div>

                    {videos.length > 0 ? (
                        <div className="grid gap-6">
                           {/* Video list will go here */}
                        </div>
                    ) : (
                        <div className="text-center py-12">
                            <div className="text-gray-400 text-6xl mb-4">🎬</div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Videos Generated Yet</h3>
                            <p className="text-gray-500 mb-4">Upload a video or multiple images to generate animation videos.</p>
                             {/* 3. Changed <a> to <Link> */}
                            <Link to="/" className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
                                Generate Your First Animation
                            </Link>
                        </div>
                    )}
                </div>
            </div>
        </div>
    </div>
  );
}

export default VideosPage;