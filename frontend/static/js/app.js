/**
 * 旅游攻略智能体 - 前端交互逻辑
 */

const API_BASE = '/api';

// ============ DOM元素 ============
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const clearChatBtn = document.getElementById('clearChat');
const guidesList = document.getElementById('guidesList');
const addGuideForm = document.getElementById('addGuideForm');
const guideModal = document.getElementById('guideModal');
const guideDetail = document.getElementById('guideDetail');

// ============ 初始化 ============
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initChat();
    loadGuides();
    loadWelcome();
});

// ============ 导航 ============
function initNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const panel = btn.dataset.panel;
            
            // 更新按钮状态
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 切换面板
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.getElementById(panel + 'Panel').classList.add('active');
            
            // 刷新攻略列表
            if (panel === 'guides') {
                loadGuides();
            }
        });
    });
}

// ============ 聊天功能 ============
function initChat() {
    // 发送按钮
    sendBtn.addEventListener('click', sendMessage);
    
    // 回车发送
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 自动调整输入框高度
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });
    
    // 快捷按钮
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            chatInput.value = btn.dataset.msg;
            sendMessage();
        });
    });
    
    // 清空对话
    clearChatBtn.addEventListener('click', async () => {
        await fetch(API_BASE + '/clear', { method: 'POST' });
        chatMessages.innerHTML = '';
        loadWelcome();
        showToast('对话已清空', 'info');
    });
}

async function loadWelcome() {
    try {
        const res = await fetch(API_BASE + '/welcome');
        const data = await res.json();
        addMessage('system', data.message);
    } catch (e) {
        addMessage('system', '👋 你好！我是旅智，你的旅游攻略智能助手！');
    }
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // 显示用户消息
    addMessage('user', message);
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // 显示加载状态
    const loadingEl = addLoading();
    sendBtn.disabled = true;
    
    try {
        const res = await fetch(API_BASE + '/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });
        
        const data = await res.json();
        
        // 移除加载状态
        loadingEl.remove();
        
        if (data.success) {
            addMessage('assistant', data.response, data.tool_calls);
        } else {
            addMessage('assistant', '❌ ' + data.response);
        }
        
    } catch (e) {
        loadingEl.remove();
        addMessage('assistant', '❌ 网络错误，请检查服务是否正常运行。');
    }
    
    sendBtn.disabled = false;
    chatInput.focus();
}

function addMessage(role, content, toolCalls = null) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    
    // 处理换行
    let html = content.replace(/\n/g, '<br>');
    
    // 显示工具调用信息
    if (toolCalls && toolCalls.length > 0) {
        html += '<div class="tool-info">🔧 调用了工具: ' + 
            toolCalls.map(t => t.tool).join(', ') + '</div>';
    }
    
    div.innerHTML = html;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addLoading() {
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

// ============ 攻略列表 ============
async function loadGuides() {
    try {
        const res = await fetch(API_BASE + '/guides');
        const data = await res.json();
        
        if (data.success && data.guides.length > 0) {
            guidesList.innerHTML = data.guides.map(g => `
                <div class="guide-card" data-id="${g.id}">
                    <div class="guide-card-header">
                        <h3>${g.title}</h3>
                        <span class="badge">${g.days}天</span>
                    </div>
                    <div class="info">📍 ${g.destination} | 💰 ${g.budget} | 🌤️ ${g.season}</div>
                    <div class="tags">
                        ${g.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                    </div>
                </div>
            `).join('');
            
            // 绑定点击事件
            document.querySelectorAll('.guide-card').forEach(card => {
                card.addEventListener('click', () => {
                    showGuideDetail(parseInt(card.dataset.id));
                });
            });
        } else {
            guidesList.innerHTML = '<p style="padding:40px;text-align:center;color:var(--text-light)">暂无攻略数据</p>';
        }
    } catch (e) {
        guidesList.innerHTML = '<p style="padding:40px;text-align:center;color:var(--danger)">加载失败，请刷新重试</p>';
    }
}

async function showGuideDetail(id) {
    try {
        const res = await fetch(API_BASE + `/guides/${id}`);
        const data = await res.json();
        
        if (data.success) {
            const g = data.guide;
            guideDetail.innerHTML = `
                <h2>🗺️ ${g.title}</h2>
                <div class="meta">
                    <span class="meta-item">📍 ${g.destination}</span>
                    <span class="meta-item">📅 ${g.days}天</span>
                    <span class="meta-item">💰 ${g.budget}</span>
                    <span class="meta-item">🌤️ ${g.season}</span>
                </div>
                <div class="summary">${g.summary}</div>
                <h3 style="margin-bottom:12px">📅 每日行程</h3>
                ${g.itinerary.map(day => `
                    <div class="day-item">
                        <div class="day-title">Day ${day.day}: ${day.title}</div>
                        <div class="day-details">${day.details}</div>
                        ${day.food ? `<div class="day-food">🍜 ${day.food}</div>` : ''}
                        ${day.tips ? `<div class="day-tips">💡 ${day.tips}</div>` : ''}
                    </div>
                `).join('')}
                ${g.transport ? `<p style="margin-top:16px"><strong>🚗 交通:</strong> ${g.transport}</p>` : ''}
                ${g.accommodation ? `<p><strong>🏨 住宿:</strong> ${g.accommodation}</p>` : ''}
                ${g.estimated_cost ? `<p><strong>💵 费用:</strong> ${g.estimated_cost}</p>` : ''}
            `;
            guideModal.classList.add('active');
        }
    } catch (e) {
        showToast('加载攻略详情失败', 'error');
    }
}

// 弹窗关闭
document.querySelector('.modal-close').addEventListener('click', () => {
    guideModal.classList.remove('active');
});

guideModal.addEventListener('click', (e) => {
    if (e.target === guideModal) {
        guideModal.classList.remove('active');
    }
});

// ============ 添加攻略 ============
addGuideForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(addGuideForm);
    const data = {
        destination: formData.get('destination'),
        title: formData.get('title'),
        days: parseInt(formData.get('days')),
        budget: formData.get('budget'),
        season: formData.get('season'),
        tags: formData.get('tags') ? formData.get('tags').split(',').map(t => t.trim()) : [],
        summary: formData.get('summary'),
        transport: formData.get('transport'),
        accommodation: formData.get('accommodation'),
        estimated_cost: formData.get('estimated_cost'),
        itinerary: [],
    };
    
    try {
        const res = await fetch(API_BASE + '/guides', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        
        const result = await res.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            addGuideForm.reset();
        } else {
            showToast(result.message, 'error');
        }
    } catch (e) {
        showToast('提交失败，请检查网络', 'error');
    }
});

// ============ Toast通知 ============
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============ 键盘快捷键 ============
document.addEventListener('keydown', (e) => {
    // ESC关闭弹窗
    if (e.key === 'Escape') {
        guideModal.classList.remove('active');
    }
});
