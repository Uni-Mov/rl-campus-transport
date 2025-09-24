import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Card, CardContent } from "@/components/ui/card"

export default function Contact() {
  const members = [
    {
      name: "Francisco Natale",
      role: "Frontend developer",
      avatar: "https://github.com/sbfrancisco.png",
    },
    {
      name: "Franco Vesnaver",
      role: "Frontend developer",
      avatar: "https://github.com/FranVesnaver.png",
    },
    {
      name: "Valentino Vilar",
      role: "IA-ML developer",
      avatar: "https://github.com/valenvilar5.png",
    },
    {
      name: "Francisco Barosco",
      role: "IA-ML developer",
      avatar: "https://github.com/franBarosco.png",
    },
    {
      name: "Agustin Alieni",
      role: "Backend developer",
      avatar: "https://github.com/AlieniAgustin.png",
    },
    {
      name: "Hernan Jara",
      role: "Backend developer",
      avatar: "https://github.com/HernanJara4.png",
    },
  ]

  return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight text-foreground mb-4">Nuestro Equipo</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {members.map((member, index) => (
            <Card key={index} className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <Avatar className="w-16 h-16 ring-2 ring-border group-hover:ring-primary transition-colors">
                    <AvatarImage src={member.avatar || "/placeholder.svg"} alt={member.name} />
                    <AvatarFallback className="text-lg font-semibold">
                      {member.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex flex-col gap-2">
                    <h3 className="text-xl font-semibold tracking-tight text-foreground group-hover:text-primary transition-colors">
                      {member.name}
                    </h3>
                    <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">{member.role}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        </div>
  )
}
