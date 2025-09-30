"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Copy, ExternalLink } from 'lucide-react';
import Image from 'next/image';
import { Button } from './ui/button';
// import { cn } from '@/lib/utils';

interface SharePageProps {
  chatId: string;
  chatUrl: string;
  onCreateNew: () => void;
}

export function SharePage({ chatId, chatUrl, onCreateNew }: SharePageProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(chatUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy link:', error);
      // Fallback for browsers that don't support clipboard API
      const textArea = document.createElement('textarea');
      textArea.value = chatUrl;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleOpenInNewTab = () => {
    window.open(chatUrl, '_blank');
  };

  return (
    <div className="flex h-screen w-full bg-white">
      {/* Left side - Success message and link sharing */}
      <div className="w-1/2 flex flex-col justify-center px-12 border-r border-gray-200">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-md"
        >
          <div className="flex items-center mb-8 gap-3">
            <Image
              src="/logo.png"
              alt="DropAndChat Logo"
              width={48}
              height={48}
              className="h-12 w-auto object-contain"
            />
            <span className="text-2xl font-bold text-gray-900 tracking-tight leading-none">DropAndChat</span>
          </div>

          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Your DropAndChat is ready! 🎉
            </h1>
            <p className="text-gray-600 text-lg">
              Share this link with anyone to let them chat with your document.
            </p>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Shareable Link
              </label>
              <div className="flex items-center space-x-2">
                <div className="flex-1 p-3 bg-gray-100 rounded-lg border text-sm font-mono text-gray-700 overflow-hidden">
                  <div className="truncate">{chatUrl}</div>
                </div>
              </div>
            </div>

            <div className="flex space-x-2">
              <Button
                onClick={handleCopyLink}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                disabled={copied}
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4 mr-2" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4 mr-2" />
                    Copy Link
                  </>
                )}
              </Button>

              <Button
                onClick={handleOpenInNewTab}
                variant="outline"
                className="flex-shrink-0"
              >
                <ExternalLink className="h-4 w-4" />
              </Button>
            </div>

            <div className="text-xs text-gray-500 bg-yellow-50 p-3 rounded-lg border border-yellow-200">
              <strong>Demo Limitations:</strong> This link will expire in 24 hours.
              Maximum file size is 15MB.
            </div>

            <Button
              onClick={onCreateNew}
              variant="ghost"
              className="w-full mt-6 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
            >
              Create Another DropAndChat
            </Button>
          </div>
        </motion.div>
      </div>

      {/* Right side - Live preview of the chat */}
      <div className="w-1/2 flex flex-col">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="h-full flex flex-col"
        >
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-900">Live Preview</h2>
            <p className="text-sm text-gray-600">
              This is how others will see your DropAndChat
            </p>
          </div>

          <div className="flex-1 relative">
            <div className="absolute inset-0 scale-90 origin-top-left">
              <iframe
                src={chatUrl}
                className="w-full h-full border-0 rounded-lg"
                title="Chat Preview"
              />
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}