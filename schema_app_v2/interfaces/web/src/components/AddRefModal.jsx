import React, { useState } from 'react';
import { api } from '../api';

/**
 * AddRefModal - Modal for adding a schema reference (sh:node)
 */
export function AddRefModal({ sessionId, schemaId, components, allSchemas, onAdded, onClose }) {
  const [refSchemaId, setRefSchemaId] = useState("");
  const [attachTo, setAttachTo] = useState("");
  const [propPath, setPropPath] = useState("");
  const [label, setLabel] = useState("");

  const submit = async () => {
    if (!refSchemaId || !attachTo || !propPath) return;
    const r = await api("POST", `/session/${sessionId}/schemas/${schemaId}/refs`, {
      schema_id: refSchemaId, attach_to_brick_id: attachTo, property_path: propPath, label
    });
    if (r.status === "success") onAdded(r.data);
    else alert(r.message || "Failed");
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>Add Schema Reference (sh:node)</h2>
        <div className="form-row">
          <label>Referenced Schema *</label>
          <div className="field">
            <select value={refSchemaId} onChange={e => setRefSchemaId(e.target.value)}>
              <option value="">Select schema…</option>
              {allSchemas.filter(s => s.schema_id !== schemaId).map(s => (
                <option key={s.schema_id} value={s.schema_id}>{s.name || s.schema_id}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="form-row">
          <label>Attach to Brick *</label>
          <div className="field">
            <select value={attachTo} onChange={e => setAttachTo(e.target.value)}>
              <option value="">Select component brick…</option>
              {components.map(c => (
                <option key={c.brick_id} value={c.brick_id}>{c.name || c.brick_id}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="form-row">
          <label>Property Path *</label>
          <div className="field"><input type="text" placeholder="e.g. ex:hasAddress" value={propPath} onChange={e => setPropPath(e.target.value)}/></div>
        </div>
        <div className="form-row">
          <label>Label</label>
          <div className="field"><input type="text" placeholder="optional display label" value={label} onChange={e => setLabel(e.target.value)}/></div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" disabled={!refSchemaId || !attachTo || !propPath} onClick={submit}>Add Reference</button>
        </div>
      </div>
    </div>
  );
}
