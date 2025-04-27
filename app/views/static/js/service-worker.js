// app/views/static/service-worker.js

const CACHE_NAME = "queen-game-v1";
const ASSETS = [
  "/static/js/main.js",
  "/static/css/styles.css",
  "/static/assets/cross.png",
  "/static/assets/queen.png",
  "/static/assets/error.png",
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request)
      .then(cached => cached || fetch(event.request))
  );
});
