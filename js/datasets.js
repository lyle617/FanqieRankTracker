(function (global) {
    const cacheBuster = `v=${Math.floor(Date.now() / 600000)}`;
    let manifestPromise = null;

    function loadManifest() {
        if (!manifestPromise) {
            manifestPromise = fetch(`data/datasets.json?${cacheBuster}`)
                .then(response => {
                    if (!response.ok) throw new Error('Failed to load dataset manifest');
                    return response.json();
                });
        }
        return manifestPromise;
    }

    function normalize(manifest, requested) {
        const key = requested && manifest.datasets[requested]
            ? requested
            : manifest.default;
        return { key, ...manifest.datasets[key] };
    }

    global.FanqieDatasets = {
        async load(requested) {
            return normalize(await loadManifest(), requested);
        },
        normalize,
    };
})(window);
