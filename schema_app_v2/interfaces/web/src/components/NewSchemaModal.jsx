import React, { useState, useEffect } from 'react';
import { api } from '../api';

/**
 * NewSchemaModal - Modal for creating a new schema
 */
export function NewSchemaModal({ sessionId, brickLib, onCreated, onClose }) {
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [rootBrick, setRootBrick] = useState("");
  const [nodeShapes, setNodeShapes] = useState([]);
  const [lib, setLib] = useState(brickLib || "");

  useEffect(() => {
    if (!sessionId) return;
    const q = lib ? `?library=${encodeURIComponent(lib)}` : "";
    api("GET", `/session/${sessionId}/bricks/node-shapes${q}`).then(r => {
      if (r.status === "success") setNodeShapes(r.data || []);
    });
  }, [sessionId, lib]);

  const submit = async () => {
    if (!name.trim() || !rootBrick) return;
    const r = await api("POST", `/session/${sessionId}/schemas`, {
      name: name.trim(), description: desc, root_brick_id: rootBrick
    });
    if (r.status === "success") onCreated(r.data);
    else alert(r.message || "Failed to create schema");
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>New Schema</h2>
        <div className="form-row">
          <label>Name *</label>
          <div className="field"><input type="text" value={name} onChange={e => setName(e.target.value)} autoFocus/></div>
        </div>
        <div className="form-row">
          <label>Description</label>
          <div className="field"><textarea value={desc} onChange={e => setDesc(e.target.value)}/></div>
        </div>
        <div className="form-row">
          <label>Root Brick *</label>
          <div className="field">
            <select value={rootBrick} onChange={e => setRootBrick(e.target.value)}>
              <option value="">Select a NodeShape brick…</option>
              {nodeShapes.map(b => <option key={b.brick_id} value={b.brick_id}>{b.name || b.brick_id}</option>)}
            </select>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" disabled={!name.trim() || !rootBrick} onClick={submit}>Create Schema</button>
        </div>
      </div>
    </div>
  );
}
