// frontend/src/pages/HomePage.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Eye, Settings, ArrowRight, Upload, Check, X } from 'lucide-react'; // Added Check and X icons

// Custom hook for debouncing (from your original code)
const useDebounce = (callback, delay) => {
  const [timeoutId, setTimeoutId] = useState(null);
  return (...args) => {
    if (timeoutId) clearTimeout(timeoutId);
    const newTimeoutId = setTimeout(() => callback(...args), delay);
    setTimeoutId(newTimeoutId);
  };
};

// A reusable Tooltip component for the icons
const Tooltip = ({ children, text }) => {
  return (
    <div className="relative group flex items-center">
      {children}
      <div className="absolute bottom-full mb-2 w-max bg-brand-dark-light text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
        {text}
        <svg className="absolute text-brand-dark-light h-2 w-full left-0 top-full" x="0px" y="0px" viewBox="0 0 255 255"><polygon className="fill-current" points="0,0 127.5,127.5 255,0"/></svg>
      </div>
    </div>
  );
};


// Reusable collapsible section component (from your original code, with updated styles)
const SettingsSection = ({ title, children }) => {
  return (
    <details className="bg-brand-dark rounded-lg group" open>
      <summary className="w-full p-3 text-left transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-brand-accent">
        <span className="text-sm font-medium text-gray-300">{title}</span>
      </summary>
      <div className="p-4 pt-2 space-y-4">
        {children}
      </div>
    </details>
  );
};

// Initial form data from your original code
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
  // --- All your existing state is preserved ---
  const [selectedFile, setSelectedFile] = useState(null);
  const [formData, setFormData] = useState(initialFormData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [previewImage, setPreviewImage] = useState('');
  const [isPreviewLoading, setIsPreviewLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  // --- MODIFIED: Added state for copy button feedback ---
  const [copySuccess, setCopySuccess] = useState('');


  // --- All your existing functions are preserved ---
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
    if (showSettings) {
        debouncedFetchPreview(formData);
    }
  }, [formData, debouncedFetchPreview, showSettings]);

  const handleFileChange = (file) => {
    setSelectedFile(file || null);
  };

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    const val = type === 'checkbox' ? checked : value;
    setFormData(prev => ({ ...prev, [name]: val }));
  };
  
  const handleResetDefaults = () => {
      setFormData({...initialFormData, struct_name: formData.struct_name});
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile || !formData.struct_name.trim()) {
      setError('Please enter an animation name and select a file.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    setCopySuccess(''); // Reset copy message on new generation
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
  
  // --- MODIFIED: copyToClipboard function is now more robust ---
  const copyToClipboard = async () => {
    if (!result || !result.c_code) return;

    // The navigator.clipboard API is only available in secure contexts (HTTPS or localhost)
    if (!navigator.clipboard) {
        setCopySuccess('Copying is not supported on insecure pages.');
        setTimeout(() => setCopySuccess(''), 2000);
        return;
    }

    try {
        await navigator.clipboard.writeText(result.c_code);
        setCopySuccess('Copied!');
    } catch (err) {
        console.error('Failed to copy text: ', err);
        setCopySuccess('Failed to copy!');
    } finally {
        setTimeout(() => setCopySuccess(''), 2000); // Reset message after 2 seconds
    }
  };


  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
      e.dataTransfer.clearData();
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };
  
  const triggerFileSelect = () => document.getElementById('file-upload-input').click();

  const isGenerateEnabled = selectedFile && formData.struct_name.trim() !== '';

  return (
    <div className="pt-32 pb-8">
      <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="font-orbitron text-5xl md:text-6xl font-bold text-brand-header tracking-wider mb-2">C-CONVERTER</h1>
        <p className="text-gray-400">Upload a video or image to generate C-struct animations.</p>
      </div>

      {/* Main Input Bar */}
      <div className="mb-4">
        <form 
          onSubmit={handleSubmit}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`relative bg-brand-ui-bg border rounded-2xl transition-all duration-300 flex flex-col p-4
            ${isDragOver ? 'border-brand-accent' : 'border-gray-500 hover:border-gray-400'}`
          }
        >
          <input 
            type="text"
            name="struct_name"
            value={formData.struct_name}
            onChange={handleChange}
            placeholder="Enter animation name..."
            className="w-full bg-transparent text-white placeholder-gray-400 focus:outline-none text-lg mb-3"
          />
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-1">
                <Tooltip text="Upload File">
                    <button type="button" onClick={triggerFileSelect} className="flex items-center space-x-2 cursor-pointer p-2 rounded-lg hover:bg-brand-dark-light transition-colors">
                        <Upload size={18} className={selectedFile ? "text-green-400" : "text-gray-400"} />
                        <span className={`text-sm ${selectedFile ? "text-white" : "text-gray-400"} truncate max-w-40`}>
                            {selectedFile ? selectedFile.name : "Upload"}
                        </span>
                    </button>
                </Tooltip>
                 <Tooltip text="View generated videos">
                    <Link to="/videos" className="p-2 rounded-lg hover:bg-brand-dark-light transition-colors">
                        <Eye size={20} className="text-gray-300" />
                    </Link>
                </Tooltip>
                <Tooltip text="Adjust generation settings">
                    <button type="button" onClick={() => setShowSettings(!showSettings)} className={`p-2 rounded-lg transition-colors ${showSettings ? 'bg-brand-accent text-white' : 'hover:bg-brand-dark-light text-gray-300'}`}>
                        <Settings size={20} />
                    </button>
                </Tooltip>
            </div>
            <Tooltip text="Generate C-Struct">
              <button type="submit" disabled={!isGenerateEnabled || isLoading} className="p-3 rounded-lg transition-colors bg-brand-accent text-white disabled:bg-brand-dark-light disabled:text-gray-500 disabled:cursor-not-allowed">
                  <ArrowRight size={20} />
              </button>
            </Tooltip>
          </div>
          <input type="file" id="file-upload-input" className="hidden" onChange={(e) => handleFileChange(e.target.files[0])} />
        </form>
        {isLoading && (
          <div className="mt-4 text-center text-gray-400">
            <p>Generating, please wait...</p>
          </div>
        )}
      </div>

      {/* Collapsible Settings Panel */}
      {showSettings && (
        <div className="bg-brand-ui-bg p-6 rounded-2xl border-2 border-brand-dark-light mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                    <SettingsSection title="Grid">
                        <div>
                            <label className="block text-xs text-gray-400">Width: {formData.grid_width}px</label>
                            <input type="range" name="grid_width" value={formData.grid_width} onChange={handleChange} min="4" max="50" className="w-full accent-brand-accent" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Height: {formData.grid_height}px</label>
                            <input type="range" name="grid_height" value={formData.grid_height} onChange={handleChange} min="4" max="50" className="w-full accent-brand-accent" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Cell Aspect Ratio: {formData.cell_aspect_ratio}</label>
                            <input type="range" name="cell_aspect_ratio" value={formData.cell_aspect_ratio} onChange={handleChange} step="0.1" min="0.5" max="3.0" className="w-full accent-brand-accent" />
                        </div>
                    </SettingsSection>
                    <SettingsSection title="Filter">
                        <label className="flex items-center text-sm text-gray-300">
                            <input type="checkbox" name="enhance_contrast" checked={formData.enhance_contrast} onChange={handleChange} className="rounded border-gray-500 bg-brand-dark text-brand-accent focus:ring-brand-accent mr-2" />
                            <span>Enable contrast enhancement</span>
                        </label>
                        <div className="pt-2">
                            <label className="block text-xs text-gray-400">Contrast Strength: {formData.sigmoid_k}</label>
                            <input type="range" name="sigmoid_k" value={formData.sigmoid_k} onChange={handleChange} step="0.001" min="0.001" max="0.1" className="w-full accent-brand-accent" disabled={!formData.enhance_contrast}/>
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Contrast Center: {formData.sigmoid_center}</label>
                            <input type="range" name="sigmoid_center" value={formData.sigmoid_center} onChange={handleChange} min="0" max="255" className="w-full accent-brand-accent" disabled={!formData.enhance_contrast}/>
                        </div>
                         <div>
                            <label className="block text-xs text-gray-400">Filter Threshold: {formData.filter_threshold}</label>
                            <input type="range" name="filter_threshold" value={formData.filter_threshold} onChange={handleChange} min="0" max="255" className="w-full accent-brand-accent" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Dimming Threshold: {formData.dimming_threshold}</label>
                            <input type="range" name="dimming_threshold" value={formData.dimming_threshold} onChange={handleChange} min="0" max="255" className="w-full accent-brand-accent" />
                        </div>
                    </SettingsSection>
                    <SettingsSection title="Video">
                        <div>
                            <label className="block text-xs text-gray-400">Input FPS: {formData.fps}</label>
                            <input type="range" name="fps" value={formData.fps} onChange={handleChange} min="1" max="60" className="w-full accent-brand-accent" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400">Output Video FPS: {formData.video_fps}</label>
                            <input type="range" name="video_fps" value={formData.video_fps} onChange={handleChange} min="1" max="30" className="w-full accent-brand-accent" />
                        </div>
                    </SettingsSection>
                    <button type="button" onClick={handleResetDefaults} className="text-xs text-gray-400 hover:text-white underline">Reset to Defaults</button>
                </div>
                <div className="flex flex-col items-center justify-center bg-brand-dark p-2 rounded-lg">
                     <h4 className="text-sm font-medium text-gray-300 mb-2">Live Preview</h4>
                    <div className="w-full h-64 flex items-center justify-center">
                        {isPreviewLoading ? (
                            <p className="text-gray-500 text-xs">Loading Preview...</p>
                        ) : (
                            <img src={previewImage} alt="Live preview" className="max-w-full max-h-full object-contain" style={{ imageRendering: 'pixelated' }}/>
                        )}
                    </div>
                </div>
            </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-8 p-4 bg-red-900/50 border border-red-500/50 text-red-300 rounded-lg" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* MODIFIED: Result section with dynamic copy button */}
      {result && result.c_code && (
        <div className="mt-10">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-2xl font-bold text-brand-header">Generated C Code</h2>
            <button 
                onClick={copyToClipboard} 
                className="inline-flex items-center px-4 py-2 border border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-300 bg-brand-ui-bg hover:bg-brand-dark-light transition-colors w-28 justify-center"
            >
              {copySuccess === 'Copied!' ? (
                <>
                  <Check size={16} className="mr-2 text-green-400" /> Copied
                </>
              ) : copySuccess === 'Failed to copy!' ? (
                <>
                  <X size={16} className="mr-2 text-red-400" /> Failed
                </>
              ) : (
                'Copy Code'
              )}
            </button>
          </div>
          <pre className="bg-brand-ui-bg text-gray-300 p-4 rounded-lg overflow-x-auto text-sm"><code>{result.c_code}</code></pre>
        </div>
      )}
      </div>
    </div>
  );
}

export default HomePage;