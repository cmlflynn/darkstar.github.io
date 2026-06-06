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
    }
}

// Render Home View
function renderHome() {
    let html = `
        <div class="model-grid">
            ${modelData.map(model => `
                <div class="model-card">
                    <h2>${model.title}</h2>
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
            <h2>Paper title: ${model.title}</h2>
            <p class="subtitle">${model.subtitle}</p>
            
            <div class="content-wrapper">
                <div class="description-section">
                    <h3>About this Model</h3>
                    <p>${model.summary}</p>
                </div>

                <div class="data-section">
                    <div class="info-pane">
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
                            <a href="${model.code_url}" class="btn" target="_blank">View Python Source Code</a>
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
init();
