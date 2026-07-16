const CACHE_NAME = "glass-manager-cache-v5"; // تم رفع الإصدار لإجبار تنظيف الكاش وسحب الأيقونة الجديدة

// ⚠️ لا تضف "/" هنا أبداً — إنها صفحة ديناميكية يولّدها Shiny
// وتحتوي على session token مختلف في كل مرة. تخزينها يكسر الجلسة.
const STATIC_ASSETS = [
    "/manifest.json",
    "/models_db.json",
    "/style_v2.css",
    "/AMMAR.jpg"  // تم إضافة أيقونتك هنا لتجبر المتصفح على تحميلها وحفظها كأيقونة للتطبيق فوراً
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
// FETCH
// =========================
self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET") return;

    // ✅ طلبات التصفح (الصفحة الرئيسية وأي تنقل) دائماً من الشبكة مباشرة
    // هذا يضمن أن Shiny يحصل على session token جديد وصحيح في كل مرة
    if (event.request.mode === "navigate") {
        event.respondWith(
            fetch(event.request).catch(() => {
                // في حال انقطاع الشبكة فقط، حاول أي نسخة مخزنة كحل أخير
                return caches.match(event.request);
            })
        );
        return;
    }

    // ✅ الملفات الثابتة فقط (CSS, JSON, صور...) تستخدم cache-first
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
                return cachedResponse;
            }

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
