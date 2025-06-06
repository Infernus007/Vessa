import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"

    const incidents = [
        {
            id: "1",
            title: "API Rate Limit Exceeded",
            status: "resolved",
            timestamp: "2 hours ago",
            user: {
                name: "John Doe",
                email: "john@example.com",
                avatar: "/avatars/01.png"
            }
        },
        {
            id: "2",
            title: "Database Connection Error",
            status: "investigating",
            timestamp: "4 hours ago",
            user: {
                name: "Jane Smith",
                email: "jane@example.com",
                avatar: "/avatars/02.png"
            }
        },
        {
            id: "3",
            title: "High Memory Usage",
            status: "monitoring",
            timestamp: "6 hours ago",
            user: {
                name: "Mike Johnson",
                email: "mike@example.com",
                avatar: "/avatars/03.png"
            }
        }
    ]

export function RecentIncidents() {
    return (
        <div className="space-y-8">
            {incidents.map((incident) => (
                <div key={incident.id} className="flex items-center">
                    <Avatar className="h-9 w-9">
                        <AvatarImage src={incident.user.avatar} alt="Avatar" />
                        <AvatarFallback>{incident.user.name[0]}</AvatarFallback>
                    </Avatar>
                    <div className="ml-4 space-y-1">
                        <p className="text-sm font-medium leading-none">{incident.title}</p>
                        <div className="flex items-center gap-2">
                            <Badge 
                                variant={
                                    incident.status === "resolved" 
                                        ? "default"
                                        : incident.status === "investigating"
                                        ? "destructive"
                                        : "secondary"
                                }
                            >
                                {incident.status}
                            </Badge>
                            <p className="text-sm text-muted-foreground">
                                {incident.timestamp}
                            </p>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )
} 