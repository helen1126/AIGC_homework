(() => {
    let selectedStyle = "japanese";
    let selectedFeatures = {};
    let lastAvatarData = null;
    let lastGenData = null;
    let historyOffset = 0;
    const historyLimit = 15;

    const FEATURE_LABELS = {
        hair_style: "发型",
        hair_color: "发色",
        eye_color: "眼色",
        clothing_style: "服装",
        expression: "表情",
    };

    const STYLE_ICONS = {
        japanese: "🎌",
        american_comic: "🦸",
        chibi_q: "🎀",
        watercolor: "🎨",
        cyberpunk: "🌃",
        pixel_art: "👾",
    };

    function $(id) { return document.getElementById(id); }

    function toast(msg, type = "info") {
        const container = $("toast-container");
        const el = document.createElement("div");
        el.className = `toast ${type}`;
        el.textContent = msg;
        container.appendChild(el);
        setTimeout(() => { el.style.opacity = "0"; setTimeout(() => el.remove(), 300); }, 3500);
    }

    function showResult(area, state) {
        const ids = ["placeholder", "loading", "result", "error"];
        ids.forEach(id => {
            const el = $(`${area}-${id}`);
            if (el) el.style.display = id === state ? "" : "none";
        });
    }

    async function init() {
        setupNavigation();
        setupMobileMenu();
        setupSliders();
        await checkHealth();
        await Promise.all([
            loadStyles(),
            loadFeatures(),
            loadResolutions(),
            loadSdModels("avatar-sd-model"),
            loadSdModels("gen-sd-model"),
            loadLoraModels("avatar-lora-model"),
            loadLoraModels("gen-lora-model"),
        ]);
        setupGenerateButtons();
    }

    function setupNavigation() {
        document.querySelectorAll(".nav-item").forEach(item => {
            item.addEventListener("click", (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                switchPage(page);
            });
        });
    }

    function switchPage(page) {
        document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
        document.querySelector(`.nav-item[data-page="${page}"]`)?.classList.add("active");
        document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
        $(`page-${page}`)?.classList.add("active");
        closeMobileMenu();

        if (page === "history") loadHistory();
        if (page === "models") loadModelsPage();
        if (page === "system") loadSystemPage();
    }

    function setupMobileMenu() {
        $("menu-btn")?.addEventListener("click", () => {
            $("sidebar").classList.toggle("open");
            $("overlay").classList.toggle("active");
        });
        $("overlay")?.addEventListener("click", closeMobileMenu);
    }

    function closeMobileMenu() {
        $("sidebar").classList.remove("open");
        $("overlay").classList.remove("active");
    }

    function setupSliders() {
        $("avatar-lora-weight")?.addEventListener("input", function () {
            $("lora-weight-display").textContent = this.value;
        });
        $("gen-lora-weight")?.addEventListener("input", function () {
            $("gen-lora-weight-display").textContent = this.value;
        });
    }

    async function checkHealth() {
        const indicator = $("server-status");
        const mobileDot = $("status-mobile");
        try {
            const data = await API.health();
            indicator.className = "status-indicator online";
            indicator.querySelector(".status-text").textContent = `在线 v${data.version || "2.0"}`;
            mobileDot.style.background = "var(--success)";
        } catch {
            indicator.className = "status-indicator offline";
            indicator.querySelector(".status-text").textContent = "离线";
            mobileDot.style.background = "var(--danger)";
        }
    }

    async function loadStyles() {
        try {
            const data = await API.getStyles();
            const grid = $("style-grid");
            grid.innerHTML = "";
            for (const s of data.styles) {
                const card = document.createElement("div");
                card.className = "style-card" + (s.id === selectedStyle ? " active" : "");
                card.innerHTML = `
                    <div class="style-name">${STYLE_ICONS[s.id] || "🎨"} ${s.name}</div>
                    <div class="style-desc">${s.description}</div>`;
                card.addEventListener("click", () => {
                    grid.querySelectorAll(".style-card").forEach(c => c.classList.remove("active"));
                    card.classList.add("active");
                    selectedStyle = s.id;
                });
                grid.appendChild(card);
            }
        } catch (e) {
            console.error("加载风格失败:", e);
        }
    }

    async function loadFeatures() {
        try {
            const data = await API.getFeatures();
            const grid = $("features-grid");
            grid.innerHTML = "";
            for (const [key, options] of Object.entries(data.features)) {
                selectedFeatures[key] = "";
                const item = document.createElement("div");
                item.className = "feature-item";
                const label = document.createElement("label");
                label.textContent = FEATURE_LABELS[key] || key;
                const select = document.createElement("select");
                const defOpt = document.createElement("option");
                defOpt.value = "";
                defOpt.textContent = "不指定";
                select.appendChild(defOpt);
                for (const opt of options) {
                    const o = document.createElement("option");
                    o.value = opt.value;
                    o.textContent = opt.label;
                    select.appendChild(o);
                }
                select.addEventListener("change", () => { selectedFeatures[key] = select.value; });
                item.appendChild(label);
                item.appendChild(select);
                grid.appendChild(item);
            }
        } catch (e) {
            console.error("加载特征失败:", e);
        }
    }

    async function loadResolutions() {
        try {
            const data = await API.getResolutions();
            const select = $("avatar-resolution");
            select.innerHTML = "";
            for (const p of data.presets) {
                const o = document.createElement("option");
                o.value = p.id;
                o.textContent = `${p.label}`;
                if (p.id === "medium") o.selected = true;
                select.appendChild(o);
            }
        } catch (e) {
            console.error("加载分辨率失败:", e);
        }
    }

    async function loadSdModels(selectId) {
        try {
            const data = await API.getSdModels();
            const select = $(selectId);
            const current = select.value;
            select.innerHTML = '<option value="">默认模型</option>';
            for (const m of data.models) {
                const o = document.createElement("option");
                o.value = m.name;
                o.textContent = m.name + (m.is_default ? " ★" : "");
                select.appendChild(o);
            }
            if (current) select.value = current;
        } catch (e) {
            console.error("加载SD模型失败:", e);
        }
    }

    async function loadLoraModels(selectId) {
        try {
            const data = await API.getLoraModels();
            const select = $(selectId);
            const current = select.value;
            select.innerHTML = '<option value="">不使用</option>';
            for (const m of data.models) {
                const o = document.createElement("option");
                o.value = m.name;
                o.textContent = m.name + (m.is_default ? " ★" : "");
                select.appendChild(o);
            }
            if (current) select.value = current;
        } catch (e) {
            console.error("加载LoRA模型失败:", e);
        }
    }

    function setupGenerateButtons() {
        $("avatar-generate-btn")?.addEventListener("click", generateAvatar);
        $("gen-generate-btn")?.addEventListener("click", generateImage);
    }

    async function generateAvatar() {
        const desc = $("avatar-desc").value.trim();
        if (!desc) { toast("请输入角色描述", "error"); return; }

        const btn = $("avatar-generate-btn");
        btn.disabled = true;
        showResult("avatar", "loading");

        const features = {};
        for (const [k, v] of Object.entries(selectedFeatures)) {
            if (v) features[k] = v;
        }

        const payload = {
            description: desc,
            style: selectedStyle,
            resolution: $("avatar-resolution").value,
            quality_mode: $("avatar-quality").value,
            seed: parseInt($("avatar-seed").value) || -1,
            user_id: $("avatar-user").value || "web_user",
            lora_weight: parseFloat($("avatar-lora-weight").value),
        };

        const sdModel = $("avatar-sd-model").value;
        const loraModel = $("avatar-lora-model").value;
        if (sdModel) payload.model = sdModel;
        if (loraModel) payload.lora = loraModel;
        if (Object.keys(features).length > 0) payload.character_features = features;

        try {
            const data = await API.generateAvatar(payload);
            lastAvatarData = data;
            showAvatarResult(data);
            toast("头像生成成功!", "success");
        } catch (e) {
            showResult("avatar", "error");
            $("avatar-error").textContent = "❌ " + e.message;
            toast(e.message, "error");
        } finally {
            btn.disabled = false;
        }
    }

    function showAvatarResult(data) {
        showResult("avatar", "result");
        $("avatar-image").src = "data:image/png;base64," + data.image_base64;
        $("avatar-meta").style.display = "";
        $("avatar-actions").style.display = "";

        const params = data.parameters || {};
        const items = [
            ["风格", data.style_used],
            ["分辨率", `${data.resolution.width}×${data.resolution.height}`],
            ["种子", data.seed],
            ["耗时", `${data.generation_time}s`],
            ["缓存", data.cached ? '<span class="badge badge-success">命中</span>' : "否"],
            ["SD模型", params.sd_model ? `<span class="badge badge-info">${params.sd_model}</span>` : "默认"],
            ["LoRA", params.lora_model ? `<span class="badge badge-accent">${params.lora_model}</span>` : "无"],
            ["LoRA权重", params.lora_weight && params.lora_model ? params.lora_weight : "-"],
        ];

        $("avatar-meta-grid").innerHTML = items.map(([l, v]) =>
            `<div class="meta-item"><span class="meta-label">${l}</span><span class="meta-value">${v}</span></div>`
        ).join("");
    }

    async function generateImage() {
        const prompt = $("gen-prompt").value.trim();
        if (!prompt) { toast("请输入正向提示词", "error"); return; }

        const btn = $("gen-generate-btn");
        btn.disabled = true;
        showResult("gen", "loading");

        const payload = {
            prompt,
            negative_prompt: $("gen-neg-prompt").value,
            width: parseInt($("gen-width").value) || 512,
            height: parseInt($("gen-height").value) || 512,
            num_inference_steps: parseInt($("gen-steps").value) || 20,
            guidance_scale: parseFloat($("gen-cfg").value) || 7.5,
            seed: parseInt($("gen-seed").value) || -1,
            scheduler: $("gen-scheduler").value,
            lora_weight: parseFloat($("gen-lora-weight").value),
        };

        const sdModel = $("gen-sd-model").value;
        const loraModel = $("gen-lora-model").value;
        if (sdModel) payload.sd_model = sdModel;
        if (loraModel) payload.lora_model = loraModel;

        try {
            const data = await API.generateImage(payload);
            lastGenData = data;
            showGenResult(data);
            toast("图片生成成功!", "success");
        } catch (e) {
            showResult("gen", "error");
            $("gen-error").textContent = "❌ " + e.message;
            toast(e.message, "error");
        } finally {
            btn.disabled = false;
        }
    }

    function showGenResult(data) {
        showResult("gen", "result");
        $("gen-image").src = "data:image/png;base64," + data.image_base64;
        $("gen-meta").style.display = "";
        $("gen-actions").style.display = "";

        const p = data.parameters || {};
        const items = [
            ["尺寸", `${p.width}×${p.height}`],
            ["种子", data.seed],
            ["步数", p.num_inference_steps],
            ["CFG", p.guidance_scale],
            ["耗时", "-"],
            ["采样器", p.scheduler || "-"],
            ["SD模型", p.sd_model ? `<span class="badge badge-info">${p.sd_model}</span>` : "默认"],
            ["LoRA", p.lora_model ? `<span class="badge badge-accent">${p.lora_model}</span>` : "无"],
        ];

        $("gen-meta-grid").innerHTML = items.map(([l, v]) =>
            `<div class="meta-item"><span class="meta-label">${l}</span><span class="meta-value">${v}</span></div>`
        ).join("");
    }

    window.downloadAvatar = function () {
        if (!lastAvatarData) return;
        downloadBase64(lastAvatarData.image_base64, `avatar_${lastAvatarData.seed}.png`);
    };

    window.downloadGenImage = function () {
        if (!lastGenData) return;
        downloadBase64(lastGenData.image_base64, `image_${lastGenData.seed}.png`);
    };

    function downloadBase64(b64, filename) {
        const a = document.createElement("a");
        a.href = "data:image/png;base64," + b64;
        a.download = filename;
        a.click();
    }

    window.reuseAvatarSeed = function () {
        if (!lastAvatarData) return;
        $("avatar-seed").value = lastAvatarData.seed;
        toast(`种子已设为 ${lastAvatarData.seed}`, "info");
    };

    async function loadHistory() {
        const userId = $("history-user")?.value.trim() || null;
        try {
            const data = await API.getHistory(userId, historyLimit, historyOffset);
            renderHistory(data);
        } catch (e) {
            toast("加载历史失败: " + e.message, "error");
        }
    }

    function renderHistory(data) {
        const body = $("history-body");
        const empty = $("history-empty");
        const pagination = $("history-pagination");

        if (data.records.length === 0) {
            body.innerHTML = "";
            empty.style.display = "";
            pagination.innerHTML = "";
            return;
        }
        empty.style.display = "none";

        body.innerHTML = data.records.map(r => `
            <tr>
                <td>${r.id}</td>
                <td>${formatTime(r.timestamp)}</td>
                <td>${r.user_id}</td>
                <td><span class="badge badge-accent">${r.style}</span></td>
                <td>${r.resolution}</td>
                <td>${r.generation_time}s</td>
                <td>${r.seed}</td>
            </tr>`).join("");

        const hasPrev = historyOffset > 0;
        const hasNext = data.has_more;
        pagination.innerHTML = `
            <button ${hasPrev ? "" : "disabled"} onclick="window.__histPrev()">上一页</button>
            <span class="page-info">共 ${data.total} 条</span>
            <button ${hasNext ? "" : "disabled"} onclick="window.__histNext()">下一页</button>`;
    }

    window.__histPrev = () => { historyOffset = Math.max(0, historyOffset - historyLimit); loadHistory(); };
    window.__histNext = () => { historyOffset += historyLimit; loadHistory(); };

    window.loadHistory = loadHistory;

    window.clearHistory = async function () {
        if (!confirm("确定要清除所有历史记录吗？")) return;
        try {
            const data = await API.clearHistory();
            toast(data.message || `已清除 ${data.cleared_count} 条记录`, "success");
            historyOffset = 0;
            loadHistory();
        } catch (e) {
            toast("清除失败: " + e.message, "error");
        }
    };

    async function loadModelsPage() {
        try {
            const [sdData, loraData] = await Promise.all([API.getSdModels(), API.getLoraModels()]);
            renderModelList("sd-models-list", sdData.models, "SD");
            renderModelList("lora-models-list", loraData.models, "LoRA");
        } catch (e) {
            toast("加载模型失败: " + e.message, "error");
        }
    }

    function renderModelList(containerId, models, type) {
        const container = $(containerId);
        if (models.length === 0) {
            container.innerHTML = `<div class="empty-state"><p>暂无${type}模型</p></div>`;
            return;
        }
        container.innerHTML = models.map(m => `
            <div class="model-item">
                <div>
                    <div class="model-name">${m.name} ${m.is_default ? '<span class="badge badge-success">默认</span>' : ""}</div>
                    <div class="model-path">${m.path}</div>
                </div>
            </div>`).join("");
    }

    window.refreshModels = async function () {
        try {
            const data = await API.refreshModels();
            toast("模型列表已刷新", "success");
            loadModelsPage();
            loadSdModels("avatar-sd-model");
            loadSdModels("gen-sd-model");
            loadLoraModels("avatar-lora-model");
            loadLoraModels("gen-lora-model");
        } catch (e) {
            toast("刷新失败: " + e.message, "error");
        }
    };

    async function loadSystemPage() {
        try {
            const [cacheData, configData, healthData] = await Promise.all([
                API.getCacheStats().catch(() => null),
                API.getSystemConfig().catch(() => null),
                API.health().catch(() => null),
            ]);

            if (cacheData) {
                const cachePct = cacheData.cache_max_size > 0 ? (cacheData.cache_size / cacheData.cache_max_size * 100) : 0;
                $("cache-stats").innerHTML = `
                    <div class="stat-item"><div class="stat-value">${cacheData.cache_size}</div><div class="stat-label">缓存条目</div></div>
                    <div class="stat-item"><div class="stat-value">${cacheData.cache_max_size}</div><div class="stat-label">最大容量</div></div>
                    <div class="stat-item"><div class="stat-value">${cacheData.history_size}</div><div class="stat-label">历史记录</div></div>
                    <div class="stat-item"><div class="stat-value">${cacheData.history_max_size}</div><div class="stat-label">历史上限</div></div>
                    <div style="grid-column:1/-1"><div class="cache-bar"><div class="cache-bar-fill" style="width:${cachePct}%"></div></div></div>`;
            }

            if (configData) {
                const g = configData.generation_defaults || {};
                $("system-config").innerHTML = `
                    <div class="config-item"><span class="config-key">默认宽度</span><span class="config-val">${g.width || "-"}</span></div>
                    <div class="config-item"><span class="config-key">默认高度</span><span class="config-val">${g.height || "-"}</span></div>
                    <div class="config-item"><span class="config-key">默认步数</span><span class="config-val">${g.num_inference_steps || "-"}</span></div>
                    <div class="config-item"><span class="config-key">默认CFG</span><span class="config-val">${g.guidance_scale || "-"}</span></div>
                    <div class="config-item"><span class="config-key">默认采样器</span><span class="config-val">${g.scheduler || "-"}</span></div>
                    <div class="config-item"><span class="config-key">本地暂存</span><span class="config-val">${configData.storage_enabled ? "启用" : "禁用"}</span></div>
                    <div class="config-item"><span class="config-key">暂存路径</span><span class="config-val">${configData.storage_path || "-"}</span></div>
                    <div class="config-item"><span class="config-key">SD模型目录</span><span class="config-val">${configData.sd_models_path || "-"}</span></div>
                    <div class="config-item"><span class="config-key">LoRA模型目录</span><span class="config-val">${configData.lora_models_path || "-"}</span></div>`;
            }

            if (healthData) {
                $("service-status").innerHTML = `
                    <div class="status-row"><span>服务状态</span><span class="badge badge-success">在线</span></div>
                    <div class="status-row"><span>版本</span><span>v${healthData.version || "2.0.0"}</span></div>`;
            } else {
                $("service-status").innerHTML = `<div class="status-row"><span>服务状态</span><span class="badge badge-warning" style="background:rgba(248,113,113,0.15);color:var(--danger)">离线</span></div>`;
            }
        } catch (e) {
            console.error("加载系统信息失败:", e);
        }
    }

    window.clearCache = async function () {
        if (!confirm("确定要清除所有缓存吗？")) return;
        try {
            const data = await API.clearCache();
            toast(data.message || `已清除 ${data.cleared_count} 条缓存`, "success");
            loadSystemPage();
        } catch (e) {
            toast("清除失败: " + e.message, "error");
        }
    };

    function formatTime(ts) {
        if (!ts) return "-";
        try {
            const d = new Date(ts);
            return d.toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" });
        } catch {
            return ts;
        }
    }

    init();
})();
