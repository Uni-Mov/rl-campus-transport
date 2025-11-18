import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // shadcn paths targeting src/types
      '@/components/ui': path.resolve(__dirname, 'src/types/components/ui'),
      '@/lib': path.resolve(__dirname, 'src/types/lib'),
      '@models/lib': path.resolve(__dirname, 'src/types/lib'),
      '@models/components': path.resolve(__dirname, 'src/types/components'),
      '@models/config': path.resolve(__dirname, 'src/types/components/config'),
      // Project-wide aliases
      '@': path.resolve(__dirname, 'src'),
      '@models': path.resolve(__dirname, 'src/models'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@components': path.resolve(__dirname, 'src/components'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
  }
});
