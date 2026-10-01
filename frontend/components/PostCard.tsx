"use client";

import Link from "next/link";
import { useState } from "react";
import { formatDate, mediaUrl } from "@/lib/format";
import { api, useSession } from "@/lib/session";
import type { Post } from "@/lib/types";

// templates/core/feeds.html: one post.
export default function PostCard({ post: initial, onDelete }: { post: Post; onDelete?: (id: string) => void }) {
  const { me } = useSession();
  const [post, setPost] = useState(initial);
  const [menu, setMenu] = useState(false);

  const toggleLike = async () => {
    const result = await api<{ is_liked: boolean; likes_count: number }>(`core/posts/${post.id}/like/`, {
      method: post.is_liked ? "DELETE" : "POST",
    });
    setPost({ ...post, is_liked: result.is_liked, likes_count: result.likes_count });
  };

  const remove = async () => {
    if (!confirm("Delete this post?")) return;
    await api(`core/posts/${post.id}/`, { method: "DELETE" });
    onDelete?.(post.id);
  };

  const likes = post.likes_count === 0 ? "No Likes" : `${post.likes_count} ${post.likes_count === 1 ? "Like" : "Likes"}`;

  return (
    <div className="feed">
      <div className="head">
        <div className="user">
          <div className="profile-photo"><img src={mediaUrl(post.user.profile_img)} alt="" /></div>
          <div className="ingo">
            <Link href={`/profile/${post.user.username}/`} className="username-link"><h3>{post.user.username}</h3></Link>
            <small>{formatDate(post.creation_time)}</small>
          </div>
        </div>
        {me?.id === post.user.id && (
          <div className="post-menu">
            <button type="button" className="post-menu-toggle bi bi-three-dots" aria-label="Post options" aria-expanded={menu} onClick={() => setMenu(!menu)} />
            {menu && (
              <div className="post-menu-dropdown">
                <button type="button" className="post-menu-item post-menu-item-danger" onClick={remove}>
                  <i className="bi bi-trash" /> Delete
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="photo">
        <Link href={`/post/${post.id}/`}><img src={mediaUrl(post.image)} alt="" /></Link>
      </div>
      <div className="action-button">
        <div className="interaction-buttons">
          <button
            type="button"
            className={`icon-button bi ${post.is_liked ? "bi-suit-heart-fill" : "bi-suit-heart"}`}
            aria-label={post.is_liked ? "Unlike" : "Like"}
            onClick={toggleLike}
          />
          <span className="text-muted">{likes}</span>
          <Link href={`/post/${post.id}/#comments`} className="icon-button bi bi-chat" aria-label="Comments" />
          <span className="text-muted">{post.comments_count}</span>
        </div>
      </div>
      <div className="caption">
        <p>
          <b><Link href={`/profile/${post.user.username}/`} className="username-link">{post.user.username}</Link></b>{" "}
          {post.caption}
        </p>
      </div>
    </div>
  );
}
