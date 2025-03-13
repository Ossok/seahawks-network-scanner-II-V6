async function startScan() {
    const button = document.getElementById('scan-btn');
    const results = document.getElementById('results-content');
    
    button.disabled = true;
    button.textContent = 'Scanning...';
    
    try {
        const response = await fetch('/api/scan', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        results.innerHTML = `<p class="error">Error during scan: ${error.message}</p>`;
    } finally {
        button.disabled = false;
        button.textContent = 'Start Network Scan';
    }
}

function displayResults(data) {
    const results = document.getElementById('results-content');
    
    if (data.devices.length === 0) {
        results.innerHTML = `<p>No active network interfaces found</p>`;
        return;
    }
    
    let html = `<div class="scan-summary">
        <h3>Network Scan Results</h3>
        <p>App Version: ${data.app_version}</p>`;
    
    data.devices.forEach(device => {
        html += `
        <div class="interface-result">
            <h4>Interface: ${device.interface_name}</h4>
            <p>IP Address: ${device.ip}</p>
            
            <h5>Open Ports:</h5>
            ${device.ports.length > 0 ? `
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Port</th>
                            <th>Service</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${device.ports.map(port => `
                            <tr>
                                <td>${port.port}</td>
                                <td>${port.service}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<p>No open ports found</p>'}
        </div>
        <hr>`;
    });
    
    html += `</div>`;
    results.innerHTML = html;
}

window.addEventListener('load', async () => {
    await loadSystemInfo();
    await loadTargetUrl();
    startTimer(); // Démarrer le minuteur au chargement
});

async function loadSystemInfo() {
    try {
        const response = await fetch('/api/system-info');
        const data = await response.json();
        
        document.getElementById('hostname').textContent = data.hostname;
        
        const interfacesContainer = document.getElementById('interfaces-list');
        
        if (data.network_interfaces.length === 0) {
            interfacesContainer.innerHTML = '<p>No network interfaces found</p>';
            return;
        }
        
        let interfacesHtml = '';
        
        data.network_interfaces.forEach(interface => {
            const statusClass = interface.status === 'up' ? 'status-up' : 'status-down';
            
            interfacesHtml += `
            <div class="interface-card">
                <div class="interface-header">
                    <h4>${interface.name}</h4>
                    <span class="status ${statusClass}">${interface.status}</span>
                </div>
                
                <div class="interface-addresses">
                    ${interface.addresses.map(addr => {
                        if (addr.type === 'IPv4') {
                            return `
                            <div class="address-item">
                                <span class="address-type">${addr.type}:</span>
                                <span class="address-value">${addr.address}</span>
                                <span class="address-cidr">(${addr.cidr})</span>
                            </div>`;
                        } else {
                            return `
                            <div class="address-item">
                                <span class="address-type">${addr.type}:</span>
                                <span class="address-value">${addr.address}</span>
                            </div>`;
                        }
                    }).join('')}
                </div>
            </div>`;
        });
        
        interfacesContainer.innerHTML = interfacesHtml;
    } catch (error) {
        console.error('Error loading system info:', error);
        document.getElementById('interfaces-list').innerHTML = 
            `<p class="error">Error loading network interfaces: ${error.message}</p>`;
    }
}

async function pingServer() {
    const serverIP = document.getElementById('server-ip').value;
    const resultDiv = document.getElementById('ping-result');
    
    if (!serverIP) {
        resultDiv.innerHTML = '<div class="result-error">Please enter an IP</div>';
        return;
    }
    
    try {
        resultDiv.innerHTML = '<div>Test in progress...</div>';
        const response = await fetch(`/api/ping/${serverIP}`);
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="result-success">
                    ✓ ${data.message} (${data.ip})
                    ${data.latency !== null ? `<br>Latency: ${data.latency} ${data.latency_unit}` : ''}
                </div>`;
        } else {
            resultDiv.innerHTML = `
                <div class="result-error">
                    ✗ ${data.message} (${data.ip})
                </div>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-error">
                Test Error : ${error.message}
            </div>`;
    }
}

async function loadTargetUrl() {
    try {
        const response = await fetch('/api/get-target-url');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('current-target-url').textContent = data.target_url || 'Not set';
            document.getElementById('new-target-url').value = data.target_url || '';
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        document.getElementById('current-target-url').textContent = `Error: ${error.message}`;
    }
}

async function setTargetUrl() {
    const targetUrl = document.getElementById('new-target-url').value;
    const resultDiv = document.getElementById('set-target-result');
    
    if (!targetUrl) {
        resultDiv.innerHTML = '<div class="result-error">Please enter a target URL</div>';
        return;
    }
    
    try {
        resultDiv.innerHTML = '<div>Setting target URL...</div>';
        const response = await fetch('/api/set-target-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                target_url: targetUrl
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="result-success">
                    ✓ ${data.message}
                </div>`;
            loadTargetUrl(); // Recharger l'URL cible pour mettre à jour l'affichage
        } else {
            resultDiv.innerHTML = `
                <div class="result-error">
                    ✗ ${data.error}
                </div>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-error">
                Error setting target URL: ${error.message}
            </div>`;
    }
}


async function startTimer() {
    const timerDisplay = document.getElementById('time-remaining');

    if (!timerDisplay) {
        console.error("Timer display element not found!");
        return;
    }

    async function updateTimer() {
        try {
            const response = await fetch('/api/next-send-time');
            const data = await response.json();
            
            if (data.success) {
                let timeRemaining = data.time_remaining;

                const interval = setInterval(() => {
                    if (timeRemaining <= 0) {
                        timerDisplay.textContent = 'Sending now...';
                        clearInterval(interval);
                        setTimeout(updateTimer, 1000); // Relancer après l'envoi
                    } else {
                        const minutes = Math.floor(timeRemaining / 60);
                        const seconds = timeRemaining % 60;
                        timerDisplay.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
                        timeRemaining--;
                    }
                }, 1000);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            timerDisplay.textContent = `Error: ${error.message}`;
        }
    }

    updateTimer(); // Démarrer le minuteur

    // Réinitialiser après un envoi forcé
    window.addEventListener('forceSendComplete', () => {
        updateTimer();
    });
}


// Fonction pour forcer l'envoi des données
async function forceSendData() {
    const resultDiv = document.getElementById('send-result');
    const forceSendBtn = document.getElementById('force-send-btn');
    
    forceSendBtn.disabled = true;
    resultDiv.innerHTML = '<div>Sending data...</div>';

    try {
        const targetUrlResponse = await fetch('/api/get-target-url');
        const targetData = await targetUrlResponse.json();

        if (!targetData.success || !targetData.target_url) {
            throw new Error('Target URL not set');
        }

        const targetUrl = targetData.target_url;

        // Récupérer les données système
        const systemInfoResponse = await fetch('/api/system-info');
        const systemInfoData = await systemInfoResponse.json();

        // Récupérer les données de scan
        const scanResponse = await fetch('/api/scan', { method: 'POST' });
        const scanData = await scanResponse.json();

        // Envoyer les données système
        const responseSystem = await fetch(targetUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(systemInfoData)
        });

        // Envoyer les résultats de scan
        const responseScan = await fetch(targetUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scanData)
        });

        if (responseSystem.ok && responseScan.ok) {
            resultDiv.innerHTML = `
                <div class="result-success">
                    ✓ Data successfully sent to ${targetUrl}
                </div>`;
        } else {
            throw new Error(`Failed to send data. System Info Status: ${responseSystem.status}, Scan Status: ${responseScan.status}`);
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-error">
                Error forcing send: ${error.message}
            </div>`;
    } finally {
        forceSendBtn.disabled = false;
    }
}