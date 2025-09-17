import { ContentGeneratorForm } from "@/components/content-generator-form";
import { MadeWithDyad } from "@/components/made-with-dyad";

export default function Home() {
  return (
    <div className="min-h-screen font-[family-name:var(--font-geist-sans)]">
      <ContentGeneratorForm />
      <MadeWithDyad />
    </div>
  );
}