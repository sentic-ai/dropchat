"use client";

import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, Loader2 } from "lucide-react";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface LandingPageProps {
  onFileUpload: (file: File) => Promise<string>; // Returns the chat ID
}

export function LandingPage({ onFileUpload }: LandingPageProps) {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadingFileName, setUploadingFileName] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find((file) => file.type === "application/pdf");

    if (pdfFile) {
      await handleFileUpload(pdfFile);
    }
  };

  const handleFileInputChange = async (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = e.target.files?.[0];
    if (file) {
      await handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (file.size > 15 * 1024 * 1024) {
      // 15MB limit
      alert("File size must be less than 15MB");
      return;
    }

    setUploadingFileName(file.name);
    setUploading(true);
    try {
      await onFileUpload(file);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed. Please try again.");
    } finally {
      setUploading(false);
      setUploadingFileName("");
    }
  };

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  if (uploading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="mb-6 flex items-center justify-center">
            <Image
              src="/logo.png"
              alt="DropAndChat Logo"
              width={48}
              height={48}
              className="h-12 w-auto object-contain"
            />
          </div>
          <Loader2 className="mx-auto mb-4 h-8 w-8 animate-spin text-blue-600" />
          <h2 className="mb-2 text-xl font-semibold text-gray-900">
            Analyzing {uploadingFileName}...
          </h2>
          <p className="text-gray-600">This may take a few moments</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-full items-center justify-center bg-white">
      <div className="w-full max-w-2xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12 text-center"
        >
          <div className="mb-8 flex items-center justify-center gap-4">
            <Image
              src="/logo.png"
              alt="DropAndChat Logo"
              width={64}
              height={64}
              className="h-16 w-auto object-contain"
            />
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight leading-none">DropAndChat</h1>
          </div>

          <h2 className="mb-4 text-2xl font-semibold text-gray-900">
            Create a chat for any PDF
          </h2>

          <p className="mb-2 text-lg text-gray-600">
            Drag and drop your file to get a shareable link
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className={cn(
            "relative cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition-all duration-200 hover:bg-gray-50",
            dragOver ? "border-blue-500 bg-blue-50" : "border-gray-300",
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClickUpload}
        >
          <div className="flex flex-col items-center">
            {dragOver ? (
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                className="mb-6 rounded-full bg-blue-100 p-6"
              >
                <FileText className="h-12 w-12 text-blue-600" />
              </motion.div>
            ) : (
              <div className="mb-6 rounded-full bg-gray-100 p-6">
                <Upload className="h-12 w-12 text-gray-600" />
              </div>
            )}

            <h3 className="mb-2 text-xl font-semibold text-gray-900">
              {dragOver
                ? "Drop your PDF here"
                : "Drop your PDF or click to browse"}
            </h3>

            <p className="mb-6 text-gray-600">Supports PDF files up to 15MB</p>

            <div className="rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-500">
              <strong>Free Demo:</strong> Max 15MB file, link expires in 24
              hours
            </div>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileInputChange}
            className="hidden"
          />
        </motion.div>
      </div>
    </div>
  );
}
