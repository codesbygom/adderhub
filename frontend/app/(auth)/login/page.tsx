"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { errorMessages } from "@/lib/format";
import { ApiError, useSession } from "@/lib/session";

// Only same-site paths, so ?next= can't bounce users to another site.
function nextPath(): string {
  const next = new URLSearchParams(window.location.search).get("next") ?? "";
  return next.startsWith("/") && !next.startsWith("//") ? next : "/";
}

export default function LoginPage() {
  const router = useRouter();
  const { login } = useSession();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      router.replace(nextPath());
    } catch (err) {
      setError(err instanceof ApiError && err.status === 401 ? "Your username and password didn't match. Please try again." : errorMessages(err instanceof ApiError ? err.data : null).join(" "));
    }
  };

  return (
    <>
      <form onSubmit={submit}>
        <h2 className="fontt">Login to your Acount</h2>
        {error && <div className="alert alert-danger"><br />{error}</div>}
        <input className="textarea" placeholder="Username*" required value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
        <input className="textarea" type="password" placeholder="Password*" required value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
        <input type="submit" className="btn btn-primary fontt" value="Login" />
      </form>
      <div className="form-footer-link">
        Don&apos;t have an account? <Link href="/signup/">Sign up</Link>
      </div>
    </>
  );
}
