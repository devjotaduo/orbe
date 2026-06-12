import type { A2uiMessage, A2uiSurface } from "../../api/types/a2ui";

/** A fresh, empty surface — no root, no components, empty data model. */
export function emptySurface(surfaceId: string): A2uiSurface {
  return { surfaceId, root: "", components: {}, data: {} };
}

/**
 * Apply one A2UI message to a surface, returning a new surface (immutable).
 * Mirrors the four server→client message types from the A2UI protocol.
 */
export function applyA2uiMessage(
  surface: A2uiSurface,
  msg: A2uiMessage,
): A2uiSurface {
  switch (msg.messageType) {
    case "createSurface":
      return { ...surface, surfaceId: msg.surfaceId, root: msg.root };
    case "updateComponents": {
      const components = { ...surface.components };
      for (const c of msg.components) components[c.id] = c;
      return { ...surface, components };
    }
    case "updateDataModel":
      return { ...surface, data: { ...surface.data, ...msg.data } };
    case "deleteSurface":
      return emptySurface(msg.surfaceId);
    default:
      return surface;
  }
}
