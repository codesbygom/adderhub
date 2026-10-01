"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/session";
import type { Paginated, Post } from "@/lib/types";
import PostCard from "./PostCard";

// templates/core/feeds.html loop, backed by the paginated posts API.
export default function Feed({ path, empty }: { path: string; empty: string }) {
  const [posts, setPosts] = useState<Post[] | null>(null);
  const [next, setNext] = useState<string | null>(null);

  const load = useCallback(() => {
    api<Paginated<Post>>(path)
      .then((page) => {
        setPosts(page.results);
        setNext(page.next);
      })
      .catch(() => setPosts([]));
  }, [path]);

  useEffect(() => {
    setPosts(null);
    load();
    window.addEventListener("adderhub:posted", load);
    return () => window.removeEventListener("adderhub:posted", load);
  }, [load]);

  const more = async () => {
    if (!next) return;
    const url = new URL(next);
    const page = await api<Paginated<Post>>(`${url.pathname.replace(/^\/api\//, "")}${url.search}`);
    setPosts((prev) => [...(prev ?? []), ...page.results]);
    setNext(page.next);
  };

  if (!posts) return <div className="wrapper"><i className="bi bi-hourglass-split" /></div>;

  return (
    <div className="feeds">
      {posts.map((post) => (
        <PostCard key={post.id} post={post} onDelete={(id) => setPosts((p) => (p ?? []).filter((x) => x.id !== id))} />
      ))}
      {posts.length === 0 && <div className="wrapper">{empty}</div>}
      {next && <button type="button" className="btn btn-primary" onClick={more}>Load more</button>}
    </div>
  );
}
