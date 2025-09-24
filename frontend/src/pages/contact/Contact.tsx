import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
export default function Contact(){
  return (
    <div className="flex items-start gap-3">
      <Avatar className="size-9">
        <AvatarImage src="https://github.com/torvalds.png" alt="@shadcn" />
        <AvatarFallback>CN</AvatarFallback>
      </Avatar>
      <div className="flex flex-col gap-1">
        <span className="font-semibold tracking-tight leading-none">
        Linus Torvalds
        </span>
        <span className="leading-none text-sm text-muted-foreground">
          Vibe coder
        </span>
      </div>
    </div>
  );
}