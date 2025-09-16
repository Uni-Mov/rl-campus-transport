import type { Client } from "@models/clients"

export function LastClient({ lastClient }: { lastClient: Client | null }) {
  if (!lastClient) {
    return (
      <div className="bg-card rounded-xl border border-border p-6">
        <div className="px-2 py-1 border-b border-border mb-4 -mx-2 -mt-2 pb-4">
          <h2 className="font-heading text-lg font-semibold text-foreground">Último Cliente</h2>
        </div>
        <div className="text-center py-8">
          <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
              />
            </svg>
          </div>
          <p className="text-muted-foreground text-sm">No hay clientes agregados recientemente</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <div className="px-6 py-4 border-b border-border bg-accent/5">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
          <h2 className="font-heading text-lg font-semibold text-foreground">Último Cliente Agregado</h2>
        </div>
      </div>

      <div className="p-6">
        <div className="flex items-start space-x-4">
          <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center flex-shrink-0">
            <span className="text-accent font-heading font-bold text-xl">
              {lastClient.name.charAt(0).toUpperCase()}
            </span>
          </div>

          <div className="flex-1 space-y-3">
            <div>
              <h3 className="font-heading font-semibold text-xl text-foreground">{lastClient.name}</h3>
              <p className="text-muted-foreground text-sm mt-1">Cliente reciente</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center text-sm">
                <svg
                  className="w-4 h-4 mr-3 text-muted-foreground flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
                  />
                </svg>
                <span className="text-foreground">{lastClient.email}</span>
              </div>

              {lastClient.phone && (
                <div className="flex items-center text-sm">
                  <svg
                    className="w-4 h-4 mr-3 text-muted-foreground flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                    />
                  </svg>
                  <span className="text-foreground">{lastClient.phone}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
