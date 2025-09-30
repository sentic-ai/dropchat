"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { X, Shield, Server } from "lucide-react";
import { Button } from "./ui/button";

const FORMSPARK_ACTION_URL = process.env.NEXT_PUBLIC_FORMSPARK_URL || "https://submit-form.com/your-form-id";

interface PrivacyOverlayProps {
  isVisible: boolean;
  onClose: () => void;
  variant?: 'privacy-concern' | 'active-user';
}

export function PrivacyOverlay({ isVisible, onClose, variant = 'privacy-concern' }: PrivacyOverlayProps) {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const heading = variant === 'active-user'
    ? "Want this for your team?"
    : "Concerned about privacy?";

  const subtext = variant === 'active-user'
    ? "Run it on your own servers - unlimited documents, complete control."
    : "Get the self-hosted version and keep your documents completely private.";

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setSubmitting(true);
    try {
      await fetch(FORMSPARK_ACTION_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          email,
          interest: "self-hosted-version",
          source: "privacy-overlay",
        }),
      });
      setSubmitted(true);
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error) {
      console.error("Form submission failed:", error);
      alert("Failed to submit. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="relative mx-4 w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl"
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="mb-6 text-center">
          <div className="mb-4 flex justify-center">
            <div className="rounded-full bg-blue-100 p-3">
              <Shield className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <h2 className="mb-2 text-2xl font-bold text-gray-900">
            {heading}
          </h2>
          <p className="text-gray-600">
            {subtext}
          </p>
        </div>

        {submitted ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <div className="mb-4 flex justify-center">
              <div className="rounded-full bg-green-100 p-3">
                <Server className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <h3 className="mb-2 text-lg font-semibold text-green-900">
              Thanks for your interest!
            </h3>
          </motion.div>
        ) : (
          <form
            onSubmit={onSubmit}
            className="space-y-4"
          >
            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Email address
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <Button
              type="submit"
              disabled={submitting || !email.trim()}
              className="w-full bg-blue-600 text-white hover:bg-blue-700"
            >
              {submitting ? "Sending..." : "Get Self-Hosted Version"}
            </Button>

            <div className="text-center">
              <button
                type="button"
                onClick={onClose}
                className="text-sm text-gray-500 underline hover:text-gray-700"
              >
                Continue
              </button>
            </div>
          </form>
        )}
      </motion.div>
    </motion.div>
  );
}
