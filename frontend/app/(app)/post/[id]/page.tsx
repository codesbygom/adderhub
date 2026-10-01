"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import PostCard from "@/components/PostCard";
import { errorMessages, mediaUrl, timeSince } from "@/lib/format";
import { api, ApiError, useSession } from "@/lib/session";
import type { Comment, Paginated, Post } from "@/lib/types";

// templates/core/post-detail.html
export default function PostDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { me } = useSession();
  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [text, setText] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api<Post>(`core/posts/${id}/`).then(setPost).catch(() => router.replace("/"));
    api<Paginated<Comment>>(`core/posts/${id}/comments/`).then((p) => setComments(p.results)).catch(() => {});
  }, [id, router]);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await api<Comment>(`core/posts/${id}/comments/`, { method: "POST", body: JSON.stringify({ text }) });
      setComments((c) => [...c, created]);
      setText("");
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? errorMessages(err.data).join(" ") : "Could not post the comment.");
    }
  };

  const remove = async (commentId: string) => {
    await api(`core/comments/${commentId}/`, { method: "DELETE" });
    setComments((c) => c.filter((x) => x.id !== commentId));
  };

  if (!post) return <div className="wrapper"><i className="bi bi-hourglass-split" /></div>;

  return (
    <>
      <div className="feeds">
        <PostCard post={post} onDelete={() => router.replace("/")} />
      </div>

      <div className="comments" id="comments">
        <h4>Comments</h4>
        {comments.map((c) => (
          <div className="comment" key={c.id}>
            <Link href={`/profile/${c.user.username}/`} className="profile-photo">
              <img src={mediaUrl(c.user.profile_img)} alt="" />
            </Link>
            <div className="comment-body">
              <p>
                <b><Link href={`/profile/${c.user.username}/`} className="username-link">{c.user.username}</Link></b>{" "}
                {c.text}
              </p>
              <small className="text-muted">{timeSince(c.creation_time)} ago</small>
            </div>
            {(me?.id === c.user.id || me?.id === post.user.id) && (
              <button type="button" className="icon-button bi bi-trash" aria-label="Delete comment" onClick={() => remove(c.id)} />
            )}
          </div>
        ))}
        {comments.length === 0 && <p className="text-muted">No comments yet. Be the first!</p>}

        <form className="comment-form" onSubmit={add}>
          <textarea maxLength={1000} rows={2} required placeholder="Add a comment..." value={text} onChange={(e) => setText(e.target.value)} />
          <button type="submit" className="btn btn-primary">Post</button>
        </form>
        {error && <p style={{ color: "var(--color-danger)" }}>{error}</p>}
      </div>
    </>
  );
}
