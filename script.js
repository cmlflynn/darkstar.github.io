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
// Density Calculation Functions
const ModelPhysics = {
    // Normalization at the Sun (R=8.275 typically)
    // All models return L_sun/pc^3
    
    // Constant core for all power laws
    applyCore: (r, coreRadius, densityFunc) => {
        if (r < coreRadius) return densityFunc(coreRadius);
        return densityFunc(r);
    },

    staf256: (r) => {
        // Horta 2025: Triaxial Plummer
        const a = 3.48;
        const rho_0 = 1.89e+06 / (1000**3); // pc^3
        return rho_0 * Math.pow(1 + (r / a)**2, -2.5);
    },

    han2022: (r) => {
        // Han 2022: Doubly Broken Power Law
        const a1=1.70, a2=3.09, a3=4.58;
        const rb1=11.85, rb2=28.33;
        const R_sun=8.122;
        const core=1.0;
        const getRaw = (rad) => {
            if (rad < rb1) return Math.pow(rad, -a1);
            if (rad < rb2) return Math.pow(rb1, a2-a1) * Math.pow(rad, -a2);
            return Math.pow(rb1, a2-a1) * Math.pow(rb2, a3-a2) * Math.pow(rad, -a3);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    amarante2024: (r) => {
        const alpha_in = 2.9, alpha_out = 4.5, r_br = 19.1, r_core = 1.0;
        const R_sun = 8.275;
        const getRaw = (rad) => {
            if (rad < r_br) return Math.pow(rad, -alpha_in);
            return Math.pow(r_br, alpha_out - alpha_in) * Math.pow(rad, -alpha_out);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, r_core, (rad) => rho_norm * getRaw(rad));
    },

    chen2023: (r) => {
        const s1 = 2.83, s2 = 4.49, r0 = 27.45, r_core = 1.0;
        const R_sun = 8.275;
        const getRaw = (rad) => {
            if (rad < r0) return Math.pow(rad, -s1);
            return Math.pow(r0, s2 - s1) * Math.pow(rad, -s2);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, r_core, (rad) => rho_norm * getRaw(rad));
    },

    yang2022: (r) => {
        const a1=1.5, a2=2.8, a3=6.1, rb1=10.0, rb2=25.0, r_core=1.0;
        const R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb1) return Math.pow(rad, -a1);
            if (rad < rb2) return Math.pow(rb1, a2-a1) * Math.pow(rad, -a2);
            return Math.pow(rb1, a2-a1) * Math.pow(rb2, a3-a2) * Math.pow(rad, -a3);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, r_core, (rad) => rho_norm * getRaw(rad));
    },

    hernitschek2018: (r) => {
        const ai=2.4, ao=4.5, rb=26.0, core=1.0;
        const R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    horta2021: (r) => {
        const a=3.5, R_sun=8.275;
        const rho_0 = 1.90e+06 / (1000**3);
        return rho_0 * Math.pow(1 + (r / a)**2, -2.5);
    },

    kurbatov2024: (r) => {
        const a=3.4, core=1.0, R_sun=8.275;
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    libinney2022: (r) => {
        const ai=1.0, ao=4.5, rb=20.0, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    lopezcorredoira2024: (r) => {
        const a=4.6, core=1.0, R_sun=8.275;
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    lucey2026: (r) => {
        const ai=2.1, ao=3.8, rb=18.0, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    mackereth2020: (r) => {
        const a=3.49, r_cut=25.0, core=1.0, R_sun=8.275;
        const getRaw = (rad) => Math.pow(rad, -a) * Math.exp(-rad / r_cut);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    medina2024: (r) => {
        const ai=2.05, ao=4.57, rb=24.3, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    medina2018: (r) => {
        const a=4.17, core=1.0, R_sun=8.275;
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    nibauer2025: (r) => {
        const ai=1.0, ao=3.5, rb=20.0, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    stringer2021: (r) => {
        const ai=2.5, ao=4.25, rb=20.0, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    suzuki2026: (r) => {
        const ai=3.3, ao=4.8, rb=17.4, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    wu2025: (r) => {
        const a=4.65, core=1.0, R_sun=8.275;
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    wu2022: (r) => {
        const ai=2.5, ao=4.5, rb=20.0, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    rix2022: (r) => {
        const a=4.0, core=1.0, R_sun=8.275;
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    cavieres2025: (r) => {
        const a1=2.2, a2=3.4, a3=5.0, rb1=12.0, rb2=28.0, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb1) return Math.pow(rad, -a1);
            if (rad < rb2) return Math.pow(rb1, a2-a1) * Math.pow(rad, -a2);
            return Math.pow(rb1, a2-a1) * Math.pow(rb2, a3-a2) * Math.pow(rad, -a3);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    feng2024: (r) => {
        const a=4.5, core=1.0, R_sun=8.275;
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    fukushima2025: (r) => {
        const ai=3.90, ao=9.1, rb=184.0, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    yi2023: (r) => {
        const ai=2.44, ao=4.41, rb=26.5, core=1.0, R_sun=8.275;
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    tao2026: (r) => {
        const a=3.5, core=1.0, R_sun=8.275;
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    }
};

function renderComparison() {
    let html = `
        <div class="comparison-page">
            <a href="#/" class="back-link">&larr; Back to all models</a>
            <h2>Interactive Model Comparison</h2>
            <div class="comparison-controls">
                <p><strong>Plotting Instructions:</strong> Each model is plotted only within its <em>Valid Data Range</em>. You can toggle models on and off by clicking their names in the legend or the list below. Use the plot tools to zoom or pan. Units are in Galactocentric radius (kpc) vs Luminosity Density ($L_{\\odot}/pc^3$).</p>
            </div>
            
            <div id="comparisonPlot"></div>
            
            <div class="plot-legend-custom" id="customLegend">
                <!-- Custom legend items for easier toggling -->
            </div>
        </div>
    `;
    app.innerHTML = html;
    
    // Generate data for Plotly
    const traces = modelData.map((model, index) => {
        const physFunc = ModelPhysics[model.id];
        if (!physFunc) return null;

        const r_min = Math.max(0.1, model.range.min);
        const r_max = model.range.max;
        
        // Generate points in log space
        const points = 200;
        const r_vals = [];
        const rho_vals = [];
        
        const logMin = Math.log10(r_min);
        const logMax = Math.log10(r_max);
        
        for (let i = 0; i <= points; i++) {
            const r = Math.pow(10, logMin + (i / points) * (logMax - logMin));
            r_vals.push(r);
            rho_vals.push(physFunc(r));
        }

        return {
            x: r_vals,
            y: rho_vals,
            mode: 'lines',
            name: model.title,
            line: { width: 3 },
            visible: index < 5 ? true : 'legendonly' // Only show first 5 by default
        };
    }).filter(t => t !== null);

    const layout = {
        title: 'Stellar Halo Density Profiles Comparison',
        xaxis: {
            title: 'Galactocentric Radius [kpc]',
            type: 'log',
            range: [-0.5, 3.0],
            gridcolor: '#eee'
        },
        yaxis: {
            title: 'Luminosity Density [L⊙/pc³]',
            type: 'log',
            range: [-10, -1],
            gridcolor: '#eee'
        },
        margin: { t: 50, b: 80, l: 80, r: 50 },
        hovermode: 'closest',
        plot_bgcolor: '#fff',
        paper_bgcolor: '#fff',
        legend: {
            orientation: 'h',
            y: -0.2
        }
    };

    Plotly.newPlot('comparisonPlot', traces, layout, {responsive: true});
}

// ... existing router logic ...

let currentSort = { col: 'title', asc: true };
let luminosityChartInstance = null;

// Render Home View
function renderHome() {
    const getSortClass = (col) => {
        if (currentSort.col !== col) return '';
        return currentSort.asc ? 'sort-asc' : 'sort-desc';
    };

    let html = `
        <div class="intro-banner">
            <p>Compare all 20 stellar halo models in our new <a href="#/comparison" class="accent-link">Interactive Comparison Tool</a>.</p>
        </div>

        <div class="model-table-container">
            <table class="model-table">
                <thead>
                    <tr>
                        <th class="${getSortClass('title')}" onclick="sortData('title')">Authors</th>
                        <th class="${getSortClass('tracer')}" onclick="sortData('tracer')">Tracer Stars</th>
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
                            <td>${model.tracer || 'N/A'}</td>
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
        } else if (col === 'tracer') {
            valA = (a.tracer || '').toLowerCase();
            valB = (b.tracer || '').toLowerCase();
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
                            <tr><th>Tracer Stars</th><td>${model.tracer || 'N/A'}</td></tr>
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
