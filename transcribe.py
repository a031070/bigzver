#!/usr/bin/env python3
"""
One-off ASR transcription for two-part Russian programming lecture.
Usage:  python transcribe.py
Output: transcript.txt in the project root

Part 1: Программирую на питоне [9ks3CF4PWZw].wav  (~84 min)
Part 2: Программирую на питоне [hvpf2ZdQ9ko].wav  (~64 min)
"""
import wave
from pathlib import Path
from faster_whisper import WhisperModel

BASE = Path(__file__).parent
AUDIO_DIR = BASE / "audio_for_asr"

PARTS = [
    AUDIO_DIR / "Программирую на питоне [9ks3CF4PWZw].wav",
    AUDIO_DIR / "Программирую на питоне [hvpf2ZdQ9ko].wav",
]

OUTPUT = BASE / "transcript.txt"
MODEL_SIZE = "large-v3"


def fmt_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def wav_duration(path: Path) -> float:
    with wave.open(str(path)) as wf:
        return wf.getnframes() / wf.getframerate()


def main():
    print(f"Loading model {MODEL_SIZE}...")
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

    time_offset = 0.0
    all_segments = []

    for i, audio_path in enumerate(PARTS, 1):
        duration = wav_duration(audio_path)
        print(f"\nPart {i}: {audio_path.name} ({duration / 60:.1f} min)")

        segments, info = model.transcribe(
            str(audio_path),
            language="ru",
            beam_size=5,
            word_timestamps=False,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
        )

        count = 0
        for seg in segments:
            all_segments.append({
                "start": seg.start + time_offset,
                "end": seg.end + time_offset,
                "text": seg.text.strip(),
            })
            count += 1
            if count % 50 == 0:
                print(f"  {count} segments, at {fmt_ts(seg.end + time_offset)}")

        print(f"  Part {i} done: {count} segments.")
        time_offset += duration

    print(f"\nWriting {len(all_segments)} segments → {OUTPUT}")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("# Программирую на питоне — транскрипт полной лекции\n")
        f.write(f"# Part 1: {PARTS[0].name}\n")
        f.write(f"# Part 2: {PARTS[1].name}\n\n")
        for seg in all_segments:
            f.write(f"[{fmt_ts(seg['start'])} --> {fmt_ts(seg['end'])}]  {seg['text']}\n")

    print("Done.")


if __name__ == "__main__":
    main()
