import { fileURLToPath, URL } from "node:url";

import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import svgLoader from "vite-svg-loader";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load .env from parent directory
  const env = loadEnv(mode, process.cwd() + '/..');

  // Merge environment variables loaded with process.env
  Object.assign(env, process.env);

  return {
    server: {
      port: env.VITE_PORT || 3000
    },
    plugins: [vue(), svgLoader()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
    build: {
      minify: false,
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@import "./src/assets/scss/app.scss";`
        }
      }
    }
  };
});
