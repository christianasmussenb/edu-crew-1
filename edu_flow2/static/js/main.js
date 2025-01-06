document.getElementById('contentForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const form = this;
    const button = form.querySelector('button');
    const result = document.getElementById('result');
    
    // UI States
    button.disabled = true;
    button.querySelector('.normal-state').classList.add('hidden');
    button.querySelector('.loading-state').classList.remove('hidden');
    
    try {
        const response = await fetch('/', {
            method: 'POST',
            body: new FormData(form)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Content generated successfully!', 'success');
            result.innerHTML = `
                <div class="bg-green-50 border-l-4 border-green-500 p-4">
                    <pre class="whitespace-pre-wrap">${JSON.stringify(data.result, null, 2)}</pre>
                </div>
            `;
        } else {
            showNotification('❌ ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('❌ An error occurred', 'error');
    } finally {
        button.disabled = false;
        button.querySelector('.normal-state').classList.remove('hidden');
        button.querySelector('.loading-state').classList.add('hidden');
    }
});

function showNotification(message, type) {
    const notifications = document.getElementById('notifications');
    const notification = document.createElement('div');
    
    notification.className = `
        p-4 rounded-lg shadow-lg text-white transform transition-all duration-500
        ${type === 'success' ? 'bg-green-500' : 'bg-red-500'}
    `;
    
    notification.textContent = message;
    notifications.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
} 