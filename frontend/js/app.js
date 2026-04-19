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

    function esc(str) {
        const d = document.createElement("div");
        d.textContent = String(str ?? "");
        return d.innerHTML;
    }

    function toast(msg, type = "info") {
        const container = $("toast-container");
        const el = document.createElement("div");
        el.className = `toast ${type}`;
        el.textContent = msg;
        container.appendChild(el);
        setTimeout(() => {
            el.style.opacity = "0";
            el.style.transition = "opacity 0.3s";
            setTimeout(() => el.remove(), 300);
        }, 3500);
    }

    function showResult(area, state) {
        ["placeholder", "loading", "result", "error"].forEach(id => {
            const el = $(`${area}-${id}`);
            if (el) el.style.display = id === state ? "" : "none";
        });
    }

    function setMetaGrid(gridId, items) {
        const grid = $(gridId);
        grid.innerHTML = "";
        for (const [label, value, isHtml] of items) {
            const item = document.createElement("div");
            item.className = "meta-item";
            const labelSpan = document.createElement("span");
            labelSpan.className = "meta-label";
            labelSpan.textContent = label;
            const valueSpan = document.createElement("span");
            valueSpan.className = "meta-value";
            if (isHtml) {
                valueSpan.innerHTML = value;
            } else {
                valueSpan.textContent = String(value ?? "-");
            }
            item.appendChild(labelSpan);
            item.appendChild(valueSpan);
            grid.appendChild(item);
        }
    }

    async function init() {
        setupNavigation();
        setupMobileMenu();
        setupSliders();
        setupKeyboard();
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
                switchPage(item.dataset.page);
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

    function setupKeyboard() {
        document.addEventListener("keydown", (e) => {
            if (e.ctrlKey && e.key === "Enter") {
                e.preventDefault();
                const activePage = document.querySelector(".page.active");
                if (activePage?.id === "page-avatar") generateAvatar();
                else if (activePage?.id === "page-generation") generateImage();
            }
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
                const nameEl = document.createElement("div");
                nameEl.className = "style-name";
                nameEl.textContent = `${STYLE_ICONS[s.id] || "🎨"} ${s.name}`;
                const descEl = document.createElement("div");
                descEl.className = "style-desc";
                descEl.textContent = s.description;
                card.appendChild(nameEl);
                card.appendChild(descEl);
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
                o.textContent = p.label;
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
        if (!desc) {
            toast("请输入角色描述", "error");
            $("avatar-desc").focus();
            return;
        }

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
        setMetaGrid("avatar-meta-grid", [
            ["风格", data.style_used],
            ["分辨率", `${data.resolution.width}×${data.resolution.height}`],
            ["种子", data.seed],
            ["耗时", `${data.generation_time}s`],
            ["缓存", data.cached ? "命中" : "否", false],
            ["SD模型", params.sd_model || "默认"],
            ["LoRA", params.lora_model || "无"],
            ["LoRA权重", params.lora_model ? params.lora_weight : "-"],
        ]);
    }

    async function generateImage() {
        const promptEl = $("gen-prompt");
        if (!promptEl) {
            toast("页面加载异常，请刷新页面重试", "error");
            console.error("找不到 gen-prompt 元素");
            return;
        }
        const prompt = promptEl.value.trim();
        if (!prompt) {
            toast("请输入正向提示词", "error");
            promptEl.focus();
            return;
        }

        const btn = $("gen-generate-btn");
        btn.disabled = true;
        showResult("gen", "loading");

        const payload = {
            prompt,
            negative_prompt: $("gen-negative")?.value || "",
            width: parseInt($("gen-width")?.value) || 512,
            height: parseInt($("gen-height")?.value) || 512,
            num_inference_steps: parseInt($("gen-steps")?.value) || 20,
            guidance_scale: parseFloat($("gen-cfg")?.value) || 7.5,
            seed: parseInt($("gen-seed")?.value) || -1,
            scheduler: $("gen-scheduler")?.value || "euler",
            lora_weight: parseFloat($("gen-lora-weight")?.value) || 1.0,
        };

        const sdModel = $("gen-sd-model")?.value;
        const loraModel = $("gen-lora-model")?.value;
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
        setMetaGrid("gen-meta-grid", [
            ["尺寸", `${p.width}×${p.height}`],
            ["种子", data.seed],
            ["步数", p.num_inference_steps],
            ["CFG", p.guidance_scale],
            ["采样器", p.scheduler],
            ["SD模型", p.sd_model || "默认"],
            ["LoRA", p.lora_model || "无"],
            ["LoRA权重", p.lora_model ? p.lora_weight : "-"],
        ]);
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

        if (!data.records || data.records.length === 0) {
            body.innerHTML = "";
            empty.style.display = "";
            pagination.innerHTML = "";
            return;
        }
        empty.style.display = "none";

        body.innerHTML = "";
        for (const r of data.records) {
            const tr = document.createElement("tr");
            const fields = [r.id, formatTime(r.timestamp), r.user_id, r.style, r.resolution, `${r.generation_time}s`, r.seed];
            for (const f of fields) {
                const td = document.createElement("td");
                td.textContent = String(f ?? "-");
                tr.appendChild(td);
            }
            body.appendChild(tr);
        }

        const hasPrev = historyOffset > 0;
        const hasNext = data.has_more;
        pagination.innerHTML = "";

        const prevBtn = document.createElement("button");
        prevBtn.textContent = "上一页";
        prevBtn.disabled = !hasPrev;
        prevBtn.addEventListener("click", () => { historyOffset = Math.max(0, historyOffset - historyLimit); loadHistory(); });

        const info = document.createElement("span");
        info.className = "page-info";
        info.textContent = `共 ${data.total} 条`;

        const nextBtn = document.createElement("button");
        nextBtn.textContent = "下一页";
        nextBtn.disabled = !hasNext;
        nextBtn.addEventListener("click", () => { historyOffset += historyLimit; loadHistory(); });

        pagination.appendChild(prevBtn);
        pagination.appendChild(info);
        pagination.appendChild(nextBtn);
    }

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
        container.innerHTML = "";
        if (!models || models.length === 0) {
            const empty = document.createElement("div");
            empty.className = "empty-state";
            empty.textContent = `暂无${type}模型`;
            container.appendChild(empty);
            return;
        }
        for (const m of models) {
            const item = document.createElement("div");
            item.className = "model-item";

            const info = document.createElement("div");
            const nameEl = document.createElement("div");
            nameEl.className = "model-name";
            nameEl.textContent = m.name;
            if (m.is_default) {
                const badge = document.createElement("span");
                badge.className = "badge badge-success";
                badge.textContent = "默认";
                nameEl.appendChild(document.createTextNode(" "));
                nameEl.appendChild(badge);
            }
            const pathEl = document.createElement("div");
            pathEl.className = "model-path";
            pathEl.textContent = m.path || "";
            info.appendChild(nameEl);
            info.appendChild(pathEl);
            item.appendChild(info);
            container.appendChild(item);
        }
    }

    window.refreshModels = async function () {
        try {
            await API.refreshModels();
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
                const statsEl = $("cache-stats");
                statsEl.innerHTML = "";

                const statItems = [
                    [cacheData.cache_size, "缓存条目"],
                    [cacheData.cache_max_size, "最大容量"],
                    [cacheData.history_size, "历史记录"],
                    [cacheData.history_max_size, "历史上限"],
                ];
                for (const [val, label] of statItems) {
                    const item = document.createElement("div");
                    item.className = "stat-item";
                    const valEl = document.createElement("div");
                    valEl.className = "stat-value";
                    valEl.textContent = val;
                    const labelEl = document.createElement("div");
                    labelEl.className = "stat-label";
                    labelEl.textContent = label;
                    item.appendChild(valEl);
                    item.appendChild(labelEl);
                    statsEl.appendChild(item);
                }

                const barWrap = document.createElement("div");
                barWrap.style.gridColumn = "1/-1";
                const bar = document.createElement("div");
                bar.className = "cache-bar";
                const fill = document.createElement("div");
                fill.className = "cache-bar-fill";
                fill.style.width = `${cachePct}%`;
                bar.appendChild(fill);
                barWrap.appendChild(bar);
                statsEl.appendChild(barWrap);
            }

            if (configData) {
                const g = configData.generation_defaults || {};
                const configItems = [
                    ["默认宽度", g.width],
                    ["默认高度", g.height],
                    ["默认步数", g.num_inference_steps],
                    ["默认CFG", g.guidance_scale],
                    ["默认采样器", g.scheduler],
                    ["本地暂存", configData.storage_enabled ? "启用" : "禁用"],
                    ["暂存路径", configData.storage_path],
                    ["SD模型目录", configData.sd_models_path],
                    ["LoRA模型目录", configData.lora_models_path],
                ];
                const configEl = $("system-config");
                configEl.innerHTML = "";
                for (const [key, val] of configItems) {
                    const item = document.createElement("div");
                    item.className = "config-item";
                    const keySpan = document.createElement("span");
                    keySpan.className = "config-key";
                    keySpan.textContent = key;
                    const valSpan = document.createElement("span");
                    valSpan.className = "config-val";
                    valSpan.textContent = String(val ?? "-");
                    item.appendChild(keySpan);
                    item.appendChild(valSpan);
                    configEl.appendChild(item);
                }
            }

            const statusEl = $("service-status");
            statusEl.innerHTML = "";
            const row = document.createElement("div");
            row.className = "status-row";
            const label = document.createElement("span");
            label.textContent = "服务状态";
            const badge = document.createElement("span");
            if (healthData) {
                badge.className = "badge badge-success";
                badge.textContent = "在线";
            } else {
                badge.className = "badge";
                badge.style.background = "rgba(248,113,113,0.15)";
                badge.style.color = "var(--danger)";
                badge.textContent = "离线";
            }
            row.appendChild(label);
            row.appendChild(badge);
            statusEl.appendChild(row);

            if (healthData) {
                const verRow = document.createElement("div");
                verRow.className = "status-row";
                const verLabel = document.createElement("span");
                verLabel.textContent = "版本";
                const verVal = document.createElement("span");
                verVal.textContent = `v${healthData.version || "2.0.0"}`;
                verRow.appendChild(verLabel);
                verRow.appendChild(verVal);
                statusEl.appendChild(verRow);
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
