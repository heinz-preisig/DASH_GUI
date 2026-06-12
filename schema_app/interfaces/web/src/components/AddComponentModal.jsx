import React, { useState, useEffect } from 'react';
import { api } from '../api';

/**
 * AddComponentModal - Modal for adding a brick component to a schema
 */
export function AddComponentModal({ sessionId, schemaId, existingIds, brickLibraries, brickLib, onAdded, onClose }) {
  const [bricks, setBricks] = useState([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [selectedLibrary, setSelectedLibrary] = useState(brickLib || "default");

  useEffect(() => {
    if (!sessionId) return;
    const lib = selectedLibrary || "default";
    const q = lib ? `?library=${encodeURIComponent(lib)}` : "";
    api("GET", `/session/${sessionId}/bricks${q}`).then(r => {
      if (r.status === "success") setBricks(r.data || []);
    });
  }, [sessionId, selectedLibrary]);

  const filtered = bricks.filter(b => {
    const s = search.toLowerCase();
    return !s || (b.name || "").toLowerCase().includes(s) || (b.brick_id || "").toLowerCase().includes(s);
  }).filter(b => !existingIds.includes(b.brick_id));

  const add = async () => {
    if (!selected) return;
    const r = await api("POST", `/session/${sessionId}/schemas/${schemaId}/components`, { brick_id: selected });
    if (r.status === "success") onAdded(selected);
    else alert(r.message || "Failed");
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>Add Component Brick</h2>
        <div className="form-row">
          <label>Library</label>
          <div className="field">
            <select value={selectedLibrary} onChange={e => setSelectedLibrary(e.target.value)} style={{ width: "100%", padding: 6 }}>
              {brickLibraries && brickLibraries.map(lib => (
                <option key={lib} value={lib}>{lib}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="form-row">
          <label>Search</label>
          <div className="field"><input type="text" placeholder="Filter bricks…" value={search} onChange={e => setSearch(e.target.value)} autoFocus/></div>
        </div>
        <div className="brick-browser">
          {filtered.length === 0
            ? <div className="empty-hint">No bricks available</div>
            : filtered.map(b => (
              <div key={b.brick_id} className={`brick-pick ${selected === b.brick_id ? "selected" : ""}`}
                   onClick={() => setSelected(b.brick_id)}>
                {b.name || b.brick_id}
                <span className={`brick-type-badge ${b.object_type === "NodeShape" ? "badge-node" : "badge-prop"}`}>
                  {b.object_type === "NodeShape" ? "N" : "P"}
                </span>
                {b.description && <div style={{ fontSize:11, color:"#7a8899" }}>{b.description}</div>}
              </div>
            ))
          }
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" disabled={!selected} onClick={add}>Add</button>
        </div>
      </div>
    </div>
  );
}
