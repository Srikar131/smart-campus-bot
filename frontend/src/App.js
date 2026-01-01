import React, { useState, useEffect, useCallback } from 'react';
import { Toaster, toast } from 'sonner';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { DocumentManager } from './components/DocumentManager';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [isDark, setIsDark] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const [sessionId] = useState(() => uuidv4());

  // Handle theme
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (isDark) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
  };

  // Fetch documents
  const fetchDocuments = useCallback(async () => {
    try {
      const response = await fetch('/api/documents');
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setIsLoadingDocs(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Upload document
  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const newDoc = await response.json();
        setDocuments((prev) => [...prev, newDoc]);
        toast.success(`${file.name} uploaded successfully`);
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      toast.error(error.message || 'Failed to upload document');
    }
  };

  // Delete document
  const handleDelete = async (docId) => {
    try {
      const response = await fetch(`/api/documents/${docId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setDocuments((prev) => prev.filter((doc) => doc.id !== docId));
        toast.success('Document deleted');
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      toast.error('Failed to delete document');
    }
  };

  return (
    <div className="flex h-screen bg-background noise-bg relative">
      <Toaster 
        position="top-right" 
        toastOptions={{
          className: 'glass',
        }}
      />
      
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isDark={isDark}
        onThemeToggle={toggleTheme}
      />

      <main className="flex-1 overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-border flex items-center px-6 glass">
          <h1 className="font-heading text-2xl font-semibold">
            {activeTab === 'chat' ? 'Smart Campus Bot' : 'Document Manager'}
          </h1>
        </header>

        {/* Content */}
        <div className="h-[calc(100vh-4rem)]">
          {activeTab === 'chat' ? (
            <ChatInterface sessionId={sessionId} />
          ) : (
            <div className="p-6 overflow-y-auto h-full">
              <DocumentManager
                documents={documents}
                onUpload={handleUpload}
                onDelete={handleDelete}
                isLoading={isLoadingDocs}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
