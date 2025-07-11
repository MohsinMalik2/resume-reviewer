import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Mail, Download, CheckCircle, XCircle, Star, ArrowLeft, Copy, FileSpreadsheet } from 'lucide-react';
import { useResumeContext } from '../context/ResumeContext';
import * as XLSX from 'xlsx';
import Header from './Header';

const ResultsPage: React.FC = () => {
  const {
    processedResumes,
    rejectionEmails,
    resetProcess,
  } = useResumeContext();

  const [activeTab, setActiveTab] = useState<'shortlist' | 'rejections'>('shortlist');
  const [copiedStates, setCopiedStates] = useState<{ [key: string]: boolean }>({});

  const shortlistedCandidates = processedResumes.filter(resume => resume.status === 'shortlisted');
  const rejectedCandidates = processedResumes.filter(resume => resume.status === 'rejected');

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedStates(prev => ({ ...prev, [id]: true }));
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [id]: false }));
      }, 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const downloadShortlistExcel = () => {
    const worksheetData = [
      ['Candidate Name', 'Email', 'Score (%)', 'Experience', 'Skills', 'Summary', 'File Name'],
      ...shortlistedCandidates.map(resume => [
        resume.candidate,
        resume.email,
        resume.score,
        resume.experience,
        resume.skills.join(', '),
        resume.summary,
        resume.fileName
      ])
    ];

    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
    
    // Set column widths
    const colWidths = [
      { wch: 20 }, // Candidate Name
      { wch: 25 }, // Email
      { wch: 10 }, // Score
      { wch: 15 }, // Experience
      { wch: 30 }, // Skills
      { wch: 50 }, // Summary
      { wch: 25 }  // File Name
    ];
    worksheet['!cols'] = colWidths;

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Shortlisted Candidates');
    
    XLSX.writeFile(workbook, 'shortlisted_candidates.xlsx');
  };

  const downloadRejectionEmails = () => {
    const content = rejectionEmails.map(email => 
      `To: ${email.email}\nSubject: ${email.subject}\n\n${email.content}\n\n${'='.repeat(50)}\n`
    ).join('\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rejection_emails.txt';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleNewScreening = () => {
    resetProcess();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">Screening Results</h1>
                <p className="opacity-90">Processed {processedResumes.length} resumes • {shortlistedCandidates.length} shortlisted • {rejectedCandidates.length} rejected</p>
              </div>
              <div className="flex space-x-3">
                <Link
                  to="/dashboard"
                  onClick={handleNewScreening}
                  className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>New Screening</span>
                </Link>
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6">
            <div className="bg-green-50 border border-green-200 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-600 font-semibold">Shortlisted</p>
                  <p className="text-3xl font-bold text-green-800">{shortlistedCandidates.length}</p>
                </div>
                <CheckCircle className="w-12 h-12 text-green-500" />
              </div>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-red-600 font-semibold">Rejected</p>
                  <p className="text-3xl font-bold text-red-800">{rejectedCandidates.length}</p>
                </div>
                <XCircle className="w-12 h-12 text-red-500" />
              </div>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-600 font-semibold">Avg Score</p>
                  <p className="text-3xl font-bold text-blue-800">
                    {Math.round(processedResumes.reduce((sum, r) => sum + r.score, 0) / processedResumes.length)}
                  </p>
                </div>
                <Star className="w-12 h-12 text-blue-500" />
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <div className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('shortlist')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'shortlist'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4" />
                  <span>Shortlisted Candidates ({shortlistedCandidates.length})</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('rejections')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'rejections'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Mail className="w-4 h-4" />
                  <span>Rejection Emails ({rejectionEmails.length})</span>
                </div>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === 'shortlist' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Top Candidates</h2>
                  <button
                    onClick={downloadShortlistExcel}
                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
                  >
                    <FileSpreadsheet className="w-4 h-4" />
                    <span>Export to Excel</span>
                  </button>
                </div>
                <div className="space-y-4">
                  {shortlistedCandidates.map((resume) => (
                    <div key={resume.id} className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">{resume.candidate}</h3>
                            <button
                              onClick={() => copyToClipboard(resume.email, `email-${resume.id}`)}
                              className="text-blue-600 hover:text-blue-700 transition-colors flex items-center space-x-1"
                            >
                              <Copy className="w-4 h-4" />
                              <span className="text-sm">
                                {copiedStates[`email-${resume.id}`] ? 'Copied!' : 'Copy Email'}
                              </span>
                            </button>
                          </div>
                          <p className="text-gray-600">{resume.email}</p>
                          <p className="text-sm text-gray-500 mt-1">{resume.fileName}</p>
                        </div>
                        <div className="text-right">
                          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold mb-2">
                            Score: {resume.score}%
                          </div>
                          <p className="text-sm text-gray-600">{resume.experience} experience</p>
                        </div>
                      </div>
                      <p className="text-gray-700 mb-3">{resume.summary}</p>
                      <div className="flex flex-wrap gap-2">
                        {resume.skills.map((skill, index) => (
                          <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'rejections' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Rejection Email Drafts</h2>
                  <button
                    onClick={downloadRejectionEmails}
                    className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>Export Emails</span>
                  </button>
                </div>
                <div className="space-y-6">
                  {rejectionEmails.map((email) => (
                    <div key={email.candidateId} className="border border-gray-200 rounded-xl p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <h3 className="text-lg font-semibold text-gray-900">{email.candidate}</h3>
                          <button
                            onClick={() => copyToClipboard(email.email, `rejection-email-${email.candidateId}`)}
                            className="text-blue-600 hover:text-blue-700 transition-colors flex items-center space-x-1"
                          >
                            <Copy className="w-4 h-4" />
                            <span className="text-sm">
                              {copiedStates[`rejection-email-${email.candidateId}`] ? 'Copied!' : 'Copy Email'}
                            </span>
                          </button>
                        </div>
                        <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-semibold">
                          Rejected
                        </span>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-4 mb-4">
                        <p className="text-sm text-gray-600 mb-2"><strong>To:</strong> {email.email}</p>
                        <p className="text-sm text-gray-600"><strong>Subject:</strong> {email.subject}</p>
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg p-4 relative">
                        <button
                          onClick={() => copyToClipboard(email.content, `content-${email.candidateId}`)}
                          className="absolute top-2 right-2 text-blue-600 hover:text-blue-700 transition-colors flex items-center space-x-1 bg-blue-50 px-2 py-1 rounded"
                        >
                          <Copy className="w-3 h-3" />
                          <span className="text-xs">
                            {copiedStates[`content-${email.candidateId}`] ? 'Copied!' : 'Copy'}
                          </span>
                        </button>
                        <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans pr-16">{email.content}</pre>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;