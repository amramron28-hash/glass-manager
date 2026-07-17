const CACHE_NAME = "glass-manager-cache-v6";

// الملفات التي سيتم حفظها
const STATIC_ASSETS = [
    "/",
    "/manifest.json",
    "/style_v2.css?v=7",
    "/AMMAR.jpg",
    "/phone_image.webp",
    "/models_db.json"
];

// =======================
// INSTALL
// =======================

self.addEventListener("install", (event) => {

    self.skipWaiting();

    event.waitUntil(

        caches.open(CACHE_NAME).then((cache) => {

            return cache.addAll(STATIC_ASSETS);

        })

    );

});

// =======================
// ACTIVATE
// =======================

self.addEventListener("activate", (event) => {

    event.waitUntil(

        caches.keys().then((keys) => {

            return Promise.all(

                keys.map((key) => {

                    if (key !== CACHE_NAME) {

                        return caches.delete(key);

                    }

                })

            );

        }).then(() => self.clients.claim())

    );

});

// =======================
// FETCH
// =======================

self.addEventListener("fetch", (event) => {

    if (event.request.method !== "GET") return;

    // صفحات Shiny دائماً من الشبكة
    if (event.request.mode === "navigate") {

        event.respondWith(

            fetch(event.request).catch(() => caches.match("/"))

        );

        return;

    }

    // لا نضع طلبات Supabase أو WebSocket في الكاش
    if (
        event.request.url.includes("supabase") ||
        event.request.url.includes("/websocket/")
    ) {
        return;
    }

    event.respondWith(

        caches.match(event.request).then((cached) => {

            if (cached) {

                return cached;

            }

            return fetch(event.request).then((response) => {

                if (!response || response.status !== 200) {

                    return response;

                }

                const copy = response.clone();

                caches.open(CACHE_NAME).then((cache) => {

                    cache.put(event.request, copy);

                });

                return response;

            });

        })

    );

});
