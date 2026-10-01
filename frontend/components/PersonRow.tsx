import Link from "next/link";
import { mediaUrl } from "@/lib/format";
import type { Profile } from "@/lib/types";

// One user in the search results and follower/following lists.
export default function PersonRow({ person, withBio = false }: { person: Profile; withBio?: boolean }) {
  return (
    <div className="wrapper">
      <div>
        <div className="row">
          <div className="row1">
            <Link href={`/profile/${person.username}/`} className="profile-link">
              <img src={mediaUrl(person.profile_img)} className="profile-img" alt="" />
            </Link>
            <div className="profile-marg">
              <p className="profile-name">{`${person.first_name ?? ""} ${person.last_name ?? ""}`.trim()}</p>
              <span><Link href={`/profile/${person.username}/`}>@{person.username}</Link></span>
            </div>
          </div>
        </div>
        {withBio && <p>{person.bio}</p>}
      </div>
    </div>
  );
}
