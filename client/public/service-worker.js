'use strict';

// Update cache names any time any of the cached files change.
const CACHE_NAME = 'static-cache-v1';

// Add list of files to cache here.
const FILES_TO_CACHE = [
    '/',
    '/build/bundle.css',
    '/build/bundle.js',
    '/favicon.png',
    '/global.css',
    '/manifest.json',
    '/service-worker.js',

];

var FILES_TO_NOT_CACHE = [
    '/lastUpdate',
    '/testOnline',
    '/note',
    '/noteDeflussiMinimi',
    '/noteLimnimetri',
    '/noteMeteo',
    '/sensori',
    '/stazioni',
    '/livereload.js?snipver=1'
];

function hasUrlCacheExcludeMatch(url) {
    // Note: .endsWith() does not work in IE.
    return FILES_TO_NOT_CACHE.some(path => url.endsWith(path));
}


self.addEventListener('install', (evt) => {
    console.log('[ServiceWorker] Install');

    evt.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[ServiceWorker] Pre-caching offline page');
            return cache.addAll(FILES_TO_CACHE);
        })
    );

    self.skipWaiting();
});

self.addEventListener('activate', (evt) => {
    console.log('[ServiceWorker] Activate');
    // Remove previous cached data from disk.
    evt.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== CACHE_NAME) {
                    console.log('[ServiceWorker] Removing old cache', key);
                    return caches.delete(key);
                }
            }));
        })
    );

    self.clients.claim();
});

/*
self.addEventListener('fetch', (evt) => {
    console.log('[ServiceWorker] Fetch', evt.request.url);
    // Add fetch event handler here.
    if (evt.request.mode !== 'navigate') {
        // Not a page navigation, bail.
        return;
    }
    evt.respondWith(
        fetch(evt.request)
            .catch(() => {
                return caches.open(CACHE_NAME)
                    .then((cache) => {
                        return cache.match('App.svelte');
                    });
            })
    );
});

 */

self.addEventListener('fetch', (e) => {
    if(e.request.method === "GET"){
        e.respondWith((async () => {
            const r = await caches.match(e.request);
            console.log(`[Service Worker] Fetching resource: ${e.request.url}`);
            if (r) {
                console.log(`[Service Worker] Fetching resource: ${e.request.url} from cache`)
                return r;
            }
            const response = await fetch(e.request);
            if(!hasUrlCacheExcludeMatch(e.request.url)) {
                const cache = await caches.open(CACHE_NAME);
                console.log(`[Service Worker] Caching new resource: ${e.request.url}`);
                await cache.put(e.request, response.clone());
            }
            return response;
        })());
    }else{
        console.log("METHOD POST")
    }

});