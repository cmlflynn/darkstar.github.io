const app = document.getElementById('app');
let modelData = [];

// Fetch the data
async function init() {
    try {
        const response = await fetch('data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        modelData = await response.json();
        // Initial sort by default column without rendering
        performSort(currentSort.col, true);
        router();
    } catch (err) {
        app.innerHTML = `<div class="error">
            <h3>Error loading model data</h3>
            <p>${err.message}</p>
            <p>Please ensure you are viewing this via a web server (e.g., using <code>python3 -m http.server</code>).</p>
        </div>`;
        console.error("Initialization error:", err);
    }
}

// Router
function router() {
    const hash = window.location.hash || '#/';
    
    if (hash === '#/') {
        renderHome();
    } else if (hash === '#/comparison') {
        renderComparison();
    } else if (hash.startsWith('#/model/')) {
        const id = hash.replace('#/model/', '');
        renderDetail(id);
    } else if (hash.startsWith('#/plot/')) {
        const id = hash.replace('#/plot/', '');
        renderFullPlotView(id);
    } else if (hash.startsWith('#/code/')) {
        const id = hash.replace('#/code/', '');
        renderCodeView(id);
    }
}

let currentSort = { col: 'title', asc: true };
let luminosityChartInstance = null;

function getLuminosityValue(model) {
    return ModelPhysics.calculateLuminosity(model.id, ModelPhysics.currentCoreRadius);
}

function formatLuminosity(val) {
    return val.toExponential(2).replace('e+', 'e') + ' L⊙';
}

function renderCoreSelectorHTML() {
    const active1 = ModelPhysics.currentCoreRadius === 1.0 ? 'active' : '';
    const active3 = ModelPhysics.currentCoreRadius === 3.0 ? 'active' : '';
    const active5 = ModelPhysics.currentCoreRadius === 5.0 ? 'active' : '';
    return `
        <div class="core-selector-container">
            <span class="core-selector-label">Core Radius (R<sub>core</sub>):</span>
            <div class="core-selector-options">
                <button class="core-btn ${active1}" data-core="1.0">1 kpc</button>
                <button class="core-btn ${active3}" data-core="3.0">3 kpc</button>
                <button class="core-btn ${active5}" data-core="5.0">5 kpc</button>
            </div>
        </div>
    `;
}

// Global click delegation for Core Selector
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.core-btn');
    if (btn) {
        ModelPhysics.currentCoreRadius = parseFloat(btn.getAttribute('data-core'));
        router();
    }
});

// Density Calculation and Geometry Data
const ModelPhysics = {
    currentCoreRadius: 1.0,
    currentRsun: null,
    getRsun: (id) => ModelPhysics.currentRsun || (id === 'han2022' ? 8.122 : 8.275),
    RHO_LOCAL_PC3: 1.7e-5,
    R_SUN: 8.275,

    // Volume factor helper: returns 4 * pi * p * q
    getVolumeFactor: (id, r) => {
        const factors = {
            staf256: 4 * Math.PI * 0.80 * 0.66,
            han2022: 4 * Math.PI * 0.81 * 0.73,
            amarante2024: (rad) => rad < 30 ? 4 * Math.PI * 1.0 * 0.77 : 4 * Math.PI * 1.0 * 0.99,
            ablimit2018: 4 * Math.PI * 1.0 * 1.0,
            chen2023: 4 * Math.PI * 1.0 * 0.73,
            deason2011: 4 * Math.PI * 1.0 * 0.59,
            yang2022: (rad) => {
                const q = rad < 5 ? 0.5 : (rad > 30 ? 0.8 : 0.5 + 0.3 * (rad - 5) / 25);
                return 4 * Math.PI * 1.0 * q;
            },
            hernitschek2018: 4 * Math.PI * 1.0 * 0.918,
            horta2021: 4 * Math.PI * 0.73 * 0.56,
            kurbatov2024: 4 * Math.PI * 1.0 * 0.5,
            libinney2022: 4 * Math.PI * 1.0 * 0.65,
            lopezcorredoira2024: 4 * Math.PI * 1.0 * 1.0,
            lucey2026: (rad) => rad < 10.0 ? 4 * Math.PI * 1.0 * 1.31 : 4 * Math.PI * 1.0 * 0.70,
            mackereth2020: 4 * Math.PI * 0.73 * 0.56,
            medina2024: 4 * Math.PI * 1.0 * 1.0,
            medina2018: 4 * Math.PI * 1.0 * 1.0,
            stringer2021: 4 * Math.PI * 1.0 * 0.7,
            suzuki2026: 4 * Math.PI * 1.0 * 1.0,
            thomas2018: 4 * Math.PI * 1.0 * 0.86,
            li2026: 4 * Math.PI * 0.85 * 0.74,
            yu2024: 4 * Math.PI * 1.0 * 1.0,
            wu2025: (rad) => rad < 8 ? 4 * Math.PI * 1.0 * 0.4 : (rad > 25 ? 4 * Math.PI * 1.0 * 0.8 : 4 * Math.PI * 1.0 * (0.4 + 0.4 * (rad - 8) / 17)),
            wu2022: (rad) => rad < 8 ? 4 * Math.PI * 1.0 * 0.4 : (rad > 25 ? 4 * Math.PI * 1.0 * 0.8 : 4 * Math.PI * 1.0 * (0.4 + 0.4 * (rad - 8) / 17)),
            rix2022: 4 * Math.PI * 1.0 * 1.0,
            cavieres2025: 4 * Math.PI * 1.0 * 0.98,
            feng2024: 4 * Math.PI * 1.0 * 1.0,
            fukushima2025: 4 * Math.PI * 1.0 * 1.56,
            ye2023: 4 * Math.PI * 1.0 * 0.81,
            tao2026: 4 * Math.PI * 1.0 * 0.8,
            lane2023: 4 * Math.PI * 0.9 * 0.58
        };
        const f = factors[id];
        return (typeof f === 'function') ? f(r) : f;
    },

    getQ: (id, r) => {
        const qFactors = {
            staf256: 0.66,
            han2022: 0.73,
            amarante2024: (rad) => rad < 30 ? 0.77 : 0.99,
            chen2023: 0.73,
            deason2011: 0.59,
            yang2022: (rad) => rad < 5 ? 0.5 : (rad > 30 ? 0.8 : 0.5 + 0.3 * (rad - 5) / 25),
            hernitschek2018: 0.918,
            horta2021: 0.56,
            kurbatov2024: 0.5,
            libinney2022: 0.65,
            lopezcorredoira2024: 1.0,
            lucey2026: (rad) => rad < 10.0 ? 1.31 : 0.70,
            mackereth2020: 0.56,
            medina2024: 1.0,
            medina2018: 1.0,
            stringer2021: 0.7,
            suzuki2026: 1.0,
            thomas2018: 0.86,
            li2026: 0.74,
            ablimit2018: 1.0,
            yu2024: 1.0,
            wu2025: (rad) => rad < 8 ? 0.4 : (rad > 25 ? 0.8 : 0.4 + 0.4 * (rad - 8) / 17),
            wu2022: (rad) => rad < 8 ? 0.4 : (rad > 25 ? 0.8 : 0.4 + 0.4 * (rad - 8) / 17),
            rix2022: 1.0,
            cavieres2025: 0.98,
            feng2024: 1.0,
            fukushima2025: 1.56,
            ye2023: 0.81,
            tao2026: 0.8,
            lane2023: 0.58
        };
        const q = qFactors[id];
        return (typeof q === 'function') ? q(r) : q;
    },

    applyCore: (r, coreRadius, densityFunc) => {
        if (r < coreRadius) return densityFunc(coreRadius);
        return densityFunc(r);
    },

    // Individual density functions
    staf256: (r) => {
        const a = 3.48, rho_0 = 1.89e+06 / (1000**3);
        return rho_0 * Math.pow(1 + (r / a)**2, -2.5);
    },

    deason2011: (r) => {
        const ai=2.3, ao=4.6, rb=27.0, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('deason2011');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    li2026: (r) => {
        const a1=1.50, a2=3.45, a3=5.20, rb1=16.0, rb2=76.3, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('li2026');
        const getRaw = (rad) => {
            if (rad < rb1) return Math.pow(rad, -a1);
            if (rad < rb2) return Math.pow(rb1, a2-a1) * Math.pow(rad, -a2);
            return Math.pow(rb1, a2-a1) * Math.pow(rb2, a3-a2) * Math.pow(rad, -a3);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    han2022: (r) => {
        const a1=1.7, a2=3.1, a3=4.6, rb1=12.0, rb2=28.0, R_sun=ModelPhysics.getRsun('han2022'), core=ModelPhysics.currentCoreRadius;
        const getRaw = (rad) => {
            if (rad < rb1) return Math.pow(rad, -a1);
            if (rad < rb2) return Math.pow(rb1, a2-a1) * Math.pow(rad, -a2);
            return Math.pow(rb1, a2-a1) * Math.pow(rb2, a3-a2) * Math.pow(rad, -a3);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    amarante2024: (r) => {
        const ai=2.9, ao=4.5, rb=19.1, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('amarante2024');
        const getRaw = (rad) => {
            if (rad < rb) return Math.pow(rad, -ai);
            return Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    ablimit2018: (r) => {
        const ai=2.8, ao=4.8, rb=21.0, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('ablimit2018');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    chen2023: (r) => {
        const s1=2.83, s2=4.49, r0=27.45, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('chen2023');
        const getRaw = (rad) => {
            if (rad < r0) return Math.pow(rad, -s1);
            return Math.pow(r0, s2-s1) * Math.pow(rad, -s2);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    yang2022: (r) => {
        const a1=1.5, a2=2.8, a3=6.1, rb1=10.0, rb2=25.0, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('yang2022');
        const getRaw = (rad) => {
            if (rad < rb1) return Math.pow(rad, -a1);
            if (rad < rb2) return Math.pow(rb1, a2-a1) * Math.pow(rad, -a2);
            return Math.pow(rb1, a2-a1) * Math.pow(rb2, a3-a2) * Math.pow(rad, -a3);
        };
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    hernitschek2018: (r) => {
        const a=4.40, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('hernitschek2018');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    horta2021: (r) => {
        const a=3.5, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('horta2021');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    kurbatov2024: (r) => {
        const a=3.4, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('kurbatov2024');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    libinney2022: (r) => {
        const ai=1.0, ao=4.5, rb=20.0, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('libinney2022');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    lopezcorredoira2024: (r) => {
        const a=4.6, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('lopezcorredoira2024');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    lucey2026: (r) => {
        const a=4.0, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('lucey2026');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    mackereth2020: (r) => {
        const a=3.49, r_cut=25.0, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('mackereth2020');
        const getRaw = (rad) => Math.pow(rad, -a) * Math.exp(-rad / r_cut);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    medina2024: (r) => {
        const ai=2.05, ao=4.47, rb=18.1, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('medina2024');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    medina2018: (r) => {
        const a=4.17, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('medina2018');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    stringer2021: (r) => {
        const ai=2.54, ao=5.42, rb=32.1, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('stringer2021');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    suzuki2026: (r) => {
        const ai=3.3, ao=4.8, rb=17.4, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('suzuki2026');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    wu2025: (r) => {
        const a=4.65, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('wu2025');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    wu2022: (r) => {
        const a1=4.92, a2=4.25, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('wu2022');
        const r_match = Math.exp(3.0);
        const getRaw = (rad) => Math.pow(r_match, a1 - a2) * Math.pow(rad, -a1) + Math.pow(rad, -a2);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    rix2022: (r) => {
        const sigma=2.7, R_sun=ModelPhysics.getRsun('rix2022');
        const rho_norm = 1.7e-5;
        return rho_norm * Math.exp(-(r*r - R_sun*R_sun) / (2 * sigma*sigma));
    },

    cavieres2025: (r) => {
        const ai=3.13, ao=7.46, rb=67.5, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('cavieres2025');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    feng2024: (r) => {
        const a=4.09, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('feng2024');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    fukushima2025: (r) => {
        const ai=3.90, ao=9.1, rb=184.0, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('fukushima2025');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    ye2023: (r) => {
        const ai=2.34, ao=2.86, rb=22.99, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('ye2023');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    yu2024: (r) => {
        const a=4.34, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('yu2024');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    tao2026: (r) => {
        const a=3.5, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('tao2026');
        const rho_norm = (1.7e-5) / Math.pow(R_sun, -a);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * Math.pow(rad, -a));
    },

    thomas2018: (r) => {
        const ai=4.24, ao=3.21, rb=41.4, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('thomas2018');
        const getRaw = (rad) => rad < rb ? Math.pow(rad, -ai) : Math.pow(rb, ao-ai) * Math.pow(rad, -ao);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    lane2023: (r) => {
        const a=2.5, core=ModelPhysics.currentCoreRadius, R_sun=ModelPhysics.getRsun('lane2023');
        const getRaw = (rad) => Math.pow(rad, -a);
        const rho_norm = (1.7e-5) / getRaw(R_sun);
        return ModelPhysics.applyCore(r, core, (rad) => rho_norm * getRaw(rad));
    },

    getDensity: (id, r) => {
        return ModelPhysics[id](r);
    },

    calculateLuminosity: (id, coreRadius, rsun = null) => {
        const savedCore = ModelPhysics.currentCoreRadius;
        const savedRsun = ModelPhysics.currentRsun;
        ModelPhysics.currentCoreRadius = coreRadius;
        ModelPhysics.currentRsun = rsun;
        
        const cr_plot_max = 500;
        const integrationSteps = 5000;
        const logIntMin = -4; // 0.0001 kpc
        const logIntMax = Math.log10(cr_plot_max);
        const dv = (logIntMax - logIntMin) / integrationSteps;
        const ln10 = Math.log(10);
        let runningL = 0;

        const physFunc = ModelPhysics[id];
        if (!physFunc) return 0;

        for (let j = 0; j <= integrationSteps; j++) {
            const v = logIntMin + j * dv;
            const r = Math.pow(10, v);
            const rho_kpc3 = physFunc(r) * (1000**3);
            const volFactor = ModelPhysics.getVolumeFactor(id, r);
            const dL = rho_kpc3 * volFactor * (r**2) * (r * ln10 * dv);
            runningL += dL;
        }

        ModelPhysics.currentCoreRadius = savedCore;
        ModelPhysics.currentRsun = savedRsun;
        return runningL;
    }
};

function renderComparison() {
    const existingPlot = document.getElementById('unifiedComparisonPlot');
    const visibilityState = {};
    if (existingPlot && existingPlot.data) {
        existingPlot.data.forEach(trace => {
            if (trace.legendgroup) {
                visibilityState[trace.legendgroup] = trace.visible !== undefined ? trace.visible : true;
            }
        });
    }

    let html = `
        <div class="comparison-page">
            <a href="#/" class="back-link">&larr; Back to all models</a>
            <h2>Interactive Model Comparison</h2>
            <div class="comparison-controls">
                <p><strong>Plotting Instructions:</strong> Upper panel: Bold solid lines indicate the <em>Valid Data Range</em>. Dashed lines represent the model's extrapolation. You can toggle models on and off by clicking their names in the legend. Top panel: Luminosity Density ($L_{\\odot}/pc^3$); Bottom panel: Cumulative Enclosed Luminosity ($L_{\\odot}$).</p>
                <div class="toggle-controls" style="margin-top: 15px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                    <div>
                        <button class="btn small" onclick="toggleAllModels(true)">Show All Models</button>
                        <button class="btn secondary small" onclick="toggleAllModels(false)" style="margin-left: 10px;">Hide All Models</button>
                    </div>
                    <div class="comparison-selector-wrapper">
                        ${renderCoreSelectorHTML()}
                    </div>
                </div>
            </div>
            <div id="unifiedComparisonPlot" style="height: 850px; margin-top: 20px;"></div>
        </div>
    `;
    app.innerHTML = html;
    
    if (typeof Plotly === 'undefined') {
        setTimeout(renderComparison, 100);
        return;
    }

    const colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#a52a2a', '#00008b', '#008b8b', '#bdb76b', '#8b008b',
        '#556b2f', '#ff8c00', '#9932cc', '#8b0000', '#e9967a',
        '#8fbc8f', '#483d8b', '#2f4f4f', '#00ced1', '#9400d3', '#ff1493'
    ];

    try {
        const traces = [];
        modelData.forEach((model, index) => {
            const physFunc = ModelPhysics[model.id];
            if (!physFunc) return;

            const color = colors[index % colors.length];
            const visible = (model.id in visibilityState) ? visibilityState[model.id] : (index < 5 ? true : 'legendonly');

            // 1. Full Range Density (Dashed)
            const fr_min = 0.01, fr_max = 500, points = 300;
            const fr_vals = [], fr_rho_vals = [];
            const flMin = Math.log10(fr_min), flMax = Math.log10(fr_max);
            for (let i = 0; i <= points; i++) {
                const r = Math.pow(10, flMin + (i / points) * (flMax - flMin));
                fr_vals.push(r);
                fr_rho_vals.push(physFunc(r));
            }

            traces.push({
                x: fr_vals, y: fr_rho_vals, mode: 'lines', name: model.title + ' (Extrapolation)',
                line: { width: 1.5, color: color, dash: 'dash' }, visible: visible,
                legendgroup: model.id, showlegend: false,
                xaxis: 'x', yaxis: 'y', hoverinfo: 'none'
            });

            // 2. Valid Range Density (Solid)
            const vr_min = Math.max(0.1, model.range.min);
            const vr_max = model.range.max;
            const vr_vals = [], vr_rho_vals = [];
            const vlMin = Math.log10(vr_min), vlMax = Math.log10(vr_max);
            for (let i = 0; i <= 100; i++) {
                const r = Math.pow(10, vlMin + (i / 100) * (vlMax - vlMin));
                vr_vals.push(r);
                vr_rho_vals.push(physFunc(r));
            }

            traces.push({
                x: vr_vals, y: vr_rho_vals, mode: 'lines', name: model.title,
                line: { width: 4, color: color }, visible: visible,
                legendgroup: model.id, showlegend: true,
                xaxis: 'x', yaxis: 'y', hoverinfo: 'x+y'
            });

            // 3. Cumulative Trace
            const cr_plot_min = 0.01, cr_plot_max = 500;
            const cr_vals = [], l_cum_vals = [];
            const clogMin = Math.log10(cr_plot_min), clogMax = Math.log10(cr_plot_max);
            
            // High-precision log-spaced integration
            const integrationSteps = 5000;
            const logIntMin = -4; // Start at 0.0001 kpc for central luminosity
            const logIntMax = Math.log10(cr_plot_max);
            const dv = (logIntMax - logIntMin) / integrationSteps;
            const ln10 = Math.log(10);
            let runningL = 0;
            
            const targetRadii = Array.from({length: 401}, (_, i) => Math.pow(10, clogMin + (i / 400) * (clogMax - clogMin)));
            let targetIdx = 0;

            for (let j = 0; j <= integrationSteps; j++) {
                const v = logIntMin + j * dv;
                const r = Math.pow(10, v);
                const rho_kpc3 = physFunc(r) * (1000**3);
                const volFactor = ModelPhysics.getVolumeFactor(model.id, r);
                // dr = r * ln(10) * dv
                const dL = rho_kpc3 * volFactor * (r**2) * (r * ln10 * dv);
                runningL += dL;

                while (targetIdx < targetRadii.length && r >= targetRadii[targetIdx]) {
                    cr_vals.push(targetRadii[targetIdx]);
                    l_cum_vals.push(runningL);
                    targetIdx++;
                }
            }

            traces.push({
                x: cr_vals, y: l_cum_vals, mode: 'lines', name: model.title + ' (Cumulative)',
                line: { width: 3, color: color }, visible: visible,
                legendgroup: model.id, showlegend: false,
                xaxis: 'x2', yaxis: 'y2', hoverinfo: 'x+y'
            });
        });

        const layout = {
            grid: { rows: 2, columns: 1, pattern: 'independent', roworder: 'top to bottom' },
            plot_bgcolor: '#fff', paper_bgcolor: '#fff',
            margin: { t: 50, b: 80, l: 80, r: 50 },
            hovermode: 'closest', 
            legend: { orientation: 'h', y: -0.15, x: 0.5, xanchor: 'center' },
            // Panel 1: Density
            xaxis: { 
                title: 'Galactocentric Radius [kpc]', type: 'log', range: [-1.0, 2.7], gridcolor: '#eee', 
                showline: true, linewidth: 1.0, linecolor: '#000', mirror: 'all', anchor: 'y'
            },
            yaxis: { 
                title: 'Luminosity density [L⊙/pc³]', type: 'log', range: [-14, 1], gridcolor: '#eee', 
                showline: true, linewidth: 1.0, linecolor: '#000', mirror: 'all', domain: [0.55, 1.0],
                exponentformat: 'E', showexponent: 'all'
            },
            // Panel 2: Cumulative
            xaxis2: { 
                title: 'Galactocentric Radius [kpc]', type: 'log', range: [-1.0, 2.7], gridcolor: '#eee', 
                showline: true, linewidth: 1.0, linecolor: '#000', mirror: 'all', anchor: 'y2'
            },
            yaxis2: { 
                title: 'Total Enclosed Luminosity [L⊙]', type: 'log', range: [3, 10.5], gridcolor: '#eee', 
                showline: true, linewidth: 1.0, linecolor: '#000', mirror: 'all', domain: [0, 0.45],
                exponentformat: 'E', showexponent: 'all'
            },
            shapes: [
                // Shaded core region on panel 1 (Density)
                {
                    type: 'rect', xref: 'x', yref: 'y',
                    x0: 0.01, x1: ModelPhysics.currentCoreRadius,
                    y0: 1e-14, y1: 10,
                    fillcolor: 'rgba(230, 126, 34, 0.08)', line: { width: 0 }, layer: 'below'
                },
                // Line marking core radius on panel 1
                {
                    type: 'line', xref: 'x', yref: 'paper',
                    x0: ModelPhysics.currentCoreRadius, x1: ModelPhysics.currentCoreRadius,
                    y0: 0.55, y1: 1,
                    line: { color: '#e67e22', width: 2, dash: 'dot' }
                },
                // Line marking core radius on panel 2 (Cumulative)
                {
                    type: 'line', xref: 'x2', yref: 'paper',
                    x0: ModelPhysics.currentCoreRadius, x1: ModelPhysics.currentCoreRadius,
                    y0: 0, y1: 0.45,
                    line: { color: '#e67e22', width: 2, dash: 'dot' }
                }
            ],
            annotations: [
                {
                    xref: 'x', yref: 'paper',
                    x: ModelPhysics.currentCoreRadius * 0.8,
                    y: 0.98, xanchor: 'right', yanchor: 'top',
                    text: `Core Regularization: R < ${ModelPhysics.currentCoreRadius} kpc`,
                    showarrow: false, font: { color: '#e67e22', size: 11, weight: 'bold' }
                }
            ]
        };

        Plotly.newPlot('unifiedComparisonPlot', traces, layout, {responsive: true, displaylogo: false});
    } catch (err) { console.error("Comparison plot error:", err); }
}

function toggleAllModels(show) {
    const visibility = show ? true : 'legendonly';
    const update = { visible: visibility };
    const plot = document.getElementById('unifiedComparisonPlot');
    if (plot && typeof Plotly !== 'undefined') {
        Plotly.restyle(plot, update);
    }
}

function renderHome() {
    const getSortClass = (col) => {
        if (currentSort.col !== col) return '';
        return currentSort.asc ? 'sort-asc' : 'sort-desc';
    };

    let html = `
        <div class="intro-banner">
            <p>Compare all ${modelData.length} stellar halo models in our new <a href="#/comparison" class="accent-link">Interactive Comparison Tool</a>.</p>
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
                            <td><a href="${model.paper_url}" target="_blank">${model.title}</a></td>
                            <td>${model.tracer || 'N/A'}</td>
                            <td>${model.parameters.Model}</td>
                            <td>${model.range ? `${model.range.min} - ${model.range.max} kpc` : 'N/A'}</td>
                            <td>${formatLuminosity(getLuminosityValue(model))}</td>
                            <td><a href="#/model/${model.id}" class="btn">Explore Model</a></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        <div class="chart-section">
            <h3>Luminosity Comparison</h3>
            <div class="chart-container"><canvas id="luminosityChart"></canvas></div>
        </div>
        <div class="home-selector-wrapper" style="text-align: center; margin-top: 30px; display: flex; flex-direction: column; align-items: center; gap: 15px;">
            ${renderCoreSelectorHTML()}
            <div>
                <a href="compendium_data.csv" download class="btn" id="downloadCsvBtn">Download Results (CSV)</a>
            </div>
        </div>
    `;
    app.innerHTML = html;
    renderLuminosityChart();
}

function renderLuminosityChart() {
    const canvas = document.getElementById('luminosityChart');
    if (!canvas) return;
    if (typeof Chart === 'undefined') {
        setTimeout(renderLuminosityChart, 100);
        return;
    }
    try {
        const ctx = canvas.getContext('2d');
        if (luminosityChartInstance) luminosityChartInstance.destroy();
        const labels = modelData.map(m => m.title);
        const data = modelData.map(m => {
            const val = getLuminosityValue(m);
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
                responsive: true, maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: 'Luminosity (L⊙)' } },
                    x: { ticks: { minRotation: 45, maxRotation: 45 } }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) label += context.parsed.y.toExponential(2) + ' L⊙';
                                return label;
                            }
                        }
                    }
                }
            }
        });
    } catch (err) { console.error('Error rendering chart:', err); }
}

function performSort(col, skipRender = false) {
    if (!skipRender) {
        if (currentSort.col === col) currentSort.asc = !currentSort.asc;
        else { currentSort.col = col; currentSort.asc = true; }
    }
    modelData.sort((a, b) => {
        let valA, valB;
        if (col === 'title') { valA = a.title.toLowerCase(); valB = b.title.toLowerCase(); }
        else if (col === 'tracer') { valA = (a.tracer || '').toLowerCase(); valB = (b.tracer || '').toLowerCase(); }
        else if (col === 'model_type') { valA = a.parameters.Model.toLowerCase(); valB = b.parameters.Model.toLowerCase(); }
        else if (col === 'range') { valA = a.range ? a.range.max : 0; valB = b.range ? b.range.max : 0; }
        else if (col === 'luminosity') {
            valA = getLuminosityValue(a);
            valB = getLuminosityValue(b);
        }
        if (valA < valB) return currentSort.asc ? -1 : 1;
        if (valA > valB) return currentSort.asc ? 1 : -1;
        return 0;
    });
    if (!skipRender) renderHome();
}

function sortData(col) { performSort(col); }

function renderDetail(id) {
    const model = modelData.find(m => m.id === id);
    if (!model) { app.innerHTML = `<h2>Model not found</h2><a href="#/">Back to home</a>`; return; }
    const currentIndex = modelData.findIndex(m => m.id === id);
    const prevModel = currentIndex > 0 ? modelData[currentIndex - 1] : null;
    const nextModel = currentIndex < modelData.length - 1 ? modelData[currentIndex + 1] : null;
    const paramRows = Object.entries(model.parameters)
        .map(([key, val]) => `<tr><th>${key}</th><td>${val}</td></tr>`).join('');
    app.innerHTML = `
        <div class="model-detail">
            <div class="detail-header">
                <a href="#/" class="back-link">&larr; Back to all models</a>
                <div class="model-nav">
                    ${prevModel ? `<a href="#/model/${prevModel.id}" class="btn secondary small">&larr; Previous: ${prevModel.title}</a>` : '<span class="nav-placeholder"></span>'}
                    ${nextModel ? `<a href="#/model/${nextModel.id}" class="btn secondary small">Next: ${nextModel.title} &rarr;</a>` : '<span class="nav-placeholder"></span>'}
                </div>
            </div>
            <h2>${model.paper_url ? `<a href="${model.paper_url}" target="_blank">${model.title}</a>` : model.title}</h2>
            <p class="subtitle">Paper title: ${model.subtitle}</p>
            <div class="content-wrapper">
                <div class="description-section">
                    <h3>About this Model</h3>
                    <p>${model.summary}</p>
                </div>
                <div class="data-section">
                    <div class="info-pane">
                        ${model.eqn_url ? `<div class="equation-container"><h3>Model Equation</h3><img src="${model.eqn_url}" alt="Equation" class="equation-img"></div>` : ''}
                        <h3>Model Parameters</h3>
                        <table class="parameters-table">
                            <tr><th>Tracer Stars</th><td>${model.tracer || 'N/A'}</td></tr>
                            <tr><th>Valid Data Range</th><td>${model.range ? `${model.range.min} - ${model.range.max} kpc` : 'N/A'}</td></tr>
                            ${paramRows}
                        </table>
                        <div class="luminosity-highlight">
                            <h3>Total Halo Luminosity</h3>
                            <div style="margin-bottom: 12px;">
                                <p style="margin-bottom: 2px;">Local norm: 1.7E-5 L<sub>&odot;</sub>/pc<sup>3</sup> at R=${model.id === 'han2022' ? '8.122' : '8.275'} kpc</p>
                                <div class="luminosity-value">${formatLuminosity(getLuminosityValue(model))}</div>
                            </div>
                            <div style="border-top: 1px dashed rgba(255,255,255,0.3); padding-top: 8px; margin-top: 8px;">
                                <p style="margin-bottom: 2px;">Assuming R = 8.0 kpc (local norm at R = 8.0 kpc):</p>
                                <div class="luminosity-value" style="color: #a5d6a7;">${formatLuminosity(ModelPhysics.calculateLuminosity(model.id, ModelPhysics.currentCoreRadius, 8.0))}</div>
                            </div>
                            ${model.id !== 'rix2022' ? `
                            <div class="core-sensitivity-container" style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 15px;">
                                <h4 style="font-size: 0.95rem; margin-bottom: 10px; color: var(--accent-color);">Sensitivity to Core Radius (R<sub>core</sub>)</h4>
                                <table class="sensitivity-table" style="width:100%; font-size:0.9rem; text-align:left; border-collapse:collapse; color:white;">
                                    <thead>
                                        <tr style="border-bottom:1px solid rgba(255,255,255,0.2); font-weight:bold;">
                                            <th style="padding:6px 0;">Core Radius</th>
                                            <th style="padding:6px 0;">Total Luminosity</th>
                                            <th style="padding:6px 0; text-align:right;">Change</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${[1.0, 3.0, 5.0].map(c => {
                                            const val = ModelPhysics.calculateLuminosity(model.id, c);
                                            const baseVal = ModelPhysics.calculateLuminosity(model.id, 1.0);
                                            const pct = c === 1.0 ? '—' : ((val - baseVal) / baseVal * 100).toFixed(1) + '%';
                                            const isActive = ModelPhysics.currentCoreRadius === c ? 'font-weight:bold; color:var(--accent-color);' : '';
                                            return `
                                                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); ${isActive}">
                                                    <td style="padding:6px 0;">${c} kpc ${ModelPhysics.currentCoreRadius === c ? '★' : ''}</td>
                                                    <td style="padding:6px 0;">${formatLuminosity(val)}</td>
                                                    <td style="padding:6px 0; text-align:right; color:${c === 1.0 ? 'white' : '#ff9f43'};">${pct}</td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                            ` : ''}
                        </div>
                        <div class="code-footer">
                            <a href="#/code/${model.id}" class="btn secondary">View Python Source Code</a>
                            <a href="${model.code_url}" class="btn" download>Download Python Source Code</a>
                        </div>
                    </div>
                    <div class="plot-pane">
                        <h3>Interactive Model Analysis</h3>
                        <div class="plot-container" id="unifiedPlotContainer" style="height: 600px;"></div>
                        <div style="margin-top: 20px; display: flex; justify-content: ${model.id !== 'rix2022' ? 'space-between' : 'flex-end'}; align-items: center; flex-wrap: wrap; gap: 15px;">
                            ${model.id !== 'rix2022' ? `
                            <div class="detail-selector-wrapper">
                                ${renderCoreSelectorHTML()}
                            </div>
                            ` : ''}
                            <div class="code-footer" style="margin-top: 0;">
                                <a href="#/plot/${model.id}" class="btn secondary">View Full Sized Version</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    renderUnifiedPlot(model);
}

function renderUnifiedPlot(model, containerId = 'unifiedPlotContainer') {
    if (typeof Plotly === 'undefined') {
        setTimeout(() => renderUnifiedPlot(model, containerId), 100);
        return;
    }
    try {
        const qFunc = ModelPhysics.getQ;
        const rhoFunc = ModelPhysics[model.id];
        if (!rhoFunc) throw new Error(`Density function not found for model: ${model.id}`);
        const r_min = 0.01, r_max = 150, points = 200;
        const r_vals = [], q_vals = [], rho_vals = [];
        const logMin = Math.log10(r_min), logMax = Math.log10(r_max);
        for (let i = 0; i <= points; i++) {
            const r = Math.pow(10, logMin + (i / points) * (logMax - logMin));
            r_vals.push(r);
            q_vals.push(qFunc(model.id, r));
            rho_vals.push(rhoFunc(r));
        }

        const traces = [];
        traces.push({
            x: r_vals, y: q_vals, mode: 'lines',
            line: { color: 'orange', width: 3 },
            name: 'Flattening q', xaxis: 'x', yaxis: 'y2', hoverinfo: 'x+y'
        });

        if (model.id === 'wu2022') {
            const a1 = 4.92, a2 = 4.25, core = ModelPhysics.currentCoreRadius, R_sun = 8.275;
            const r_match = Math.exp(3.0);
            const getRawShape = (rad) => Math.pow(r_match, a1 - a2) * Math.pow(rad, -a1) + Math.pow(rad, -a2);
            const rho_norm = (1.7e-5) / getRawShape(R_sun);
            const comp1_vals = r_vals.map(r => rho_norm * Math.pow(r_match, a1 - a2) * Math.pow(Math.max(r, core), -a1));
            const comp2_vals = r_vals.map(r => rho_norm * Math.pow(Math.max(r, core), -a2));
            traces.push({ x: r_vals, y: comp1_vals, mode: 'lines', line: { color: 'gray', width: 2, dash: 'dash' }, name: 'Component 1 (α=4.92)', xaxis: 'x', yaxis: 'y', hoverinfo: 'x+y' });
            traces.push({ x: r_vals, y: comp2_vals, mode: 'lines', line: { color: 'gray', width: 2, dash: 'dot' }, name: 'Component 2 (α=4.25)', xaxis: 'x', yaxis: 'y', hoverinfo: 'x+y' });
        }

        traces.push({
            x: r_vals, y: rho_vals, mode: 'lines',
            line: { color: model.id === 'wu2022' ? 'black' : '#2c3e50', width: 3.5 },
            name: model.id === 'wu2022' ? 'Total Density (Sum)' : 'Luminosity density', 
            xaxis: 'x', yaxis: 'y', hoverinfo: 'x+y'
        });

        const shapes = [
            { type: 'rect', xref: 'x', yref: 'paper', x0: model.range.min, x1: model.range.max, y0: 0, y1: 1, fillcolor: 'rgba(52, 152, 219, 0.15)', line: { width: 0 }, layer: 'below' },
            { type: 'line', xref: 'x', yref: 'paper', x0: 8.275, x1: 8.275, y0: 0, y1: 1, line: { color: 'green', width: 2, dash: 'dashdot' } }
        ];
        if (model.id !== 'rix2022') {
            shapes.push({ type: 'line', xref: 'x', yref: 'paper', x0: ModelPhysics.currentCoreRadius, x1: ModelPhysics.currentCoreRadius, y0: 0, y1: 0.6, line: { color: '#e67e22', width: 2, dash: 'dot' } });
        }
        Object.entries(model.parameters).forEach(([key, val]) => {
            if (key.toLowerCase().includes('break') || key.toLowerCase().includes('radius')) {
                const r_break = parseFloat(val);
                if (!isNaN(r_break)) shapes.push({ type: 'line', xref: 'x', yref: 'paper', x0: r_break, x1: r_break, y0: 0, y1: 1, line: { color: 'red', width: 1.5, dash: 'dot' } });
            }
        });

        const layout = {
            grid: { rows: 2, columns: 1, pattern: 'independent', roworder: 'top to bottom' },
            margin: { t: 50, b: 60, l: 80, r: 30 }, plot_bgcolor: '#fff', paper_bgcolor: '#fff',
            xaxis: { title: 'Galactocentric Radius [kpc]', type: 'log', range: [-2, 2.2], gridcolor: '#eee', anchor: 'y', showline: true, linewidth: 1.0, linecolor: '#000', mirror: 'all' },
            yaxis: { title: 'Luminosity density [L⊙/pc³]', type: 'log', range: [-10, 1], gridcolor: '#eee', domain: [0, 0.6], showline: true, linewidth: 1.0, linecolor: '#000', mirror: 'all' },
            yaxis2: { title: 'Flattening q (c/a)', range: [0, 2], gridcolor: '#eee', domain: [0.7, 1.0], anchor: 'x', showline: true, linewidth: 1.0, linecolor: '#000', mirror: 'all' },
            shapes: shapes, showlegend: true, legend: { orientation: 'h', y: -0.2, x: 0.5, xanchor: 'center' }
        };

        traces.push({ x: [null], y: [null], mode: 'lines', line: { color: 'rgba(52, 152, 219, 0.3)', width: 10 }, name: 'Valid Data Range' });
        traces.push({ x: [null], y: [null], mode: 'lines', line: { color: 'green', width: 2, dash: 'dashdot' }, name: 'Sun (R₀=8.275)' });
        if (model.id !== 'rix2022') {
            traces.push({ x: [null], y: [null], mode: 'lines', line: { color: '#e67e22', width: 2, dash: 'dot' }, name: `Core Radius (${ModelPhysics.currentCoreRadius} kpc)` });
        }
        traces.push({ x: [null], y: [null], mode: 'lines', line: { color: 'red', width: 1.5, dash: 'dot' }, name: 'Break/Scale Radii' });
        
        Plotly.newPlot(containerId, traces, layout, {responsive: true, displaylogo: false});
    } catch (err) { console.error("Plot error:", err); }
}

function renderFullPlotView(id) {
    const model = modelData.find(m => m.id === id);
    if (!model) { app.innerHTML = `<h2>Model not found</h2><a href="#/">Back to home</a>`; return; }
    app.innerHTML = `<div class="comparison-page"><a href="#/model/${model.id}" class="back-link">&larr; Back to model details</a><h2>Full Analysis Plot: ${model.title}</h2><div id="fullPlotContainer" style="width: 100%; height: 80vh; margin-top: 30px;"></div></div>`;
    renderFullPlotViewWithRender(model, 'fullPlotContainer');
}

function renderFullPlotViewWithRender(model, containerId) {
    renderUnifiedPlot(model, containerId);
}

window.addEventListener('hashchange', router);

async function renderCodeView(id) {
    const model = modelData.find(m => m.id === id);
    if (!model) { app.innerHTML = `<h2>Model not found</h2><a href="#/">Back to home</a>`; return; }
    app.innerHTML = `<div class="code-page"><a href="#/model/${model.id}" class="back-link">&larr; Back to model details</a><h2>Python Source Code: ${model.title}</h2><div class="code-viewer-container"><pre><code id="code-content-loading">Loading source code...</code></pre></div></div>`;
    try {
        const response = await fetch(model.code_url);
        const code = await response.text();
        document.getElementById('code-content-loading').textContent = code;
    } catch (err) { document.getElementById('code-content-loading').textContent = 'Error loading source code.'; }
}

init();
