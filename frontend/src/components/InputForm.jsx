import React, { useState } from 'react';

const InputForm = ({ onSubmit, isLoading }) => {
    const [activeTab, setActiveTab] = useState('text'); // 'text', 'upload', 'youtube'
    const [formData, setFormData] = useState({
        text: '',
        url: '',
        context: '',
        file: null
    });

    const handleChange = (e) => {
        const { name, value, files } = e.target;
        if (name === 'file') {
            setFormData(prev => ({ ...prev, file: files[0] }));
        } else {
            setFormData(prev => ({ ...prev, [name]: value }));
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        // Construct FormData
        const data = new FormData();
        if (activeTab === 'text') {
            data.append('text', formData.text);
        } else if (activeTab === 'upload' && formData.file) {
            data.append('file', formData.file);
        } else if (activeTab === 'youtube') {
            data.append('url', formData.url);
        }

        if (formData.context) {
            data.append('context', formData.context);
        }

        onSubmit(data);
    };

    const tabs = [
        { id: 'text', label: 'Text Analysis' },
        { id: 'upload', label: 'Video Upload' },
        { id: 'youtube', label: 'YouTube URL' },
    ];

    return (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700">
            <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white">Analyze Content</h2>

            {/* Tabs */}
            <div className="flex space-x-2 mb-6 border-b border-gray-200 dark:border-gray-700">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`pb-2 px-4 text-sm font-medium transition-colors relative ${activeTab === tab.id
                                ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400'
                                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                            }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">

                {/* Text Input */}
                {activeTab === 'text' && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Content Text</label>
                        <textarea
                            name="text"
                            rows="4"
                            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all resize-none"
                            placeholder="Paste text content here..."
                            value={formData.text}
                            onChange={handleChange}
                            required
                        />
                    </div>
                )}

                {/* Video Upload */}
                {activeTab === 'upload' && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Upload Video</label>
                        <input
                            type="file"
                            name="file"
                            accept="video/*"
                            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 dark:file:bg-gray-600 dark:file:text-indigo-300"
                            onChange={handleChange}
                            required
                        />
                    </div>
                )}

                {/* YouTube Input */}
                {activeTab === 'youtube' && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">YouTube URL</label>
                        <input
                            type="url"
                            name="url"
                            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all"
                            placeholder="https://youtube.com/..."
                            value={formData.url}
                            onChange={handleChange}
                            required
                        />
                    </div>
                )}

                <button
                    type="submit"
                    disabled={isLoading}
                    className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all transform ${isLoading
                            ? 'bg-indigo-400 cursor-not-allowed'
                            : 'bg-indigo-600 hover:bg-indigo-700 active:scale-95 shadow-md hover:shadow-lg'
                        }`}
                >
                    {isLoading ? (
                        <span className="flex items-center justify-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Analyzing...
                        </span>
                    ) : 'Analyze Content'}
                </button>
            </form>
        </div>
    );
};

export default InputForm;
