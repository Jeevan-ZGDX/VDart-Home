/** Client-side transcript merge (browser speech API + WS fallback). */

function normalize(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

function wordOverlap(existingWords: string[], newWords: string[]): number {
  const maxK = Math.min(existingWords.length, newWords.length, 24);
  for (let k = maxK; k > 0; k--) {
    const a = existingWords.slice(-k).map((w) => w.toLowerCase());
    const b = newWords.slice(0, k).map((w) => w.toLowerCase());
    if (a.every((w, i) => w === b[i])) return k;
  }
  return 0;
}

export function mergeTranscript(existing: string, segment: string): string {
  const prev = normalize(existing);
  const next = normalize(segment);
  if (!next) return prev;
  if (!prev) return next;
  if (prev.toLowerCase() === next.toLowerCase()) return prev;

  const pl = prev.toLowerCase();
  const nl = next.toLowerCase();

  if (nl.startsWith(pl)) return next;
  if (nl.includes(pl)) return next;
  if (pl.includes(nl)) return prev;

  const ew = prev.split(/\s+/);
  const nw = next.split(/\s+/);
  const overlap = wordOverlap(ew, nw);
  if (overlap > 0) {
    return [...ew, ...nw.slice(overlap)].join(" ");
  }

  return `${prev} ${next}`.trim();
}
