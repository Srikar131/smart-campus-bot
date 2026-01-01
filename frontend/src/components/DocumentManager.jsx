import React, { useState, useRef } from 'react';
import { Upload, FileText, Trash2, Loader2, CheckCircle, File } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

export function DocumentManager({ documents, onUpload, onDelete, isLoading }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    await handleFiles(files);
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    await handleFiles(files);
    e.target.value = '';
  };

  const handleFiles = async (files) => {
    for (const file of files) {
      if (file.type === 'application/pdf' || 
          file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        setUploadingFile(file.name);
        await onUpload(file);
        setUploadingFile(null);
      }
    }
  };

  const getFileIcon = (fileType) => {
    return fileType === 'pdf' ? (
      <FileText className="w-5 h-5 text-red-500" />
    ) : (
      <File className="w-5 h-5 text-blue-500" />
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-200
          ${isDragging 
            ? 'border-electric-indigo bg-electric-indigo/5' 
            : 'border-border hover:border-academic-teal hover:bg-academic-teal/5'
          }
        `}
        data-testid="upload-area"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          data-testid="file-input"
        />
        <div className="flex flex-col items-center gap-3">
          {uploadingFile ? (
            <>
              <Loader2 className="w-10 h-10 text-electric-indigo animate-spin" />
              <p className="text-sm text-muted-foreground">Uploading {uploadingFile}...</p>
            </>
          ) : (
            <>
              <Upload className="w-10 h-10 text-muted-foreground" strokeWidth={1.5} />
              <div>
                <p className="font-medium">Drop files here or click to upload</p>
                <p className="text-sm text-muted-foreground mt-1">PDF and DOCX files supported</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Document Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="text-center">
          <CardContent className="pt-6">
            <p className="text-3xl font-heading font-bold text-academic-teal">
              {documents.length}
            </p>
            <p className="text-xs uppercase tracking-widest text-muted-foreground mt-1">
              Documents
            </p>
          </CardContent>
        </Card>
        <Card className="text-center">
          <CardContent className="pt-6">
            <p className="text-3xl font-heading font-bold text-electric-indigo">
              {documents.reduce((acc, doc) => acc + (doc.chunk_count || 0), 0)}
            </p>
            <p className="text-xs uppercase tracking-widest text-muted-foreground mt-1">
              Chunks
            </p>
          </CardContent>
        </Card>
        <Card className="text-center">
          <CardContent className="pt-6">
            <div className="flex items-center justify-center gap-1">
              <CheckCircle className="w-6 h-6 text-green-500" />
            </div>
            <p className="text-xs uppercase tracking-widest text-muted-foreground mt-1">
              Ready
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Document List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Uploaded Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-muted-foreground/50 mx-auto mb-3" strokeWidth={1} />
              <p className="text-muted-foreground">No documents uploaded yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-3 border border-border hover:bg-muted/50 transition-colors group"
                  data-testid={`document-${doc.id}`}
                >
                  <div className="flex items-center gap-3">
                    {getFileIcon(doc.file_type)}
                    <div>
                      <p className="font-medium text-sm truncate max-w-[200px]">
                        {doc.filename}
                      </p>
                      <p className="text-xs text-muted-foreground font-mono">
                        {doc.chunk_count} chunks • {formatDate(doc.upload_date)}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => onDelete(doc.id)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-600 hover:bg-red-50"
                    data-testid={`delete-${doc.id}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
