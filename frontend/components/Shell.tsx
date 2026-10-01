"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { displayName, mediaUrl } from "@/lib/format";
import { api, useSession } from "@/lib/session";
import type { Paginated, Profile } from "@/lib/types";
import UploadOverlay from "./UploadOverlay";

// templates/base.html: navbar, left profile + menu, right suggestions.
export default function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { ready, me, logout } = useSession();
  const [suggestions, setSuggestions] = useState<Profile[]>([]);
  const [uploadOpen, setUploadOpen] = useState(false);

  useEffect(() => {
    if (ready && !me) router.replace(`/login/?next=${encodeURIComponent(pathname)}`);
  }, [ready, me, pathname, router]);

  useEffect(() => {
    if (!me) return;
    api<Profile[] | Paginated<Profile>>("account/suggestions/")
      .then((data) => setSuggestions((Array.isArray(data) ? data : data.results).slice(0, 5)))
      .catch(() => setSuggestions([]));
  }, [me, pathname]);

  const onSearch = useCallback(
    (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      const q = new FormData(e.currentTarget).get("search")?.toString().trim();
      if (q) router.push(`/search/?search=${encodeURIComponent(q)}`);
    },
    [router],
  );

  if (!me) {
    return (
      <div className="wrapper" style={{ margin: "4rem auto", maxWidth: 300, textAlign: "center" }}>
        <i className="bi bi-hourglass-split" />
      </div>
    );
  }

  const profilePath = `/profile/${me.username}/`;
  const active = (path: string) => (pathname === path ? " active" : "");

  return (
    <>
      <nav>
        <div className="container">
          <h2 className="logo">
            <Link href="/"><img src="/images/logo.png" alt="AdderHub" className="logo-img" /></Link>
          </h2>
          <div className="search-bar">
            <form id="search-form" onSubmit={onSearch}>
              <button type="submit" id="submit"><i className="bi bi-search" /></button>
              <input id="search" name="search" type="search" required placeholder="Search for users" />
            </form>
          </div>
        </div>
      </nav>

      <main>
        <div className="container container1">
          <div className="left">
            <Link href={profilePath} className="profile">
              <div className="profile-photo"><img src={mediaUrl(me.profile_img)} alt="profpic" /></div>
              <div className="handle">
                <h4>{displayName(me)}</h4>
                <p className="text-muted">@{me.username}</p>
              </div>
            </Link>
            <div className="sidebar">
              <Link href="/" className={`menu-item${active("/")}`}><span><i className="bi bi-house" /></span><h3>Home</h3></Link>
              <Link href={profilePath} className={`menu-item${active(profilePath)}`}><span><i className="bi bi-person" /></span><h3>Profile</h3></Link>
              <Link href="/settings/" className={`menu-item${active("/settings/")}`}><span><i className="bi bi-gear" /></span><h3>Settings</h3></Link>
              <button type="button" className="menu-item" onClick={() => setUploadOpen(true)}>
                <span><i className="bi bi-plus-square" /></span><h3>Upload Post</h3>
              </button>
              <button type="button" className="menu-item menu-item-danger" onClick={() => { logout(); router.push("/login/"); }}>
                <span><i className="bi bi-door-closed" /></span><h3>Logout</h3>
              </button>
            </div>
          </div>

          <div className="middle">{children}</div>

          <div className="right">
            <div className="suggestions">
              <div className="heading"><h4>Suggestions</h4></div>
              {suggestions.length === 0 && <p className="text-muted">No suggestions yet.</p>}
              {suggestions.map((s) => (
                <Link key={s.id} href={`/profile/${s.username}/`} className="suggest">
                  <div className="profile-photo"><img src={mediaUrl(s.profile_img)} alt="profpic" /></div>
                  <div className="ingo"><h3>{s.username}</h3></div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </main>

      {uploadOpen && (
        <UploadOverlay
          onClose={() => setUploadOpen(false)}
          onDone={() => {
            setUploadOpen(false);
            window.dispatchEvent(new Event("adderhub:posted"));
          }}
        />
      )}
    </>
  );
}
