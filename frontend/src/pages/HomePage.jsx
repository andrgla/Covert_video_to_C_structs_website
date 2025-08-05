import React, { useState } from 'react';
import { Link } from 'react-router-dom';

// Defines the default state for all form fields
const initialFormData = {
  struct_name: 'my_animation',
  grid_width: 18,
  grid_height: 11,
  cell_aspect_ratio: 1.6,
  enhance_contrast: true,
  sigmoid_k: 0.042,
  sigmoid_center: 175,
  filter_threshold: 5,
  dimming_threshold: 15,
  fps: 30,
  video_fps: 10,
  generate_video: true,
};

function HomePage() {
  // State for UI interactivity
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  // State for form data and submission
  const [selectedFile, setSelectedFile] = useState(null);
  const [formData, setFormData] = useState(initialFormData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null); // Will hold { c_code, video_path }

  // --- Event Handlers ---

  const handleToggleSettings = () => setIsSettingsOpen(!isSettingsOpen);
  
  const handleFileChange = (event) => setSelectedFile(event.target.files[0] || null);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    // Use the 'checked' property for checkboxes, otherwise use 'value'
    const val = type === 'checkbox' ? checked : value;
    setFormData(prev => ({ ...prev, [name]: val }));
  };

  const handleResetDefaults = () => setFormData(initialFormData);

  const handleSubmit = async (event) => {
    event.preventDefault(); // Prevent the browser from reloading the page
    if (!selectedFile) {
      setError('Please select a file to upload.');
      return;
    }

    // Reset previous results and start loading
    setIsLoading(true);
    setError(null);
    setResult(null);

    // Create a FormData object to send the file and form data
    const data = new FormData();
    data.append('file', selectedFile);
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });

    try {
      // The vite.config.js proxy will forward this request to your Python server
      const response = await fetch('/upload', { method: 'POST', body: data });
      
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ error: 'An unknown server error occurred.' }));
        throw new Error(errData.error);
      }
      
      const resData = await response.json();
      setResult(resData); // Save the successful result
    } catch (err) {
      setError(err.message); // Save the error message
    } finally {
      setIsLoading(false); // Stop loading
    }
  };
  
  const copyToClipboard = () => {
    if (result && result.c_code) {
      navigator.clipboard.writeText(result.c_code);
      // You could add a visual "Copied!" confirmation here if you like
    }
  };

  return (
    <div className="px-6 py-8 md:px-10">
      <div className="text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900">Animation to C-Code Converter</h1>
        <p className="text-gray-600 mt-2">Upload a video, image, or a zip file of images to generate C-struct animations.</p>
        <Link to="/videos" className="inline-block mt-3 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition text-sm">
          🎬 View Generated Videos
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* --- File Upload --- */}
        <div>
          <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-2">1. Upload File</label>
          <div className="flex items-center justify-center w-full">
            <label htmlFor="file-upload" className="flex flex-col items-center justify-center w-full h-48 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <svg className="w-10 h-10 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-4-4V7a4 4 0 014-4h1.586a1 1 0 01.707.293l1.414 1.414a1 1 0 00.707.293H13a4 4 0 014 4v5m-4 4h4a4 4 0 004-4v-1.586a1 1 0 00-.293-.707l-1.414-1.414a1 1 0 00-.707-.293H9.5a4 4 0 00-4 4v5a4 4 0 004 4z"></path></svg>
                <p className="mb-2 text-sm text-gray-500"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                <p className="text-xs text-gray-500">MP4, MOV, PNG, JPG, or ZIP</p>
              </div>
              <input id="file-upload" name="file" type="file" className="hidden" onChange={handleFileChange} />
            </label>
          </div>
          <p className="text-sm text-gray-500 mt-2">{selectedFile ? `Selected file: ${selectedFile.name}` : 'No file chosen'}</p>
        </div>

        {/* --- C Struct Name --- */}
        <div>
          <label htmlFor="struct_name" className="block text-sm font-medium text-gray-700">2. C Struct Name</label>
          <input type="text" name="struct_name" id="struct_name" value={formData.struct_name} onChange={handleChange} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
        </div>

        {/* --- Advanced Settings --- */}
        <div className="border border-gray-200 rounded-lg">
          <button type="button" onClick={handleToggleSettings} className="w-full px-4 py-3 text-left bg-gray-50 hover:bg-gray-100 transition-colors rounded-t-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">3. Advanced Settings (Optional)</span>
              <svg className={`w-5 h-5 text-gray-400 transform transition-transform ${isSettingsOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </button>
          <div className={`${isSettingsOpen ? '' : 'hidden'} px-4 py-4 space-y-4 border-t border-gray-200`}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Grid Dimensions */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Grid Dimensions</h4>
                <div className="space-y-2">
                  <div>
                    <label htmlFor="grid_width" className="block text-xs text-gray-600">Width (pixels)</label>
                    <input type="number" name="grid_width" id="grid_width" value={formData.grid_width} onChange={handleChange} min="1" max="50" className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label htmlFor="grid_height" className="block text-xs text-gray-600">Height (pixels)</label>
                    <input type="number" name="grid_height" id="grid_height" value={formData.grid_height} onChange={handleChange} min="1" max="50" className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label htmlFor="cell_aspect_ratio" className="block text-xs text-gray-600">Cell Aspect Ratio (height/width)</label>
                    <input type="number" name="cell_aspect_ratio" id="cell_aspect_ratio" value={formData.cell_aspect_ratio} onChange={handleChange} step="0.1" min="0.5" max="3.0" className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                    <small className="text-xs text-gray-500">1.0 = square, 1.6 = default rectangular</small>
                  </div>
                </div>
              </div>
              {/* Contrast Enhancement */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Contrast Enhancement</h4>
                <div className="space-y-2">
                  <div>
                    <label className="flex items-center">
                      <input type="checkbox" name="enhance_contrast" id="enhance_contrast" checked={formData.enhance_contrast} onChange={handleChange} className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                      <span className="ml-2 text-xs text-gray-600">Enable contrast enhancement</span>
                    </label>
                  </div>
                  <div>
                    <label htmlFor="sigmoid_k" className="block text-xs text-gray-600">Contrast Strength</label>
                    <input type="number" name="sigmoid_k" id="sigmoid_k" value={formData.sigmoid_k} onChange={handleChange} step="0.001" min="0.001" max="0.1" className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label htmlFor="sigmoid_center" className="block text-xs text-gray-600">Contrast Center (0-255)</label>
                    <input type="number" name="sigmoid_center" id="sigmoid_center" value={formData.sigmoid_center} onChange={handleChange} min="0" max="255" className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                  </div>
                </div>
              </div>
              {/* Dark Pixel Filtering */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Dark Pixel Filtering</h4>
                <div className="space-y-2">
                  <div>
                    <label htmlFor="filter_threshold" className="block text-xs text-gray-600">Filter Threshold (0-255)</label>
                    <input type="number" name="filter_threshold" id="filter_threshold" value={formData.filter_threshold} onChange={handleChange} min="0" max="255" className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label htmlFor="dimming_threshold" className="block text-xs text-gray-600">Dimming Threshold (0-255)</label>
                    <input type="number" name="dimming_threshold" id="dimming_threshold" value={formData.dimming_threshold} onChange={handleChange} min="0" max="255" className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                  </div>
                </div>
              </div>
              {/* Video Settings */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Video Processing</h4>
                <div className="space-y-2">
                  <div>
                    <label htmlFor="fps" className="block text-xs text-gray-600">Frames per Second</label>
                    <input type="number" name="fps" id="fps" value={formData.fps} onChange={handleChange} min="1" max="60" className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                  </div>
                  <div>
                    <label htmlFor="video_fps" className="block text-xs text-gray-600">Output Video FPS</label>
                    <input type="number" name="video_fps" id="video_fps" value={formData.video_fps} onChange={handleChange} min="1" max="30" className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                    <small className="text-xs text-gray-500">FPS for generated preview video</small>
                  </div>
                  <div>
                    <label className="flex items-center">
                      <input type="checkbox" name="generate_video" id="generate_video" checked={formData.generate_video} onChange={handleChange} className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                      <span className="ml-2 text-xs text-gray-600">Generate preview video (for multiple frames)</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <div className="pt-2 border-t border-gray-100">
              <button type="button" onClick={handleResetDefaults} className="text-xs text-indigo-600 hover:text-indigo-800 underline">Reset to Defaults</button>
            </div>
          </div>
        </div>

        {/* --- Submit Button --- */}
        <div className="text-center">
          <button type="submit" disabled={isLoading} className="w-full md:w-auto inline-flex justify-center py-3 px-8 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition disabled:bg-indigo-400 disabled:cursor-not-allowed">
            {isLoading ? 'Generating...' : 'Generate C Code'}
          </button>
        </div>
      </form>

      {/* --- UI Feedback: Error Message --- */}
      {error && (
        <div className="mt-8 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* --- UI Feedback: Success Result --- */}
      {result && result.c_code && (
        <div className="mt-10">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-2xl font-bold text-gray-900">Generated C Code</h2>
            <div className="tooltip">
              <button onClick={copyToClipboard} className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                <svg className="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                Copy Code
              </button>
            </div>
          </div>
          <pre className="bg-gray-900 text-white p-4 rounded-lg overflow-x-auto text-sm"><code>{result.c_code}</code></pre>
        </div>
      )}
    </div>
  );
}

export default HomePage;
