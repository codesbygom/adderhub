"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import FollowButton from "@/components/FollowButton";
import { displayName, mediaUrl } from "@/lib/format";
import { api, useSession } from "@/lib/session";
import type { Paginated, Post, Profile } from "@/lib/types";

// Looks a profile up by username through the search endpoint, since the
// detail endpoint is keyed by id.
async function findProfile(username: string): Promise<Profile | null> {
  const page = await api<Paginated<Profile>>(`account/?search=${encodeURIComponent(username)}`);
  return page.results.find((p) => p.username.toLowerCase() === username.toLowerCase()) ?? null;
}

// templates/account/profile.html
export default function ProfilePage() {
  const { username } = useParams<{ username: string }>();
  const { me, reloadMe } = useSession();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [missing, setMissing] = useState(false);
  const avatarInput = useRef<HTMLInputElement>(null);
  const bgInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setProfile(null);
    setMissing(false);
    (async () => {
      // The search endpoint excludes yourself, so your own profile comes from /me/.
      const p = me && me.username.toLowerCase() === username.toLowerCase() ? me : await findProfile(username);
      if (!p) return setMissing(true);
      setProfile(p);
      const list = await api<Paginated<Post>>(`core/posts/?user=${p.id}`);
      setPosts(list.results);
    })().catch(() => setMissing(true));
  }, [username, me]);

  if (missing) return <div className="wrapper">No such user.</div>;
  if (!profile) return <div className="wrapper"><i className="bi bi-hourglass-split" /></div>;

  const own = me?.id === profile.id;
  const upload = async (field: "profile_img" | "background_img", file?: File) => {
    if (!file) return;
    const body = new FormData();
    body.append(field, file);
    await api("account/update/", { method: "PATCH", body });
    await reloadMe();
  };

  return (
    <>
      <div className="wrapper">
        <div className={`profile-bg${own ? " avatar-edit" : ""}`}>
          <img src={mediaUrl(profile.background_img)} alt="" />
          {own && (
            <>
              <button type="button" className="avatar-edit-btn bi bi-pencil-fill" aria-label="Change background picture" onClick={() => bgInput.current?.click()} />
              <input ref={bgInput} type="file" accept="image/*" hidden onChange={(e) => upload("background_img", e.target.files?.[0])} />
            </>
          )}
        </div>
        <div>
          <div className="row">
            <div className="row1">
              <div className={`profile-link${own ? " avatar-edit" : ""}`}>
                <img src={mediaUrl(profile.profile_img)} className="profile-img" alt="" />
                {own && (
                  <>
                    <button type="button" className="avatar-edit-btn bi bi-pencil-fill" aria-label="Change profile picture" onClick={() => avatarInput.current?.click()} />
                    <input ref={avatarInput} type="file" accept="image/*" hidden onChange={(e) => upload("profile_img", e.target.files?.[0])} />
                  </>
                )}
              </div>
              <div className="profile-marg">
                <div>
                  <p className="profile-name">{displayName(profile) === profile.username ? "" : displayName(profile)}</p>
                  <span>@{profile.username}</span>
                </div>
              </div>
            </div>
            {own ? (
              <Link className="btn btn-primary" href="/settings/">Edit Profile</Link>
            ) : (
              <FollowButton userId={profile.id} initial={profile.is_following} onChange={(n) => setProfile({ ...profile, followers_count: n })} />
            )}
          </div>
          <p>{profile.bio}</p>
          <div className="profile-state">
            <ul className="profile-Arrange">
              <li className="profile-details">
                <a href="#profile-posts">
                  <span className="profile-label d-block">Posts</span>
                  <span className="profile-number">{profile.posts_count}</span>
                </a>
              </li>
              <li className="profile-details">
                <Link href={`/profile/${profile.username}/followers/`}>
                  <span className="profile-label d-block">Followers</span>
                  <span className="profile-number">{profile.followers_count}</span>
                </Link>
              </li>
              <li className="profile-details">
                <Link href={`/profile/${profile.username}/following/`}>
                  <span className="profile-label d-block">Followings</span>
                  <span className="profile-number">{profile.followings_count}</span>
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div className="profileposts" id="profile-posts">
        <div className="post">
          {posts.map((post) => (
            <div className="photo" key={post.id}>
              <Link href={`/post/${post.id}/`}><img className="pic" src={mediaUrl(post.image)} alt="" /></Link>
            </div>
          ))}
          {posts.length === 0 && <label>No posts available</label>}
        </div>
      </div>
    </>
  );
}
