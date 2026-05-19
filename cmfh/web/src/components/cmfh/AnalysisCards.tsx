"use client";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import type { AnalyzeResponse } from "@/lib/types";

function Metric({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="text-sm text-muted-foreground">{label}</div>
      <div className="text-sm font-medium tabular-nums">{value}</div>
    </div>
  );
}

function ScoreBadge({ score }: { score: number }) {
  const variant = score >= 80 ? "secondary" : score >= 50 ? "outline" : "destructive";
  return (
    <Badge variant={variant as any}>
      {Math.round(score)}/100
    </Badge>
  );
}

export function AnalysisCards({
  analysis,
}: {
  analysis: AnalyzeResponse | null;
}) {
  if (!analysis) return null;

  const errors = analysis.grammar?.errors ?? [];
  const errorCount = analysis.grammar?.error_count ?? errors.length ?? 0;
  const overallScore = analysis.overall_score ?? 0;

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-500";
    if (score >= 50) return "text-amber-500";
    return "text-red-500";
  };

  return (
    <div className="grid gap-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Overall Score</span>
            <ScoreBadge score={overallScore} />
          </CardTitle>
          <CardDescription>Real-time analysis of your communication</CardDescription>
          <Progress value={overallScore} className="h-2 mt-2" />
        </CardHeader>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between gap-4">
              <span>Grammar & Spelling</span>
              <Badge variant={errorCount === 0 ? "secondary" : "destructive"}>
                {errorCount} issue{errorCount === 1 ? "" : "s"}
              </Badge>
            </CardTitle>
            <CardDescription>Real-time grammar and spelling checks.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <ScrollArea className="h-52 rounded-md border">
              <div className="flex flex-col gap-3 p-4">
                {errors.length === 0 ? (
                  <div className="flex items-center gap-2 text-sm text-emerald-600">
                    <span>✓</span>
                    <span>No grammar or spelling issues found!</span>
                  </div>
                ) : (
                  errors.map((e, idx) => (
                    <div key={idx} className="flex flex-col gap-1">
                      <div className="text-sm font-medium text-red-600">⚠️ {e.message}</div>
                      {e.context ? (
                        <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                          Context: "{e.context}"
                        </div>
                      ) : null}
                      {e.replacements?.length ? (
                        <div className="text-xs">
                          <span className="text-muted-foreground">Suggestion: </span>
                          <span className="font-medium text-emerald-600 bg-emerald-50 dark:bg-emerald-950/30 px-1.5 py-0.5 rounded">
                            {e.replacements.slice(0, 3).join(", ")}
                          </span>
                        </div>
                      ) : null}
                      {idx < errors.length - 1 ? <Separator className="mt-2" /> : null}
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between gap-4">
              <span>Vocabulary Analysis</span>
              <ScoreBadge score={analysis.vocabulary?.vocabulary_score ?? 0} />
            </CardTitle>
            <CardDescription>
              Word diversity, quality metrics, and usage statistics.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <Metric label="Quality" value={analysis.vocabulary?.quality ?? "—"} />
            <Metric
              label="Lexical diversity"
              value={`${analysis.vocabulary?.lexical_diversity ?? 0}%`}
            />
            <Metric label="Word count" value={analysis.vocabulary?.word_count ?? 0} />
            <Metric
              label="Unique words"
              value={analysis.vocabulary?.unique_words ?? 0}
            />
            <Metric
              label="Weak words"
              value={analysis.vocabulary?.weak_words ?? 0}
            />
            <Metric
              label="Academic words"
              value={analysis.vocabulary?.academic_words ?? 0}
            />
            <Metric
              label="Action verbs"
              value={analysis.vocabulary?.action_verbs ?? 0}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

