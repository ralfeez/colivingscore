// All Census data loaded via backend API — never from Census directly.

const STATE_ABBR_TO_FIPS = {
  AL:"01",AK:"02",AZ:"04",AR:"05",CA:"06",CO:"08",CT:"09",DE:"10",DC:"11",
  FL:"12",GA:"13",HI:"15",ID:"16",IL:"17",IN:"18",IA:"19",KS:"20",KY:"21",
  LA:"22",ME:"23",MD:"24",MA:"25",MI:"26",MN:"27",MS:"28",MO:"29",MT:"30",
  NE:"31",NV:"32",NH:"33",NJ:"34",NM:"35",NY:"36",NC:"37",ND:"38",OH:"39",
  OK:"40",OR:"41",PA:"42",RI:"44",SC:"45",SD:"46",TN:"47",TX:"48",UT:"49",
  VT:"50",VA:"51",WA:"53",WV:"54",WI:"55",WY:"56",
};

const STATE_NAMES = {
  AL:"Alabama",AK:"Alaska",AZ:"Arizona",AR:"Arkansas",CA:"California",
  CO:"Colorado",CT:"Connecticut",DE:"Delaware",DC:"District of Columbia",
  FL:"Florida",GA:"Georgia",HI:"Hawaii",ID:"Idaho",IL:"Illinois",IN:"Indiana",
  IA:"Iowa",KS:"Kansas",KY:"Kentucky",LA:"Louisiana",ME:"Maine",MD:"Maryland",
  MA:"Massachusetts",MI:"Michigan",MN:"Minnesota",MS:"Mississippi",MO:"Missouri",
  MT:"Montana",NE:"Nebraska",NV:"Nevada",NH:"New Hampshire",NJ:"New Jersey",
  NM:"New Mexico",NY:"New York",NC:"North Carolina",ND:"North Dakota",OH:"Ohio",
  OK:"Oklahoma",OR:"Oregon",PA:"Pennsylvania",RI:"Rhode Island",SC:"South Carolina",
  SD:"South Dakota",TN:"Tennessee",TX:"Texas",UT:"Utah",VT:"Vermont",VA:"Virginia",
  WA:"Washington",WV:"West Virginia",WI:"Wisconsin",WY:"Wyoming",
};

const DEFAULT_STATE = "TX";
const DEFAULT_COUNTY_FIPS = "113";

const stateSelect  = document.getElementById("state-select");
const countySelect = document.getElementById("county-select");
const lookupBtn    = document.getElementById("lookup-btn");
const errorMsg     = document.getElementById("error-msg");
const loadingMsg   = document.getElementById("loading-msg");

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.add("visible");
}

function clearError() {
  errorMsg.classList.remove("visible");
}

function setLoading(on) {
  loadingMsg.classList.toggle("visible", on);
  lookupBtn.disabled = on;
}

// Populate state dropdown alphabetically
Object.keys(STATE_NAMES)
  .sort((a, b) => STATE_NAMES[a].localeCompare(STATE_NAMES[b]))
  .forEach(abbr => {
    const opt = document.createElement("option");
    opt.value = abbr;
    opt.textContent = STATE_NAMES[abbr];
    stateSelect.appendChild(opt);
  });

stateSelect.addEventListener("change", async () => {
  const abbr = stateSelect.value;
  countySelect.innerHTML = '<option value="">Select county…</option>';
  countySelect.disabled = true;
  lookupBtn.disabled = true;
  clearError();
  if (!abbr) return;

  try {
    const resp = await fetch(`/api/silver-living/counties?state=${abbr}`);
    if (!resp.ok) throw new Error("Failed to load counties");
    const { counties } = await resp.json();
    counties.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.fips;
      opt.textContent = c.name;
      countySelect.appendChild(opt);
    });
    countySelect.disabled = false;
  } catch (e) {
    showError("Could not load county list. Please try again.");
  }
});

countySelect.addEventListener("change", () => {
  lookupBtn.disabled = !countySelect.value;
});

lookupBtn.addEventListener("click", () => {
  const stateFips = STATE_ABBR_TO_FIPS[stateSelect.value];
  const countyFips = countySelect.value;
  if (stateFips && countyFips) loadData(stateFips, countyFips);
});

function fmt(n) {
  return typeof n === "number" ? n.toLocaleString() : "—";
}

function renderChart(brackets) {
  const body   = document.getElementById("chart-body");
  const labels = document.getElementById("bar-labels");
  body.innerHTML   = "";
  labels.innerHTML = "";

  const max = Math.max(...brackets.map(b => b.count), 1);

  brackets.forEach(b => {
    const heightPx = Math.round((b.count / max) * 130);
    const color = b.target ? "var(--terracotta)" : "#c4bdb4";
    const opacity = b.target ? (b.label === "70–74" ? "1" : "0.75") : "1";
    const countLabel = b.count >= 1000 ? (b.count / 1000).toFixed(0) + "k" : String(b.count);

    const col = document.createElement("div");
    col.className = "bar-col";
    col.innerHTML = `<div class="bar-count">${countLabel}</div><div class="bar-rect" style="height:${heightPx}px;background:${color};opacity:${opacity}"></div>`;
    body.appendChild(col);

    const lbl = document.createElement("div");
    lbl.className = "bar-age";
    lbl.textContent = b.label;
    labels.appendChild(lbl);
  });
}

async function loadData(stateFips, countyFips) {
  clearError();
  setLoading(true);

  try {
    const resp = await fetch(`/api/silver-living/lookup?state=${stateFips}&county=${countyFips}`);
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.error || "Lookup failed");
    }
    const d = await resp.json();

    document.getElementById("val-pop65").textContent = fmt(d.pop65);
    document.getElementById("sub-pop65").textContent = "current estimate";
    document.getElementById("val-alone").textContent = fmt(d.living_alone);
    document.getElementById("sub-alone").textContent = `${d.living_alone_pct}% of 65+ population`;

    const g = d.growth_pct;
    const gEl = document.getElementById("val-growth");
    gEl.textContent = (g >= 0 ? "+" : "") + g + "%";
    gEl.style.color = g >= 0 ? "var(--sage)" : "var(--terracotta)";

    const stateAbbr = stateSelect.value;
    const countyName = countySelect.options[countySelect.selectedIndex].text;
    document.getElementById("chart-title").textContent = `Age Distribution — ${countyName}, ${stateAbbr}`;

    renderChart(d.age_brackets);

    const cit = d.citizenship;
    document.getElementById("cit-bar-citizen").style.width    = cit.citizen_pct + "%";
    document.getElementById("cit-pct-citizen").textContent    = cit.citizen_pct + "%";
    document.getElementById("cit-bar-noncitizen").style.width = cit.noncitizen_pct + "%";
    document.getElementById("cit-pct-noncitizen").textContent = cit.noncitizen_pct + "%";

    if (d.il_cost) {
      document.getElementById("cost-sub").textContent    = `State-level median · ${d.il_cost.state || stateAbbr}`;
      document.getElementById("cost-value").textContent  = d.il_cost.range;
      document.getElementById("cost-source").textContent = `Source: ${d.il_cost.source} · State median only — no county or MSA data available`;
    }
  } catch (e) {
    showError(e.message || "An error occurred. Please try again.");
  } finally {
    setLoading(false);
  }
}

window.addEventListener("DOMContentLoaded", async () => {
  stateSelect.value = DEFAULT_STATE;
  stateSelect.dispatchEvent(new Event("change"));

  await new Promise(resolve => {
    const interval = setInterval(() => {
      const opt = [...countySelect.options].find(o => o.value === DEFAULT_COUNTY_FIPS);
      if (opt) {
        countySelect.value = DEFAULT_COUNTY_FIPS;
        lookupBtn.disabled = false;
        clearInterval(interval);
        resolve();
      }
    }, 100);
    setTimeout(() => { clearInterval(interval); resolve(); }, 5000);
  });

  loadData(STATE_ABBR_TO_FIPS[DEFAULT_STATE], DEFAULT_COUNTY_FIPS);
});
