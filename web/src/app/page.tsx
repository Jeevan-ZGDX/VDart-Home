"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { Mic, MicOff, Video, VideoOff, Copy, Check, RefreshCw, Activity } from "lucide-react";

import { AnalysisCards } from "@/components/cmfh/AnalysisCards";
import { PoseCard } from "@/components/cmfh/PoseCard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { apiGetJson, apiPostJson } from "@/lib/api";
import { captureFrame, createAudioRecorder, getCameraStream, getMicrophoneStream, isMediaSupported, stopMediaStream } from "@/lib/media";
import type { AnalyzeResponse, FinalReportMessage, HealthResponse, MetricsMessage, PoseResponse, RewriteResponse } from "@/lib/types";
import { createSessionSocket, type SessionSocket } from "@/lib/ws";
import { mergeTranscript } from "@/lib/transcript";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";

declare global {
  interface Window {
    webkitSpeechRecognition?: any;
    SpeechRecognition?: any;
    MediaRecorder?: any;
  }
}

export default function Home() {
  const [text, setText] = useState("");
  const debouncedText = useDebouncedValue(text, 450);
  const [copied, setCopied] = useState(false);

  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [rewritten, setRewritten] = useState<RewriteResponse | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamSupported, setStreamSupported] = useState(false);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const voiceModeRef = useRef<"speech" | "backend" | null>(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRewriting, setIsRewriting] = useState(false);
  const [autoRewrite, setAutoRewrite] = useState(false);

  // Voice
  const [isListening, setIsListening] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const recognitionRef = useRef<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const sessionSocketRef = useRef<SessionSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  
  const speechAvailable = useMemo(() => {
    if (typeof window === "undefined") return false;
    return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
  }, []);

  // Camera
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [pose, setPose] = useState<PoseResponse | null>(null);
  const cameraTimerRef = useRef<number | null>(null);
  const [frameCount, setFrameCount] = useState(0);

  useEffect(() => {
    apiGetJson<HealthResponse>("/health").then((r) => {
      if (r.ok) setHealth(r.data);
    });
  }, []);

  useEffect(() => {
    setStreamSupported(isMediaSupported() && typeof window.MediaRecorder !== "undefined");
  }, []);

  useEffect(() => {
    if (!debouncedText.trim()) {
      setAnalysis(null);
      return;
    }

    let cancelled = false;
    setIsAnalyzing(true);
    apiPostJson<AnalyzeResponse>("/analyze", { text: debouncedText }).then((r) => {
      if (cancelled) return;
      setIsAnalyzing(false);
      if (!r.ok) {
        toast.error(`Analyze failed: ${r.error}`);
        return;
      }
      setAnalysis(r.data);
    });

    return () => {
      cancelled = true;
    };
  }, [debouncedText]);

  useEffect(() => {
    if (!autoRewrite) return;
    if (!debouncedText.trim()) return;
    if (health && !health.ollama_available) return; // avoid spamming fallback rewrite as you type

    let cancelled = false;
    setIsRewriting(true);
    apiPostJson<RewriteResponse>("/rewrite", { text: debouncedText, style: "professional" }).then(
      (r) => {
        if (cancelled) return;
        setIsRewriting(false);
        if (!r.ok) {
          toast.error(`Rewrite failed: ${r.error}`);
          return;
        }
        setRewritten(r.data);
      }
    );

    return () => {
      cancelled = true;
    };
  }, [autoRewrite, debouncedText, health]);

  async function startVoice() {
    if (isListening) return;
    if (!speechAvailable && !streamSupported) {
      toast.error("No supported voice recognition available in this browser.");
      return;
    }

    if (!speechAvailable && streamSupported) {
      return startBackendStream();
    }

    try {
      // Request microphone access
      const stream = await getMicrophoneStream();
      
      // Set up audio level visualization
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 256;
      
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      audioStreamRef.current = stream;

      // Update audio levels
      const updateAudioLevel = () => {
        if (!analyser || !isListening) return;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(Math.min(100, (average / 255) * 100));
        requestAnimationFrame(updateAudioLevel);
      };
      updateAudioLevel();

      // Start browser's speech recognition
      const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognitionAPI();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      // Handle results
      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        // Update text with final + interim
        setText(prev => {
          let cleaned = prev.replace(/\s*\[listening\.\.\.\]$/, '').trim();
          if (finalTranscript) {
            cleaned = cleaned ? `${cleaned} ${finalTranscript.trim()}` : finalTranscript.trim();
          }
          if (interimTranscript) {
            return `${cleaned} ${interimTranscript} [listening...]`;
          }
          return cleaned;
        });
      };

      // Handle errors - SILENTLY ignore normal browser behavior
      recognition.onerror = () => {
        // This is NORMAL in Chrome/Edge - speech recognition stops after silence
        // Don't show any error toast, just attempt to restart
        if (isListening) {
          try {
            recognition.start();
          } catch (e) {
            // Only stop if restart fails
            setIsListening(false);
          }
        }
      };

      // Handle end - auto restart
      recognition.onend = () => {
        if (isListening) {
          try {
            recognition.start();
          } catch (e) {
            setIsListening(false);
          }
        }
      };

      recognitionRef.current = recognition;
      voiceModeRef.current = "speech";
      setIsListening(true);
      recognition.start();
      toast.success("Listening... Speak now!");

    } catch (err) {
      toast.error("Could not access microphone. Check browser permissions.");
      console.error("Voice input error:", err);
      setIsListening(false);
    }
  }

  function applyMetrics(msg: MetricsMessage, fullText: string) {
    setAnalysis({
      text: fullText,
      grammar: {},
      filler: msg.filler,
      confidence: msg.confidence,
      vocabulary: msg.vocabulary as AnalyzeResponse["vocabulary"],
      structure: {},
      overall_score: msg.quick_score,
    });
  }

  function applyFinalReport(msg: FinalReportMessage) {
    if (msg.error) {
      toast.error(msg.error);
      return;
    }
    if (msg.rewritten) {
      setRewritten({
        original: msg.original ?? msg.text ?? "",
        rewritten: msg.rewritten,
        style: "tedx",
        success: true,
        source: "ollama",
      });
    }
    const overall = (msg.scores as { overall_score?: number })?.overall_score;
    if (overall != null) {
      toast.success(`Session complete — score ${Math.round(overall)}/100`);
    } else {
      toast.success("Session analysis complete");
    }
  }

  function stopVoice() {
    setIsListening(false); // Prevent auto-restart

    if (voiceModeRef.current === "backend") {
      const recorder = mediaRecorderRef.current;
      if (recorder && recorder.state === "recording") {
        recorder.stop();
      }
      const sock = sessionSocketRef.current;
      if (sock?.connected) {
        sock.endSession();
      }
    }

    const rec = recognitionRef.current;
    if (rec) {
      try {
        rec.stop();
      } catch (e) {
        console.log("Error stopping recognition:", e);
      }
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
    }

    if (audioStreamRef.current) {
      stopMediaStream(audioStreamRef.current);
      audioStreamRef.current = null;
    }

    if (mediaRecorderRef.current) {
      mediaRecorderRef.current = null;
    }

    sessionSocketRef.current?.close();
    sessionSocketRef.current = null;

    voiceModeRef.current = null;
    setIsStreaming(false);
    setText((prev) => prev.replace(/\s*\[listening\.\.\.\]$/, ""));
    setAudioLevel(0);
  }

  async function startBackendStream() {
    if (isListening) return;

    try {
      const socket = createSessionSocket();
      await socket.connect({
        onPartialTranscript: (msg) => {
          setText(msg.full_text);
        },
        onMetrics: (msg) => {
          setText((fullText) => {
            if (fullText.trim()) applyMetrics(msg, fullText);
            return fullText;
          });
        },
        onPose: (msg) => setPose(msg),
        onFinalReport: applyFinalReport,
        onError: (message) => console.warn("WS:", message),
      });
      sessionSocketRef.current = socket;

      const stream = await getMicrophoneStream();
      audioStreamRef.current = stream;

      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 256;

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      const updateAudioLevel = () => {
        if (!analyser || !isListening) return;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
        setAudioLevel(Math.min(100, (average / 255) * 100));
        requestAnimationFrame(updateAudioLevel);
      };

      let mimeType = "audio/webm;codecs=opus";
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = "audio/webm";
      }

      const recorder = createAudioRecorder(stream, mimeType);
      recorder.ondataavailable = async (event: BlobEvent) => {
        if (!event.data || event.data.size === 0) return;
        if (!sessionSocketRef.current?.connected) return;

        try {
          const arrayBuffer = await event.data.arrayBuffer();
          const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
          sessionSocketRef.current.sendAudioChunk(base64Audio, mimeType);
        } catch (e) {
          console.warn("Realtime chunk send failed:", e);
        }
      };

      recorder.onerror = (event) => {
        console.error("MediaRecorder error:", event);
      };

      recorder.start(2000);
      mediaRecorderRef.current = recorder;
      voiceModeRef.current = "backend";
      setIsListening(true);
      setIsStreaming(true);
      updateAudioLevel();
      toast.success("Real-time session started — speak now!");
    } catch (err) {
      sessionSocketRef.current?.close();
      sessionSocketRef.current = null;
      console.error("Realtime voice stream error:", err);
      toast.error("Could not start real-time session. Is the API running?");
    }
  }

  async function rewriteNow() {
    if (!text.trim()) return;
    setIsRewriting(true);
    const r = await apiPostJson<RewriteResponse>("/rewrite", {
      text,
      style: "professional",
    });
    setIsRewriting(false);
    if (!r.ok) {
      toast.error(`Rewrite failed: ${r.error}`);
      return;
    }
    setRewritten(r.data);
    toast.success("Text rewritten successfully!");
  }

  async function copyRewrittenText() {
    if (!rewritten?.rewritten) return;
    try {
      await navigator.clipboard.writeText(rewritten.rewritten);
      setCopied(true);
      toast.success("Copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error("Failed to copy text");
    }
  }

  async function startCamera() {
    if (!videoRef.current) return;
    try {
      await getCameraStream(videoRef.current, 640, 480);
      setCameraOn(true);
    } catch (e) {
      toast.error(
        `Could not start camera: ${e instanceof Error ? e.message : String(e)}`
      );
    }
  }

  function stopCamera() {
    if (cameraTimerRef.current) {
      window.clearInterval(cameraTimerRef.current);
      cameraTimerRef.current = null;
    }
    const video = videoRef.current;
    if (video?.srcObject) {
      stopMediaStream(video.srcObject as MediaStream);
      video.srcObject = null;
    }
    setCameraOn(false);
    setPose(null);
  }

  useEffect(() => {
    if (!cameraOn) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    cameraTimerRef.current = window.setInterval(async () => {
      try {
        const w = video.videoWidth || 640;
        const h = video.videoHeight || 480;
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;
        ctx.drawImage(video, 0, 0, w, h);
        const base64 = captureFrame(video, canvas);
        if (!base64) return;

        setFrameCount(prev => prev + 1);
        const sock = sessionSocketRef.current;
        if (sock?.connected) {
          sock.sendVideoFrame(base64);
          return;
        }
        const r = await apiPostJson<PoseResponse>("/vision/analyze/frame", { frame: base64 });
        if (r.ok) setPose(r.data);
      } catch (err) {
        console.warn("Frame analysis failed:", err);
      }
    }, 1000);

    return () => stopCamera();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cameraOn]);

  return (
    <div className="flex flex-1 flex-col bg-background">
      <header className="border-b">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-4">
          <div className="flex flex-col">
            <div className="text-lg font-semibold">CMFH</div>
            <div className="text-sm text-muted-foreground">
              Real-time rewrite + grammar + vocabulary (text / voice / camera)
            </div>
          </div>
          <div className="flex items-center gap-2">
            {health ? (
              <>
                <Badge variant="secondary">API: {health.status}</Badge>
                <Badge variant={health.ollama_available ? "secondary" : "outline"}>
                  Ollama: {health.ollama_available ? "on" : "off (fallback)"}
                </Badge>
              </>
            ) : (
              <Badge variant="outline">API: unknown</Badge>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-4 px-4 py-6">
        <Tabs defaultValue="text" className="w-full">
          <TabsList>
            <TabsTrigger value="text">Text</TabsTrigger>
            <TabsTrigger value="voice">Voice</TabsTrigger>
            <TabsTrigger value="camera">Camera</TabsTrigger>
          </TabsList>

          <TabsContent value="text" className="mt-4 flex flex-col gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Input</CardTitle>
                <CardDescription>Type your sentence/speech here.</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                <Label htmlFor="input">Text</Label>
                <Textarea
                  id="input"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Enter text…"
                  className="min-h-32"
                />
                <div className="flex flex-wrap items-center gap-2">
                  <Button onClick={rewriteNow} disabled={!text.trim() || isRewriting}>
                    {isRewriting ? "Rewriting…" : "Rewrite"}
                  </Button>
                  <Button
                    variant={autoRewrite ? "secondary" : "outline"}
                    onClick={() => setAutoRewrite((v) => !v)}
                  >
                    Auto rewrite: {autoRewrite ? "On" : "Off"}
                  </Button>
                  <Badge variant="outline">
                    {isAnalyzing ? "Analyzing…" : "Analysis ready"}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Rewrite output</CardTitle>
                    <CardDescription>
                      Professional rewrite (LLM if available, otherwise rule-based).
                    </CardDescription>
                  </div>
                  {rewritten?.rewritten && (
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={copyRewrittenText}
                            className="gap-2"
                          >
                            {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
                            {copied ? "Copied!" : "Copy"}
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Copy rewritten text to clipboard</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  )}
                </div>
                {rewritten && (
                  <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                    <Badge variant="outline" className="text-xs">
                      Source: {rewritten.source}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      Style: {rewritten.style}
                    </Badge>
                  </div>
                )}
              </CardHeader>
              <CardContent className="text-sm">
                {isRewriting ? (
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-[90%]" />
                    <Skeleton className="h-4 w-[95%]" />
                    <Skeleton className="h-4 w-[85%]" />
                  </div>
                ) : rewritten?.rewritten ? (
                  <div className="bg-muted/50 rounded-lg p-4 whitespace-pre-wrap leading-relaxed">
                    {rewritten.rewritten}
                  </div>
                ) : (
                  <div className="text-muted-foreground text-center py-8">
                    <RefreshCw className="size-12 mx-auto mb-4 opacity-20" />
                    Click "Rewrite" to generate a professionally rewritten version.
                  </div>
                )}
              </CardContent>
            </Card>

            <AnalysisCards analysis={analysis} />
          </TabsContent>

          <TabsContent value="voice" className="mt-4 flex flex-col gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Voice input</CardTitle>
                <CardDescription>
                  Uses browser speech-to-text for real-time transcription with audio level visualization.
                  If the browser speech API is unavailable, it streams audio chunks to the backend.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                <div className="flex flex-wrap items-center gap-3">
                  <Button 
                    onClick={startVoice} 
                    disabled={!(speechAvailable || streamSupported) || isListening}
                    className="gap-2"
                  >
                    <Mic className="size-4" />
                    Start listening
                  </Button>
                  <Button
                    variant="outline"
                    onClick={stopVoice}
                    disabled={!isListening}
                    className="gap-2"
                  >
                    <MicOff className="size-4" />
                    Stop
                  </Button>
                  <Badge variant={speechAvailable ? "secondary" : "destructive"}>
                    {speechAvailable ? "Speech recognition supported" : "Speech API unsupported"}
                  </Badge>
                  <Badge variant={streamSupported ? "secondary" : "destructive"}>
                    {streamSupported ? "Audio stream fallback ready" : "Audio stream unsupported"}
                  </Badge>
                </div>

                {isListening && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Audio level</span>
                      <span className="font-mono">{Math.round(audioLevel)}%</span>
                    </div>
                    <Progress value={audioLevel} className="h-2" />
                    <div className="flex items-center gap-2 text-sm text-emerald-600">
                      <Activity className="size-4 animate-pulse" />
                      <span>Recording... Speak clearly into your microphone</span>
                    </div>
                    {isStreaming && (
                      <div className="text-sm text-muted-foreground">
                        Streaming audio chunks to server for transcription.
                      </div>
                    )}
                  </div>
                )}

                <Label htmlFor="voiceText">Live Transcript</Label>
                <Textarea
                  id="voiceText"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Transcript will appear here as you speak..."
                  className="min-h-40 font-mono text-sm"
                />
              </CardContent>
            </Card>

            <AnalysisCards analysis={analysis} />
          </TabsContent>

          <TabsContent value="camera" className="mt-4 flex flex-col gap-4">
            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Camera & Live Action Analysis</CardTitle>
                  <CardDescription>
                    Real-time posture and body-language analysis at 1 frame/second.
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <Button onClick={startCamera} disabled={cameraOn} className="gap-2">
                      <Video className="size-4" />
                      Start camera
                    </Button>
                    <Button variant="outline" onClick={stopCamera} disabled={!cameraOn} className="gap-2">
                      <VideoOff className="size-4" />
                      Stop
                    </Button>
                    <Badge variant={cameraOn ? "secondary" : "outline"}>
                      {cameraOn ? "Live streaming" : "Camera off"}
                    </Badge>
                    {cameraOn && (
                      <Badge variant="outline" className="font-mono">
                        Frames: {frameCount}
                      </Badge>
                    )}
                  </div>

                  {cameraOn && (
                    <div className="flex items-center gap-2 text-sm text-emerald-600">
                      <Activity className="size-4 animate-pulse" />
                      <span>Analyzing your posture in real-time...</span>
                    </div>
                  )}

                  <div className="rounded-lg border bg-muted p-2 overflow-hidden">
                    <video 
                      ref={videoRef} 
                      className="aspect-video w-full rounded-md bg-black" 
                      playsInline
                      muted
                    />
                    <canvas ref={canvasRef} className="hidden" />
                  </div>
                </CardContent>
              </Card>

              <PoseCard pose={pose} />
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Notes</CardTitle>
                <CardDescription>
                  This is “live actions” via the backend pose analyzer.
                </CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                For best results, keep your full upper body in frame with good lighting.
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
