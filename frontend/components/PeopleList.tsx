"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, useSession } from "@/lib/session";
import type { Paginated, Profile } from "@/lib/types";
import PersonRow from "./PersonRow";

// templates/account/follow_list.html
export default function PeopleList({ kind }: { kind: "followers" | "following" }) {
  const { username } = useParams<{ username: string }>();
  const { me } = useSession();
  const [people, setPeople] = useState<Profile[] | null>(null);

  useEffect(() => {
    (async () => {
      let id = me && me.username.toLowerCase() === username.toLowerCase() ? me.id : undefined;
      if (!id) {
        const found = await api<Paginated<Profile>>(`account/?search=${encodeURIComponent(username)}`);
        id = found.results.find((p) => p.username.toLowerCase() === username.toLowerCase())?.id;
      }
      if (!id) return setPeople([]);
      const page = await api<Paginated<Profile>>(`account/${id}/${kind}/`);
      setPeople(page.results);
    })().catch(() => setPeople([]));
  }, [username, kind, me]);

  return (
    <>
      <h3 className="people-list-title">
        <Link href={`/profile/${username}/`} className="username-link">@{username}</Link> · {kind === "followers" ? "Followers" : "Following"}
      </h3>
      {people?.map((p) => <PersonRow key={p.id} person={p} />)}
      {people && people.length === 0 && <div className="wrapper">Nobody here yet.</div>}
    </>
  );
}
