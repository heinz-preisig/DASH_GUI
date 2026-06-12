import React, { useState } from 'react';
import { AddChildModal } from './AddChildModal';

/**
 * TreeView - Displays schema components in a hierarchical tree structure
 * Supports right-click context menu for adding children
 */
export function TreeView({ tree, rootBrickId, components, refs, groups, onAddChild, onToast, sessionId, schemaId }) {
  const compMap = Object.fromEntries(components.map(c => [c.brick_id, c]));
  const [ctxMenu, setCtxMenu] = useState(null); // { x, y, brickId, brickName }
  const [showAddChildModal, setShowAddChildModal] = useState(false);
  const [selectedParentId, setSelectedParentId] = useState(null);

  const handleContextMenu = (e, brickId, brickName) => {
    e.preventDefault();
    e.stopPropagation();
    setCtxMenu({ x: e.clientX, y: e.clientY, brickId, brickName });
  };

  const handleAddChild = () => {
    setSelectedParentId(ctxMenu.brickId);
    setShowAddChildModal(true);
    setCtxMenu(null);
  };

  const renderNode = (brickId, depth = 0) => {
    const brick = compMap[brickId];
    const children = tree.tree?.[brickId] || [];
    const brickRefs = refs.filter(r => r.attach_to_brick_id === brickId);
    return (
      <div key={brickId} style={{ paddingLeft: depth * 16 }}>
        <div
          style={{ padding: "3px 0", fontSize: 13, fontWeight: depth === 0 ? 600 : 400, cursor: "context-menu" }}
          onContextMenu={(e) => handleContextMenu(e, brickId, brick?.name || brickId)}
        >
          {depth === 0 ? "◆ " : "├ "}{brick?.name || brickId}
          {brick?.object_type && (
            <span className={`brick-type-badge ${brick.object_type === "NodeShape" ? "badge-node" : "badge-prop"}`} style={{ marginLeft: 5 }}>
              {brick.object_type === "NodeShape" ? "N" : "P"}
            </span>
          )}
        </div>
        {brickRefs.map((ref, i) => (
          <div key={i} style={{ paddingLeft: 16, fontSize: 12, color: "#8888cc", fontStyle: "italic" }}>
            └ ⬡ {ref.label || ref.schema_id} ({ref.property_path})
          </div>
        ))}
        {children.map(childId => renderNode(childId, depth + 1))}
      </div>
    );
  };

  const renderGroup = (group) => {
    // Get components that belong to this group (and are not nested under other components)
    const groupMembers = components.filter(c => {
      const isInGroup = c.group_id === group.id || c.ui_metadata?.group_id === group.id;
      const isRootOrStandalone = !tree.tree || !Object.values(tree.tree).flat().includes(c.brick_id);
      return isInGroup && isRootOrStandalone;
    });

    if (groupMembers.length === 0) return null;

    return (
      <div key={group.id} style={{ marginTop: 8 }}>
        <div style={{
          fontSize: 11,
          fontWeight: 600,
          color: "#555",
          background: "#f5f5f5",
          padding: "4px 8px",
          borderRadius: 4,
          marginBottom: 4,
          display: "flex",
          alignItems: "center",
          gap: 4
        }}>
          <span>▼</span>
          <span>{group.label || group.id}</span>
          {group.description && <span style={{ fontWeight: 400, color: "#888", marginLeft: 4 }}>— {group.description}</span>}
        </div>
        <div style={{ paddingLeft: 8 }}>
          {groupMembers.map(c => renderNode(c.brick_id, 0))}
        </div>
      </div>
    );
  };

  if (!rootBrickId && components.length === 0) {
    return <div className="empty-hint">No components yet</div>;
  }

  const roots = tree.roots?.length ? tree.roots : (rootBrickId ? [rootBrickId] : []);

  // Get standalone components that are not in any group
  const groupedBrickIds = new Set(
    components.filter(c => c.group_id || c.ui_metadata?.group_id).map(c => c.brick_id)
  );
  const standalone = components.filter(c =>
    !roots.includes(c.brick_id) &&
    !Object.values(tree.tree || {}).flat().includes(c.brick_id) &&
    !groupedBrickIds.has(c.brick_id)
  );

  return (
    <div style={{ fontFamily: "monospace" }}>
      {/* Root components (not in groups) */}
      {roots.map(id => renderNode(id, 0))}

      {/* Groups with their members */}
      {(groups || []).map(renderGroup)}

      {/* Ungrouped standalone components */}
      {standalone.length > 0 && (
        <>
          <div style={{ fontSize: 11, color: "#aaa", marginTop: 10, marginBottom: 4 }}>Ungrouped</div>
          {standalone.map(c => renderNode(c.brick_id, 0))}
        </>
      )}

      {/* Context Menu */}
      {ctxMenu && (
        <div
          style={{
            position: "fixed",
            left: ctxMenu.x,
            top: ctxMenu.y,
            background: "white",
            border: "1px solid #ccc",
            borderRadius: 4,
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
            zIndex: 1000,
            minWidth: 150
          }}
          onMouseLeave={() => setCtxMenu(null)}
        >
          <div
            style={{ padding: "8px 12px", cursor: "pointer", borderBottom: "1px solid #eee" }}
            onClick={handleAddChild}
            onMouseEnter={(e) => e.target.style.background = "#f0f0f0"}
            onMouseLeave={(e) => e.target.style.background = "white"}
          >
            Add Child…
          </div>
        </div>
      )}

      {/* Add Child Modal */}
      {showAddChildModal && (
        <AddChildModal
          sessionId={sessionId}
          schemaId={schemaId}
          parentId={selectedParentId}
          components={components}
          onToast={onToast}
          onAdded={(childId, pathIri, label) => {
            setShowAddChildModal(false);
            onAddChild && onAddChild(selectedParentId, childId, pathIri, label);
          }}
          onClose={() => setShowAddChildModal(false)}
        />
      )}
    </div>
  );
}
