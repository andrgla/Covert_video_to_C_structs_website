// frontend/src/pages/HomePage.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';

// Custom hook for debouncing
const useDebounce = (callback, delay) => {
  const [timeoutId, setTimeoutId] = useState(null);
  return (...args) => {
    if (timeoutId) clearTimeout(timeoutId);
    const newTimeoutId = setTimeout(() => callback(...args), delay);
    setTimeoutId(newTimeoutId);
  };
};

// Reusable collapsible section component
const SettingsSection = ({ title, children }) => {
  return (
    <details className="bg-brand-ui-bg rounded-lg group" open>
      <summary className="w-full p-3 text-left transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-brand-accent">
        <span className="text-sm font-medium text-gray-300">{title}</span>
      </summary>
      <div className="p-4 pt-2 space-y-4">
        {children}
      </div>
    </details>
  );
};

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

function HomePage({ result, setResult }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [formData, setFormData] = useState(initialFormData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [previewImage, setPreviewImage] = useState('');
  const [isPreviewLoading, setIsPreviewLoading] = useState(true);

  const fetchPreview = async (settings) => {
    setIsPreviewLoading(true);
    try {
      const response = await fetch('/api/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      if (!response.ok) throw new Error('Preview failed');
      const imageBlob = await response.blob();
      setPreviewImage(URL.createObjectURL(imageBlob));
    } catch (err) {
      console.error("Failed to fetch preview:", err);
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const debouncedFetchPreview = useCallback(useDebounce(fetchPreview, 300), []);

  useEffect(() => {
    const getInitialPreview = async () => {
        setIsPreviewLoading(true);
        try {
            const response = await fetch('/api/preview');
            if (!response.ok) throw new Error('Initial preview failed');
            const imageBlob = await response.blob();
            setPreviewImage(URL.createObjectURL(imageBlob));
        } catch (err) {
            console.error("Failed to fetch initial preview:", err);
        } finally {
            setIsPreviewLoading(false);
        }
    };
    getInitialPreview();
  }, []);

  useEffect(() => {
    debouncedFetchPreview(formData);
  }, [formData, debouncedFetchPreview]);

  const handleFileChange = (event) => setSelectedFile(event.target.files[0] || null);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    const val = type === 'checkbox' ? checked : value;
    setFormData(prev => ({ ...prev, [name]: val }));
  };
  
  const handleResetDefaults = () => setFormData(initialFormData);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setError('Please select a file to upload.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    const data = new FormData();
    data.append('file', selectedFile);
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    try {
      const response = await fetch('/upload', { method: 'POST', body: data });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ error: 'An unknown server error occurred.' }));
        throw new Error(errData.error);
      }
      const resData = await response.json();
      setResult(resData);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  const copyToClipboard = () => {
    if (result && result.c_code) {
      navigator.clipboard.writeText(result.c_code);
      // You could add a "Copied!" confirmation message here
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="font-orbitron text-5xl md:text-6xl font-bold text-brand-accent tracking-wider mb-2">C-CONVERTER</h1>
        <p className="text-gray-400">Upload a video or image to generate C-struct animations.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* File Upload */}
        <div>
          <h2 className="text-lg font-semibold mb-2 text-brand-header">1. Upload file</h2>
          <label htmlFor="file-upload" className="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed border-gray-600 rounded-lg cursor-pointer hover:bg-brand-dark-light transition" style={{backgroundColor: '#323237'}}>
            <div className="flex flex-col items-center justify-center">
              <p className="text-sm text-gray-300"><span className="font-semibold">Click to upload</span> or drag and drop</p>
              <p className="text-xs text-gray-400 mt-1">MP4, MOV, PNG, or JPG</p>
            </div>
            <input id="file-upload" name="file" type="file" className="hidden" onChange={handleFileChange} />
          </label>
          <p className="text-sm text-gray-500 mt-2 h-4">{selectedFile ? `Selected: ${selectedFile.name}` : ''}</p>
        </div>

        {/* C Struct Name */}
        <div>
          <h2 className="text-lg font-semibold mb-2 text-brand-header">2. C Struct Name</h2>
          <input type="text" name="struct_name" id="struct_name" value={formData.struct_name} onChange={handleChange} className="w-full px-3 py-2 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-brand-accent sm:text-sm text-white placeholder-gray-400" style={{backgroundColor: '#323237'}} />
        </div>

        {/* --- Advanced Settings & Live Preview --- */}
        <div>
            <h2 className="text-lg font-semibold mb-2 text-brand-header">3. Settings</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                    <SettingsSection title="Grid">
                        <div>
                            <label className="block text-xs text-gray-400">Width: {formData.grid_width}px</label>
                            <input type="range" name="grid_width" value={formData.grid_width} onChange={handleChange} min="4" max="50" className="w-full" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Height: {formData.grid_height}px</label>
                            <input type="range" name="grid_height" value={formData.grid_height} onChange={handleChange} min="4" max="50" className="w-full" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Cell Aspect Ratio: {formData.cell_aspect_ratio}</label>
                            <input type="range" name="cell_aspect_ratio" value={formData.cell_aspect_ratio} onChange={handleChange} step="0.1" min="0.5" max="3.0" className="w-full" />
                        </div>
                    </SettingsSection>

                    <SettingsSection title="Filter">
                        <label className="flex items-center text-xs text-gray-400">
                            <input type="checkbox" name="enhance_contrast" checked={formData.enhance_contrast} onChange={handleChange} className="rounded border-gray-500 bg-brand-dark text-brand-accent focus:ring-brand-accent" />
                            <span className="ml-2">Enable contrast enhancement</span>
                        </label>
                        <div>
                            <label className="block text-xs text-gray-400">Contrast Strength: {formData.sigmoid_k}</label>
                            <input type="range" name="sigmoid_k" value={formData.sigmoid_k} onChange={handleChange} step="0.001" min="0.001" max="0.1" className="w-full" disabled={!formData.enhance_contrast}/>
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Contrast Center: {formData.sigmoid_center}</label>
                            <input type="range" name="sigmoid_center" value={formData.sigmoid_center} onChange={handleChange} min="0" max="255" className="w-full" disabled={!formData.enhance_contrast}/>
                        </div>
                         <div>
                            <label className="block text-xs text-gray-400">Filter Threshold: {formData.filter_threshold}</label>
                            <input type="range" name="filter_threshold" value={formData.filter_threshold} onChange={handleChange} min="0" max="255" className="w-full" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Dimming Threshold: {formData.dimming_threshold}</label>
                            <input type="range" name="dimming_threshold" value={formData.dimming_threshold} onChange={handleChange} min="0" max="255" className="w-full" />
                        </div>
                    </SettingsSection>

                    <SettingsSection title="Video">
                        <div>
                            <label className="block text-xs text-gray-400">Input FPS: {formData.fps}</label>
                            <input type="range" name="fps" value={formData.fps} onChange={handleChange} min="1" max="60" className="w-full" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Output Video FPS: {formData.video_fps}</label>
                            <input type="range" name="video_fps" value={formData.video_fps} onChange={handleChange} min="1" max="30" className="w-full" />
                        </div>
                    </SettingsSection>
                    <button type="button" onClick={handleResetDefaults} className="text-xs text-gray-400 hover:text-white underline">Reset to Defaults</button>
                </div>

                <div className="flex flex-col items-center justify-center bg-brand-ui-bg p-2 rounded-lg border border-gray-700">
                    <div className="w-full h-48 flex items-center justify-center">
                        {isPreviewLoading ? (
                            <p className="text-gray-500 text-xs">Loading Preview...</p>
                        ) : (
                            <img src={previewImage} alt="Live preview" className="max-w-full max-h-full object-contain" style={{ imageRendering: 'pixelated' }}/>
                        )}
                    </div>
                </div>
            </div>
        </div>

        {/* Submit Button & Video Link */}
        <div className="text-center pt-4">
          <button 
            type="submit" 
            disabled={isLoading} 
            className="font-orbitron w-full md:w-auto text-xl font-bold py-3 px-10 rounded-lg text-white hover:opacity-90 focus:outline-none focus:ring-4 focus:ring-purple-500/50 transition disabled:bg-gray-500"
            style={{
              background: isLoading ? '#6b7280' : 'linear-gradient(90deg, #8c52ff, #ff914d)',
              border: 'none'
            }}
          >
            {isLoading ? 'GENERATING...' : 'GENERATE C STRUCT'}
          </button>
          <div className="mt-4">
             <Link to="/videos" className="text-sm text-gray-400 hover:text-white underline">
                See videos
             </Link>
          </div>
        </div>
      </form>

      {/* --- THIS IS THE RESTORED SECTION --- */}
      {/* Error Message */}
      {error && (
        <div className="mt-8 p-4 bg-red-900/50 border border-red-500/50 text-red-300 rounded-lg" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Success Result */}
      {result && result.c_code && (
        <div className="mt-10">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-2xl font-bold text-brand-header">Generated C Code</h2>
            <button onClick={copyToClipboard} className="inline-flex items-center px-4 py-2 border border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-300 hover:bg-brand-dark-light" style={{backgroundColor: '#323237'}}>
              Copy Code
            </button>
          </div>
          <pre className="text-gray-300 p-4 rounded-lg overflow-x-auto text-sm" style={{backgroundColor: '#323237'}}><code>{result.c_code}</code></pre>
        </div>
      )}
      {/* --- END OF RESTORED SECTION --- */}

    </div>
  );
}

export default HomePage;