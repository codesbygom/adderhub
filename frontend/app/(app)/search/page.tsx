"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import PersonRow from "@/components/PersonRow";
import { api } from "@/lib/session";
import type { Paginated, Profile } from "@/lib/types";

function Results() {
  const query = useSearchParams().get("search") ?? "";
  const [people, setPeople] = useState<Profile[] | null>(null);

  useEffect(() => {
    setPeople(null);
    api<Paginated<Profile>>(`account/?search=${encodeURIComponent(query)}`)
      .then((page) => setPeople(page.results))
      .catch(() => setPeople([]));
  }, [query]);

  if (!people) return <div className="wrapper"><i className="bi bi-hourglass-split" /></div>;
  if (people.length === 0) return <div className="wrapper">no users found!</div>;
  return <>{people.map((p) => <PersonRow key={p.id} person={p} withBio />)}</>;
}

// templates/core/search.html
export default function SearchPage() {
  return (
    <Suspense>
      <Results />
    </Suspense>
  );
}
