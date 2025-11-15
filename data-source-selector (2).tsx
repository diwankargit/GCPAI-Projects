import React, { useState } from 'react';
import { Database, RefreshCw, Settings, MessageSquare, FileText, Github, FileUp, Grid3x3, Upload, Link, GitBranch, CheckCircle, X, ArrowRight, Shield, Lock, Zap } from 'lucide-react';

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
      detail: 'Connect your Confluence workspace to import documentation, meeting notes, and team wikis into your knowledge base.',
      iconBg: 'bg-blue-500',
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
      detail: 'Connect to GitHub repositories to import code, documentation, and project files for analysis.',
      iconBg: 'bg-gray-800',
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
      detail: 'Upload PDF files including reports, research papers, manuals, and technical documentation.',
      iconBg: 'bg-red-500',
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
      detail: 'Connect your Jira workspace to import tickets, epics, stories, and project management data.',
      iconBg: 'bg-indigo-600',
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
      detail: 'Import data from Excel spreadsheets and CSV files for structured data analysis and processing.',
      iconBg: 'bg-green-600',
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
        <div className="h-full flex flex-col bg-gray-50">
          {!selectedSource ? (
            <>
              {/* Hero Section - Clean white with subtle accent */}
              <div className="bg-white border-b border-gray-200 py-16 px-8">
                <div className="max-w-6xl mx-auto">
                  <div className="inline-block px-4 py-2 bg-red-50 rounded-full mb-4">
                    <span className="text-sm font-semibold" style={{ color: '#9E1C33' }}>DATA INTEGRATION</span>
                  </div>
                  <h1 className="text-5xl font-bold text-gray-900 mb-4">
                    Connect Your Data Sources
                  </h1>
                  <p className="text-xl text-gray-600 max-w-3xl leading-relaxed">
                    Build a unified knowledge base by connecting your favorite tools and platforms. 
                    Choose a source below to get started and take control of your data.
                  </p>
                </div>
              </div>

              {/* Sources Grid */}
              <div className="flex-1 py-12 px-8">
                <div className="max-w-6xl mx-auto">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
                    {dataSources.map((source) => {
                      const Icon = source.icon;
                      return (
                        <button
                          key={source.id}
                          onClick={() => setSelectedSource(source.id)}
                          className="group relative bg-white rounded-lg p-8 shadow-sm hover:shadow-xl transition-all duration-300 text-left border border-gray-200 hover:border-gray-300"
                        >
                          <div className="flex items-start space-x-6">
                            {/* Icon */}
                            <div className={`flex-shrink-0 w-16 h-16 rounded-lg ${source.iconBg} flex items-center justify-center shadow-sm`}>
                              <Icon className="text-white" size={28} />
                            </div>
                            
                            {/* Content */}
                            <div className="flex-1 min-w-0">
                              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                                {source.name}
                              </h3>
                              <p className="text-gray-600 mb-4 leading-relaxed">
                                {source.detail}
                              </p>
                              <div className="flex items-center space-x-2 font-semibold text-gray-700 group-hover:translate-x-1 transition-transform duration-300">
                                <span>Get Started</span>
                                <ArrowRight size={18} />
                              </div>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>

                  {/* Stats Cards - Clean professional style */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
                      <div className="flex items-center justify-between mb-4">
                        <Shield className="text-blue-600" size={32} />
                      </div>
                      <div className="text-4xl font-bold text-gray-900 mb-2">247</div>
                      <div className="text-gray-600 font-medium">Connected Sources</div>
                    </div>
                    <div className="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
                      <div className="flex items-center justify-between mb-4">
                        <Zap className="text-yellow-500" size={32} />
                      </div>
                      <div className="text-4xl font-bold text-gray-900 mb-2">3.2TB</div>
                      <div className="text-gray-600 font-medium">Data Synced</div>
                    </div>
                    <div className="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
                      <div className="flex items-center justify-between mb-4">
                        <Lock className="text-green-600" size={32} />
                      </div>
                      <div className="text-4xl font-bold text-gray-900 mb-2">99.9%</div>
                      <div className="text-gray-600 font-medium">Uptime SLA</div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="h-full flex flex-col bg-white">
              {/* Header - Minimal red accent */}
              {(() => {
                const source = dataSources.find(s => s.id === selectedSource);
                const Icon = source.icon;
                
                return (
                  <>
                    <div className="bg-white border-b border-gray-200 py-10 px-8">
                      <div className="max-w-4xl mx-auto">
                        <button
                          onClick={() => {
                            setSelectedSource(null);
                            setFileName('');
                            setInputValue('');
                          }}
                          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 font-medium mb-6 transition-all"
                        >
                          <ArrowRight size={20} className="rotate-180" />
                          <span>Back to sources</span>
                        </button>
                        
                        <div className="flex items-center space-x-6">
                          <div className={`w-20 h-20 ${source.iconBg} rounded-lg flex items-center justify-center shadow-md`}>
                            <Icon size={36} className="text-white" />
                          </div>
                          <div>
                            <h2 className="text-4xl font-bold text-gray-900 mb-2">{source.name}</h2>
                            <p className="text-lg text-gray-600">{source.detail}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Form Section */}
                    <div className="flex-1 bg-gray-50 p-10 overflow-auto">
                      <div className="max-w-4xl mx-auto">
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                          <div className="p-10">
                            {source.inputType === 'upload' ? (
                              <div className="space-y-6">
                                <div>
                                  <label className="block text-lg font-bold text-gray-900 mb-2">
                                    Choose File
                                  </label>
                                  <p className="text-gray-600 mb-4">{source.helper}</p>
                                </div>

                                <label className="block">
                                  <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-16 text-center hover:border-gray-400 hover:bg-gray-50 transition-all cursor-pointer group">
                                    <Upload className="mx-auto text-gray-400 group-hover:text-gray-600 mb-6 transition-all" size={56} />
                                    <div className="text-xl font-bold text-gray-700 mb-2">
                                      {fileName || 'Drop files here or click to browse'}
                                    </div>
                                    <p className="text-gray-500 text-base">
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
                                  <div className="flex items-center justify-between p-5 bg-green-50 border border-green-200 rounded-lg">
                                    <div className="flex items-center space-x-4">
                                      <CheckCircle className="text-green-600 flex-shrink-0" size={24} />
                                      <div>
                                        <div className="font-bold text-green-900 text-base">{fileName}</div>
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
                                      <X size={20} />
                                    </button>
                                  </div>
                                )}
                              </div>
                            ) : source.inputType === 'clone' ? (
                              <div className="space-y-6">
                                <div>
                                  <label className="block text-lg font-bold text-gray-900 mb-2">
                                    Repository URL
                                  </label>
                                  <p className="text-gray-600 mb-4">{source.helper}</p>
                                  <div className="relative">
                                    <Link className="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                    <input
                                      type="text"
                                      value={inputValue}
                                      onChange={(e) => setInputValue(e.target.value)}
                                      placeholder={source.placeholder}
                                      className="w-full pl-14 pr-5 py-4 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-400 focus:border-gray-400 outline-none text-base transition-all"
                                    />
                                  </div>
                                </div>

                                <div>
                                  <label className="block text-lg font-bold text-gray-900 mb-2">
                                    Branch (optional)
                                  </label>
                                  <div className="relative">
                                    <GitBranch className="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                    <input
                                      type="text"
                                      placeholder="main"
                                      className="w-full pl-14 pr-5 py-4 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-400 focus:border-gray-400 outline-none text-base transition-all"
                                    />
                                  </div>
                                </div>

                                <div className="flex items-start space-x-3 p-5 bg-blue-50 border border-blue-200 rounded-lg">
                                  <input type="checkbox" id="private" className="w-5 h-5 mt-1 rounded" />
                                  <label htmlFor="private" className="text-gray-700 font-medium">
                                    This is a private repository (requires authentication)
                                  </label>
                                </div>
                              </div>
                            ) : (
                              <div className="space-y-6">
                                <div>
                                  <label className="block text-lg font-bold text-gray-900 mb-2">
                                    {source.name} URL
                                  </label>
                                  <p className="text-gray-600 mb-4">{source.helper}</p>
                                  <div className="relative">
                                    <Link className="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                                    <input
                                      type="text"
                                      value={inputValue}
                                      onChange={(e) => setInputValue(e.target.value)}
                                      placeholder={source.placeholder}
                                      className="w-full pl-14 pr-5 py-4 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-400 focus:border-gray-400 outline-none text-base transition-all"
                                    />
                                  </div>
                                </div>

                                <div className="flex items-start space-x-3 p-5 bg-amber-50 border border-amber-200 rounded-lg">
                                  <div className="text-xl">💡</div>
                                  <p className="text-amber-900 font-medium text-sm">
                                    Make sure you have the necessary permissions to access this resource
                                  </p>
                                </div>
                              </div>
                            )}

                            <button
                              onClick={handleSubmit}
                              className="w-full mt-8 text-white font-bold py-4 px-6 rounded-lg transition-all duration-300 text-base shadow-md hover:shadow-lg"
                              style={{ backgroundColor: '#9E1C33' }}
                              onMouseEnter={(e) => e.target.style.backgroundColor = '#7A1528'}
                              onMouseLeave={(e) => e.target.style.backgroundColor = '#9E1C33'}
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
        <div className="p-12 bg-white">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center space-x-4 mb-4">
              <RefreshCw className="text-gray-700" size={40} />
              <h1 className="text-4xl font-bold text-gray-900">Knowledge Sync</h1>
            </div>
            <p className="text-xl text-gray-600">Manage automated synchronization and data updates</p>
          </div>
        </div>
      );
    } else if (activePage === 'settings') {
      return (
        <div className="p-12 bg-white">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center space-x-4 mb-4">
              <Settings className="text-gray-700" size={40} />
              <h1 className="text-4xl font-bold text-gray-900">Settings</h1>
            </div>
            <p className="text-xl text-gray-600">Configure your workspace and preferences</p>
          </div>
        </div>
      );
    } else if (activePage === 'chatbot') {
      return (
        <div className="p-12 bg-white">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center space-x-4 mb-4">
              <MessageSquare className="text-gray-700" size={40} />
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
      {/* Sidebar - Neutral gray with subtle red accent */}
      <div className="w-72 bg-gray-900 flex flex-col shadow-xl">
        <div className="p-8 border-b border-gray-800">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#9E1C33' }}>
              <Database size={22} className="text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Knowledge Hub</h2>
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
                className={`w-full flex items-center space-x-4 px-5 py-4 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-gray-800 text-white font-semibold'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <Icon size={20} />
                <span className="text-base">{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="p-6 border-t border-gray-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center text-white font-semibold">
              A
            </div>
            <div className="flex-1">
              <div className="text-sm font-semibold text-white">Admin User</div>
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