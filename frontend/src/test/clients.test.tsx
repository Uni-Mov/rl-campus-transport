import { renderHook, act, waitFor } from '@testing-library/react';
import { test, describe, expect, vi } from 'vitest';
import { useClients } from '../hooks/useClients';
 // mockeamos la api de clients
vi.mock('../api/clients-api', () => ({
  // definimos que tiene que devolver cuando llamemos a fetchClients
  fetchClients: vi.fn().mockResolvedValue([
    { id: '1', name: 'Fran', email: 'fran@test.com' },
    { id: '2', name: 'Ana', email: 'ana@test.com' }
  ]),
  // definimos que tiene que devolver cuando llamemos a deleteClientAPI
  deleteClientAPI: vi.fn().mockResolvedValue(console.log("cliente eliminado"))
}));

describe('useClients hook', () => {
  test('carga clientes desde la API', async () => {
    const { result } = renderHook(() => useClients());

    await waitFor(() => {
      expect(result.current.clients.length).toBe(2);
      expect(result.current.loading).toBe(false);
    });
  });

  test('elimina el último cliente', async () => {
    const { result } = renderHook(() => useClients());
    // el waitFor espera que los clientes se carguen, cuando efectivamente se carga y el lenght es 2, se puede acceder al último cliente
    await waitFor(() => {
      expect(result.current.clients.length).toBe(2);
    });

    const lastClient = result.current.lastClient;
    await act(async () => {
      await result.current.deleteClient(lastClient.id);
    });
    const clients = result.current.clients;
    console.log("clientes eliminados: ", lastClient);
    console.log("clientes que quedaron registrados: ", clients);
    expect(result.current.clients.includes(lastClient)).toBe(false);
    expect(result.current.clients.length).toBe(1);
  });

});
