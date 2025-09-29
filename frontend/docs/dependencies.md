# Dependencias del Proyecto Frontend

## Decisiones tomadas en el transcurso del desarrollo

### Dependencias Principales

#### **React y Core**
- **React** (^18.2.0) - Biblioteca principal para la interfaz de usuario
- **React DOM** (^18.2.0) - Renderizado de React en el DOM
- **React Router DOM** (^6.20.1) - Enrutamiento para aplicaciones React

#### **UI y Componentes**
- **shadcn** (^3.3.1) - Conjunto de componentes para el desarrollo de interfaces, cuenta con ejemplos y [paletas de colores](https://ui.shadcn.com/colors) compatibles con Tailwind
- **Radix UI** - Componentes accesibles y primitivos:
  - `@radix-ui/react-avatar` (^1.1.10) - Componente de avatar
  - `@radix-ui/react-slot` (^1.2.3) - Slot composable
  - `@radix-ui/react-tooltip` (^1.2.8) - Tooltips accesibles
  - `radix-ui` (^1.4.3) - Paquete principal

#### **Iconos y Utilidades**
- **Lucide React** (^0.544.0) - Biblioteca de iconos de código abierto con más de 1000 iconos
- **class-variance-authority** (^0.7.1) - Utilidad para variantes de clases CSS
- **clsx** (^2.1.1) - Utilidad para construir nombres de clases condicionalmente
- **tailwind-merge** (^3.3.1) - Merge de clases de Tailwind CSS
- **tailwindcss-animate** (^1.0.7) - Animaciones para Tailwind CSS

#### **Mapas y Visualización**
- **Mapbox GL** (^3.15.0) - Biblioteca de mapas interactivos
- **React Map GL** (^6.1.21) - Componentes React para Mapbox GL
- **Deck.gl** - Biblioteca de visualización de datos:
  - `@deck.gl/core` (^9.1.14) - Core de Deck.gl
  - `@deck.gl/layers` (^9.1.14) - Capas de visualización
  - `@deck.gl/react` (^9.1.14) - Integración con React

#### **Utilidades**
- **path** (^0.12.7) - Utilidades para manejo de rutas

### Dependencias de Desarrollo

#### **Testing**
- **Vitest** (^3.2.4) - Framework de testing rápido
- **@testing-library/react** (^16.3.0) - Utilidades de testing para React
- **@testing-library/jest-dom** (^6.8.0) - Matchers personalizados para Jest
- **jsdom** (^26.1.0) - Implementación de DOM para Node.js

#### **TypeScript y Tipos**
- **TypeScript** (^5.2.2) - Superset tipado de JavaScript
- **@types/node** (^24.3.0) - Tipos para Node.js
- **@types/react** (^18.2.43) - Tipos para React
- **@types/react-dom** (^18.2.17) - Tipos para React DOM
- **@types/react-map-gl** (^6.1.7) - Tipos para React Map GL
- **@types/geojson** (^7946.0.16) - Tipos para GeoJSON

#### **Linting y Formateo**
- **ESLint** (^8.55.0) - Linter para JavaScript/TypeScript
- **@typescript-eslint/eslint-plugin** (^6.14.0) - Plugin de ESLint para TypeScript
- **@typescript-eslint/parser** (^6.14.0) - Parser de ESLint para TypeScript
- **eslint-plugin-react-hooks** (^4.6.0) - Reglas de ESLint para React Hooks
- **eslint-plugin-react-refresh** (^0.4.5) - Plugin para React Refresh

#### **Build y Desarrollo**
- **Vite** (^7.1.3) - Herramienta de build rápida
- **@vitejs/plugin-react** (^4.2.1) - Plugin de Vite para React
- **PostCSS** (^8.4.32) - Herramienta para transformar CSS
- **Autoprefixer** (^10.4.16) - Plugin de PostCSS para prefijos CSS
- **Tailwind CSS** (^3.4.17) - Framework de CSS utilitario

## Justificación de Dependencias

### **shadcn/ui**
Se eligió por su enfoque en componentes reutilizables, excelente documentación y compatibilidad nativa con Tailwind CSS.

### **Lucide React**
Se seleccionó por su amplia gama de iconos, consistencia visual y facilidad de uso en proyectos React.

### **Mapbox GL + React Map GL**
Se implementó para funcionalidades de mapas interactivos y visualización de datos geográficos.

### **Deck.gl**
Se integró para capacidades avanzadas de visualización de datos, especialmente útil para representaciones geoespaciales complejas.

### **Radix UI**
Se utilizó como base para componentes accesibles, proporcionando primitivos sólidos que se pueden personalizar fácilmente.