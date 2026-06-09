import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const API_PORT = globalThis.process?.env?.API_PORT || "19929";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: `http://127.0.0.1:${API_PORT}`,
        changeOrigin: true,
      },
    },
  },
});
