"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import Feed from "@/components/Feed";

function Home() {
  const following = useSearchParams().get("tab") === "following";

  return (
    <>
      <div className="feed-tabs">
        <Link href="/" className={`feed-tab${following ? "" : " active"}`}>Explore</Link>
        <Link href="/?tab=following" className={`feed-tab${following ? " active" : ""}`}>Following</Link>
      </div>
      <Feed
        path={following ? "core/posts/feed/" : "core/posts/"}
        empty={following ? "No posts yet — follow some people (or share your first post) to fill this feed." : "No posts yet."}
      />
    </>
  );
}

// templates/core/index.html
export default function HomePage() {
  return (
    <Suspense>
      <Home />
    </Suspense>
  );
}
