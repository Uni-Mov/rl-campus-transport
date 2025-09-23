export type UserRole = 'driver' | 'passenger'';
export interface User {
    id: number;
    first_name: string
    last_name: string
    dni: string
    email: string
    role:? UserRole
}