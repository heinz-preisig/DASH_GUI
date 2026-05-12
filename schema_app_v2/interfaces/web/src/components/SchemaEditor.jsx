import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { TreeView } from './TreeView';
import { AddComponentModal } from './AddComponentModal';
import { AddRefModal } from './AddRefModal';

/**
 * SchemaEditor - Main component for editing a schema
 * Handles components, refs, groups, tree view, and validation
 */
export function SchemaEditor({ sessionId, schemaData, allSchemas, brickLib, onSaved, onToast, onDeleted }) {
  const [form, setForm] = useState({ name: "", description: "" });
  const [dirty, setDirty] = useState(false);
  const [components, setComponents] = useState([]);
  const [refs, setRefs] = useState([]);
  const [tree, setTree] = useState({ tree: {}, roots: [] });
  const [groups, setGroups] = useState([]);
  const [validation, setValidation] = useState(null);
  const [tab, setTab] = useState("details");
  const [showAddComp, setShowAddComp] = useState(false);
  const [showAddRef, setShowAddRef] = useState(false);
  const [rootBrickName, setRootBrickName] = useState("");

  useEffect(() => {
    if (!schemaData) return;
    setForm({ name: schemaData.name || "", description: schemaData.description || "" });
    setDirty(false);
    setValidation(null);
    loadComponents();
    loadRefs();
    loadTree();
    loadGroups();
    loadRootBrickName();
  }, [schemaData?.schema_id]);

  const loadRootBrickName = async () => {
    if (!schemaData?.root_brick_id) return;
    console.log("Loading root brick:", schemaData.root_brick_id);
    const r = await api("GET", `/session/${sessionId}/bricks/${encodeURIComponent(schemaData.root_brick_id)}`);
    console.log("Root brick API response:", r);
    if (r.status === "success" && r.data) {
      console.log("Setting root brick name to:", r.data.name);
      setRootBrickName(r.data.name || schemaData.root_brick_id);
    } else {
      console.log("API failed, using ID as name");
      setRootBrickName(schemaData.root_brick_id);
    }
  };

  const loadComponents = async () => {
    if (!schemaData) return;
    const compIds = schemaData.component_brick_ids || [];
    const details = await Promise.all(
      compIds.map(id =>
        api("GET", `/session/${sessionId}/bricks/${encodeURIComponent(id)}`)
          .then(r => {
            if (r.status === "success") {
              console.log("Brick data for", id, ":", r.data);
              return r.data;
            }
            return { brick_id: id, name: id };
          })
      )
    );
    setComponents(details);
  };

  const loadRefs = async () => {
    if (!schemaData) return;
    const r = await api("GET", `/session/${sessionId}/schemas/${schemaData.schema_id}/refs`);
    if (r.status === "success") setRefs(r.data || []);
  };

  const loadTree = async () => {
    if (!schemaData) return;
    const r = await api("GET", `/session/${sessionId}/schemas/${schemaData.schema_id}/tree`);
    if (r.status === "success") setTree(r.data || { tree: {}, roots: [] });
  };

  const loadGroups = async () => {
    if (!schemaData) return;
    const r = await api("GET", `/session/${sessionId}/schemas/${schemaData.schema_id}/groups`);
    if (r.status === "success") setGroups(r.data || []);
  };

  const set = (k, v) => { setForm(f => ({ ...f, [k]: v })); setDirty(true); };

  const save = async () => {
    const r = await api("PUT", `/session/${sessionId}/schemas/${schemaData.schema_id}`,
      { name: form.name, description: form.description });
    if (r.status === "success") {
      onToast("Schema saved", "success");
      setDirty(false);
      onSaved(r.data);
    } else onToast(r.message || "Save failed", "error");
  };

  const validate = async () => {
    const r = await api("POST", `/session/${sessionId}/schemas/${schemaData.schema_id}/validate`);
    if (r.status === "success") setValidation(r.data);
  };

  const removeComp = async (brickId) => {
    const r = await api("DELETE", `/session/${sessionId}/schemas/${schemaData.schema_id}/components/${encodeURIComponent(brickId)}`);
    if (r.status === "success") {
      onToast("Component removed", "success");
      loadComponents();
      loadTree();
      onSaved({ ...schemaData, component_brick_ids: (schemaData.component_brick_ids || []).filter(id => id !== brickId) });
    } else onToast(r.message || "Failed", "error");
  };

  const removeRef = async (ref) => {
    const q = ref.attach_to_brick_id ? `?attach_to_brick_id=${encodeURIComponent(ref.attach_to_brick_id)}` : "";
    const r = await api("DELETE", `/session/${sessionId}/schemas/${schemaData.schema_id}/refs/${encodeURIComponent(ref.schema_id)}${q}`);
    if (r.status === "success") { onToast("Reference removed", "success"); loadRefs(); loadTree(); }
    else onToast(r.message || "Failed", "error");
  };

  const createGroup = async (groupId, label, description, sequence) => {
    const r = await api("POST", `/session/${sessionId}/schemas/${schemaData.schema_id}/groups`, {
      group_id: groupId,
      label: label || groupId,
      description: description || "",
      sequence: sequence || 0
    });
    if (r.status === "success") {
      onToast(`Group '${groupId}' created`, "success");
      loadGroups();
      return true;
    } else {
      onToast(r.message || "Failed to create group", "error");
      return false;
    }
  };

  const assignToGroup = async (brickId, groupId) => {
    const r = await api("PUT", `/session/${sessionId}/schemas/${schemaData.schema_id}/components/${encodeURIComponent(brickId)}/group`, {
      group_id: groupId
    });
    if (r.status === "success") {
      onToast("Component assigned to group", "success");
      loadGroups();
      loadComponents();
      loadTree();
    } else onToast(r.message || "Failed", "error");
  };

  const removeFromGroup = async (brickId) => {
    const r = await api("DELETE", `/session/${sessionId}/schemas/${schemaData.schema_id}/components/${encodeURIComponent(brickId)}/group`);
    if (r.status === "success") {
      onToast("Component removed from group", "success");
      loadGroups();
      loadComponents();
      loadTree();
    } else onToast(r.message || "Failed", "error");
  };

  const exportShacl = () => {
    window.open(`/api/session/${sessionId}/schemas/${schemaData.schema_id}/export/shacl`, '_blank');
  };

  const doDelete = async () => {
    if (!window.confirm(`Delete schema "${schemaData.name}"?`)) return;
    const r = await api("DELETE", `/session/${sessionId}/schemas/${schemaData.schema_id}`);
    if (r.status === "success") { onToast("Schema deleted", "success"); onDeleted(schemaData.schema_id); }
    else onToast(r.message || "Failed", "error");
  };

  if (!schemaData) return (
    <div className="card"><div className="empty-hint">Select a schema from the list, or create a new one.</div></div>
  );

  return (
    <>
      <div className="card">
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:10 }}>
          <h2 style={{ margin:0, borderBottom:"none", paddingBottom:0 }}>Schema Details</h2>
          <div style={{ display:"flex", gap:6 }}>
            <button className="btn btn-success btn-sm" onClick={exportShacl} title="Download SHACL Turtle">Export SHACL</button>
            <button className="btn btn-secondary btn-sm" onClick={validate}>Validate</button>
            <button className="btn btn-danger btn-sm" onClick={doDelete}>Delete</button>
          </div>
        </div>
        <hr className="divider"/>
        <div className="form-row">
          <label>Name</label>
          <div className="field"><input type="text" value={form.name} onChange={e => set("name", e.target.value)}/></div>
        </div>
        <div className="form-row">
          <label>Description</label>
          <div className="field"><textarea value={form.description} onChange={e => set("description", e.target.value)}/></div>
        </div>
        <div className="form-row">
          <label>Root Brick</label>
          <div className="field" style={{ paddingTop:7, fontSize:13, color:"#555" }}>
            {rootBrickName || schemaData.root_brick_id || <span style={{ color:"#aaa" }}>— not set —</span>}
          </div>
        </div>
        <div style={{ display:"flex", justifyContent:"flex-end", gap:8, marginTop:8 }}>
          <button className="btn btn-primary" disabled={!dirty} onClick={save}>Save</button>
        </div>
        {validation && (
          <div style={{ marginTop:10 }}>
            {validation.valid
              ? <div className="valid-badge">✓ Schema is valid</div>
              : <>
                  <div className="invalid-badge">✗ Validation issues:</div>
                  <div className="issue-list">
                    {validation.issues.map((iss, i) => <div key={i} className="issue-item">• {iss}</div>)}
                  </div>
                </>
            }
          </div>
        )}
      </div>

      <div className="tabs">
        <div className={`tab ${tab === "components" ? "active" : ""}`} onClick={() => setTab("components")}>
          Components ({components.length})
        </div>
        <div className={`tab ${tab === "refs" ? "active" : ""}`} onClick={() => setTab("refs")}>
          Schema Refs ({refs.length})
        </div>
        <div className={`tab ${tab === "groups" ? "active" : ""}`} onClick={() => setTab("groups")}>
          Groups ({groups.length})
        </div>
        <div className={`tab ${tab === "tree" ? "active" : ""}`} onClick={() => setTab("tree")}>
          Tree View
        </div>
      </div>

      {tab === "components" && (
        <div className="card">
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:10 }}>
            <h2 style={{ margin:0, borderBottom:"none", paddingBottom:0 }}>Components</h2>
            <button className="btn btn-primary btn-sm" onClick={() => setShowAddComp(true)}>+ Add Brick</button>
          </div>
          {components.length === 0
            ? <div className="empty-hint">No components — add bricks above</div>
            : components.map(c => (
              <div key={c.brick_id} style={{ display:"flex", alignItems:"center", gap:8, padding:"6px 0", borderBottom:"1px solid #f0f0f0" }}>
                <div style={{ flex:1 }}>
                  <div className="comp-name">{c.name || c.brick_id}</div>
                  <div className="comp-meta">
                    <span className={`brick-type-badge ${c.object_type === "NodeShape" ? "badge-node" : "badge-prop"}`}>{c.object_type || "?"}</span>
                    {c.target_class && <span style={{ marginLeft:6 }}>{c.target_class}</span>}
                    {c.property_path && <span style={{ marginLeft:6 }}>{c.property_path}</span>}
                  </div>
                </div>
                <button className="btn btn-danger btn-sm" onClick={() => removeComp(c.brick_id)}>✕</button>
              </div>
            ))
          }
        </div>
      )}

      {tab === "refs" && (
        <div className="card">
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:10 }}>
            <h2 style={{ margin:0, borderBottom:"none", paddingBottom:0 }}>Schema References</h2>
            <button className="btn btn-primary btn-sm" disabled={components.length === 0} onClick={() => setShowAddRef(true)}>+ Add Ref</button>
          </div>
          {refs.length === 0
            ? <div className="empty-hint">No schema references — embed another schema via sh:node</div>
            : refs.map((ref, i) => (
              <div key={i} style={{ display:"flex", alignItems:"flex-start", gap:8, padding:"8px 0", borderBottom:"1px solid #f0f0f0" }}>
                <div style={{ flex:1 }}>
                  <div className="ref-name">⬡ {ref.label || ref.schema_id}</div>
                  <div className="ref-meta">
                    <span>schema: {ref.schema_id}</span>
                    {ref.attach_to_brick_id && <span> · attach: {ref.attach_to_brick_id}</span>}
                    {ref.property_path && <span> · path: {ref.property_path}</span>}
                  </div>
                </div>
                <button className="btn btn-danger btn-sm" onClick={() => removeRef(ref)}>✕</button>
              </div>
            ))
          }
        </div>
      )}

      {tab === "groups" && (
        <div className="card">
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:10 }}>
            <h2 style={{ margin:0, borderBottom:"none", paddingBottom:0 }}>Groups</h2>
            <button className="btn btn-primary btn-sm" onClick={() => {
              const id = prompt("Group ID (e.g., 'products'):");
              if (id) {
                const label = prompt("Group label (optional):", id);
                const desc = prompt("Description (optional):", "");
                createGroup(id, label, desc, groups.length);
              }
            }}>+ New Group</button>
          </div>

          {groups.length === 0
            ? <div className="empty-hint">No groups — create groups to organize components visually</div>
            : groups.map(g => (
              <div key={g.id} style={{ border:"1px solid #e0e0e0", borderRadius:4, marginBottom:10, padding:10 }}>
                <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                  <div>
                    <strong>{g.label || g.id}</strong>
                    <span style={{ color:"#888", marginLeft:8, fontSize:12 }}>({g.id})</span>
                  </div>
                  <button className="btn btn-danger btn-sm" onClick={() => {
                    if (confirm(`Delete group '${g.id}'? Components will be ungrouped.`)) {
                      api("DELETE", `/session/${sessionId}/schemas/${schemaData.schema_id}/groups/${g.id}`)
                        .then(r => { if (r.status === "success") { onToast("Group deleted", "success"); loadGroups(); loadComponents(); }});
                    }
                  }}>✕</button>
                </div>
                {g.description && <div style={{ color:"#666", fontSize:12, marginTop:4 }}>{g.description}</div>}

                {/* Members of this group */}
                <div style={{ marginTop:8, paddingLeft:8, borderLeft:"2px solid #ddd" }}>
                  <div style={{ fontSize:11, color:"#888", marginBottom:4 }}>Members:</div>
                  {(() => {
                    const members = components.filter(c =>
                      (c.group_id === g.id || c.ui_metadata?.group_id === g.id) &&
                      !Object.values(tree.tree || {}).flat().includes(c.brick_id)
                    );
                    return members.length === 0
                      ? <div style={{ fontSize:12, color:"#aaa", fontStyle:"italic" }}>No components assigned</div>
                      : members.map(m => (
                        <div key={m.brick_id} style={{ display:"flex", alignItems:"center", gap:8, padding:"2px 0", fontSize:12 }}>
                          <span>{m.name || m.brick_id}</span>
                          <span className={`brick-type-badge ${m.object_type === "NodeShape" ? "badge-node" : "badge-prop"}`} style={{ fontSize:10 }}>
                            {m.object_type === "NodeShape" ? "N" : "P"}
                          </span>
                          <button className="btn btn-secondary btn-sm" style={{ fontSize:10, padding:"2px 6px" }}
                            onClick={() => removeFromGroup(m.brick_id)}>Remove</button>
                        </div>
                      ));
                  })()}
                </div>
              </div>
            ))
          }

          {/* Ungrouped components - quick assign */}
          {components.length > 0 && groups.length > 0 && (
            <div style={{ marginTop:20, borderTop:"1px solid #eee", paddingTop:15 }}>
              <h3 style={{ margin:"0 0 10px 0", fontSize:14 }}>Ungrouped Components</h3>
              <div style={{ fontSize:12, color:"#666", marginBottom:8 }}>Click a group to assign:</div>
              {(() => {
                const groupedIds = new Set(components.filter(c => c.group_id || c.ui_metadata?.group_id).map(c => c.brick_id));
                const ungrouped = components.filter(c => !groupedIds.has(c.brick_id) && !Object.values(tree.tree || {}).flat().includes(c.brick_id));
                return ungrouped.length === 0
                  ? <div style={{ fontSize:12, color:"#aaa", fontStyle:"italic" }}>All components are grouped</div>
                  : ungrouped.map(c => (
                    <div key={c.brick_id} style={{ display:"flex", alignItems:"center", gap:8, padding:"4px 0", borderBottom:"1px solid #f5f5f5" }}>
                      <span style={{ flex:1 }}>{c.name || c.brick_id}</span>
                      <select style={{ fontSize:12, padding:"2px 4px" }} onChange={e => { if (e.target.value) { assignToGroup(c.brick_id, e.target.value); e.target.value = ""; }}}>
                        <option value="">Assign to group...</option>
                        {groups.map(g => <option key={g.id} value={g.id}>{g.label || g.id}</option>)}
                      </select>
                    </div>
                  ));
              })()}
            </div>
          )}
        </div>
      )}

      {tab === "tree" && (
        <div className="card">
          <h2>UI Tree Structure</h2>
          <TreeView
            tree={tree}
            rootBrickId={schemaData.root_brick_id}
            components={components}
            refs={refs}
            groups={groups}
            sessionId={sessionId}
            schemaId={schemaData.schema_id}
            onToast={onToast}
            onAddChild={(parentId, childId, pathIri, label) => {
              loadComponents();
              loadTree();
              onToast(`Added ${label || childId} as child of parent`, "success");
            }}
          />
        </div>
      )}

      {showAddComp && (
        <AddComponentModal
          sessionId={sessionId}
          schemaId={schemaData.schema_id}
          existingIds={schemaData.component_brick_ids || []}
          brickLib={brickLib}
          onAdded={id => {
            setShowAddComp(false);
            onToast("Component added", "success");
            const updated = { ...schemaData, component_brick_ids: [...(schemaData.component_brick_ids || []), id] };
            onSaved(updated);
            loadComponents();
            loadTree();
          }}
          onClose={() => setShowAddComp(false)}
        />
      )}

      {showAddRef && (
        <AddRefModal
          sessionId={sessionId}
          schemaId={schemaData.schema_id}
          components={components}
          allSchemas={allSchemas}
          onAdded={ref => {
            setShowAddRef(false);
            onToast("Schema reference added", "success");
            loadRefs();
            loadTree();
          }}
          onClose={() => setShowAddRef(false)}
        />
      )}
    </>
  );
}
