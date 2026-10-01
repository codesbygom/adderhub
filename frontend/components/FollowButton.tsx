"use client";

import { useState } from "react";
import { api } from "@/lib/session";

export default function FollowButton({ userId, initial, onChange }: { userId: string; initial: boolean; onChange?: (followers: number) => void }) {
  const [following, setFollowing] = useState(initial);

  const toggle = async () => {
    const r = await api<{ is_following: boolean; followers_count: number }>(`account/${userId}/follow/`, {
      method: following ? "DELETE" : "POST",
    });
    setFollowing(r.is_following);
    onChange?.(r.followers_count);
  };

  return (
    <button type="button" className="btn btn-primary" onClick={toggle}>
      {following ? "Unfollow" : "Follow"}
    </button>
  );
}
