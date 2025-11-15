import React, { useState } from 'react';
import { Database, RefreshCw, Settings, MessageSquare, FileText, Github, FileUp, Grid3x3, Upload, Link, GitBranch, CheckCircle } from 'lucide-react';

const KnowledgeDashboard = () => {
  const [activePage, setActivePage] = useState('knowledge-lake');
  const [selectedSource, setSelectedSource] = useState(null);
  const [fileName, setFileName] = useState('');

  const sidebarItems = [
    { id: 'knowledge-lake', name: 'Knowledge Lake', icon: Database },
    { id: 'knowledge-sync', name: 'Knowledge Sync', icon: RefreshCw },
    { id: 'settings', name: 'Settings', icon: Settings },
    { id: 'chatbot', name: 'Chatbot', icon: MessageSquare }
  ];

  const dataSources = [
    {
      id: 'confluence',
      name: 'Confluence',
      icon: FileText,
      description: 'Import from Confluence pages',
      color: 'from-blue-500 to-blue-600',
      inputType: 'url',
      placeholder: 'https://your-domain.atlassian.net/wiki/...',
      buttonText: 'Connect Confluence'
    },
    {
      id: 'github',
      name: 'GitHub',
      icon: Github,
      description: 'Clone a GitHub repository',
      color: 'from-gray-700 to-gray-900',
      inputType: 'clone',
      placeholder: 'https://github.com/username/repository',
      buttonText: 'Clone Repository'
    },
    {
      id: 'pdf',
      name: 'PDF',
      icon: FileUp,
      description: 'Upload PDF documents',
      color: 'from-red-500 to-red-600',
      inputType: 'upload',
      accept: '.pdf',
      buttonText: 'Upload PDF'
    },
    {
      id: 'jira',
      name: 'Jira',
      icon: Grid3x3,
      description: 'Connect to Jira projects',
      color: 'from-blue-600 to-indigo-600',
      inputType: 'url',
      placeholder: 'https://your-domain.atlassian.net/browse/...',
      buttonText: 'Connect Jira'
    },
    {
      id: 'spreadsheet',
      name: 'Spreadsheet',
      icon: FileText,
      description: 'Upload Excel or CSV files',
      color: 'from-green-500 to-green-600',
      inputType: 'upload',
      accept: '.xlsx,.xls,.csv',
      buttonText: 'Upload Spreadsheet'
    }
  ];

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFileName(e.target.files[0].name);
    }
  };

  const handleSubmit = () => {
    console.log('Submitted:', selectedSource);
    setFileName('');
  };

  const renderContent = () => {
    if (activePage === 'knowledge-lake') {
      return (
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Knowledge Lake</h1>
            <p className="text-gray-600">Import data from various sources to build your knowledge base</p>
          </div>

          {!selectedSource ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {dataSources.map((source) => {
                const Icon = source.icon;
                return (
                  <button
                    key={source.id}
                    onClick={() => setSelectedSource(source.id)}
                    className="group relative bg-white rounded-xl p-6 border-2 border-gray-200 hover:border-indigo-500 transition-all duration-300 hover:shadow-xl text-left"
                  >
                    <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${source.color} mb-4`}>
                      <Icon className="text-white" size={28} />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{source.name}</h3>
                    <p className="text-gray-600 text-sm">{source.description}</p>
                    <div className="mt-4 text-indigo-600 font-medium group-hover:translate-x-1 transition-transform inline-block">
                      Connect →
                    </div>
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="max-w-3xl">
              <button
                onClick={() => {
                  setSelectedSource(null);
                  setFileName('');
                }}
                className="mb-6 text-indigo-600 hover:text-indigo-700 font-medium"
              >
                ← Back to sources
              </button>

              {(() => {
                const source = dataSources.find(s => s.id === selectedSource);
                const Icon = source.icon;
                
                return (
                  <div className="bg-white rounded-xl border-2 border-gray-200 p-8">
                    <div className="flex items-center space-x-4 mb-6">
                      <div className={`p-3 rounded-lg bg-gradient-to-br ${source.color}`}>
                        <Icon className="text-white" size={32} />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900">{source.name}</h2>
                        <p className="text-gray-600">{source.description}</p>
                      </div>
                    </div>

                    <div className="space-y-6">
                      {source.inputType === 'upload' ? (
                        <>
                          <label className="block">
                            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-indigo-400 hover:bg-indigo-50 transition-all cursor-pointer">
                              <Upload className="mx-auto text-gray-400 mb-4" size={48} />
                              <div className="text-lg font-medium text-gray-700 mb-2">
                                {fileName || 'Click to upload or drag and drop'}
                              </div>
                              <p className="text-gray-500 text-sm">
                                Supported formats: {source.accept.replace(/\./g, '').toUpperCase()}
                              </p>
                              <input
                                type="file"
                                accept={source.accept}
                                className="hidden"
                                onChange={handleFileChange}
                              />
                            </div>
                          </label>

                          {fileName && (
                            <div className="flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                              <CheckCircle className="text-green-600" size={20} />
                              <span className="text-green-800 font-medium">{fileName}</span>
                            </div>
                          )}
                        </>
                      ) : source.inputType === 'clone' ? (
                        <>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Repository URL
                            </label>
                            <div className="relative">
                              <Link className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                              <input
                                type="text"
                                placeholder={source.placeholder}
                                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                              />
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Branch (optional)
                            </label>
                            <div className="relative">
                              <GitBranch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                              <input
                                type="text"
                                placeholder="main"
                                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                              />
                            </div>
                          </div>

                          <div className="flex items-center space-x-2 p-4 bg-blue-50 rounded-lg">
                            <input type="checkbox" id="private" className="w-4 h-4 text-indigo-600" />
                            <label htmlFor="private" className="text-sm text-gray-700">
                              Private repository (requires authentication)
                            </label>
                          </div>
                        </>
                      ) : (
                        <>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              {source.name} URL
                            </label>
                            <div className="relative">
                              <Link className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                              <input
                                type="text"
                                placeholder={source.placeholder}
                                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                              />
                            </div>
                          </div>

                          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <p className="text-sm text-yellow-800">
                              💡 Ensure you have the necessary permissions to access this resource
                            </p>
                          </div>
                        </>
                      )}

                      <button
                        onClick={handleSubmit}
                        className={`w-full bg-gradient-to-r ${source.color} text-white font-semibold py-3 rounded-lg hover:opacity-90 transition-opacity shadow-lg`}
                      >
                        {source.buttonText}
                      </button>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </div>
      );
    } else if (activePage === 'knowledge-sync') {
      return (
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Knowledge Sync</h1>
          <p className="text-gray-600">Synchronization settings and status</p>
        </div>
      );
    } else if (activePage === 'settings') {
      return (
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
          <p className="text-gray-600">Configure your application preferences</p>
        </div>
      );
    } else if (activePage === 'chatbot') {
      return (
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Chatbot</h1>
          <p className="text-gray-600">Interact with your knowledge base</p>
        </div>
      );
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Knowledge Hub</h2>
          <p className="text-xs text-gray-500 mt-1">Data Management</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActivePage(item.id);
                  setSelectedSource(null);
                  setFileName('');
                }}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon size={20} />
                <span className="font-medium">{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500">v1.0.0</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {renderContent()}
      </div>
    </div>
  );
};

export default KnowledgeDashboard;