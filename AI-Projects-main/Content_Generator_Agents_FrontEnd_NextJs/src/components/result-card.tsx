"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Copy, Download } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from 'remark-gfm'; // Import remarkGfm

interface ResultCardProps {
  imageUrl?: string | null;
  content: string;
  contentType: string; // Added contentType prop
}

// Helper function to escape special characters in a string for use in a RegExp
const escapeRegExp = (string: string) => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

export const ResultCard: React.FC<ResultCardProps> = ({ imageUrl, content, contentType }) => {
  // Normalize image url to undefined for JSX attributes
  const imageSrc: string | undefined = imageUrl ?? undefined;
  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(content);
      toast.success("Content copied to clipboard!");
    } catch (err) {
      toast.error("Failed to copy content.");
      console.error("Failed to copy: ", err);
    }
  };

  const handleDownloadImage = async () => {
    if (!imageSrc) return;
    try {
      const response = await fetch(imageSrc);
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = blobUrl;
      const urlPath = new URL(imageSrc, window.location.href).pathname;
      const fileNameFromUrl = urlPath.split("/").filter(Boolean).pop();
      const extensionFromType = blob.type.split("/")[1] || "png";
      link.download = fileNameFromUrl || `generated-image.${extensionFromType}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(blobUrl);
      toast.success("Image downloaded");
    } catch (error) {
      console.error("Failed to download image", error);
      toast.error("Failed to download image");
    }
  };

  // If an imageUrl is provided, remove any markdown image syntax that matches it from the content
  const processedContent = imageSrc
    ? content.replace(new RegExp(`!\\[.*?\\]\\(${escapeRegExp(imageSrc)}\\)`, 'g'), '')
    : content;

  console.log("Processed Content for ReactMarkdown:", processedContent);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-2xl"
    >
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex justify-between items-center">
            Generated Content
            <div className="flex items-center gap-2">
              {imageSrc && (
                <Button variant="outline" size="sm" onClick={handleDownloadImage}>
                  <Download className="h-4 w-4 mr-2" /> Download Image
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={handleCopyToClipboard}>
                <Copy className="h-4 w-4 mr-2" /> Copy
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {imageSrc && (
            <div className="mb-4">
              <img
                src={imageSrc}
                alt="Generated content visual"
                className="w-full h-auto rounded-md object-cover"
              />
            </div>
          )}
          <div className="prose dark:prose-invert max-w-none">
            {contentType === "blog" ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{processedContent}</ReactMarkdown>
            ) : (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{processedContent}</ReactMarkdown>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};