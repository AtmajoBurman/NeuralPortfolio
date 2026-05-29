import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  envDir: '../',
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        projects: resolve(__dirname, 'projects.html'),
        achievements: resolve(__dirname, 'achievements.html'),
        chitchat: resolve(__dirname, 'chitchat.html'),
      },
    },
  },
});
