import { API_BASE } from "@/lib/api";
import type {
  FinalReportMessage,
  MetricsMessage,
  PartialTranscriptMessage,
  PoseResponse,
} from "@/lib/types";

export type WsServerMessage =
  | { type: "pong" }
  | PartialTranscriptMessage
  | MetricsMessage
  | ({ type: "pose" } & PoseResponse & { seq?: number })
  | FinalReportMessage
  | { type: "error"; message: string; seq?: number };

export type SessionSocketHandlers = {
  onPartialTranscript?: (msg: PartialTranscriptMessage) => void;
  onMetrics?: (msg: MetricsMessage) => void;
  onPose?: (msg: PoseResponse) => void;
  onFinalReport?: (msg: FinalReportMessage) => void;
  onError?: (message: string) => void;
  onOpen?: () => void;
  onClose?: () => void;
};

function apiBaseToWsUrl(apiBase: string): string {
  const url = new URL(apiBase.endsWith("/") ? apiBase : `${apiBase}/`);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = url.pathname.replace(/\/?$/, "/ws/session");
  return url.toString();
}

export class SessionSocket {
  private ws: WebSocket | null = null;
  private audioSeq = 0;
  private frameSeq = 0;
  private handlers: SessionSocketHandlers = {};

  constructor(private readonly wsUrl: string) {}

  get connected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  connect(handlers: SessionSocketHandlers): Promise<void> {
    this.handlers = handlers;
    this.audioSeq = 0;
    this.frameSeq = 0;

    return new Promise((resolve, reject) => {
      const ws = new WebSocket(this.wsUrl);
      this.ws = ws;

      ws.onopen = () => {
        handlers.onOpen?.();
        resolve();
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data as string) as WsServerMessage;
          this.dispatch(msg);
        } catch {
          handlers.onError?.("Invalid server message");
        }
      };

      ws.onerror = () => {
        reject(new Error("WebSocket connection failed"));
      };

      ws.onclose = () => {
        handlers.onClose?.();
        this.ws = null;
      };
    });
  }

  private dispatch(msg: WsServerMessage) {
    switch (msg.type) {
      case "partial_transcript":
        this.handlers.onPartialTranscript?.(msg);
        break;
      case "metrics":
        this.handlers.onMetrics?.(msg);
        break;
      case "pose":
        this.handlers.onPose?.(msg as PoseResponse);
        break;
      case "final_report":
        this.handlers.onFinalReport?.(msg);
        break;
      case "error":
        this.handlers.onError?.(msg.message);
        break;
      default:
        break;
    }
  }

  sendAudioChunk(base64Data: string, mime: string) {
    if (!this.connected) return;
    const seq = this.audioSeq++;
    this.ws!.send(
      JSON.stringify({
        type: "audio_chunk",
        data: base64Data,
        mime,
        seq,
      })
    );
  }

  sendVideoFrame(base64Data: string) {
    if (!this.connected) return;
    const seq = this.frameSeq++;
    this.ws!.send(
      JSON.stringify({
        type: "video_frame",
        data: base64Data,
        seq,
      })
    );
  }

  endSession() {
    if (!this.connected) return;
    this.ws!.send(JSON.stringify({ type: "end_session" }));
  }

  close() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export function createSessionSocket(): SessionSocket {
  return new SessionSocket(apiBaseToWsUrl(API_BASE));
}
