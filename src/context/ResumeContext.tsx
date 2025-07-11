import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { CandidateResult, RejectionEmail } from '../types/api';

// Re-export types for backward compatibility
export type Resume = CandidateResult;
export type { RejectionEmail } from '../types/api';

interface ResumeContextType {
  jobDescription: string;
  setJobDescription: (description: string) => void;
  uploadedFiles: File[];
  setUploadedFiles: (files: File[]) => void;
  processedResumes: CandidateResult[];
  setProcessedResumes: (resumes: CandidateResult[]) => void;
  rejectionEmails: RejectionEmail[];
  setRejectionEmails: (emails: RejectionEmail[]) => void;
  processing: boolean;
  setProcessing: (processing: boolean) => void;
  currentJobId: string | null;
  setCurrentJobId: (jobId: string | null) => void;
  resetProcess: () => void;
}

const ResumeContext = createContext<ResumeContextType | undefined>(undefined);

export const useResumeContext = () => {
  const context = useContext(ResumeContext);
  if (context === undefined) {
    throw new Error('useResumeContext must be used within a ResumeProvider');
  }
  return context;
};

interface ResumeProviderProps {
  children: ReactNode;
}

export const ResumeProvider: React.FC<ResumeProviderProps> = ({ children }) => {
  const [jobDescription, setJobDescription] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [processedResumes, setProcessedResumes] = useState<CandidateResult[]>([]);
  const [rejectionEmails, setRejectionEmails] = useState<RejectionEmail[]>([]);
  const [processing, setProcessing] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);

  const resetProcess = () => {
    setJobDescription('');
    setUploadedFiles([]);
    setProcessedResumes([]);
    setRejectionEmails([]);
    setProcessing(false);
    setCurrentJobId(null);
  };

  const value = {
    jobDescription,
    setJobDescription,
    uploadedFiles,
    setUploadedFiles,
    processedResumes,
    setProcessedResumes,
    rejectionEmails,
    setRejectionEmails,
    processing,
    setProcessing,
    currentJobId,
    setCurrentJobId,
    resetProcess,
  };

  return (
    <ResumeContext.Provider value={value}>
      {children}
    </ResumeContext.Provider>
  );
};