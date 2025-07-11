import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Filter, Upload, Users, Mail, BarChart3, Clock, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Header from './Header';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center space-x-3 mb-6">
              <div className="bg-blue-600 p-4 rounded-2xl">
                <Filter className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-5xl font-bold text-gray-900">Auto Screener Agent</h1>
            </div>
            <p className="text-xl text-blue-600 mb-4">Welcome back, {user?.firstName}!</p>
            <p className="text-2xl text-gray-600 mb-8">AI-Powered Resume Screening & Rejection Automation for Recruiters</p>
            <p className="text-lg text-gray-500 max-w-3xl mx-auto">
              Transform your hiring process with intelligent automation. Upload resumes, provide job requirements, 
              and let our AI handle the screening, ranking, and rejection communications automatically.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="bg-blue-100 p-3 rounded-xl w-fit mb-4">
                <Upload className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Smart Upload</h3>
              <p className="text-gray-600">
                Drag and drop multiple resumes in PDF, DOC, or DOCX format. Our system handles bulk processing seamlessly.
              </p>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="bg-green-100 p-3 rounded-xl w-fit mb-4">
                <BarChart3 className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Scoring</h3>
              <p className="text-gray-600">
                Advanced algorithms analyze resumes against job requirements and provide detailed fit scores for each candidate.
              </p>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="bg-purple-100 p-3 rounded-xl w-fit mb-4">
                <Users className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Auto Shortlisting</h3>
              <p className="text-gray-600">
                Automatically identify top candidates based on customizable criteria and generate comprehensive shortlists.
              </p>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="bg-orange-100 p-3 rounded-xl w-fit mb-4">
                <Mail className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Rejection Emails</h3>
              <p className="text-gray-600">
                Generate personalized, professional rejection emails automatically for candidates who don't meet requirements.
              </p>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="bg-indigo-100 p-3 rounded-xl w-fit mb-4">
                <Clock className="w-8 h-8 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Time Saving</h3>
              <p className="text-gray-600">
                Reduce screening time from hours to minutes. Focus on interviewing the best candidates instead of manual review.
              </p>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow">
              <div className="bg-red-100 p-3 rounded-xl w-fit mb-4">
                <CheckCircle className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Export Ready</h3>
              <p className="text-gray-600">
                Download shortlists in Excel format and rejection emails ready to send. Seamless integration with your workflow.
              </p>
            </div>
          </div>

          {/* CTA Section */}
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Transform Your Hiring Process?</h2>
            <p className="text-xl text-gray-600 mb-8">
              Start screening resumes with AI in just a few clicks. No setup required.
            </p>
            <Link
              to="/upload"
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-12 py-4 rounded-xl font-semibold text-lg transition-all duration-200 transform hover:scale-105 inline-flex items-center space-x-3"
            >
              <Filter className="w-6 h-6" />
              <span>Start Screening Now</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;