import React, { useState, useEffect, useCallback } from "react";
import { Toaster, toast } from "sonner";
import { v4 as uuidv4 } from "uuid";
import { Sidebar } from "./components/Sidebar";
import { ChatInterface } from "./components/ChatInterface";
import { DocumentManager } from "./components/DocumentManager";
import { listDocuments, uploadDocument, deleteDocument } from "./lib/api";

// Stable session id across reloads so chat history persists.
function getSessionId() {
  let id = localStorage.getItem("scb_session_id");
  if (!id) {
    id = uuidv4();
    localStorage.setItem("scb_session_id", id);
  }
  return id;
}

function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [isDark, setIsDark] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const [sessionId] = useState(getSessionId);

  useEffect(() => {
    const saved = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const dark = saved === "dark" || (!saved && prefersDark);
    setIsDark(dark);
    document.documentElement.classList.toggle("dark", dark);
  }, []);

  const toggleTheme = () => {
    setIsDark((prev) => {
      const next = !prev;
      document.documentElement.classList.toggle("dark", next);
      localStorage.setItem("theme", next ? "dark" : "light");
      return next;
    });
  };

  const fetchDocuments = useCallback(async () => {
    try {
      setDocuments(await listDocuments());
    } catch (e) {
      toast.error("Failed to load documents");
    } finally {
      setIsLoadingDocs(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleUpload = async (file) => {
    try {
      const newDoc = await uploadDocument(file);
      setDocuments((prev) => [newDoc, ...prev]);
      toast.success(`${file.name} indexed successfully`);
    } catch (e) {
      toast.error(e.message || "Failed to upload document");
      throw e;
    }
  };

  const handleDelete = async (docId) => {
    try {
      await deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      toast.success("Document removed");
    } catch (e) {
      toast.error("Failed to delete document");
    }
  };

  return (
    <div className="ambient flex h-screen overflow-hidden bg-background text-foreground">
      <Toaster position="top-right" theme={isDark ? "dark" : "light"} richColors />

      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isDark={isDark}
        onThemeToggle={toggleTheme}
        documentCount={documents.length}
      />

      <main className="relative z-10 flex-1 flex flex-col overflow-hidden">
        <header className="h-16 shrink-0 border-b border-border/60 flex items-center justify-between px-6 glass">
          <div>
            <h1 className="font-heading text-lg font-semibold leading-tight">
              {activeTab === "chat" ? "Assistant" : "Knowledge Base"}
            </h1>
            <p className="text-xs text-muted-foreground">
              {activeTab === "chat"
                ? "Ask questions about your campus documents"
                : "Upload and manage source documents"}
            </p>
          </div>
        </header>

        <div className="flex-1 overflow-hidden">
          {activeTab === "chat" ? (
            <ChatInterface sessionId={sessionId} hasDocuments={documents.length > 0} />
          ) : (
            <div className="h-full overflow-y-auto p-6">
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
