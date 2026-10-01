"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { errorMessages } from "@/lib/format";
import { api, ApiError, useSession } from "@/lib/session";

export default function SignupPage() {
  const router = useRouter();
  const { login } = useSession();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [errors, setErrors] = useState<string[]>([]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api("account/signup/", { method: "POST", body: JSON.stringify(form) });
      await login(form.username, form.password);
      router.replace("/");
    } catch (err) {
      setErrors(err instanceof ApiError ? errorMessages(err.data) : ["Could not reach the server."]);
    }
  };

  return (
    <>
      <form onSubmit={submit}>
        <h2 className="fontt">Create your account</h2>
        {errors.length > 0 && <div className="alert alert-danger"><br />{errors.map((m) => <div key={m}>{m}</div>)}</div>}
        <input className="textarea" placeholder="Username*" required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} autoComplete="username" />
        <input className="textarea" type="email" placeholder="Email*" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} autoComplete="email" />
        <input className="textarea" type="password" placeholder="Password*" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} autoComplete="new-password" />
        <input type="submit" className="btn btn-primary fontt" value="Sign up" />
      </form>
      <div className="form-footer-link">
        Already have an account? <Link href="/login/">Log in</Link>
      </div>
    </>
  );
}
