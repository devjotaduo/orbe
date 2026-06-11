/**
 * A2UI generative-UI types (TypeScript mirror of `src/qwenpaw/a2ui/schema.py`).
 *
 * The UI is a flat adjacency list of components; the tree is rebuilt implicitly
 * from `children` id references. Server→client messages: createSurface /
 * updateComponents / updateDataModel / deleteSurface. `A2uiSurface` is the
 * client-side accumulated state produced by the surface reducer.
 */
export interface A2uiComponent {
  id: string;
  type: string;
  properties: Record<string, unknown>;
  children: string[];
}

export type A2uiMessage =
  | { messageType: "createSurface"; surfaceId: string; root: string }
  | {
      messageType: "updateComponents";
      surfaceId: string;
      components: A2uiComponent[];
    }
  | {
      messageType: "updateDataModel";
      surfaceId: string;
      data: Record<string, unknown>;
    }
  | { messageType: "deleteSurface"; surfaceId: string };

export interface A2uiSurface {
  surfaceId: string;
  /** id of the root component (empty until createSurface arrives) */
  root: string;
  /** id -> component */
  components: Record<string, A2uiComponent>;
  /** raw data model carried by updateDataModel (for future data-binding) */
  data: Record<string, unknown>;
}
