import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Card, CardContent } from "@/components/ui/card"

interface MemberProps {
  member: {
    name: string;
    role: string;
    avatar: string;
    github: string;
  }
}

export default function Member({ member }: MemberProps) {
  return (
    <a key={member.github} href={member.github} target="_blank" rel="noopener noreferrer">
      <Card className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1 cursor-pointer">
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <Avatar className="w-16 h-16">
              <AvatarImage src={member.avatar} alt={member.name} />
              <AvatarFallback>{member.name.split(" ").map(n => n[0]).join("")}</AvatarFallback>
            </Avatar>
            <div>
              <h3 className="text-xl font-semibold">{member.name}</h3>
              <p className="text-sm text-muted-foreground uppercase">{member.role}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </a>
  )
}
