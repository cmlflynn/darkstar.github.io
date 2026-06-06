const app = document.getElementById('app');
let modelData = [];

// Fetch the data
async function init() {
    try {
        const response = await fetch('data.json');
        modelData = await response.json();
        router();
    } catch (err) {
        app.innerHTML = `<div class="error">Error loading model data. Please ensure you are viewing this via a web server.</div>`;
        console.error(err);
    }
}

// Router
function router() {
    const hash = window.location.hash || '#/';
    
    if (hash === '#/') {
        renderHome();
    } else if (hash.startsWith('#/model/')) {
        const id = hash.replace('#/model/', '');
        renderDetail(id);
    } else if (hash.startsWith('#/code/')) {
        const id = hash.replace('#/code/', '');
        renderCodeView(id);
    }
}

// Render Home View
function renderHome() {
    let html = `
        <div class="model-grid">
            ${modelData.map(model => `
                <div class="model-card">
                    <h2>${model.paper_url ? `<a href="${model.paper_url}" target="_blank">${model.title}</a>` : model.title}</h2>
                    <p class="subtitle">Paper title: ${model.subtitle}</p>
                    <p>${model.summary}</p>
                    <a href="#/model/${model.id}" class="btn">Explore Model</a>
                </div>
            `).join('')}
        </div>
    `;
    app.innerHTML = html;
}

// Render Detail View
function renderDetail(id) {
    const model = modelData.find(m => m.id === id);
    if (!model) {
        app.innerHTML = `<h2>Model not found</h2><a href="#/">Back to home</a>`;
        return;
    }

    const paramRows = Object.entries(model.parameters)
        .map(([key, val]) => `<tr><th>${key}</th><td>${val}</td></tr>`)
        .join('');

    let html = `
        <div class="model-detail">
            <a href="#/" class="back-link">&larr; Back to all models</a>
            <h2>${model.paper_url ? `<a href="${model.paper_url}" target="_blank">${model.title}</a>` : model.title}</h2>
            <p class="subtitle">Paper title: ${model.subtitle}</p>
            
            <div class="content-wrapper">
                <div class="description-section">
                    <h3>About this Model</h3>
                    <p>${model.summary}</p>
                </div>

                <div class="data-section">
                    <div class="info-pane">
                        ${model.eqn_url ? `
                        <div class="equation-container">
                            <h3>Model Equation</h3>
                            <img src="${model.eqn_url}" alt="Mathematical equation for ${model.title}" class="equation-img">
                        </div>
                        ` : ''}
                        
                        <h3>Model Parameters</h3>
                        <table class="parameters-table">
                            ${paramRows}
                        </table>
                        
                        <div class="luminosity-highlight">
                            <h3>Total Halo Luminosity</h3>
                            <p>Local norm: 1.7E-5 L<sub>&odot;</sub>/pc<sup>3</sup></p>
                            <div class="luminosity-value">${model.luminosity}</div>
                        </div>

                        <div class="code-footer">
                            <a href="#/code/${model.id}" class="btn secondary">View Python Source Code</a>
                            <a href="${model.code_url}" class="btn" download>Download Python Source Code</a>
                        </div>
                    </div>
                    
                    <div class="plot-pane">
                        <h3>Density Profile Plot</h3>
                        <div class="plot-container">
                            <a href="${model.plot_url}" target="_blank" title="Click to view full size">
                                <img src="${model.plot_url}" alt="Density Profile for ${model.title}">
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    app.innerHTML = html;
}

window.addEventListener('hashchange', router);

async function renderCodeView(id) {
    const model = modelData.find(m => m.id === id);
    if (!model) {
        app.innerHTML = `<h2>Model not found</h2><a href="#/">Back to home</a>`;
        return;
    }

    app.innerHTML = `
        <div class="code-page">
            <a href="#/model/${model.id}" class="back-link">&larr; Back to model details</a>
            <h2>Python Source Code: ${model.title}</h2>
            <div class="code-viewer-container">
                <pre><code id="code-content-loading">Loading source code...</code></pre>
            </div>
        </div>
    `;

    try {
        const response = await fetch(model.code_url);
        const code = await response.text();
        document.getElementById('code-content-loading').textContent = code;
    } catch (err) {
        document.getElementById('code-content-loading').textContent = 'Error loading source code.';
    }
}

init();
