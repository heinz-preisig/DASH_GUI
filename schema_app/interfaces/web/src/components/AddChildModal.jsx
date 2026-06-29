import React, { useState } from 'react';
import { api } from '../api';

/**
 * AddChildModal - Modal for adding an existing component as a child of another component
 */
export function AddChildModal({ sessionId, schemaId, parentId, components, onAdded, onClose, onToast }) {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [pathIri, setPathIri] = useState("org:has");
  const [label, setLabel] = useState("");

  // Filter candidates: not already a child of parent, not the parent itself
  const candidates = components.filter(c =>
    c.brick_id !== parentId &&
    (!c.parent_id || c.parent_id !== parentId)
  );

  const filtered = candidates.filter(c =>
    c.name?.toLowerCase().includes(search.toLowerCase()) ||
    c.brick_id.toLowerCase().includes(search.toLowerCase())
  );

  const submit = async () => {
    if (!selected) return;

    try {
      const r = await api('POST', `/session/${sessionId}/schemas/${schemaId}/components/${encodeURIComponent(selected)}/parent`, {
        parent_brick_id: parentId,
        path_iri: pathIri,
        label: label || selected
      });

      if (r.status === "success") {
        onToast && onToast("Child added", "success");
        onAdded(selected, pathIri, label);
      } else {
        onToast && onToast(r.message || "Failed to add child", "error");
      }
    } catch (error) {
      onToast && onToast(`Error: ${error.message}`, "error");
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>Add Child Component</h3>
        <p style={{ color: "#666", fontSize: 12, marginBottom: 10 }}>
          Add an existing component as a child of the selected parent.
        </p>

        <input
          type="text"
          placeholder="Search components..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: "100%", marginBottom: 10, padding: 8 }}
        />

        <div style={{ maxHeight: 200, overflow: "auto", border: "1px solid #eee", marginBottom: 10 }}>
          {filtered.map((c) => (
            <div
              key={c.brick_id}
              onClick={() => { setSelected(c.brick_id); setLabel(c.name); }}
              style={{
                padding: "8px",
                cursor: "pointer",
                background: selected === c.brick_id ? "#e6f2ff" : "white",
                borderBottom: "1px solid #f0f0f0"
              }}
            >
              <strong>{c.name}</strong>
              <div style={{ fontSize: 11, color: "#888" }}>{c.brick_id}</div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div style={{ padding: 10, color: "#888" }}>No available components</div>
          )}
        </div>

        <div style={{ marginBottom: 10 }}>
          <label style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Property Path IRI:</label>
          <input
            type="text"
            value={pathIri}
            onChange={(e) => setPathIri(e.target.value)}
            style={{ width: "100%", padding: 6 }}
            placeholder="e.g., org:hasContact"
          />
        </div>

        <div style={{ marginBottom: 15 }}>
          <label style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Display Label:</label>
          <input
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            style={{ width: "100%", padding: 6 }}
            placeholder="e.g., Company Contact"
          />
        </div>

        <div className="modal-actions">
          <button onClick={onClose} className="btn secondary">Cancel</button>
          <button onClick={submit} className="btn primary" disabled={!selected}>Add Child</button>
        </div>
      </div>
    </div>
  );
}
