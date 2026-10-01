"use client";

import { useState } from "react";
import { errorMessages } from "@/lib/format";
import { api, ApiError, useSession } from "@/lib/session";

const PROFILE_FIELDS = [
  { name: "username", label: "Username" },
  { name: "first_name", label: "First name" },
  { name: "last_name", label: "Last name" },
  { name: "email", label: "Email", type: "email" },
  { name: "bio", label: "Bio", area: true },
] as const;

const PASSWORD_FIELDS = [
  { name: "old_password", label: "Old password" },
  { name: "new_password", label: "New password" },
  { name: "confirm_new_password", label: "Confirm new password" },
] as const;

type Notice = { kind: "ok" | "error"; lines: string[] } | null;

// templates/account/settings.html and password.html
export default function SettingsPage() {
  const { me, reloadMe } = useSession();
  const [form, setForm] = useState({
    username: me?.username ?? "",
    first_name: me?.first_name ?? "",
    last_name: me?.last_name ?? "",
    email: me?.email ?? "",
    bio: me?.bio ?? "",
  });
  const [passwords, setPasswords] = useState({ old_password: "", new_password: "", confirm_new_password: "" });
  const [profileNotice, setProfileNotice] = useState<Notice>(null);
  const [passwordNotice, setPasswordNotice] = useState<Notice>(null);

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api("account/update/", { method: "PATCH", body: JSON.stringify(form) });
      await reloadMe();
      setProfileNotice({ kind: "ok", lines: ["Profile updated."] });
    } catch (err) {
      setProfileNotice({ kind: "error", lines: err instanceof ApiError ? errorMessages(err.data) : ["Could not save."] });
    }
  };

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api("account/changepassword/", { method: "PUT", body: JSON.stringify(passwords) });
      setPasswords({ old_password: "", new_password: "", confirm_new_password: "" });
      setPasswordNotice({ kind: "ok", lines: ["Password changed."] });
    } catch (err) {
      setPasswordNotice({ kind: "error", lines: err instanceof ApiError ? errorMessages(err.data) : ["Could not change the password."] });
    }
  };

  const show = (n: Notice) =>
    n && <p style={{ color: n.kind === "ok" ? "var(--color-success)" : "var(--color-danger)" }}>{n.lines.join(" ")}</p>;

  return (
    <div className="settings">
      <div className="edit">
        <form onSubmit={saveProfile}>
          <h2 className="fontt">Edit Profile</h2>
          <br />
          {PROFILE_FIELDS.map((f) => (
            <div key={f.name}>
              <label htmlFor={f.name}>{f.label}</label>
              {"area" in f ? (
                <textarea id={f.name} className="textarea1" rows={3} value={form[f.name]} onChange={(e) => setForm({ ...form, [f.name]: e.target.value })} />
              ) : (
                <input id={f.name} className="textarea1" type={"type" in f ? f.type : "text"} value={form[f.name]} onChange={(e) => setForm({ ...form, [f.name]: e.target.value })} />
              )}
            </div>
          ))}
          {show(profileNotice)}
          <input type="submit" className="btn btn-primary fontt" value="Change" />
        </form>
      </div>

      <div className="edit" style={{ marginTop: "1.5rem" }}>
        <form onSubmit={changePassword}>
          <h2 className="fontt">Change password</h2>
          <br />
          {PASSWORD_FIELDS.map((f) => (
            <div key={f.name}>
              <label htmlFor={f.name}>{f.label}</label>
              <input id={f.name} className="textarea1" type="password" required value={passwords[f.name]} onChange={(e) => setPasswords({ ...passwords, [f.name]: e.target.value })} />
            </div>
          ))}
          {show(passwordNotice)}
          <input type="submit" className="btn btn-primary fontt" value="Change password" />
        </form>
      </div>
    </div>
  );
}
