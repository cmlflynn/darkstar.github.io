const app = document.getElementById('app');
let modelData = [];

// Fetch the data
async function init() {
    try {
        const response = await fetch('data.json');
        modelData = await response.json();
        // Initial sort by default column without rendering
        performSort(currentSort.col, true);
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

let currentSort = { col: 'title', asc: true };
let luminosityChartInstance = null;

// Render Home View
function renderHome() {
    const getSortClass = (col) => {
        if (currentSort.col !== col) return '';
        return currentSort.asc ? 'sort-asc' : 'sort-desc';
    };

    let html = `
        <div class="model-table-container">
            <table class="model-table">
                <thead>
                    <tr>
                        <th class="${getSortClass('title')}" onclick="sortData('title')">Authors</th>
                        <th class="${getSortClass('model_type')}" onclick="sortData('model_type')">Model Type</th>
                        <th class="${getSortClass('range')}" onclick="sortData('range')">Valid Range</th>
                        <th class="${getSortClass('luminosity')}" onclick="sortData('luminosity')">Luminosity</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${modelData.map(model => `
                        <tr>
                            <td>
                                <a href="${model.paper_url}" target="_blank">${model.title}</a>
                            </td>
                            <td>${model.parameters.Model}</td>
                            <td>${model.range ? `${model.range.min} - ${model.range.max} kpc` : 'N/A'}</td>
                            <td>${model.luminosity}</td>
                            <td>
                                <a href="#/model/${model.id}" class="btn">Explore Model</a>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>

        <div class="chart-section">
            <h3>Luminosity Comparison</h3>
            <div class="chart-container">
                <canvas id="luminosityChart"></canvas>
            </div>
        </div>
    `;
    app.innerHTML = html;
    renderLuminosityChart();
}

function renderLuminosityChart() {
    const canvas = document.getElementById('luminosityChart');
    if (!canvas) return;

    // Ensure Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded yet. Retrying in 100ms...');
        setTimeout(renderLuminosityChart, 100);
        return;
    }

    try {
        const ctx = canvas.getContext('2d');
        if (luminosityChartInstance) {
            luminosityChartInstance.destroy();
        }

        const labels = modelData.map(m => m.title);
        const data = modelData.map(m => {
            const val = parseFloat(m.luminosity.split(' ')[0]);
            return isNaN(val) ? 0 : val;
        });

        luminosityChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Halo Luminosity (L⊙)',
                    data: data,
                    backgroundColor: 'rgba(44, 62, 80, 0.7)',
                    borderColor: 'rgba(44, 62, 80, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Luminosity (L⊙)'
                        }
                    },
                    x: {
                        ticks: {
                            minRotation: 45,
                            maxRotation: 45
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toExponential(2) + ' L⊙';
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    } catch (err) {
        console.error('Error rendering chart:', err);
    }
}

function performSort(col, skipRender = false) {
    if (!skipRender) {
        if (currentSort.col === col) {
            currentSort.asc = !currentSort.asc;
        } else {
            currentSort.col = col;
            currentSort.asc = true;
        }
    }

    modelData.sort((a, b) => {
        let valA, valB;

        if (col === 'title') {
            valA = a.title.toLowerCase();
            valB = b.title.toLowerCase();
        } else if (col === 'model_type') {
            valA = a.parameters.Model.toLowerCase();
            valB = b.parameters.Model.toLowerCase();
        } else if (col === 'range') {
            valA = a.range ? a.range.max : 0;
            valB = b.range ? b.range.max : 0;
        } else if (col === 'luminosity') {
            // Parse "3.61e+08 L⊙" into a number
            valA = parseFloat(a.luminosity.split(' ')[0]);
            valB = parseFloat(b.luminosity.split(' ')[0]);
        }

        if (valA < valB) return currentSort.asc ? -1 : 1;
        if (valA > valB) return currentSort.asc ? 1 : -1;
        return 0;
    });

    if (!skipRender) renderHome();
}

function sortData(col) {
    performSort(col);
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
                            <tr><th>Valid Data Range</th><td>${model.range ? `${model.range.min} - ${model.range.max} kpc` : 'N/A'}</td></tr>
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
