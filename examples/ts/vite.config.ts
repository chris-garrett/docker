import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ["localhost", "ts.fbi.com"],
    host: true,
    port: 5173,
  },
});
