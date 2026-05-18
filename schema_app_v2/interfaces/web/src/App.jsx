import React, { useState, useEffect, useCallback } from 'react';
import { SchemaEditor, NewSchemaModal, Toast } from './components';
import { api } from './api';

// Main App component
export function App() {
  const [sessionId, setSessionId] = useState(null);
  const [schemaLibraries, setSchemaLibraries] = useState([]);
  const [brickLibraries, setBrickLibraries] = useState([]);
  const [activeSchemaLib, setActiveSchemaLib] = useState("");
  const [activeBrickLib, setActiveBrickLib] = useState("");
  const [schemas, setSchemas] = useState([]);
  const [selectedSchemaId, setSelectedSchemaId] = useState(null);
  const [schemaData, setSchemaData] = useState(null);
  const [status, setStatus] = useState("Initialising…");
  const [toast, setToast] = useState(null);
  const [showNewSchema, setShowNewSchema] = useState(false);

  const showToast = (msg, type = "success") => setToast({ msg, type });

  // Init session
  useEffect(() => {
    api("POST", "/session", { client_type: "web" }).then(r => {
      if (r.status === "success") {
        setSessionId(r.data.session_id);
        setStatus("Ready");
      } else {
        setStatus("Error creating session");
      }
    }).catch(() => setStatus("Cannot connect to server"));
  }, []);

  // Push libraries to session, then reload schema list
  const pushLibrariesAndReload = useCallback(async (sid, sLib, bLib) => {
    if (!sid) return;
    await api("PUT", `/session/${sid}/libraries`, {
      schema_library: sLib || null,
      brick_library: bLib || null,
    });
    const r = await api("GET", `/session/${sid}/schemas`);
    if (r.status === "success") setSchemas(r.data || []);
  }, []);

  // Load libraries on session ready
  useEffect(() => {
    if (!sessionId) return;
    (async () => {
      const r = await api("GET", `/libraries?session_id=${sessionId}`);
      if (r.status === "success") {
        const schemaLibs = r.data.schema_libraries || [];
        const brickLibs = r.data.brick_libraries || [];
        setSchemaLibraries(schemaLibs);
        setBrickLibraries(brickLibs);
        const sLib = schemaLibs[0] || null;
        const bLib = brickLibs[0] || null;
        if (sLib) setActiveSchemaLib(sLib);
        if (bLib) setActiveBrickLib(bLib);
        await pushLibrariesAndReload(sessionId, sLib, bLib);
      }
    })();
  }, [sessionId, pushLibrariesAndReload]);

  // Reload schemas when user changes library dropdowns
  const loadSchemas = useCallback(async () => {
    if (!sessionId || (!activeSchemaLib && !activeBrickLib)) return;
    await pushLibrariesAndReload(sessionId, activeSchemaLib, activeBrickLib);
    setSchemaData(null);
    setSelectedSchemaId(null);
  }, [sessionId, activeSchemaLib, activeBrickLib, pushLibrariesAndReload]);

  const prevLibRef = React.useRef(null);
  useEffect(() => {
    const key = `${activeSchemaLib}|${activeBrickLib}`;
    if (prevLibRef.current === null) { prevLibRef.current = key; return; }
    if (prevLibRef.current !== key) { prevLibRef.current = key; loadSchemas(); }
  }, [activeSchemaLib, activeBrickLib, loadSchemas]);

  // Select schema
  const selectSchema = async (id) => {
    setSelectedSchemaId(id);
    const r = await api("GET", `/session/${sessionId}/schemas/${encodeURIComponent(id)}`);
    if (r.status === "success") {
      setSchemaData(r.data);
      setStatus(`Loaded: ${r.data?.name || id}`);
    } else showToast("Failed to load schema", "error");
  };

  const handleSaved = (updated) => {
    setSchemaData(updated);
    setSchemas(prev => prev.map(s => s.schema_id === updated.schema_id ? { ...s, ...updated } : s));
  };

  const handleDeleted = (id) => {
    setSchemas(prev => prev.filter(s => s.schema_id !== id));
    setSelectedSchemaId(null);
    setSchemaData(null);
    setStatus("Schema deleted");
  };

  const handleCreated = async (schema) => {
    setShowNewSchema(false);
    await loadSchemas();
    selectSchema(schema.schema_id);
    showToast("Schema created", "success");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* Header */}
      <header style={{
        background: "#1e40af",
        color: "white",
        padding: "12px 20px",
        display: "flex",
        alignItems: "center",
        gap: 20
      }}>
        <h1 style={{ margin: 0, fontSize: 20 }}>Schema App v2</h1>
        <div style={{ fontSize: 12, opacity: 0.8 }}>{status}</div>
      </header>

      {/* Main content */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Sidebar */}
        <aside style={{
          width: 280,
          background: "white",
          borderRight: "1px solid #e5e7eb",
          padding: 16,
          overflow: "auto"
        }}>
          {/* Library selectors */}
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 4 }}>
              Schema Library
            </label>
            <select
              value={activeSchemaLib}
              onChange={(e) => setActiveSchemaLib(e.target.value)}
              style={{ width: "100%", padding: 6 }}
            >
              {schemaLibraries.map(lib => (
                <option key={lib} value={lib}>{lib}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, marginBottom: 4 }}>
              Brick Library
            </label>
            <select
              value={activeBrickLib}
              onChange={(e) => setActiveBrickLib(e.target.value)}
              style={{ width: "100%", padding: 6 }}
            >
              {brickLibraries.map(lib => (
                <option key={lib} value={lib}>{lib}</option>
              ))}
            </select>
          </div>

          {/* Schema list */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <label style={{ fontSize: 12, fontWeight: 600 }}>Schemas</label>
              <button
                onClick={() => setShowNewSchema(true)}
                style={{
                  padding: "4px 12px",
                  fontSize: 12,
                  background: "#3b82f6",
                  color: "white",
                  border: "none",
                  borderRadius: 4,
                  cursor: "pointer"
                }}
              >
                New
              </button>
            </div>
            <div style={{ border: "1px solid #e5e7eb", borderRadius: 4, maxHeight: 200, overflow: "auto" }}>
              {schemas.map(s => (
                <div
                  key={s.schema_id}
                  onClick={() => selectSchema(s.schema_id)}
                  style={{
                    padding: "8px 12px",
                    cursor: "pointer",
                    background: selectedSchemaId === s.schema_id ? "#dbeafe" : "white",
                    borderBottom: "1px solid #f3f4f6"
                  }}
                >
                  {s.name}
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Main panel */}
        <main style={{ flex: 1, padding: 20, overflow: "auto" }}>
          {schemaData ? (
            <SchemaEditor
              sessionId={sessionId}
              schemaData={schemaData}
              allSchemas={schemas}
              brickLibraries={brickLibraries}
              brickLib={activeBrickLib}
              onSaved={handleSaved}
              onToast={showToast}
              onDeleted={handleDeleted}
            />
          ) : (
            <div className="empty-hint">Select a schema to view details</div>
          )}
        </main>
      </div>

      {/* Toast */}
      {toast && <Toast msg={toast.msg} type={toast.type} onDone={() => setToast(null)} />}

      {/* New Schema Modal */}
      {showNewSchema && (
        <NewSchemaModal
          sessionId={sessionId}
          brickLibraries={brickLibraries}
          brickLib={activeBrickLib}
          onCreated={handleCreated}
          onClose={() => setShowNewSchema(false)}
        />
      )}
    </div>
  );
}
