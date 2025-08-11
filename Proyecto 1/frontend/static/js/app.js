// Global variables
let authToken = localStorage.getItem('authToken');
const API_BASE_URL = '/api/v1';

// DOM Elements
const loginSection = document.getElementById('loginSection');
const registerSection = document.getElementById('registerSection');
const dashboardSection = document.getElementById('dashboardSection');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const uploadForm = document.getElementById('uploadForm');
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    if (authToken) {
        showDashboard();
        loadSummary();
        loadPerformance();
    } else {
        showLogin();
    }

    // Event listeners
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    uploadForm.addEventListener('submit', handleFileUpload);
    loginBtn.addEventListener('click', showLogin);
    logoutBtn.addEventListener('click', handleLogout);
});

// Authentication functions
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/token`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showAlert('Login exitoso', 'success');
            showDashboard();
            loadSummary();
            loadPerformance();
        } else {
            const error = await response.json();
            showAlert('Error de login: ' + (error.detail || 'Credenciales incorrectas'), 'danger');
        }
    } catch (error) {
        showAlert('Error de conexión: ' + error.message, 'danger');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const fullName = document.getElementById('regFullName').value;
    const password = document.getElementById('regPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                full_name: fullName,
                password
            })
        });

        if (response.ok) {
            showAlert('Usuario registrado exitosamente. Ahora puedes iniciar sesión.', 'success');
            showLogin();
            registerForm.reset();
        } else {
            const error = await response.json();
            showAlert('Error de registro: ' + (error.detail || 'Error desconocido'), 'danger');
        }
    } catch (error) {
        showAlert('Error de conexión: ' + error.message, 'danger');
    }
}

function handleLogout() {
    authToken = null;
    localStorage.removeItem('authToken');
    showLogin();
}

// UI functions
function showLogin() {
    loginSection.classList.remove('d-none');
    registerSection.classList.add('d-none');
    dashboardSection.classList.add('d-none');
    loginBtn.classList.remove('d-none');
    logoutBtn.classList.add('d-none');
}

function showRegister() {
    loginSection.classList.add('d-none');
    registerSection.classList.remove('d-none');
    dashboardSection.classList.add('d-none');
}

function showDashboard() {
    loginSection.classList.add('d-none');
    registerSection.classList.add('d-none');
    dashboardSection.classList.remove('d-none');
    loginBtn.classList.add('d-none');
    logoutBtn.classList.remove('d-none');
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    document.querySelectorAll('.alert').forEach(alert => alert.remove());

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild.nextSibling);

    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// API functions with authentication
async function apiRequest(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        handleLogout();
        showAlert('Sesión expirada. Por favor, inicia sesión nuevamente.', 'warning');
        return null;
    }

    return response;
}

// File upload function
async function handleFileUpload(e) {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const uploadResult = document.getElementById('uploadResult');

    if (!fileInput.files[0]) {
        showAlert('Por favor, selecciona un archivo', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        uploadResult.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div> Subiendo archivo...';

        const response = await fetch(`${API_BASE_URL}/files/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            uploadResult.innerHTML = `
                <div class="alert alert-success">
                    ✅ Archivo procesado exitosamente<br>
                    📊 Registros importados: ${data.records_imported}<br>
                    🆔 Batch ID: ${data.batch_id}
                </div>
            `;
            
            // Refresh data
            loadSummary();
            loadPerformance();
            
            // Reset form
            fileInput.value = '';
        } else {
            const error = await response.json();
            uploadResult.innerHTML = `
                <div class="alert alert-danger">
                    ❌ Error: ${error.detail || 'Error al procesar archivo'}
                </div>
            `;
        }
    } catch (error) {
        uploadResult.innerHTML = `
            <div class="alert alert-danger">
                ❌ Error de conexión: ${error.message}
            </div>
        `;
    }
}

// Load summary data
async function loadSummary() {
    try {
        const response = await apiRequest('/analytics/summary');
        if (response && response.ok) {
            const data = await response.json();
            
            document.getElementById('totalProduced').textContent = data.summary.total_produced || 0;
            document.getElementById('totalSold').textContent = data.summary.total_sold || 0;
            document.getElementById('totalRevenue').textContent = '$' + (data.summary.total_revenue || 0).toFixed(2);
            document.getElementById('activeProducts').textContent = data.summary.active_products || 0;
        }
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

// Load performance data
async function loadPerformance() {
    try {
        const response = await apiRequest('/analytics/performance?limit=10');
        if (response && response.ok) {
            const data = await response.json();
            const tbody = document.getElementById('performanceTable');
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay datos disponibles</td></tr>';
                return;
            }

            tbody.innerHTML = data.map(item => `
                <tr>
                    <td>${item.product_name}</td>
                    <td>${item.category_name || 'Sin Categoría'}</td>
                    <td>${item.total_produced}</td>
                    <td>${item.total_sold}</td>
                    <td>$${item.total_revenue.toFixed(2)}</td>
                    <td>${item.sell_through_rate.toFixed(1)}%</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading performance:', error);
    }
}

// Download reports
async function downloadReport(type) {
    try {
        const endpoints = {
            'performance': '/reports/performance',
            'trends': '/reports/trends',
            'categories': '/reports/categories',
            'complete': '/reports/complete'
        };

        const response = await fetch(`${API_BASE_URL}${endpoints[type]}?format=excel`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `reporte_${type}_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            showAlert(`Reporte de ${type} descargado exitosamente`, 'success');
        } else {
            showAlert('Error al descargar el reporte', 'danger');
        }
    } catch (error) {
        showAlert('Error de conexión: ' + error.message, 'danger');
    }
}

// Utility functions
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('es-ES');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}