const API = (() => {
    const BASE = window.location.origin;

    async function request(method, path, body = null, timeout = 120000) {
        const opts = {
            method,
            headers: { "Content-Type": "application/json" },
            signal: AbortSignal.timeout(timeout),
        };
        if (body && method !== "GET") opts.body = JSON.stringify(body);
        const resp = await fetch(`${BASE}${path}`, opts);
        const data = await resp.json();
        if (!resp.ok) {
            const msg = data.detail || data.message || `请求失败 (${resp.status})`;
            throw new Error(msg);
        }
        return data;
    }

    return {
        health: () => request("GET", "/health", null, 5000),

        getStyles: () => request("GET", "/api/v1/avatar/styles"),
        getFeatures: () => request("GET", "/api/v1/avatar/features"),
        getResolutions: () => request("GET", "/api/v1/avatar/resolutions"),
        generateAvatar: (params) => request("POST", "/api/v1/avatar/generate", params),

        generateImage: (params) => request("POST", "/api/v1/generation/text2img", params),

        getHistory: (userId, limit = 20, offset = 0) => {
            const params = new URLSearchParams({ limit, offset });
            if (userId) params.set("user_id", userId);
            return request("GET", `/api/v1/history?${params}`);
        },
        clearHistory: (userId = null) => {
            const params = userId ? `?user_id=${encodeURIComponent(userId)}` : "";
            return request("DELETE", `/api/v1/history${params}`);
        },

        getCacheStats: () => request("GET", "/api/v1/cache/stats"),
        clearCache: () => request("DELETE", "/api/v1/cache"),

        getSdModels: () => request("GET", "/api/v1/models/sd"),
        getLoraModels: () => request("GET", "/api/v1/models/lora"),
        refreshModels: () => request("POST", "/api/v1/models/refresh"),
        getSystemConfig: () => request("GET", "/api/v1/models/config"),
    };
})();
