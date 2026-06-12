import React, { useEffect } from 'react';

/**
 * Toast - Auto-dismissing notification component
 */
export function Toast({ msg, type, onDone }) {
  useEffect(() => {
    const t = setTimeout(onDone, 3200);
    return () => clearTimeout(t);
  }, [onDone]);

  return <div className={`toast ${type}`}>{msg}</div>;
}
