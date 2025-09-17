"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { motion } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { toast } from "sonner";
import { LoadingSpinner } from "./loading-spinner";
import { ResultCard } from "./result-card";

const formSchema = z.object({
  url: z.string().url({ message: "Please enter a valid URL." }),
  content_type: z.enum(["blog", "x", "facebook", "linkedin", "newsletter"], {
    required_error: "Please select a content type.",
  }),
});

type FormData = z.infer<typeof formSchema>;

interface GeneratedContent {
  url: string;
  content_type: string;
  image_url?: string | null;
  content: string | { raw: string; [key: string]: any };
}

export const ContentGeneratorForm: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GeneratedContent | null>(null);

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      url: "",
      content_type: "blog", // Default content type
    },
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setResult(null); // Clear previous result on new submission
    try {
      const payload = {
        url: data.url,
        content_type: data.content_type,
      };

      const response = await fetch(
        "https://167aliraza-crewai.hf.space/generate-content-with-image",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate content.");
      }

      let resultData: GeneratedContent = await response.json();
      let displayContent: string;

      // Check if content is an object and extract 'raw' or stringify the whole object
      if (typeof resultData.content === 'object' && resultData.content !== null) {
        if (resultData.content.raw && typeof resultData.content.raw === 'string') {
          displayContent = resultData.content.raw;
        } else {
          // Fallback if 'raw' is not present or not a string
          displayContent = "```json\n" + JSON.stringify(resultData.content, null, 2) + "\n```";
        }
      } else if (typeof resultData.content === 'string') {
        displayContent = resultData.content;
      } else {
        // Fallback for any other unexpected content type
        displayContent = String(resultData.content);
      }
      
      // If blog content is wrapped in triple backticks, strip them so markdown renders
      const isBlog = resultData.content_type === "blog";
      const unFenced = isBlog
        ? displayContent.replace(/^```[a-zA-Z0-9]*\n?[\s\S]*?$/m, (match) => {
            // Remove the leading and trailing code fences only when both exist
            if (match.startsWith("```")) {
              const withoutStart = match.replace(/^```[a-zA-Z0-9]*\n?/, "");
              return withoutStart.replace(/\n?```\s*$/, "");
            }
            return match;
          })
        : displayContent;

      setResult({
        ...resultData,
        content: unFenced,
      });
      toast.success("Content generated successfully!");
    } catch (error: any) {
      toast.error(error.message || "An unexpected error occurred.");
      console.error("API call failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewGeneration = () => {
    setResult(null); // Clear the displayed result
    form.reset({ // Reset form fields to default values
      url: "",
      content_type: "blog",
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center justify-center min-h-screen p-4 sm:p-8 bg-background text-foreground"
    >
      <div className="w-full max-w-2xl bg-card p-6 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-6 text-foreground">
          AI Content Generator
        </h1>

        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <Label htmlFor="url" className="mb-2 block">
              URL <span className="text-destructive">*</span>
            </Label>
            <Input
              id="url"
              placeholder="Enter article URL"
              {...form.register("url")}
              className={form.formState.errors.url ? "border-destructive" : ""}
            />
            {form.formState.errors.url && (
              <p className="text-destructive text-sm mt-1">
                {form.formState.errors.url.message}
              </p>
            )}
          </div>

          <div>
            <Label className="mb-2 block">
              Content Type <span className="text-destructive">*</span>
            </Label>
            <RadioGroup
              onValueChange={(value) => form.setValue("content_type", value as FormData["content_type"])}
              defaultValue={form.getValues("content_type")}
              className="flex flex-wrap gap-4"
            >
              {["blog", "x", "facebook", "linkedin", "newsletter"].map((type) => (
                <div key={type} className="flex items-center space-x-2">
                  <RadioGroupItem value={type} id={`content-type-${type}`} />
                  <Label htmlFor={`content-type-${type}`} className="capitalize">
                    {type}
                  </Label>
                </div>
              ))}
            </RadioGroup>
            {form.formState.errors.content_type && (
              <p className="text-destructive text-sm mt-1">
                {form.formState.errors.content_type.message}
              </p>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <LoadingSpinner /> Generating...
              </>
            ) : (
              "Generate Content"
            )}
          </Button>
        </form>

        {result && (
          <>
            <ResultCard 
              imageUrl={result.image_url ?? undefined} 
              content={result.content as string} 
              contentType={result.content_type} // Pass content_type here
            />
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="mt-4 w-full max-w-2xl"
            >
              <Button variant="outline" className="w-full" onClick={handleNewGeneration}>
                Generate New Content
              </Button>
            </motion.div>
          </>
        )}
      </div>
    </motion.div>
  );
};