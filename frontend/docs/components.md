# Guía de Componentes - shadcn/ui

## Componentes utilizados

- [Alert (Soft)](https://www.shadcnui-blocks.com/components/alert) en la pagina de login
- [Avatar (With text)](https://www.shadcnui-blocks.com/components/avatar) en la pagina de contacto

## Cómo Agregar Nuevos Componentes

### 1. Buscar el Componente
Ingresá a [shadcn/ui blocks](https://www.shadcnui-blocks.com/) y buscá el componente que necesitás.

### 2. Instalar el Componente
Ejecutá el comando de instalación correspondiente:   
Un ejemplo   

```bash
npx shadcn@latest add https://www.shadcnui-blocks.com/r/alert-01.json
```

### 3. Copiar el Código del Componente
Una vez instalado, copiá el código del componente desde la página de shadcn/ui blocks.

### 4. Usar el Componente
Importá y usá el componente en tu aplicación:

```tsx
import Alert from "@/components/Alert"

export default function MiPagina() {
  return (
    <Alert>
      ¡Este es un mensaje de alerta!
    </Alert>
  )
}
```

