"use client";

import { useEffect, useState } from "react";
import { errorMessages } from "@/lib/format";
import { api, ApiError } from "@/lib/session";

// templates/core/partials/post_upload_overlay.html (without the cropper).
export default function UploadOverlay({ onClose, onDone }: { onClose: () => void; onDone: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [caption, setCaption] = useState("");
  const [drag, setDrag] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const save = async () => {
    if (!file) return;
    setBusy(true);
    setError("");
    const body = new FormData();
    body.append("image", file);
    body.append("caption", caption);
    try {
      await api("core/posts/", { method: "POST", body });
      onDone();
    } catch (e) {
      setError(e instanceof ApiError ? errorMessages(e.data).join(" ") : "Upload failed.");
      setBusy(false);
    }
  };

  return (
    <div className="upload-overlay" dir="ltr" lang="en">
      <div
        className={`upload-box${drag ? " dragover" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          setFile(e.dataTransfer.files[0] ?? null);
        }}
      >
        {!preview && (
          <>
            <i className="bi bi-cloud-arrow-up" />
            <p>Drag and drop your photo here, or</p>
            <label htmlFor="file-post" className="btn btn-primary">Browse</label>
          </>
        )}
        <input type="file" id="file-post" accept="image/*" hidden onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        {preview && <img className="preview" src={preview} alt="" style={{ display: "block", maxHeight: 320, objectFit: "contain" }} />}
        <textarea className="textarea2" placeholder="Caption" rows={3} value={caption} onChange={(e) => setCaption(e.target.value)} />
        {error && <p style={{ color: "var(--color-danger)" }}>{error}</p>}
      </div>
      <div className="upload-actions">
        <button type="button" className="btn" onClick={onClose}>Cancel</button>
        <button type="button" className="btn btn-primary" onClick={save} disabled={!file || busy}>
          {busy ? "Saving…" : "Save"}
        </button>
      </div>
    </div>
  );
}
