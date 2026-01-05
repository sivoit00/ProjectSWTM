import { useEffect, useMemo, useRef, useState } from "react";
import { Mic, Square } from "lucide-react";

type VoiceRecorderProps = {
  disabled?: boolean;
  onRecorded: (file: File) => void;
  onTranscript?: (text: string) => void;
  onRecordingChange?: (recording: boolean) => void;
};

type SpeechRecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: any) => void) | null;
  onerror: ((event: any) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
};

function createSpeechRecognition(): SpeechRecognitionLike | null {
  const w = window as any;
  const Ctor = w.SpeechRecognition || w.webkitSpeechRecognition;
  if (!Ctor) return null;
  try {
    return new Ctor();
  } catch {
    return null;
  }
}

function pickMimeType() {
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/ogg;codecs=opus",
    "audio/ogg",
  ];

  for (const c of candidates) {
    if (typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(c)) return c;
  }
  return "";
}

function extFromMime(mime: string) {
  const m = (mime || "").toLowerCase();
  if (m.includes("mp4")) return "m4a";
  if (m.includes("ogg")) return "ogg";
  if (m.includes("wav")) return "wav";
  if (m.includes("mpeg") || m.includes("mp3")) return "mp3";
  return "webm";
}

export default function VoiceRecorder({
  disabled,
  onRecorded,
  onTranscript,
  onRecordingChange,
}: VoiceRecorderProps) {
  const [recording, setRecording] = useState(false);
  const chunksRef = useRef<BlobPart[]>([]);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const speechRef = useRef<SpeechRecognitionLike | null>(null);
  const stopRequestedRef = useRef(false);
  const emittedRef = useRef(false);
  const transcriptRef = useRef<{ finalText: string; interimText: string }>({
    finalText: "",
    interimText: "",
  });

  const preferredMimeType = useMemo(() => pickMimeType(), []);

  const cleanup = () => {
    mediaRecorderRef.current = null;
    stopRequestedRef.current = false;
    emittedRef.current = false;

    if (speechRef.current) {
      try {
        speechRef.current.onresult = null;
        speechRef.current.onerror = null;
        speechRef.current.onend = null;
        speechRef.current.abort();
      } catch {
        // ignore
      }
      speechRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }

    chunksRef.current = [];
  };

  useEffect(() => cleanup, []);

  const start = async () => {
    if (disabled || recording) return;

    stopRequestedRef.current = false;
    emittedRef.current = false;
    transcriptRef.current = { finalText: "", interimText: "" };
    onTranscript?.("");

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;

    // Optional live speech-to-text (browser-dependent)
    const speech = createSpeechRecognition();
    if (speech && onTranscript) {
      speechRef.current = speech;
      speech.lang = (navigator.language || "de-DE").toString();
      speech.continuous = true;
      speech.interimResults = true;

      speech.onresult = (event: any) => {
        let finalChunk = "";
        let interimChunk = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const res = event.results[i];
          const text = (res?.[0]?.transcript || "").toString();
          if (res?.isFinal) finalChunk += text;
          else interimChunk += text;
        }

        const nextFinal = (transcriptRef.current.finalText + finalChunk).trim();
        const nextInterim = interimChunk.trim();
        transcriptRef.current = { finalText: nextFinal, interimText: nextInterim };

        const combined = [nextFinal, nextInterim].filter(Boolean).join(" ").trim();
        onTranscript(combined);
      };

      speech.onerror = () => {
        // Don't fail recording if recognition fails.
      };

      try {
        speech.start();
      } catch {
        speechRef.current = null;
      }
    }

    const recorder = new MediaRecorder(
      stream,
      preferredMimeType ? { mimeType: preferredMimeType } : undefined
    );

    mediaRecorderRef.current = recorder;
    chunksRef.current = [];

    recorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = () => {
      if (emittedRef.current) return;
      emittedRef.current = true;
      const mime = recorder.mimeType || preferredMimeType || "audio/webm";
      const blob = new Blob(chunksRef.current, { type: mime });
      const ext = extFromMime(mime);
      const file = new File([blob], `voice-${Date.now()}.${ext}`, { type: mime });
      onRecorded(file);
      cleanup();
    };

    recorder.start();
    setRecording(true);
    onRecordingChange?.(true);
  };

  const stop = () => {
    if (!mediaRecorderRef.current) return;
    if (stopRequestedRef.current) return;
    stopRequestedRef.current = true;

    if (speechRef.current) {
      try {
        speechRef.current.stop();
      } catch {
        // ignore
      }
    }

    // Only stop if actively recording; avoids double stop triggering extra events.
    if (mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);
    onRecordingChange?.(false);
  };

  return (
    <button
      type="button"
      onClick={recording ? stop : start}
      disabled={disabled}
      className={`p-3 rounded-xl transition-colors ${
        recording
          ? "bg-indigo-600 text-white"
          : "bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
      } disabled:opacity-50`}
      aria-label={recording ? "Stop recording" : "Start recording"}
      title={recording ? "Stop" : "Record"}
    >
      {recording ? <Square size={20} /> : <Mic size={20} />}
    </button>
  );
}
