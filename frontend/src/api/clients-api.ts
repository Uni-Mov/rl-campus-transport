import type { Client } from "@models/clients";

export const fetchClients = async (): Promise<Client[]> => {
  const res = await fetch("https://jsonplaceholder.typicode.com/users");
  console.log(res);
  if (!res.ok) throw new Error("Error fetching clients");
  return res.json();
};

export const deleteClientAPI = async (id: string) => {
  console.log(`Deleting client with id: ${id}`);
};  
