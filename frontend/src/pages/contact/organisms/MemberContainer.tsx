import Member from "./Member"
import GetMembers from "../constant/GetMembers"

export default function MemberList() {
  const members = GetMembers()
    return(
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {members.map((member) => (
          <Member key={member.github} member={member} />
        ))}
      </div>
    )
}