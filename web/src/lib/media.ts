export function isMediaSupported(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof navigator !== "undefined" &&
    Boolean(navigator.mediaDevices?.getUserMedia)
  );
}

export async function getMicrophoneStream(): Promise<MediaStream> {
  if (!isMediaSupported()) {
    throw new Error("Media devices are not supported in this browser.");
  }

  return navigator.mediaDevices.getUserMedia({ audio: true, video: false });
}

export async function getCameraStream(
  videoElement: HTMLVideoElement,
  width = 640,
  height = 480
): Promise<MediaStream> {
  if (!isMediaSupported()) {
    throw new Error("Media devices are not supported in this browser.");
  }

  const stream = await navigator.mediaDevices.getUserMedia({
    video: { width: { ideal: width }, height: { ideal: height } },
    audio: false,
  });

  videoElement.srcObject = stream;
  await videoElement.play();
  return stream;
}

export function captureFrame(
  videoElement: HTMLVideoElement,
  canvasElement: HTMLCanvasElement,
  quality = 0.7
): string {
  const width = videoElement.videoWidth || 640;
  const height = videoElement.videoHeight || 480;

  canvasElement.width = width;
  canvasElement.height = height;

  const ctx = canvasElement.getContext("2d");
  if (!ctx) {
    throw new Error("Unable to acquire canvas rendering context.");
  }

  ctx.drawImage(videoElement, 0, 0, width, height);
  const dataUrl = canvasElement.toDataURL("image/jpeg", quality);
  return dataUrl.split(",")[1] ?? "";
}

export function stopMediaStream(stream: MediaStream | null): void {
  if (!stream) {
    return;
  }
  stream.getTracks().forEach((track) => track.stop());
}

export function createAudioRecorder(
  stream: MediaStream,
  mimeType = "audio/webm;codecs=opus"
): MediaRecorder {
  if (typeof MediaRecorder === "undefined") {
    throw new Error("MediaRecorder is not available in this browser.");
  }

  if (!MediaRecorder.isTypeSupported(mimeType)) {
    mimeType = "audio/webm";
  }

  return new MediaRecorder(stream, { mimeType });
}
