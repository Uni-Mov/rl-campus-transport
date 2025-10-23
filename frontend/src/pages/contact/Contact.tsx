import HeaderContact from "./organisms/HeaderContact"
import Member from "./organisms/Member"
import MemberContainer from "./organisms/MemberContainer"

export default function Contact() {
  return (
    <div className="max-w-4xl mx-auto">
      <HeaderContact />
      <MemberContainer />
    </div>
  )
}
