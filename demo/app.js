const API_BASE = window.location.origin;

let selectedStyle = "japanese";
let selectedFeatures = {};

async function init() {
    await Promise.all([
        loadStyles(),
        loadFeatures(),
        loadResolutions(),
        loadSdModels(),
        loadLoraModels(),
    ]);
    bindEvents();
}

function bindEvents() {
    document.getElementById("lora-weight").addEventListener("input", function () {
        document.getElementById("lora-weight-val").textContent = this.value;
    });
}

async function loadStyles() {
    try {
        const resp = await fetch(`${API_BASE}/api/v1/avatar/styles`);
        const data = await resp.json();
        const container = document.getElementById("style-options");
        container.innerHTML = "";
        for (const style of data.styles) {
            const card = document.createElement("div");
            card.className = "style-card" + (style.id === selectedStyle ? " active" : "");
            card.innerHTML = `<div class="style-name">${style.name}</div><div class="style-desc">${style.description}</div>`;
            card.addEventListener("click", () => {
                container.querySelectorAll(".style-card").forEach(c => c.classList.remove("active"));
                card.classList.add("active");
                selectedStyle = style.id;
            });
            container.appendChild(card);
        }
    } catch (e) {
        console.error("加载风格列表失败:", e);
    }
}

async function loadFeatures() {
    try {
        const resp = await fetch(`${API_BASE}/api/v1/avatar/features`);
        const data = await resp.json();
        const container = document.getElementById("feature-options");
        container.innerHTML = "";
        const featureLabels = {
            hair_style: "发型",
            hair_color: "发色",
            eye_color: "眼色",
            clothing_style: "服装",
            expression: "表情",
        };
        for (const [key, options] of Object.entries(data.features)) {
            selectedFeatures[key] = "";
            const row = document.createElement("div");
            row.className = "feature-row";
            const label = document.createElement("label");
            label.textContent = featureLabels[key] || key;
            const select = document.createElement("select");
            const defaultOpt = document.createElement("option");
            defaultOpt.value = "";
            defaultOpt.textContent = "不指定";
            select.appendChild(defaultOpt);
            for (const opt of options) {
                const option = document.createElement("option");
                option.value = opt.value;
                option.textContent = opt.label;
                select.appendChild(option);
            }
            select.addEventListener("change", () => {
                selectedFeatures[key] = select.value;
            });
            row.appendChild(label);
            row.appendChild(select);
            container.appendChild(row);
        }
    } catch (e) {
        console.error("加载角色特征失败:", e);
    }
}

async function loadResolutions() {
    try {
        const resp = await fetch(`${API_BASE}/api/v1/avatar/resolutions`);
        const data = await resp.json();
        const select = document.getElementById("resolution");
        select.innerHTML = "";
        for (const preset of data.presets) {
            const option = document.createElement("option");
            option.value = preset.id;
            option.textContent = `${preset.label} (${preset.width}x${preset.height})`;
            if (preset.id === "medium") option.selected = true;
            select.appendChild(option);
        }
    } catch (e) {
        console.error("加载分辨率预设失败:", e);
    }
}

async function loadSdModels() {
    try {
        const resp = await fetch(`${API_BASE}/api/v1/models/sd`);
        const data = await resp.json();
        const select = document.getElementById("sd-model");
        select.innerHTML = '<option value="">默认模型</option>';
        for (const m of data.models) {
            const option = document.createElement("option");
            option.value = m.name;
            option.textContent = m.name + (m.is_default ? " (默认)" : "");
            select.appendChild(option);
        }
    } catch (e) {
        console.error("加载SD模型列表失败:", e);
    }
}

async function loadLoraModels() {
    try {
        const resp = await fetch(`${API_BASE}/api/v1/models/lora`);
        const data = await resp.json();
        const select = document.getElementById("lora-model");
        select.innerHTML = '<option value="">不使用LoRA</option>';
        for (const m of data.models) {
            const option = document.createElement("option");
            option.value = m.name;
            option.textContent = m.name + (m.is_default ? " (默认)" : "");
            select.appendChild(option);
        }
    } catch (e) {
        console.error("加载LoRA模型列表失败:", e);
    }
}

async function generateAvatar() {
    const description = document.getElementById("description").value.trim();
    if (!description) {
        showError("请输入角色描述");
        return;
    }

    const btn = document.getElementById("generate-btn");
    btn.disabled = true;
    showLoading();

    const characterFeatures = {};
    for (const [key, value] of Object.entries(selectedFeatures)) {
        if (value) characterFeatures[key] = value;
    }

    const payload = {
        description: description,
        style: selectedStyle,
        resolution: document.getElementById("resolution").value,
        quality_mode: document.getElementById("quality-mode").value,
        seed: parseInt(document.getElementById("seed").value) || -1,
        user_id: document.getElementById("user-id").value || "demo_user",
        lora_weight: parseFloat(document.getElementById("lora-weight").value),
    };

    const sdModel = document.getElementById("sd-model").value;
    const loraModel = document.getElementById("lora-model").value;
    if (sdModel) payload.model = sdModel;
    if (loraModel) payload.lora = loraModel;

    if (Object.keys(characterFeatures).length > 0) {
        payload.character_features = characterFeatures;
    }

    try {
        const resp = await fetch(`${API_BASE}/api/v1/avatar/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await resp.json();

        if (resp.ok && data.success) {
            showResult(data);
        } else {
            showError(data.detail || data.message || "生成失败");
        }
    } catch (e) {
        showError("请求失败: " + e.message);
    } finally {
        btn.disabled = false;
    }
}

function showLoading() {
    document.getElementById("placeholder").style.display = "none";
    document.getElementById("loading").style.display = "block";
    document.getElementById("result").style.display = "none";
    document.getElementById("error").style.display = "none";
}

function showResult(data) {
    document.getElementById("placeholder").style.display = "none";
    document.getElementById("loading").style.display = "none";
    document.getElementById("result").style.display = "block";
    document.getElementById("error").style.display = "none";

    const img = document.getElementById("result-image");
    img.src = "data:image/png;base64," + data.image_base64;

    const params = data.parameters || {};
    const info = document.getElementById("result-info");
    const items = [
        { label: "风格", value: data.style_used },
        { label: "分辨率", value: `${data.resolution.width}x${data.resolution.height}` },
        { label: "种子", value: data.seed },
        { label: "耗时", value: `${data.generation_time}秒` },
        { label: "缓存", value: data.cached ? '<span class="badge badge-cached">命中</span>' : "否" },
        { label: "SD模型", value: params.sd_model ? `<span class="badge badge-model">${params.sd_model}</span>` : "默认" },
        { label: "LoRA", value: params.lora_model ? `<span class="badge badge-lora">${params.lora_model} (${params.lora_weight})</span>` : "无" },
    ];

    info.innerHTML = items.map(item =>
        `<div class="info-item"><span class="info-label">${item.label}</span><span class="info-value">${item.value}</span></div>`
    ).join("");
}

function showError(msg) {
    document.getElementById("placeholder").style.display = "none";
    document.getElementById("loading").style.display = "none";
    document.getElementById("result").style.display = "none";
    const err = document.getElementById("error");
    err.style.display = "block";
    err.textContent = "❌ " + msg;
}

init();
