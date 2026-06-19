import React, { useState, useRef } from "react";
import { Upload, FileText, Trash2, Loader2, File, Database, Layers } from "lucide-react";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

const ACCEPTED = {
  "application/pdf": "pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
};

const MAX_MB = 50;

function isAccepted(file) {
  if (ACCEPTED[file.type]) return true;
  const name = (file.name || "").toLowerCase();
  return name.endsWith(".pdf") || name.endsWith(".docx");
}

export function DocumentManager({ documents, onUpload, onDelete, isLoading }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(null);
  const inputRef = useRef(null);

  const handleFiles = async (files) => {
    for (const file of files) {
      if (!isAccepted(file)) {
        toast.error(`${file.name}: only PDF and DOCX are supported`);
        continue;
      }
      if (file.size > MAX_MB * 1024 * 1024) {
        toast.error(
          `${file.name} is ${(file.size / 1024 / 1024).toFixed(1)} MB — over the ${MAX_MB} MB limit`
        );
        continue;
      }
      setUploading(file.name);
      try {
        await onUpload(file);
      } catch {
        /* error toast handled upstream */
      } finally {
        setUploading(null);
      }
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(Array.from(e.dataTransfer.files));
  };

  const onSelect = (e) => {
    handleFiles(Array.from(e.target.files));
    e.target.value = "";
  };

  const totalChunks = documents.reduce((a, d) => a + (d.chunk_count || 0), 0);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <StatCard icon={Database} label="Documents" value={documents.length} />
        <StatCard icon={Layers} label="Indexed chunks" value={totalChunks} />
        <StatCard
          icon={FileText}
          label="Status"
          value={documents.length > 0 ? "Ready" : "Empty"}
          accent={documents.length > 0}
        />
      </div>

      {/* Upload */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition-all ${
          isDragging
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50 hover:bg-muted/40"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          multiple
          onChange={onSelect}
          className="hidden"
        />
        <div className="flex flex-col items-center gap-3">
          {uploading ? (
            <>
              <Loader2 className="h-10 w-10 animate-spin text-primary" />
              <p className="text-sm font-medium">Indexing {uploading}…</p>
              <p className="text-xs text-muted-foreground">Extracting text and generating embeddings</p>
            </>
          ) : (
            <>
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-primary/10">
                <Upload className="h-6 w-6 text-primary" strokeWidth={1.8} />
              </div>
              <p className="font-medium">Drop files here or click to upload</p>
              <p className="text-xs text-muted-foreground">PDF and DOCX · up to {MAX_MB} MB each</p>
            </>
          )}
        </div>
      </div>

      {/* Document list */}
      <Card>
        <div className="flex items-center justify-between p-5 pb-3">
          <h3 className="font-heading text-base font-semibold">Uploaded documents</h3>
          <span className="text-xs text-muted-foreground">{documents.length} total</span>
        </div>
        <CardContent className="pt-0">
          {isLoading ? (
            <div className="flex justify-center py-10">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : documents.length === 0 ? (
            <div className="py-10 text-center">
              <FileText className="mx-auto mb-3 h-10 w-10 text-muted-foreground/40" strokeWidth={1.2} />
              <p className="text-sm text-muted-foreground">No documents yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <DocumentRow key={doc.id} doc={doc} onDelete={onDelete} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, accent }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-4">
        <div className={`grid h-10 w-10 place-items-center rounded-lg ${accent ? "bg-green-500/10" : "bg-primary/10"}`}>
          <Icon className={`h-5 w-5 ${accent ? "text-green-500" : "text-primary"}`} />
        </div>
        <div className="min-w-0">
          <p className="font-heading text-xl font-bold leading-none">{value}</p>
          <p className="mt-1 text-[11px] uppercase tracking-wide text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function DocumentRow({ doc, onDelete }) {
  const date = doc.upload_date
    ? new Date(doc.upload_date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "";

  return (
    <div className="group flex items-center justify-between rounded-lg border border-border p-3 transition-colors hover:bg-muted/40">
      <div className="flex min-w-0 items-center gap-3">
        <div className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg ${doc.file_type === "pdf" ? "bg-red-500/10" : "bg-blue-500/10"}`}>
          {doc.file_type === "pdf" ? (
            <FileText className="h-4 w-4 text-red-500" />
          ) : (
            <File className="h-4 w-4 text-blue-500" />
          )}
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium">{doc.filename}</p>
          <p className="font-mono text-[11px] text-muted-foreground">
            {doc.chunk_count} chunks{date ? ` · ${date}` : ""}
          </p>
        </div>
      </div>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onDelete(doc.id)}
        className="h-8 w-8 text-muted-foreground opacity-0 transition-opacity hover:text-red-500 group-hover:opacity-100"
        aria-label="Delete document"
      >
        <Trash2 className="h-4 w-4" />
      </Button>
    </div>
  );
}
