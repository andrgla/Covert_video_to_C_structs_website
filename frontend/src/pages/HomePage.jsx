// frontend/src/pages/HomePage.jsx

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Eye, Settings, ArrowRight, Upload, Check, X, Square } from 'lucide-react';

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
      <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 w-max bg-gray-800 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
        {text}
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
  const [showVideos, setShowVideos] = useState(false);
  const [videos, setVideos] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [copySuccess, setCopySuccess] = useState('');
  const [settingsHeight, setSettingsHeight] = useState(0);
  const [currentLoadingMessage, setCurrentLoadingMessage] = useState(0);
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const settingsRef = useRef(null);
  const loadingIntervalRef = useRef(null);
  const typingIntervalRef = useRef(null);
  const fadeTimeoutRef = useRef(null);


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

  // Fetch videos when video panel opens
  useEffect(() => {
    if (showVideos) {
      fetch('/api/videos')
        .then(response => response.json())
        .then(data => setVideos(data))
        .catch(error => console.error('Error fetching videos:', error));
    }
  }, [showVideos]);

  // Measure settings panel height when it changes
  useEffect(() => {
    if (showSettings && settingsRef.current) {
      const height = settingsRef.current.offsetHeight;
      setSettingsHeight(height);
    }
  }, [showSettings, formData]); // Re-measure when settings change

  // Handle loading message cycling with typing animation
  useEffect(() => {
    if (isLoading) {
      setCurrentLoadingMessage(0);
      const messages = getLoadingMessages();
      
      // Start typing the first message immediately
      typeMessage(messages[0]);
      
      let messageIndex = 0;
      loadingIntervalRef.current = setInterval(() => {
        messageIndex = (messageIndex + 1) % messages.length;
        setCurrentLoadingMessage(messageIndex);
        
        // Clear any existing typing animation and timeouts
        if (typingIntervalRef.current) {
          clearInterval(typingIntervalRef.current);
        }
        if (fadeTimeoutRef.current) {
          clearTimeout(fadeTimeoutRef.current);
        }
        
        // Start typing the next message
        typeMessage(messages[messageIndex]);
      }, 4500); // Change message every 4.5 seconds (typing + display + fade)
          } else {
        // Clear all intervals when not loading
        if (loadingIntervalRef.current) {
          clearInterval(loadingIntervalRef.current);
          loadingIntervalRef.current = null;
        }
        if (typingIntervalRef.current) {
          clearInterval(typingIntervalRef.current);
          typingIntervalRef.current = null;
        }
        if (fadeTimeoutRef.current) {
          clearTimeout(fadeTimeoutRef.current);
          fadeTimeoutRef.current = null;
        }
        setCurrentLoadingMessage(0);
        setDisplayedText('');
        setIsTyping(false);
        setIsFadingOut(false);
      }

    return () => {
      if (loadingIntervalRef.current) {
        clearInterval(loadingIntervalRef.current);
      }
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }
      if (fadeTimeoutRef.current) {
        clearTimeout(fadeTimeoutRef.current);
      }
    };
  }, [isLoading, formData.fps, formData.struct_name]);

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
    setCopySuccess('');
    const data = new FormData();
    data.append('file', selectedFile);
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    // Use input FPS as output video FPS (they should be the same)
    data.append('video_fps', formData.fps);
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
  
  const copyToClipboard = async () => {
    if (!result || !result.c_code) return;

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
        setTimeout(() => setCopySuccess(''), 2000);
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

  // Dynamic loading messages
  const getLoadingMessages = () => {
    const frameCount = Math.floor(Math.random() * 50) + 10; // Random frame count for demo
    return [
      "Generating, please wait...",
      `Slicing video to ${formData.fps} frames per second...`,
      `Success! Extracted ${frameCount} frames...`,
      `Validating C struct data for ${frameCount} frames...`,
      "C struct array saved",
      `Generated animation video: ${formData.struct_name}_animation.mp4`
    ];
  };

  // Typing animation function with smooth transitions and fade-out
  const typeMessage = (message, callback) => {
    setIsFadingOut(false);
    setDisplayedText('');
    setIsTyping(true);
    let currentIndex = 0;
    
    typingIntervalRef.current = setInterval(() => {
      if (currentIndex <= message.length) {
        setDisplayedText(message.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(typingIntervalRef.current);
        setIsTyping(false);
        // Keep the message displayed for longer before transitioning
        fadeTimeoutRef.current = setTimeout(() => {
          // Start fade-out animation
          setIsFadingOut(true);
          // After fade-out completes, trigger callback
          setTimeout(() => {
            if (callback) callback();
          }, 500); // Fade-out duration
        }, 2000); // Display complete message for 2 seconds
      }
    }, 60); // Smooth typing: 60ms per character
  };

  return (
    <div className={`pt-32 ${showSettings ? 'pb-96' : 'pb-8'}`}>
      <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-10">
                 <h1 className="font-mono text-4xl md:text-5xl text-brand-header tracking-wider mb-2">C-CONVERTER</h1>
        <p className="text-gray-400">Upload a video or image to generate C-struct animations.</p>
      </div>

      {/* MODIFIED: Container for layering */}
      <div className="relative">
        {/* MODIFIED: Input Bar with dynamic classes */}
        <form 
          onSubmit={handleSubmit}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`relative z-10 bg-brand-ui-bg transition-all duration-300 flex flex-col p-4 border
            ${isDragOver ? 'border-brand-accent' : 'border-gray-500 hover:border-gray-400'}
            ${showSettings || showVideos ? 'rounded-t-2xl border-b-transparent' : 'rounded-2xl'}`
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
                        <Upload size={18} className={selectedFile ? "text-[#91d16c]" : "text-gray-400"} />
                        <span className={`text-sm ${selectedFile ? "text-white" : "text-gray-400"} truncate max-w-40`}>
                            {selectedFile ? selectedFile.name : "Upload"}
                        </span>
                    </button>
                </Tooltip>
                 <Tooltip text="View generated videos">
                    <button type="button" onClick={() => {
                      setShowVideos(!showVideos);
                      if (!showVideos) setShowSettings(false);
                    }} className={`p-2 rounded-lg transition-colors ${showVideos ? 'bg-brand-accent text-white' : 'hover:bg-brand-dark-light text-gray-300'}`}>
                        <Eye size={20} />
                    </button>
                </Tooltip>
                <Tooltip text="Adjust generation settings">
                    <button type="button" onClick={() => {
                      setShowSettings(!showSettings);
                      if (!showSettings) setShowVideos(false);
                    }} className={`p-2 rounded-lg transition-colors ${showSettings ? 'bg-brand-accent text-white' : 'hover:bg-brand-dark-light text-gray-300'}`}>
                        <Settings size={20} />
                    </button>
                </Tooltip>
            </div>
                          <Tooltip text="Generate C-Struct">
                  <button 
                    type="submit" 
                    disabled={!isGenerateEnabled || isLoading} 
                    className={`p-3 rounded-lg transition-colors text-white disabled:bg-brand-dark-light disabled:text-gray-500 disabled:cursor-not-allowed
                      ${isGenerateEnabled ? 'bg-[#91d16c] hover:bg-[#76a859]' : 'bg-brand-accent'}`}
                  >
                      {isLoading ? <Square size={20} className="text-white" /> : <ArrowRight size={20} className="text-white" />}
                  </button>
              </Tooltip>
          </div>
          <input type="file" id="file-upload-input" className="hidden" onChange={(e) => handleFileChange(e.target.files[0])} />
        </form>

                 {/* MODIFIED: Settings panel with adjusted classes for seamless overlap */}
         {showSettings && (
           <div className="bg-brand-ui-bg p-6 rounded-b-2xl border-x border-b border-gray-500 shadow-[0_20px_50px_-12px_rgba(0,0,0,0.6)] -mt-1 mb-0">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                                            <SettingsSection title="Grid">
                        <div className="grid grid-cols-3 gap-3">
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Width</label>
                                <input type="number" name="grid_width" value={formData.grid_width} onChange={handleChange} min="4" max="50" className="w-full px-2 py-1 bg-brand-dark border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-brand-accent" />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Height</label>
                                <input type="number" name="grid_height" value={formData.grid_height} onChange={handleChange} min="4" max="50" className="w-full px-2 py-1 bg-brand-dark border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-brand-accent" />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Ratio</label>
                                <input type="number" name="cell_aspect_ratio" value={formData.cell_aspect_ratio} onChange={handleChange} step="0.1" min="0.5" max="3.0" className="w-full px-2 py-1 bg-brand-dark border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-brand-accent" />
                            </div>
                        </div>
                    </SettingsSection>
                        <SettingsSection title="Filter">
                            <label className="flex items-center text-sm text-gray-300">
                                <input type="checkbox" name="enhance_contrast" checked={formData.enhance_contrast} onChange={handleChange} className="rounded border-gray-500 bg-brand-dark accent-[#91d16c] focus:ring-[#91d16c] mr-2" />
                                <span>Enable contrast enhancement</span>
                            </label>
                            <div className="pt-2">
                                <label className="block text-xs text-gray-400">Contrast Strength: {formData.sigmoid_k}</label>
                                <input type="range" name="sigmoid_k" value={formData.sigmoid_k} onChange={handleChange} step="0.001" min="0.001" max="0.1" className="w-full accent-[#91d16c]" disabled={!formData.enhance_contrast}/>
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400">Contrast Center: {formData.sigmoid_center}</label>
                                <input type="range" name="sigmoid_center" value={formData.sigmoid_center} onChange={handleChange} min="0" max="255" className="w-full accent-[#91d16c]" disabled={!formData.enhance_contrast}/>
                            </div>
                             <div>
                                <label className="block text-xs text-gray-400">Filter Threshold: {formData.filter_threshold}</label>
                                <input type="range" name="filter_threshold" value={formData.filter_threshold} onChange={handleChange} min="0" max="255" className="w-full accent-[#91d16c]" />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400">Dimming Threshold: {formData.dimming_threshold}</label>
                                <input type="range" name="dimming_threshold" value={formData.dimming_threshold} onChange={handleChange} min="0" max="255" className="w-full accent-[#91d16c]" />
                            </div>
                        </SettingsSection>
                                            <SettingsSection title="Video">
                        <div className="w-32">
                            <label className="block text-xs text-gray-400 mb-1">Input FPS</label>
                            <input type="number" name="fps" value={formData.fps} onChange={handleChange} min="1" max="60" className="w-full px-2 py-1 bg-brand-dark border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-brand-accent" />
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

         {/* Videos Panel */}
         {showVideos && (
           <div className="bg-brand-ui-bg p-6 rounded-b-2xl border-x border-b border-gray-500 shadow-[0_20px_50px_-12px_rgba(0,0,0,0.6)] -mt-1 mb-0">
             <h3 className="text-lg font-semibold mb-4 text-brand-header">Generated Videos</h3>
             {videos.length === 0 ? (
               <p className="text-gray-400 text-center py-8">No videos generated yet. Upload a video to create animations!</p>
             ) : (
               <div className="grid grid-cols-1 gap-6">
                 {videos.map((video, index) => (
                   <div key={index} className="bg-brand-dark rounded-lg p-6 flex flex-col items-center">
                     <h4 className="text-white font-medium mb-2 text-center">{video.name}</h4>
                     <p className="text-gray-400 text-sm mb-4 text-center">Folder: {video.folder}</p>
                     <video 
                       controls 
                       preload="metadata" 
                       className="rounded shadow-lg"
                       style={{ maxWidth: '600px', maxHeight: '400px', width: '100%' }}
                     >
                       <source src={video.path} type="video/mp4" />
                       Your browser does not support the video tag.
                     </video>
                     <p className="text-gray-500 text-xs mt-3 text-center">Size: {Math.round(video.size / 1024)} KB</p>
                   </div>
                 ))}
               </div>
             )}
           </div>
         )}
 
         {isLoading && (
           <div className="mt-4 text-center text-gray-400">
             <p className={`font-mono transition-all duration-500 ease-in-out ${
               isFadingOut ? 'opacity-0 transform translate-y-2' : 'opacity-100 transform translate-y-0'
             }`}>
               <span className="inline-block">
                 {displayedText.split('').map((char, index) => (
                   <span 
                     key={`${currentLoadingMessage}-${index}`}
                     className="inline-block animate-[fadeInRight_0.4s_ease-out] opacity-0"
                     style={{
                       animationDelay: `${index * 30}ms`,
                       animationFillMode: 'forwards'
                     }}
                   >
                     {char === ' ' ? '\u00A0' : char}
                   </span>
                 ))}
               </span>
             </p>
           </div>
         )}
         
         {/* Extra space when settings are open for better scrolling */}
         {showSettings && <div className="h-96"></div>}
       </div>



      {/* Error Message */}
      {error && (
        <div className={`mt-8 p-4 bg-red-900/50 border border-red-500/50 text-red-300 rounded-lg ${showSettings ? 'relative z-0' : ''}`} role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Result section with dynamic copy button */}
      {result && result.c_code && (
        <div className={`${showSettings || showVideos ? 'mt-0 relative z-0' : 'mt-10'}`}>
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
          <pre className="bg-brand-ui-bg text-gray-300 p-4 rounded-lg overflow-x-auto text-sm font-mono"><code>{result.c_code}</code></pre>
        </div>
      )}
      </div>
    </div>
  );
}

export default HomePage;