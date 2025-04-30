// app/views/static/js/service-worker.js

const CACHE_NAME = "queen-game-v2";    // ← bump the version!

const ASSETS = [
  // All of your JS modules:
  "/static/js/main.js",
  "/static/js/dom.js",
  "/static/js/state.js",
  "/static/js/utils.js",
  "/static/js/drag.js",
  "/static/js/buildBoard.js",
  "/static/js/settings.js",
  "/static/js/hint.js",
  "/static/js/timer.js",

  // CSS and images
  "/static/css/styles.css",
  "/static/assets/cross.png",
  "/static/assets/queen.png",
  "/static/assets/error.png",
  "/static/assets/settings_icon.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener("activate", event => {
  // delete any old caches
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== CACHE_NAME)
          .map(old => caches.delete(old))
      )
    )
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request)
      .then(cached => cached || fetch(event.request))
  );
});
