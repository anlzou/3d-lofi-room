// The first paint waits on two big downloads (the model and the lightmap set), the decoder,
// and the work of assembling the room. Byte sizes on disk weight the bar before the server has
// told us a real Content-Length — and when a host sends none at all, the nominal size is all we
// have, so the bar still moves instead of sitting at zero.
export const loadStages = [
  { id: 'model', label: '正在加载房间模型', bytes: 2.76e6 },
  { id: 'decode', label: '正在解码模型', bytes: 3.5e5 },
  { id: 'lighting', label: '正在加载光照贴图', bytes: 2.62e6 },
  { id: 'build', label: '正在布置房间', bytes: 2e5 },
] as const;
export type LoadStage = typeof loadStages[number]['id'];
export const loadStageLabel = (id: LoadStage) => loadStages.find(stage => stage.id === id)!.label;
export function loadingProgress() {
  const sent = new Map<LoadStage, number>();
  const size = new Map<LoadStage, number>();
  const nominal = (id: LoadStage) => loadStages.find(stage => stage.id === id)!.bytes;
  const totals = () => loadStages.map(stage => size.get(stage.id) ?? nominal(stage.id));
  return {
    /** `sent`/`total` come from a download progress event; a total of 0 means "not told". */
    report(id: LoadStage, progress: number, total: number) {
      size.set(id, total > 0 ? total : nominal(id));
      // Monotonic: a retried range request must never walk the bar backwards.
      sent.set(id, Math.max(sent.get(id) ?? 0, progress));
    },
    /** Marks a stage finished. Decoding and assembly report no bytes of their own. */
    done(id: LoadStage) { size.set(id, size.get(id) ?? nominal(id)); sent.set(id, size.get(id)!); },
    label: (id: LoadStage) => loadStageLabel(id),
    /** 0..1 across every stage, weighted by size. */
    value() {
      const sizes = totals();
      const done = loadStages.reduce((sum, stage, i) => sum + Math.min(sent.get(stage.id) ?? 0, sizes[i]), 0);
      const all = sizes.reduce((sum, bytes) => sum + bytes, 0);
      return all > 0 ? Math.min(1, done / all) : 0;
    },
    /** An estimate in bytes, for the "1.2 / 5.6 MB" line; nominal where the host stayed silent. */
    estimate() {
      const sizes = totals();
      const done = loadStages.reduce((sum, stage, i) => sum + Math.min(sent.get(stage.id) ?? 0, sizes[i]), 0);
      return { loaded: done, total: sizes.reduce((sum, bytes) => sum + bytes, 0) };
    },
  };
}
