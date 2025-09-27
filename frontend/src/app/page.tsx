"use client";

import { Thread } from "@/components/thread";
import { StreamProvider } from "@/providers/Stream";
import { ThreadProvider } from "@/providers/Thread";
import { ArtifactProvider } from "@/components/thread/artifact";
import { LandingPage } from "@/components/landing-page";
import { SharePage } from "@/components/share-page";
import { Toaster } from "@/components/ui/sonner";
// Removed unused import
import React, { useState, useEffect } from "react";

type AppState = 'landing' | 'share' | 'chat';

export default function DemoPage(): React.ReactNode {
  const [appState, setAppState] = useState<AppState>('landing');
  const [chatId, setChatId] = useState<string | null>(null);

  useEffect(() => {
    // Check if we have a chat path in the URL
    const currentPath = window.location.pathname;
    if (currentPath.startsWith('/chat/')) {
      setChatId(currentPath);
      setAppState('chat');
    }
  }, []);

  const handleFileUpload = async (file: File): Promise<string> => {
    console.log('Uploading file:', file.name);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('files', file);
      formData.append('project_name', file.name.replace('.pdf', ''));

      // Call the backend API
      const response = await fetch('/api/create', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      const chatUrl = `/chat/${result.user_hash}/${result.project_id}`;
      setChatId(chatUrl);
      setAppState('share');

      return chatUrl;
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  };

  const handleCreateNew = () => {
    setChatId(null);
    setAppState('landing');
  };

  const generateChatUrl = (chatPath: string) => {
    const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
    return `${baseUrl}${chatPath}`;
  };

  const renderContent = () => {
    switch (appState) {
      case 'landing':
        return <LandingPage onFileUpload={handleFileUpload} />;

      case 'share':
        return (
          <SharePage
            chatId={chatId!}
            chatUrl={generateChatUrl(chatId!)}
            onCreateNew={handleCreateNew}
          />
        );

      case 'chat':
        return (
          <ThreadProvider>
            <StreamProvider>
              <ArtifactProvider>
                <Thread />
              </ArtifactProvider>
            </StreamProvider>
          </ThreadProvider>
        );

      default:
        return <LandingPage onFileUpload={handleFileUpload} />;
    }
  };

  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Toaster />
      {renderContent()}
    </React.Suspense>
  );
}
