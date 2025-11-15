import React, { useState } from 'react';
import { Database, RefreshCw, Settings, MessageSquare, FileText, Github, FileUp, Grid3x3, Upload, Link, GitBranch, CheckCircle, X, Sparkles, ArrowRight, Cloud, Lock, Zap } from 'lucide-react';

const KnowledgeDashboard = () => {
  const [activePage, setActivePage] = useState('knowledge-lake');
  const [selectedSource, setSelectedSource] = useState(null);
  const [fileName, setFileName] = useState('');
  const [inputValue, setInputValue] = useState('');

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
      description: 'Import wikis, docs & pages',
      detail: 'Connect your Confluence workspace to import documentation, meeting notes, and team wikis.',
      gradient: 'from-blue-600 via-blue-500 to-cyan-400',
      hoverGradient: 'hover:from-blue-700 hover:via-blue-600 hover:to-cyan-500',
      iconColor: 'text-blue-600',
      inputType: 'url',
      placeholder: 'https://your-workspace.atlassian.net/wiki/...',
      buttonText: 'Import from Confluence',
      helper: 'Enter the URL of your Confluence space or page'
    },
    {
      id: 'github',
      name: 'GitHub',
      icon: Github,
      description: 'Clone repos & code files',
      detail: 'Connect to GitHub repositories to import code, documentation, and project files.',
      gradient: 'from-gray-800 via-gray-700 to-gray-600',
      hoverGradient: 'hover:from-gray-900 hover:via-gray-800 hover:to-gray-700',
      iconColor: 'text-gray-800',
      inputType: 'clone',
      placeholder: 'https://github.com/username/repository',
      buttonText: 'Clone Repository',
      helper: 'Paste your GitHub repository URL'
    },
    {
      id: 'pdf',
      name: 'PDF Files',
      icon: FileUp,
      description: 'Upload PDF documents',
      detail: 'Upload PDF files including reports, research papers, manuals, and documentation.',
      gradient: 'from-red-600 via-red-500 to-orange-500',
      hoverGradient: 'hover:from-red-700 hover:via-red-600 hover:to-orange-600',
      iconColor: 'text-red-600',
      inputType: 'upload',
      accept: '.pdf',
      buttonText: 'Upload PDF Files',
      helper: 'Drag and drop or click to select files'
    },
    {
      id: 'jira',
      name: 'Jira',
      icon: Grid3x3,
      description: 'Import issues & projects',
      detail: 'Connect your Jira workspace to import tickets, epics, stories, and project data.',
      gradient: 'from-indigo-600 via-purple-500 to-pink-500',
      hoverGradient: 'hover:from-indigo-700 hover:via-purple-600 hover:to-pink-600',
      iconColor: 'text-indigo-600',
      inputType: 'url',
      placeholder: 'https://your-workspace.atlassian.net/browse/...',
      buttonText: 'Connect to Jira',
      helper: 'Enter your Jira project or board URL'
    },
    {
      id: 'spreadsheet',
      name: 'Spreadsheets',
      icon: Grid3x3,
      description: 'Upload Excel & CSV files',
      detail: 'Import data from Excel spreadsheets and CSV files for analysis and processing.',
      gradient: 'from-green-600 via-emerald-500 to-teal-500',
      hoverGradient: 'hover:from-green-700 hover:via-emerald-600 hover:to-teal-600',
      iconColor: 'text-green-600',
      inputType: 'upload',
      accept: '.xlsx,.xls,.csv',
      buttonText: 'Upload Spreadsheet',
      helper: 'Supports XLSX, XLS, and CSV formats'
    }
  ];

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFileName(e.target.files[0].name);
    }
  };

  const handleSubmit = () => {
    const source = dataSources.find(s => s.id === selectedSource);
    alert(`✅ Successfully connected to ${source.name}!`);
    setFileName('');
    setInputValue('');
    setSelectedSource(null);
  };

  const renderContent = () => {
    if (activePage === 'knowledge-lake') {
      return (
        <div className="h-full flex flex-col">
          {!selectedSource ? (
            <>
              {/* Header Section */}
              <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 text-white p-12">
                <div className="max-w-6xl mx-auto">
                  <div className="flex items-center space-x-3 mb-4">
                    <Sparkles size={32} />
                    <h1 className="text-5xl font-bold">Connect Your Data Sources</h1>
                  </div>
                  <p className="text-xl text-white text-opacity-90 max-w-3xl">
                    Build a unified knowledge base by connecting your favorite tools and platforms. Choose a source below to get started.
                  </p>
                </div>
              </div>

              {/* Sources Grid */}
              <div className="flex-1 bg-gray-50 p-12">
                <div className="max-w-6xl mx-auto">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {dataSources.map((source) => {
                      const Icon = source.icon;
                      return (
                        <button
                          key={source.id}
                          onClick={() => setSelectedSource(source.id)}
                          className="group relative bg-white rounded-3xl p-8 shadow-md hover:shadow-2xl transition-all duration-500 text-left border-2 border-transparent hover:border-indigo-200 overflow-hidden"
                        >
                          {/* Gradient Background on Hover */}
                          <div className={`absolute inset-0 bg-gradient-to-br ${source.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}></div>
                          
                          <div className="relative flex items-start space-x-6">
                            {/* Icon */}
                            <div className={`flex-shrink-0 w-20 h-20 rounded-2xl bg-gradient-to-br ${source.gradient} flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-transform duration-500`}>
                              <Icon className="text-white" size={36} />
                            </div>
                            
                            {/* Content */}
                            <div className="flex-1 min-w-0">
                              <h3 className="text-2xl font-bold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">
                                {source.name}
                              </h3>
                              <p className="text-gray-600 mb-3 leading-relaxed">
                                {source.detail}
                              </p>
                              <div className="flex items-center space-x-2 text-indigo-600 font-semibold group-hover:translate-x-2 transition-transform duration-300">
                                <span>Get Started</span>
                                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                              </div>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>

                  {/* Stats Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-100">
                      <div className="flex items-center justify-between mb-3">
                        <Cloud className="text-blue-500" size={32} />
                        <span className="text-sm font-medium text-gray-500">Active</span>
                      </div>
                      <div className="text-3xl font-bold text-gray-900 mb-1">247</div>
                      <div className="text-sm text-gray-600">Connected Sources</div>
                    </div>
                    <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-100">
                      <div className="flex items-center justify-between mb-3">
                        <Zap className="text-yellow-500" size={32} />
                        <span className="text-sm font-medium text-gray-500">Speed</span>
                      </div>
                      <div className="text-3xl font-bold text-gray-900 mb-1">3.2TB</div>
                      <div className="text-sm text-gray-600">Data Synced</div>
                    </div>
                    <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-100">
                      <div className="flex items-center justify-between mb-3">
                        <Lock className="text-green-500" size={32} />
                        <span className="text-sm font-medium text-gray-500">Secure</span>
                      </div>
                      <div className="text-3xl font-bold text-gray-900 mb-1">99.9%</div>
                      <div className="text-sm text-gray-600">Uptime SLA</div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="h-full flex flex-col">
              {/* Header */}
              {(() => {
                const source = dataSources.find(s => s.id === selectedSource);
                const Icon = source.icon;
                
                return (
                  <>
                    <div className={`bg-gradient-to-r ${source.gradient} text-white p-10`}>
                      <div className="max-w-4xl mx-auto">
                        <button
                          onClick={() => {
                            setSelectedSource(null);
                            setFileName('');
                            setInputValue('');
                          }}
                          className="flex items-center space-x-2 text-white text-opacity-90 hover:text-opacity-100 font-medium mb-6 transition-all"
                        >
                          <ArrowRight size={20} className="rotate-180" />
                          <span>Back to sources</span>
                        </button>
                        
                        <div className="flex items-center space-x-5">
                          <div className="w-20 h-20 bg-white bg-opacity-20 backdrop-blur rounded-2xl flex items-center justify-center">
                            <Icon size={40} />
                          </div>
                          <div>
                            <h2 className="text-4xl font-bold mb-2">{source.name}</h2>
                            <p className="text-lg text-white text-opacity-90">{source.detail}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Form Section */}
                    <div className="flex-1 bg-gray-50 p-10 overflow-auto">
                      <div className="max-w-4xl mx-auto">
                        <div className="bg-white rounded-3xl shadow-xl border border-gray-200 overflow-hidden">
                          <div className="p-10">
                            {source.inputType === 'upload' ? (
                              <div className="space-y-6">
                                <div>
                                  <label className="block text-lg font-semibold text-gray-900 mb-3">
                                    Choose File
                                  </label>
                                  <p className="text-gray-600 mb-4">{source.helper}</p>
                                </div>

                                <label className="block">
                                  <div className="relative border-3 border-dashed border-gray-300 rounded-2xl p-20 text-center hover:border-indigo-400 hover:bg-gradient-to-br hover:from-indigo-50 hover:to-purple-50 transition-all cursor-pointer group">
                                    <Upload className="mx-auto text-gray-400 group-hover:text-indigo-500 mb-6 group-hover:scale-110 transition-all" size={64} />
                                    <div className="text-2xl font-bold text-gray-700 mb-3">
                                      {fileName || 'Drop files here or click to browse'}
                                    </div>
                                    <p className="text-gray-500 text-lg">
                                      {source.accept.replace(/\./g, '').toUpperCase()} • Max size 100MB
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
                                  <div className="flex items-center justify-between p-6 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 rounded-2xl">
                                    <div className="flex items-center space-x-4">
                                      <CheckCircle className="text-green-600 flex-shrink-0" size={28} />
                                      <div>
                                        <div className="font-bold text-green-900 text-lg">{fileName}</div>
                                        <div className="text-green-700 text-sm">Ready to upload</div>
                                      </div>
                                    </div>
                                    <button
                                      onClick={(e) => {
                                        e.preventDefault();
                                        setFileName('');
                                      }}
                                      className="text-green-600 hover:text-green-800 p-2"
                                    >
                                      <X size={24} />
                                    </button>
                                  </div>
                                )}
                              </div>
                            ) : source.inputType === 'clone' ? (
                              <div className="space-y-6">
                                <div>
                                  <label className="block text-lg font-semibold text-gray-900 mb-3">
                                    Repository URL
                                  </label>
                                  <p className="text-gray-600 mb-4">{source.helper}</p>
                                  <div className="relative">
                                    <Link className="absolute left-6 top-1/2 transform -translate-y-1/2 text-gray-400" size={24} />
                                    <input
                                      type="text"
                                      value={inputValue}
                                      onChange={(e) => setInputValue(e.target.value)}
                                      placeholder={source.placeholder}
                                      className="w-full pl-16 pr-6 py-5 border-2 border-gray-300 rounded-2xl focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 outline-none text-lg transition-all"
                                    />
                                  </div>
                                </div>

                                <div>
                                  <label className="block text-lg font-semibold text-gray-900 mb-3">
                                    Branch (optional)
                                  </label>
                                  <div className="relative">
                                    <GitBranch className="absolute left-6 top-1/2 transform -translate-y-1/2 text-gray-400" size={24} />
                                    <input
                                      type="text"
                                      placeholder="main"
                                      className="w-full pl-16 pr-6 py-5 border-2 border-gray-300 rounded-2xl focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 outline-none text-lg transition-all"
                                    />
                                  </div>
                                </div>

                                <div className="flex items-start space-x-3 p-5 bg-blue-50 border-2 border-blue-200 rounded-2xl">
                                  <input type="checkbox" id="private" className="w-5 h-5 mt-1 text-indigo-600 rounded" />
                                  <label htmlFor="private" className="text-gray-700 font-medium">
                                    This is a private repository (requires authentication)
                                  </label>
                                </div>
                              </div>
                            ) : (
                              <div className="space-y-6">
                                <div>
                                  <label className="block text-lg font-semibold text-gray-900 mb-3">
                                    {source.name} URL
                                  </label>
                                  <p className="text-gray-600 mb-4">{source.helper}</p>
                                  <div className="relative">
                                    <Link className="absolute left-6 top-1/2 transform -translate-y-1/2 text-gray-400" size={24} />
                                    <input
                                      type="text"
                                      value={inputValue}
                                      onChange={(e) => setInputValue(e.target.value)}
                                      placeholder={source.placeholder}
                                      className="w-full pl-16 pr-6 py-5 border-2 border-gray-300 rounded-2xl focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 outline-none text-lg transition-all"
                                    />
                                  </div>
                                </div>

                                <div className="flex items-start space-x-3 p-5 bg-amber-50 border-2 border-amber-200 rounded-2xl">
                                  <div className="text-2xl">💡</div>
                                  <p className="text-amber-900 font-medium">
                                    Make sure you have the necessary permissions to access this resource
                                  </p>
                                </div>
                              </div>
                            )}

                            <button
                              onClick={handleSubmit}
                              className={`w-full mt-8 bg-gradient-to-r ${source.gradient} ${source.hoverGradient} text-white font-bold py-6 rounded-2xl shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300 text-xl`}
                            >
                              {source.buttonText}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                );
              })()}
            </div>
          )}
        </div>
      );
    } else if (activePage === 'knowledge-sync') {
      return (
        <div className="p-12">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center space-x-4 mb-4">
              <RefreshCw className="text-purple-600" size={40} />
              <h1 className="text-4xl font-bold text-gray-900">Knowledge Sync</h1>
            </div>
            <p className="text-xl text-gray-600">Manage automated synchronization and data updates</p>
          </div>
        </div>
      );
    } else if (activePage === 'settings') {
      return (
        <div className="p-12">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center space-x-4 mb-4">
              <Settings className="text-gray-600" size={40} />
              <h1 className="text-4xl font-bold text-gray-900">Settings</h1>
            </div>
            <p className="text-xl text-gray-600">Configure your workspace and preferences</p>
          </div>
        </div>
      );
    } else if (activePage === 'chatbot') {
      return (
        <div className="p-12">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center space-x-4 mb-4">
              <MessageSquare className="text-green-600" size={40} />
              <h1 className="text-4xl font-bold text-gray-900">Chatbot</h1>
            </div>
            <p className="text-xl text-gray-600">Ask questions and interact with your knowledge base</p>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <div className="w-72 bg-gradient-to-b from-gray-900 to-gray-800 text-white flex flex-col shadow-2xl">
        <div className="p-8 border-b border-gray-700">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Database size={24} />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Knowledge Hub</h2>
            </div>
          </div>
          <p className="text-sm text-gray-400">Enterprise Platform</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
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
                  setInputValue('');
                }}
                className={`w-full flex items-center space-x-4 px-5 py-4 rounded-xl transition-all duration-300 ${
                  isActive
                    ? 'bg-white text-gray-900 shadow-lg'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                <Icon size={22} />
                <span className="font-semibold text-lg">{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="p-6 border-t border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-11 h-11 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
              A
            </div>
            <div className="flex-1">
              <div className="text-sm font-semibold">Admin User</div>
              <div className="text-xs text-gray-400">admin@company.com</div>
            </div>
          </div>
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