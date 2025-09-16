/* handle state, logic, and prepare data/callbacks for the UI. */ 
import { useState, useEffect } from "react";
import type { Client } from "../types/clients";
import { fetchClients, deleteClientAPI } from "../api/clients-api";

export const useClients = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClients()
      .then(data => setClients(data))
      .finally(() => setLoading(false));
  }, []);

  const deleteClient = async (id: string) => {
    await deleteClientAPI(id);
    setClients(prev => prev.filter(c => c.id !== id));
  };

  const lastClient = clients[clients.length - 1] || null;

  return { clients, lastClient, deleteClient, loading };
};
