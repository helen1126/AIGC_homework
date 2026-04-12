// 后端服务基础URL
const API_BASE_URL = 'http://localhost:8000';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化模型列表
    loadSDModels();
    loadLoRAModels();
    
    // 绑定表单提交事件
    document.getElementById('text2imgForm').addEventListener('submit', handleText2ImgSubmit);
    document.getElementById('text2imgSimpleForm').addEventListener('submit', handleText2ImgSimpleSubmit);
    
    // 绑定模型管理事件
    document.getElementById('refresh-sd-models').addEventListener('click', loadSDModels);
    document.getElementById('refresh-lora-models').addEventListener('click', loadLoRAModels);
    document.getElementById('get-config').addEventListener('click', getConfig);
    document.getElementById('refresh-all-models').addEventListener('click', refreshAllModels);
    
    // 绑定健康检查事件
    document.getElementById('check-health').addEventListener('click', checkHealth);
});

// 加载SD基础模型列表
function loadSDModels() {
    fetch(`${API_BASE_URL}/api/v1/models/sd`)
        .then(response => response.json())
        .then(data => {
            // 更新SD模型选择器
            const selectElement = document.getElementById('sd_model');
            const simpleSelectElement = document.getElementById('simple_sd_model');
            selectElement.innerHTML = '';
            simpleSelectElement.innerHTML = '';
            
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.name;
                option.textContent = model.name + (model.is_default ? ' (默认)' : '');
                selectElement.appendChild(option);
                
                const simpleOption = document.createElement('option');
                simpleOption.value = model.name;
                simpleOption.textContent = model.name + (model.is_default ? ' (默认)' : '');
                simpleSelectElement.appendChild(simpleOption);
            });
            
            // 更新SD模型列表显示
            const modelsList = document.getElementById('sd-models-list');
            modelsList.innerHTML = '';
            data.models.forEach(model => {
                const modelItem = document.createElement('div');
                modelItem.className = 'mb-2 p-2 border rounded';
                modelItem.innerHTML = `
                    <strong>${model.name}</strong>${model.is_default ? ' (默认)' : ''}
                    <br>
                    <small class="text-muted">路径: ${model.path}</small>
                `;
                modelsList.appendChild(modelItem);
            });
            
            modelsList.innerHTML += `<p class="mt-2 text-muted">共 ${data.total} 个模型</p>`;
        })
        .catch(error => {
            console.error('加载SD模型失败:', error);
            showError('加载SD模型失败，请检查服务是否运行');
        });
}

// 加载LoRA模型列表
function loadLoRAModels() {
    fetch(`${API_BASE_URL}/api/v1/models/lora`)
        .then(response => response.json())
        .then(data => {
            // 更新LoRA模型选择器
            const selectElement = document.getElementById('lora_model');
            const simpleSelectElement = document.getElementById('simple_lora_model');
            selectElement.innerHTML = '';
            simpleSelectElement.innerHTML = '';
            
            // 添加空选项
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = '无';
            selectElement.appendChild(emptyOption);
            
            const simpleEmptyOption = document.createElement('option');
            simpleEmptyOption.value = '';
            simpleEmptyOption.textContent = '无';
            simpleSelectElement.appendChild(simpleEmptyOption);
            
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.name;
                option.textContent = model.name + (model.is_default ? ' (默认)' : '');
                selectElement.appendChild(option);
                
                const simpleOption = document.createElement('option');
                simpleOption.value = model.name;
                simpleOption.textContent = model.name + (model.is_default ? ' (默认)' : '');
                simpleSelectElement.appendChild(simpleOption);
            });
            
            // 更新LoRA模型列表显示
            const modelsList = document.getElementById('lora-models-list');
            modelsList.innerHTML = '';
            data.models.forEach(model => {
                const modelItem = document.createElement('div');
                modelItem.className = 'mb-2 p-2 border rounded';
                modelItem.innerHTML = `
                    <strong>${model.name}</strong>${model.is_default ? ' (默认)' : ''}
                    <br>
                    <small class="text-muted">路径: ${model.path}</small>
                `;
                modelsList.appendChild(modelItem);
            });
            
            modelsList.innerHTML += `<p class="mt-2 text-muted">共 ${data.total} 个模型</p>`;
        })
        .catch(error => {
            console.error('加载LoRA模型失败:', error);
            showError('加载LoRA模型失败，请检查服务是否运行');
        });
}

// 处理完整参数文本生成图片
function handleText2ImgSubmit(event) {
    event.preventDefault();
    
    const formData = {
        prompt: document.getElementById('prompt').value,
        negative_prompt: document.getElementById('negative_prompt').value,
        width: parseInt(document.getElementById('width').value),
        height: parseInt(document.getElementById('height').value),
        num_inference_steps: parseInt(document.getElementById('num_inference_steps').value),
        guidance_scale: parseFloat(document.getElementById('guidance_scale').value),
        seed: parseInt(document.getElementById('seed').value),
        sd_model: document.getElementById('sd_model').value,
        lora_model: document.getElementById('lora_model').value || null,
        lora_weight: parseFloat(document.getElementById('lora_weight').value),
        scheduler: document.getElementById('scheduler').value
    };
    
    // 移除lora_model为null的情况
    if (!formData.lora_model) {
        delete formData.lora_model;
    }
    
    generateImage(`${API_BASE_URL}/api/v1/generation/text2img`, formData);
}

// 处理简单模式文本生成图片
function handleText2ImgSimpleSubmit(event) {
    event.preventDefault();
    
    const prompt = document.getElementById('simple_prompt').value;
    const negative_prompt = document.getElementById('simple_negative_prompt').value;
    const sd_model = document.getElementById('simple_sd_model').value;
    const lora_model = document.getElementById('simple_lora_model').value;
    
    let url = `${API_BASE_URL}/api/v1/generation/text2img/simple?prompt=${encodeURIComponent(prompt)}`;
    
    if (negative_prompt) {
        url += `&negative_prompt=${encodeURIComponent(negative_prompt)}`;
    }
    
    if (sd_model) {
        url += `&sd_model=${encodeURIComponent(sd_model)}`;
    }
    
    if (lora_model) {
        url += `&lora_model=${encodeURIComponent(lora_model)}`;
    }
    
    generateImage(url, null, 'GET');
}

// 生成图片通用函数
function generateImage(url, data, method = 'POST') {
    // 显示加载状态
    const resultMessage = document.getElementById('result-message');
    resultMessage.innerHTML = '生成中... <div class="loading"></div>';
    
    // 隐藏之前的结果和错误
    document.getElementById('result-image').style.display = 'none';
    document.getElementById('result-info').style.display = 'none';
    document.getElementById('error-message').style.display = 'none';
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && method === 'POST') {
        options.body = JSON.stringify(data);
    }
    
    fetch(url, options)
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw errorData;
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // 显示结果
                const resultImage = document.getElementById('result-image');
                resultImage.src = `data:image/png;base64,${data.image_base64}`;
                resultImage.style.display = 'block';
                
                const resultInfo = document.getElementById('result-info');
                const resultParams = document.getElementById('result-params');
                resultParams.textContent = JSON.stringify(data.parameters, null, 2);
                resultInfo.style.display = 'block';
                
                resultMessage.textContent = '生成成功！';
            } else {
                showError(data.message || '生成失败');
            }
        })
        .catch(error => {
            console.error('生成图片失败:', error);
            showError(error.message || '生成图片失败，请检查服务是否运行');
        });
}

// 获取系统配置
function getConfig() {
    fetch(`${API_BASE_URL}/api/v1/models/config`)
        .then(response => response.json())
        .then(data => {
            const configInfo = document.getElementById('config-info');
            configInfo.innerHTML = `
                <div class="p-3 border rounded">
                    <h5>生成默认参数</h5>
                    <pre>${JSON.stringify(data.generation_defaults, null, 2)}</pre>
                    <h5 class="mt-3">存储设置</h5>
                    <p>存储启用: ${data.storage_enabled ? '是' : '否'}</p>
                    <p>存储路径: ${data.storage_path}</p>
                    <h5 class="mt-3">模型路径</h5>
                    <p>SD模型路径: ${data.sd_models_path}</p>
                    <p>LoRA模型路径: ${data.lora_models_path}</p>
                </div>
            `;
        })
        .catch(error => {
            console.error('获取配置失败:', error);
            const configInfo = document.getElementById('config-info');
            configInfo.innerHTML = `<div class="error-message">获取配置失败，请检查服务是否运行</div>`;
        });
}

// 刷新所有模型
function refreshAllModels() {
    const refreshMessage = document.getElementById('refresh-message');
    refreshMessage.innerHTML = '刷新中... <div class="loading"></div>';
    
    fetch(`${API_BASE_URL}/api/v1/models/refresh`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                refreshMessage.innerHTML = `<div class="success-message">${data.message}</div>`;
                // 重新加载模型列表
                loadSDModels();
                loadLoRAModels();
            } else {
                refreshMessage.innerHTML = `<div class="error-message">${data.message}</div>`;
            }
        })
        .catch(error => {
            console.error('刷新模型失败:', error);
            refreshMessage.innerHTML = `<div class="error-message">刷新模型失败，请检查服务是否运行</div>`;
        });
}

// 检查健康状态
function checkHealth() {
    const healthStatus = document.getElementById('health-status');
    healthStatus.innerHTML = '检查中... <div class="loading"></div>';
    
    fetch(`${API_BASE_URL}/health`)
        .then(response => response.json())
        .then(data => {
            healthStatus.innerHTML = `
                <div class="p-3 border rounded bg-success text-white">
                    <h5>服务状态: ${data.status}</h5>
                    <p>版本: ${data.version}</p>
                </div>
            `;
        })
        .catch(error => {
            console.error('健康检查失败:', error);
            healthStatus.innerHTML = `
                <div class="p-3 border rounded bg-danger text-white">
                    <h5>服务状态: 异常</h5>
                    <p>无法连接到服务，请检查服务是否运行</p>
                </div>
            `;
        });
}

// 显示错误信息
function showError(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    const resultMessage = document.getElementById('result-message');
    resultMessage.textContent = '生成失败';
}
