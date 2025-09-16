import { useClients } from "../../hooks/useClients"
import { ListClients } from "./organisms/list-clients"
import { LastClient } from "./organisms/last-clients"

export default function Clients() {
  const { clients, lastClient, deleteClient, loading } = useClients()

  if (loading)
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <div className="relative">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-muted border-t-primary"></div>
          <div
            className="absolute inset-0 rounded-full h-12 w-12 border-4 border-transparent border-t-secondary animate-spin"
            style={{ animationDelay: "0.15s", animationDuration: "1.5s" }}
          ></div>
        </div>
        <p className="mt-6 text-muted-foreground font-medium">Cargando clientes...</p>
      </div>
    )

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="font-heading text-4xl font-bold text-foreground">Gestión de Clientes</h1>
       
        <div className="flex justify-center items-center space-x-8 pt-4">
          <div className="text-center">
            <div className="text-2xl font-heading font-bold text-primary">{clients.length}</div>
            <div className="text-sm text-muted-foreground">Total Clientes</div>
          </div>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-3 xl:gap-12">
        <div className="lg:col-span-2">
          <ListClients clients={clients} deleteClient={deleteClient} />
        </div>
          <LastClient lastClient={lastClient} />
        </div>
      </div>
  )
}
