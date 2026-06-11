/**
 * A2UI data-model binding helpers.
 *
 * Paths are json-pointer-like, `/`-separated, without the leading slash
 * (e.g. `proposed_team/0/name`). `{$bind: "<path>"}` objects inside component
 * properties are resolved against the surface data model; editable components
 * write back through `setPath` (immutable, array-aware).
 */
export interface BindRef {
  $bind: string;
}

export function isBind(v: unknown): v is BindRef {
  return (
    typeof v === "object" &&
    v !== null &&
    typeof (v as BindRef).$bind === "string"
  );
}

/** Join a base path and a relative path (`joinBase("a/0", "b") === "a/0/b"`). */
export function joinBase(basePath: string | undefined, path: string): string {
  return basePath ? `${basePath}/${path}` : path;
}

/** Walk `data` along a `/`-separated path; `undefined` when the path misses. */
export function resolveBind(data: unknown, path: string): unknown {
  let cur: unknown = data;
  for (const seg of path.split("/")) {
    if (cur === null || typeof cur !== "object") return undefined;
    cur = (cur as Record<string, unknown>)[seg];
  }
  return cur;
}

/** Immutable deep-set along a json-pointer-like path. */
export function setPath<T>(data: T, path: string, value: unknown): T {
  const segs = path.split("/");
  function rec(node: unknown, i: number): unknown {
    if (i === segs.length) return value;
    const seg = segs[i];
    if (Array.isArray(node)) {
      const idx = Number(seg);
      const copy = node.slice();
      copy[idx] = rec(node[idx], i + 1);
      return copy;
    }
    const obj = (node ?? {}) as Record<string, unknown>;
    return { ...obj, [seg]: rec(obj[seg], i + 1) };
  }
  return rec(data, 0) as T;
}

/** Resolve every `{$bind}` in properties against data (relative to basePath). */
export function resolveProps(
  properties: Record<string, unknown>,
  data: unknown,
  basePath?: string,
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(properties)) {
    out[k] = isBind(v) ? resolveBind(data, joinBase(basePath, v.$bind)) : v;
  }
  return out;
}
