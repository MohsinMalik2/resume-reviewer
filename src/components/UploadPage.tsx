import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Upload, FileText, XCircle, Briefcase, ArrowLeft, ArrowRight } from 'lucide-react';
import { useResumeContext } from '../context/ResumeContext';
import Header from './Header';

const UploadPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    jobDescription,
    setJobDescription,
    uploadedFiles,
    setUploadedFiles,
    comparisonScore,
    setComparisonScore,
  } = useResumeContext();

  const handleFileUpload = (files: FileList | null) => {
    if (files) {
      const newFiles = Array.from(files).filter(file => 
        file.type === 'application/pdf' || 
        file.name.toLowerCase().endsWith('.doc') || 
        file.name.toLowerCase().endsWith('.docx')
      );
      setUploadedFiles([...uploadedFiles, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(uploadedFiles.filter((_, i) => i !== index));
  };

  const handleProcess = () => {
    navigate('/processing');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <Link
              to="/dashboard"
              className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Dashboard</span>
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Upload & Process</h1>
            <div className="w-24"></div>
          </div>

          {/* Main Card */}
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            {/* Job Description Section */}
            <div className="p-8 border-b border-gray-200">
              <div className="flex items-center space-x-3 mb-4">
                <Briefcase className="w-6 h-6 text-blue-600" />
                <h2 className="text-2xl font-semibold text-gray-900">Job Description</h2>
              </div>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste your job description here. Include key requirements, skills, and qualifications to help our AI match the best candidates..."
                className="w-full h-32 p-4 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* File Upload Section */}
            <div className="p-8">
              <div className="flex items-center space-x-3 mb-6">
                <Upload className="w-6 h-6 text-blue-600" />
                <h2 className="text-2xl font-semibold text-gray-900">Upload Resumes</h2>
              </div>

              {/* Drag and Drop Area */}
              <div
                onDrop={(e) => {
                  e.preventDefault();
                  handleFileUpload(e.dataTransfer.files);
                }}
                onDragOver={(e) => e.preventDefault()}
                className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-400 transition-colors cursor-pointer"
              >
                <input
                  type="file"
                  id="file-upload"
                  multiple
                  accept=".pdf,.doc,.docx"
                  onChange={(e) => handleFileUpload(e.target.files)}
                  className="hidden"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    Drop resume files here or click to browse
                  </p>
                  <p className="text-gray-600">Supports PDF, DOC, and DOCX files</p>
                </label>
              </div>

              {/* Uploaded Files List */}
              {uploadedFiles.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Uploaded Files ({uploadedFiles.length})
                  </h3>
                  <div className="space-y-2">
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <FileText className="w-5 h-5 text-blue-600" />
                          <span className="text-gray-900">{file.name}</span>
                          <span className="text-sm text-gray-500">
                            ({(file.size / 1024 / 1024).toFixed(2)} MB)
                          </span>
                        </div>
                        <button
                          onClick={() => removeFile(index)}
                          className="text-red-600 hover:text-red-800 transition-colors"
                        >
                          <XCircle className="w-5 h-5" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Process Button */}
              <div className="mt-8 flex flex-col items-center">
                <div className="mb-4 w-full max-w-xs">
                  <label htmlFor="comparison-score" className="block text-sm font-medium text-gray-700 mb-2">
                    Comparison Score (default: 50)
                  </label>
                  <input
                    id="comparison-score"
                    type="number"
                    min={0}
                    max={100}
                    value={comparisonScore}
                    onChange={e => setComparisonScore(Number(e.target.value) || 50)}
                    className="block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <button
                  onClick={handleProcess}
                  disabled={!jobDescription.trim() || uploadedFiles.length === 0}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200 transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed flex items-center space-x-3"
                >
                  <span>Process Resumes with AI</span>
                  <ArrowRight className="w-6 h-6" />
                </button>
              </div>

              {(!jobDescription.trim() || uploadedFiles.length === 0) && (
                <p className="text-center text-gray-500 mt-4">
                  Please provide a job description and upload at least one resume to continue
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;