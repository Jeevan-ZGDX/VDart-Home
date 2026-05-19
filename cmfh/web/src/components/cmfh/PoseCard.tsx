"use client";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { PoseResponse } from "@/lib/types";

export function PoseCard({ pose }: { pose: PoseResponse | null }) {
  if (!pose) return null;

  if (!pose.detected) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Camera analysis</CardTitle>
          <CardDescription>Body-language feedback (live).</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          {pose.message ?? "No person detected."}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between gap-4">
          <span>Camera analysis</span>
          <Badge variant="secondary">{pose.posture_score}% posture</Badge>
        </CardTitle>
        <CardDescription>Body-language feedback (live).</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <div className="flex items-center justify-between gap-4">
          <div className="text-sm text-muted-foreground">Confidence</div>
          <div className="text-sm font-medium">{pose.confidence_level}</div>
        </div>
        <div className="flex items-center justify-between gap-4">
          <div className="text-sm text-muted-foreground">Hands</div>
          <div className="text-sm font-medium">{pose.hand_gesture}</div>
        </div>
        <div className="flex items-center justify-between gap-4">
          <div className="text-sm text-muted-foreground">Arms</div>
          <div className="text-sm font-medium">{pose.arm_position}</div>
        </div>
        <div className="flex items-center justify-between gap-4">
          <div className="text-sm text-muted-foreground">Shoulder balance</div>
          <div className="text-sm font-medium">{pose.shoulder_balance}%</div>
        </div>

        <Separator />

        <div className="text-sm font-medium">Tips</div>
        <ul className="list-disc pl-5 text-sm text-muted-foreground">
          {(pose.suggestions ?? []).slice(0, 3).map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

