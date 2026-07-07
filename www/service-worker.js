const CACHE_NAME = "glass-manager-cache-v3"; // تم تحديث الإصدار لإجبار المتصفح على التحديث

const STATIC_ASSETS = [
    "/",
    "/manifest.json",
    "/models_db.json",
    "/style_v2.css" // تم ربطه بالملف الصحيح الجديد
];

// =========================
// INSTALL
// =========================
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        }).then(() => {
            return self.skipWaiting();
        })
    );
});

// =========================
// ACTIVATE (clean old caches)
// =========================
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            return self.clients.claim();
        })
    );
});

// =========================
// FETCH (cache-first strategy)
// =========================
self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET") return;

    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            // إذا وجد الملف في الكاش، نستخدمه
            if (cachedResponse) {
                return cachedResponse;
            }

            // إذا لم يوجد، نطلبه من الشبكة
            return fetch(event.request).then((networkResponse) => {
                if (
                    !networkResponse ||
                    networkResponse.status !== 200 ||
                    networkResponse.type !== "basic"
                ) {
                    return networkResponse;
                }

                const responseClone = networkResponse.clone();

                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseClone);
                });

                return networkResponse;
            });
        })
    );
});
