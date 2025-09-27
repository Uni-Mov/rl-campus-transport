

# contexto - hook - estados 


En principio, definimos un **contexto** que permite que toda la aplicación acceda a ciertas propiedades que tengan sentido ser compartidas globalmente, en este caso, información de autenticación.
Otros casos de uso, podria ser idioma de la aplicacion, tema dark/light

# Contextualizacion 
Con react, **cada vez que recargamos una página**, esto es lo que sucede por debajo:

1. El navegador carga el bundle (JavaScript, HTML, CSS).  
2. React monta el árbol de componentes desde el componente raíz (`index.tsx`).

Supongamos un archivo `index.tsx` algo así:

```tsx
<AuthProvider>
  <App />
</AuthProvider>
```

Aquí, `AuthProvider` va a envolver toda nuestra app y le dará a todos los hijos acceso al contexto de autenticación.

---

Veamos unos fragmentos de código para entender
Primero, veamos cómo está definido el hook `useAuth`:

```ts
export const useAuth = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // en caso de que en localStorage esté el token, setea el estado logeado con true
    useEffect(() => {
        const token = localStorage.getItem("authToken");
        setIsLoggedIn(!!token);
    }, []);

    return { isLoggedIn };
};
```

**Qué hace esto:**

- `useState` define un estado local `isLoggedIn` que por defecto es `false`.  
- `useEffect` se ejecuta **después del primer render**, busca en `localStorage` un token de autenticación y actualiza el estado `isLoggedIn` a `true` si existe.  
- Retornamos `isLoggedIn` para que cualquier componente que use este hook pueda leer el estado

---

Luego, definimos el **contexto** y el **provider**:

```ts
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const auth = useAuth();
    return (
        <AuthContext.Provider value={auth}>
            {children}
        </AuthContext.Provider>
    );
}
```

**Qué hace esto:**

- `createContext` crea un contexto de React, que es básicamente un "contenedor" para datos que queremos compartir en todo el árbol de componentes.  
- `AuthProvider` es un componente que envuelve a todos los hijos (`children`) y les provee acceso al estado de `auth` (nuestro hook).  
- Esto permite que cualquier componente dentro de `<AuthProvider>` use el contexto mediante `useContext(AuthContext)`.

---

### Notas importantes:

- La búsqueda en `localStorage` garantiza que si la página se recarga, React vuelva a leer el token y actualice el estado `isLoggedIn` automáticamente. Esto es lo que hace que la sesión sea **"persistente"**. 

- Si navegamos internamente dentro de la app (cambiando rutas con React Router, por ejemplo), React **no vuelve a montar el árbol completo**, por lo que el estado de `AuthProvider` se mantiene intacto.  

- Diferencias entre `localStorage` y `sessionStorage`:  
  - `localStorage`: persiste aunque cierres y abras el navegador.  
  - `sessionStorage`: persiste solo mientras la pestaña o ventana esté abierta.

---

### Uso en componentes hijos

Para acceder al estado en cualquier componente hijo:

```ts
const { isLoggedIn } = useContext(AuthContext);

if (isLoggedIn) {
    console.log("Usuario logueado");
} else {
    console.log("Usuario no logueado");
}
```

**Puntos clave:**

- `useContext` **solo funciona dentro de un componente hijo** de un `Provider`.  
- No necesitas pasar props manualmente a cada componente; todo el árbol que esté dentro del `AuthProvider` puede acceder al estado de autenticación.
