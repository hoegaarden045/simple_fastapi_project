const API_BASE = '../api/v1';
let currentUser = null;
let wallets = [];
let operations = [];

function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

function showToast(title, message, isError = false) {
    const toastEl = document.getElementById('toastNotification');
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');
    const toastHeader = toastEl.querySelector('.toast-header');
    
    toastTitle.textContent = title;
    toastBody.textContent = message;
    
    if (isError) {
        toastHeader.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
    } else {
        toastHeader.style.background = 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
    }
    toastHeader.style.color = 'white';
    
    const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 3000 });
    toast.show();
}

function showError(message) { showToast('❌ Ошибка', message, true); }
function showSuccess(message) { showToast('✅ Успешно', message, false); }

function closeModal(modalId) {
    const modalEl = document.getElementById(modalId);
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
}

async function register() {
    const loginValue = document.getElementById('username').value.trim();
    const passwordValue = document.getElementById('password').value;

    if (!loginValue || !passwordValue) {
        showError('Введите логин и пароль');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login: loginValue, password: passwordValue })
        });

        if (response.ok) {
            showSuccess('Регистрация успешна! Теперь войдите.');
        } else {
            const error = await response.json();
            
            if (error.detail && Array.isArray(error.detail)) {
                const cleanMsg = error.detail[0].msg.replace('Value error, ', '');
                showError(cleanMsg);
            } else {
                showError(error.detail || 'Ошибка регистрации');
            }
        }
    } catch (e) {
        showError('Не удалось подключиться к серверу');
    }
}

async function login() {
    const loginValue = document.getElementById('username').value.trim();
    const passwordValue = document.getElementById('password').value;

    if (!loginValue || !passwordValue) {
        showError('Введите логин и пароль');
        return;
    }

    try {
        // FastAPI ожидает данные формы для логина
        const formData = new URLSearchParams();
        formData.append('username', loginValue);
        formData.append('password', passwordValue);

        const response = await fetch(`${API_BASE}/users/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            
            // Получаем данные о себе, чтобы убедиться, что вход прошел
            await checkAuth();
        } else {
            showError('Неверный логин или пароль');
        }
    } catch (e) {
        showError('Ошибка сервера');
    }
}

async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const resp = await fetch(`${API_BASE}/users/me`, {
            headers: getAuthHeaders()
        });
        if (resp.ok) {
            const userData = await resp.json();
            currentUser = userData.login;
            showMainSection();
        } else {
            logout();
        }
    } catch (e) {
        logout();
    }
}

function logout() {
    localStorage.removeItem('token');
    currentUser = null;
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('mainSection').style.display = 'none';
}

function showMainSection() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('mainSection').style.display = 'block';
    document.getElementById('currentUser').textContent = currentUser;

    initReportDates();
    loadAllData();
}

async function loadAllData() {
    await loadWallets();
    await loadOperations();
    await updateTotalBalance();
}

async function loadWallets() {
    try {
        const response = await fetch(`${API_BASE}/wallets`, { headers: getAuthHeaders() });
        if (response.ok) {
            const rawWallets = await response.json();
            wallets = rawWallets.map(w => ({
                ...w,
                currency: String(w.currency || '').toLowerCase(),
                balance: Number(w.balance) || 0
            }));
            renderWalletsTable();
            updateWalletSelects();
        }
    } catch (e) { console.error(e); }
}

async function loadOperations() {
    try {
        const response = await fetch(`${API_BASE}/operations`, { headers: getAuthHeaders() });
        if (response.ok) {
            const rawOps = await response.json();
            operations = rawOps.map(op => ({
                ...op,
                currency: String(op.currency || '').toLowerCase(),
                amount: Number(op.amount) || 0
            }));
            renderOperationsTable();
        }
    } catch (e) { console.error(e); }
}

function renderWalletsTable() {
    const tbody = document.getElementById('walletsTable');
    if (wallets.length === 0) { tbody.innerHTML = 'Нет кошельков'; return; }
    const symbols = { 'rub': '₽', 'usd': '$', 'eur': '€' };
    tbody.innerHTML = wallets.map(w => `
        <tr>
            <td>${w.name}</td>
            <td>${w.currency.toUpperCase()}</td>
            <td>${w.balance.toFixed(2)} ${symbols[w.currency] || w.currency}</td>
        </tr>
    `).join('');
}

function renderOperationsTable() {
    const tbody = document.getElementById('transactionsTable');
    if (operations.length === 0) { tbody.innerHTML = 'Нет транзакций'; return; }
    const last10 = operations.slice(-10).reverse();
    tbody.innerHTML = last10.map(t => {
        const wallet = wallets.find(w => w.id === t.wallet_id);
        const date = new Date(t.created_at).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
        return `
            <tr>
                <td>${date}</td>
                <td>${t.type === 'income' ? '➕' : t.type === 'expense' ? '➖' : '🔄'}</td>
                <td>${wallet ? wallet.name : '-'}</td>
                <td>${t.category || '-'}</td>
                <td>${t.amount.toFixed(2)} ${t.currency}</td>
            </tr>
        `;
    }).join('');
}

async function updateTotalBalance() {
    try {
        const response = await fetch(`${API_BASE}/balance`, { headers: getAuthHeaders() });
        if (response.ok) {
            const data = await response.json();
            document.getElementById('totalBalance').innerHTML = `${Number(data.total_balance).toFixed(2)} ₽<br><small>Общий баланс</small>`;
        }
    } catch (e) { console.error(e); }
}

function updateWalletSelects() {
    const selects = ['incomeWallet', 'expenseWallet', 'transferFrom', 'transferTo'];
    selects.forEach(id => {
        const select = document.getElementById(id);
        if (!select) return;
        select.innerHTML = wallets.map(w => `<option value="${w.id}">${w.name} (${w.balance.toFixed(2)})</option>`).join('');
    });
}

async function addWallet() {
    const name = document.getElementById('walletName').value;
    const currency = document.getElementById('walletCurrency').value;
    const balance = parseFloat(document.getElementById('walletBalance').value);
    
    const response = await fetch(`${API_BASE}/wallets`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ name, currency, initial_balance: balance })
    });
    if (response.ok) { closeModal('addWalletModal'); loadAllData(); }
}

async function addIncome() {
    const wallet_id = parseInt(document.getElementById('incomeWallet').value);
    const amount = parseFloat(document.getElementById('incomeAmount').value);
    const wallet = wallets.find(w => w.id === wallet_id);

    const response = await fetch(`${API_BASE}/operations/income`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ wallet_name: wallet.name, amount, description: document.getElementById('incomeDescription').value })
    });
    if (response.ok) { closeModal('addIncomeModal'); loadAllData(); }
}

async function addExpense() {
    const wallet_id = parseInt(document.getElementById('expenseWallet').value);
    const amount = parseFloat(document.getElementById('expenseAmount').value);
    const wallet = wallets.find(w => w.id === wallet_id);

    const response = await fetch(`${API_BASE}/operations/expense`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ 
            wallet_name: wallet.name, 
            amount, 
            category: document.getElementById('expenseCategory').value,
            description: document.getElementById('expenseDescription').value 
        })
    });
    if (response.ok) { closeModal('addExpenseModal'); loadAllData(); }
}

async function transfer() {
    const fromWalletId = parseInt(document.getElementById('transferFrom').value);
    const toWalletId = parseInt(document.getElementById('transferTo').value);
    const amount = parseFloat(document.getElementById('transferAmount').value);

    if (fromWalletId === toWalletId) {
        showError('Нельзя перевести деньги в тот же самый кошелек');
        return; 
    }

    if (!amount || amount <= 0) {
        showError('Введите корректную сумму для перевода');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/operations/transfer`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ 
                from_wallet_id: fromWalletId,
                to_wallet_id: toWalletId,
                amount: amount
            })
        });

        if (response.ok) { 
            showSuccess('Перевод успешно выполнен!');
            closeModal('transferModal'); 
            document.getElementById('transferAmount').value = ''; 
            loadAllData(); 
        } else {
            const error = await response.json();
            if (error.detail && Array.isArray(error.detail)) {
                showError(error.detail[0].msg.replace('Value error, ', ''));
            } else {
                showError(error.detail || 'Ошибка при переводе');
            }
        }
    } catch (e) {
        showError('Ошибка подключения к серверу');
    }
}

function initReportDates() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    
    const fromInput = document.getElementById('reportDateFrom');
    const toInput = document.getElementById('reportDateTo');
    
    if (fromInput && toInput) {
        fromInput.valueAsDate = firstDay;
        toInput.valueAsDate = tomorrow;
    }
}

async function loadReport() {
    const dateFrom = document.getElementById('reportDateFrom').value;
    const dateTo = document.getElementById('reportDateTo').value;

    if (!dateFrom || !dateTo) {
        showError('Выберите период');
        return;
    }

    if (dateFrom > dateTo) {
        showError('Дата начала не может быть позже даты окончания');
        return;
    }

    try {
        const params = new URLSearchParams({
            date_from: `${dateFrom}T00:00:00`,
            date_to: `${dateTo}T23:59:59`
        });

        // Отправляем запрос с нашим токеном авторизации!
        const response = await fetch(`${API_BASE}/operations?${params}`, {
            headers: getAuthHeaders() 
        });

        if (response.ok) {
            const rawOperations = await response.json();
            const tbody = document.getElementById('reportTable');
            
            if (rawOperations.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">Нет операций за выбранный период</td></tr>';
            } else {
                const symbols = { 'rub': '₽', 'usd': '$', 'eur': '€' };
                tbody.innerHTML = rawOperations.reverse().map(t => {
                    const wallet = wallets.find(w => w.id === t.wallet_id);
                    const date = new Date(t.created_at).toLocaleString('ru-RU', {
                        day: '2-digit', month: '2-digit', year: 'numeric',
                        hour: '2-digit', minute: '2-digit'
                    });
                    const currency = String(t.currency || '').toLowerCase();
                    const amount = Number(t.amount) || 0;
                    
                    return `
                        <tr>
                            <td>${date}</td>
                            <td>${t.type === 'income' ? '➕' : t.type === 'expense' ? '➖' : '🔄'}</td>
                            <td>${wallet ? wallet.name : '-'}</td>
                            <td>${t.category || '-'}</td>
                            <td>${amount.toFixed(2)} ${symbols[currency] || currency.toUpperCase()}</td>
                        </tr>
                    `;
                }).join('');
            }

            document.getElementById('reportContent').style.display = 'block';
            showSuccess('Отчет сформирован!');
        } else {
            const error = await response.json();
            showError(error.detail || 'Ошибка загрузки отчета');
        }
    } catch (e) {
        showError('Ошибка подключения к серверу');
    }
}

checkAuth();