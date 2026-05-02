# CoLivingFurnish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a standalone static web tool (`colivingfurnish/index.html` + `colivingfurnish/furnishings.csv`) that operators use to plan and budget co-living property furnishings — 4-step wizard, room-by-room checklist, budget tracker, and printable export.

**Architecture:** Enhance the existing `CoLivingFurnish.html` prototype directly. Remove the prototype-only TweaksPanel, replace the inline mock data object with a PapaParse CSV fetch, add tenant/climate filtering logic, add mobile CSS breakpoints, and add a print checklist feature. No build step — React via CDN, deployed as two static files on Netlify.

**Tech Stack:** React 18 (CDN), Babel Standalone (CDN), PapaParse 5 (CDN), `window.print()` + `@media print` for PDF export, Netlify for hosting.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `colivingfurnish/index.html` | Create (from prototype) | All UI + logic — React/JSX, CSS, print styles |
| `colivingfurnish/furnishings.csv` | Create (from modified CSV) | Product data — all items, prices, affiliate links, filter columns |

---

## Task 1: Project Scaffold

**Files:**
- Create: `colivingfurnish/index.html` (copy of prototype with TweaksPanel stripped and PapaParse added)
- Create: `colivingfurnish/furnishings.csv` (copy of `furnishingcosttool/coliving_furnishings_list_modified.csv`)

- [ ] **Step 1: Create the project folder and copy the base files**

```bash
mkdir -p "colivingfurnish"
cp "furnishingcosttool/extracted/design_handoff_colivingfurnish/CoLivingFurnish.html" "colivingfurnish/index.html"
cp "furnishingcosttool/coliving_furnishings_list_modified.csv" "colivingfurnish/furnishings.csv"
```

- [ ] **Step 2: Add PapaParse CDN to `<head>` in `colivingfurnish/index.html`**

Add after the Babel script tag (line ~12):

```html
<script src="https://unpkg.com/papaparse@5.4.1/papaparse.min.js" integrity="sha384-LvuBZ+9RKVKMT8ExBjPsxFQwYcMJLgAbMkGfFfhpMH3Jd4u0qdoJiOkPR0NvGVM" crossorigin="anonymous"></script>
```

- [ ] **Step 3: Remove the TweaksPanel block from `colivingfurnish/index.html`**

In the `<script type="text/babel">` block, delete everything from the comment `// tweaks-panel.jsx` down to and including the `TweakButton` function (approximately lines 234–695 in the prototype). The block to delete starts with:

```js
// tweaks-panel.jsx
// Reusable Tweaks shell + form-control helpers.
```

And ends after:

```js
function TweakButton({ label, onClick, secondary = false }) {
```

Keep everything from `// ── Logo ──` onward.

- [ ] **Step 4: Remove the inline `window.FURNISHINGS_DATA` block**

Delete the entire `<script>` block between `</style>` and `<script type="text/babel">` — the one that starts with:

```js
window.FURNISHINGS_DATA = {
  rooms: [
```

And ends with `};`. Replace it with a single comment placeholder:

```html
<script>
// FURNISHINGS_DATA is populated at runtime from furnishings.csv via PapaParse.
// See the loadFurnishingsData() call in the App component.
window.FURNISHINGS_DATA = null;
</script>
```

- [ ] **Step 5: Verify the file opens without JS errors (data-less state)**

Open `colivingfurnish/index.html` directly in a browser. The page should render the wizard's left-panel layout (though broken without data). No console errors other than "Cannot read properties of null" (expected — data not loaded yet). If there are unrelated parse errors, fix the TweaksPanel removal first.

- [ ] **Step 6: Commit**

```bash
git add colivingfurnish/
git commit -m "feat: scaffold CoLivingFurnish — prototype base + PapaParse wired"
```

---

## Task 2: Update furnishings.csv

**Files:**
- Modify: `colivingfurnish/furnishings.csv`

The CSV needs two new columns (`tenant_types`, `climate_zones`) and new optional items per the agreed mapping. Required items leave these columns blank. Optional items that apply to everyone use `all`.

- [ ] **Step 1: Add `tenant_types` and `climate_zones` column headers**

Open `colivingfurnish/furnishings.csv` in Excel or a text editor. Add two columns at the end of the header row:

```
tenant_types,climate_zones
```

- [ ] **Step 2: Fill in existing optional items — assign tenant/climate values**

For each row where `Required = No`, fill in the new columns. Rules:
- Blank = shows for all (same as "all") — use this for optional items with no specific audience
- `all` = explicit show-for-all
- Comma-separated values, no spaces: `seniors,sober` or `cold,temperate`

Assignments for existing optional items:

| Item | tenant_types | climate_zones |
|---|---|---|
| Clothes hanger / closet organizer | all | |
| Curtain rod | all | |
| Blackout drapes | nurses,trades | |
| Blinds | all | |
| Register booster fan | nurses,trades | cold |
| Door chain | all | |
| Rolling / foldable shelving unit | students | |
| Fabric storage cubes | students | |
| Under bed storage | students | |
| Folding chairs | all | |
| Electric Tea Kettle | all | cold |
| Sofa / couch | all | |
| Coffee table | all | |
| Area rug(s) | all | |
| Side table(s) | seniors | |
| Storage ottoman | seniors,sober | |
| Shower curtain rod | all | |
| Shower curtain + liner | all | |
| Over-door hook organizer | seniors | |
| Vanity mirror | all | |
| Drying rack (foldable) | all | |
| WiFi mesh network | professionals,nomads | |
| WiFi gateway / router | professionals,nomads | |
| Key lockbox / keybox | all | |
| Non-smart punch-code lock | all | |
| Noise monitor | professionals | |
| Security camera (exterior only) | all | |
| Wall art / decor | all | |
| Whiteboard or corkboard | students,sober | |

- [ ] **Step 3: Add new optional items for climate: Cold**

Append these rows in the `Bedroom` section (after existing bedroom items):

```csv
Bedroom,Extra blanket / throw,"Warm extra layer for cold climates. Washable.",,,,,No,,20.00,20.00,1,,
Bedroom,Draft stopper,"Door draft blocker — reduces heat loss in cold rooms.",1,,,,No,,15.00,15.00,1,,
```

Append in `Tech & safety` or `Common area` section:

```csv
Common area optional,Space heater,"Portable ceramic heater. For rooms that run cold.",,,,,No,,45.00,45.00,1,,
```

Fill `tenant_types` = blank, `climate_zones` = `cold` for all three.

- [ ] **Step 4: Add new optional items for climate: Hot**

```csv
Bedroom,Tower / portable fan,"Supplements AC. Tower fan is quieter than box fans.",1,,,,No,,45.00,45.00,1,,
Bedroom,Cooling mattress pad,"Draws heat away from the body. Cold-side tech.",,,1,,No,,60.00,60.00,1,,
```

Fill `tenant_types` = blank, `climate_zones` = `hot`.

- [ ] **Step 5: Add new optional items per tenant type**

Add to appropriate room sections:

**Students:**
```csv
Common area optional,Bike hook / storage,"Wall-mounted hook for bicycle storage. Students frequently need this.",1,,,,No,,25.00,25.00,1,,
```
`tenant_types` = `students`, `climate_zones` = blank

**Professionals / Nomads (shared):**
```csv
Bedroom,Monitor stand / riser,"Raises laptop or monitor to ergonomic height.",1,,,,No,,30.00,30.00,1,,
Bedroom,USB-C charging hub,"Multi-port hub. Power strip + USB at the desk.",1,,,,No,,20.00,20.00,1,,
Bedroom,Desk lamp (task lighting),"Focused task light for desk work. Reduces eye strain.",1,,,,No,,35.00,35.00,1,,
Bedroom,Laptop stand,"Portable stand for laptop. Pairs with external keyboard.",1,,,,No,,25.00,25.00,1,,
Bedroom,Ring light,"Clip-on ring light for video calls.",1,,,,No,,20.00,20.00,1,,
```
`tenant_types` = `professionals,nomads`, `climate_zones` = blank

**Nurses / Trades:**
```csv
Bedroom,White noise machine,"Masks daytime noise for shift workers sleeping days.",1,,,,No,,30.00,30.00,1,,
Bedroom,Eye mask and earplugs kit,"Essentials for shift workers. Replace between tenants.",1,,,,No,,15.00,15.00,1,,
Bedroom,Mini fridge (bedroom),"Compact fridge for meals prepped off-hours.",1,,,,No,,80.00,80.00,1,,
```
`tenant_types` = `nurses,trades`, `climate_zones` = blank

**Seniors:**
```csv
Shared living room,Puzzles and board games,"Community activities. Popular in senior and sober households.",1,,,,No,,25.00,25.00,1,,
Shared living room,Reading chair (accent),"Comfortable reading chair for the living area.",1,,,,No,,150.00,150.00,1,,
Shared bathroom(s),Grab bar (bathroom),"Installed grab bar for safety. Mount to studs.",,,1,,No,,35.00,35.00,1,,
Shared bathroom(s),Extra non-slip bath mat,"Additional bath mat for safer footing.",,,1,,No,,12.00,12.00,1,,
```
`tenant_types` = `seniors` (or `seniors,sober` for puzzles/reading chair), `climate_zones` = blank

**Sober:**
```csv
Bedroom,Journaling kit,"Notebook and pen set. Supports well-being routines.",1,,,,No,,20.00,20.00,1,,
Bedroom,Meditation cushion / yoga mat,"Supports mindfulness routines in the room.",1,,,,No,,30.00,30.00,1,,
```
`tenant_types` = `sober`, `climate_zones` = blank

- [ ] **Step 6: Update window item prices to $20**

In the Bedroom section, find these three items and update `Cost Each` to `$20.00`:
- Curtain rod (currently `$10.00`)
- Blackout drapes (currently `$23.95`)
- Blinds (currently `$10.00`)

- [ ] **Step 7: Verify CSV structure**

Open the CSV in Excel or Google Sheets. Confirm:
- All rows have the same number of columns
- New `tenant_types` and `climate_zones` columns are present on every row (blank is fine for required items)
- No row has commas inside unquoted fields (quote any Notes fields with commas)
- Window items have `$20.00` in `Cost Each`

- [ ] **Step 8: Commit**

```bash
git add colivingfurnish/furnishings.csv
git commit -m "feat: add tenant_types + climate_zones columns, new optional items"
```

---

## Task 3: CSV Parser and Data Builder

**Files:**
- Modify: `colivingfurnish/index.html` — add `buildFurnishingsData()` function in the `<script type="text/babel">` block

This function takes PapaParse output and builds the `window.FURNISHINGS_DATA` structure the React app expects. Write and inline-test the pure helper functions first.

- [ ] **Step 1: Write inline test harness in `index.html`**

Inside `<script type="text/babel">`, at the top after `const { useState, useEffect, useRef, useMemo, useCallback } = React;`, add:

```js
function runTests() {
  const assert = (cond, msg) => {
    if (!cond) { console.error("FAIL:", msg); } else { console.log("PASS:", msg); }
  };
  // Tests will be added inline below
  return assert;
}
```

- [ ] **Step 2: Write and test `parseItemFilters(val)` — parses comma-separated filter column**

```js
function parseItemFilters(val) {
  const s = (val || "").toString().trim().toLowerCase();
  if (!s) return [];
  return s.split(",").map(v => v.trim()).filter(Boolean);
}
```

Test:

```js
const assert = runTests();
assert(parseItemFilters("").length === 0, "blank → empty array");
assert(parseItemFilters("all").length === 1, "all → ['all']");
assert(parseItemFilters("seniors,sober").length === 2, "two values parsed");
assert(parseItemFilters(" cold , hot ").includes("cold"), "values trimmed");
```

Run: open browser console after page load. Expected: 4 PASS lines.

- [ ] **Step 3: Write and test `isItemVisible(item, tenantType, climate)` — core filter function**

```js
function isItemVisible(item, tenantType, climate) {
  if (item.required) return true;

  const tt = item.tenant_types;
  const cz = item.climate_zones;

  const tenantOk = tt.length === 0 || tt.includes("all") || tt.includes(tenantType);
  const climateOk = cz.length === 0 || cz.includes("all") || cz.includes(climate);

  return tenantOk && climateOk;
}
```

Test:

```js
const req = { required: true, tenant_types: [], climate_zones: [] };
const optAll = { required: false, tenant_types: [], climate_zones: [] };
const optSeniors = { required: false, tenant_types: ["seniors"], climate_zones: [] };
const optCold = { required: false, tenant_types: [], climate_zones: ["cold"] };
const optBoth = { required: false, tenant_types: ["nurses"], climate_zones: ["cold"] };

assert(isItemVisible(req, "students", "hot"), "required always shows");
assert(isItemVisible(optAll, "students", "hot"), "blank cols → shows for all");
assert(isItemVisible(optSeniors, "seniors", "cold"), "seniors item shows for seniors");
assert(!isItemVisible(optSeniors, "students", "cold"), "seniors item hidden from students");
assert(isItemVisible(optCold, "students", "cold"), "cold item shows in cold");
assert(!isItemVisible(optCold, "students", "hot"), "cold item hidden in hot");
assert(isItemVisible(optBoth, "nurses", "cold"), "nurses+cold: both match");
assert(!isItemVisible(optBoth, "nurses", "hot"), "nurses+cold: wrong climate hidden");
assert(!isItemVisible(optBoth, "students", "cold"), "nurses+cold: wrong tenant hidden");
```

Run: 9 PASS lines expected in console.

- [ ] **Step 4: Write `computeMultiplier(item, beds, baths)` — scales cost by beds/baths**

```js
function computeMultiplier(item, beds, baths) {
  if (item.per_window) return 1;
  if (item.qty_per_bedroom > 0) return item.qty_per_bedroom * beds;
  if (item.qty_per_bath > 0) return item.qty_per_bath * baths;
  if (item.qty_per_home > 0) return item.qty_per_home;
  return 1;
}
```

Test:

```js
const bedItem = { per_window: false, qty_per_bedroom: 1, qty_per_bath: 0, qty_per_home: 0 };
const bathItem = { per_window: false, qty_per_bedroom: 0, qty_per_bath: 2, qty_per_home: 0 };
const homeItem = { per_window: false, qty_per_bedroom: 0, qty_per_bath: 0, qty_per_home: 3 };
const winItem  = { per_window: true,  qty_per_bedroom: 0, qty_per_bath: 0, qty_per_home: 0 };

assert(computeMultiplier(bedItem, 4, 2) === 4, "bed item ×4 beds");
assert(computeMultiplier(bathItem, 4, 2) === 4, "bath item ×2 baths × qty 2");
assert(computeMultiplier(homeItem, 4, 2) === 3, "home item fixed qty 3");
assert(computeMultiplier(winItem, 4, 2) === 1, "window item always ×1");
```

- [ ] **Step 5: Write `buildFurnishingsData(rows)` — converts PapaParse rows into `window.FURNISHINGS_DATA`**

```js
// Room ID mapping: CSV "Room / Area" value → stable room id
const ROOM_ID_MAP = {
  "bedroom": "bedroom",
  "shared kitchen": "kitchen",
  "shared living room": "living",
  "shared bathroom(s)": "bathroom",
  "laundry area": "laundry",
  "tech & safety": "tech",
  "common area": "common",
  "common area optional": "common",
};

// Room display config: id → { name, icon, story }
const ROOM_CONFIG = {
  bedroom: {
    name: "Private Bedroom", icon: "🛏",
    story: {
      students: "Students need a room that does double duty: a place to crash after late nights AND grind through coursework. The desk placement matters. Natural light in the morning helps regulate sleep. Storage is always the pain point — they never have enough.",
      professionals: "Working professionals often bring less than they think they need, and quickly realize they need more than they brought. A great desk setup and blackout curtains are the non-negotiables. Think: hotel room that actually feels like home.",
      seniors: "For 55+ tenants, the bedroom is a sanctuary. Accessibility matters — no sharp corners, good lighting, easy-to-reach storage. A comfortable chair for reading makes a room feel complete, not just functional.",
      trades: "Construction and trades workers keep irregular hours and need solid blackout curtains, a durable mattress, and simple storage. Less is more — they want easy maintenance.",
      nurses: "Traveling nurses work rotating shifts and sleep at odd hours. Blackout curtains are essential. Noise machines help. The room should feel calming and instantly familiar.",
      nomads: "Digital nomads treat the bedroom as a base of operations. Fast WiFi access point nearby, a monitor stand on the desk, and good lighting for video calls are the true essentials.",
      sober: "For sober living tenants, the bedroom should feel safe, calm, and welcoming. Personal touches like good lighting and a comfortable reading chair support well-being and a sense of ownership.",
      default: "Every bedroom tells a story the moment a new tenant walks in. The right furnishings — a quality mattress, thoughtful lighting, and real storage — turn a room into a home within hours."
    }
  },
  kitchen: {
    name: "Shared Kitchen", icon: "🍳",
    story: {
      students: "A student kitchen needs to survive everything from ramen at midnight to meal-prep Sundays. Label-able shelf space, a big enough fridge, and a kitchen table that fits everyone — these are the essentials that make shared cooking feel collaborative, not chaotic.",
      professionals: "Working professionals often meal-prep on Sundays and grab-and-go during the week. A well-equipped kitchen with quality appliances and clearly defined storage prevents the friction that kills housemate relationships.",
      seniors: "For 55+ tenants, the kitchen should feel familiar and accessible. Good overhead lighting, easy-to-open storage, and quality appliances signal that this isn't temporary housing — it's a real home.",
      trades: "Construction workers often have early starts and need a kitchen that's easy to use at 5am. A good coffee maker, easy-clean surfaces, and a large fridge are the priorities.",
      default: "The shared kitchen is where housemates become neighbors and neighbors become community. The right layout and appliances can turn daily cooking into a shared ritual instead of a daily negotiation."
    }
  },
  living: {
    name: "Shared Living Room", icon: "🛋",
    story: {
      students: "The shared living room in a student house becomes the social hub — the place where friendships form over late-night study sessions and weekend hangouts. It needs to handle everything from Netflix marathons to impromptu board game nights.",
      professionals: "Working professionals use the common area as a decompression zone. After a long day, it's where they decompress, connect with housemates, or take a work call from the couch. It should feel polished, not chaotic.",
      seniors: "For 55+ tenants, the shared living room is often the heart of community. Comfortable seating, good lighting, and a TV at the right height make it a place they actually want to spend time.",
      sober: "The shared living room in a sober living home is especially important — it's a safe, welcoming space for community and support. Comfortable, non-institutional furniture signals care and respect.",
      default: "The shared living room sets the tone for the entire home. It's the first space new tenants see and the last they remember. Get this right and the whole house feels like a home."
    }
  },
  bathroom: {
    name: "Shared Bathroom(s)", icon: "🚿",
    story: {
      default: "A shared bathroom is the most personal shared space in any co-living home — and the one most likely to cause friction if not set up right. Designated shelf space, good lighting, and enough hooks and towel bars go around make the difference between a functional bathroom and a daily argument."
    }
  },
  laundry: {
    name: "Laundry Area", icon: "🧺",
    story: {
      default: "Often the most overlooked room in a co-living home, the laundry area can become a major pain point without the right setup. Clear days and times for laundry, proper supplies, and a folding surface transform a functional necessity into a smooth operation."
    }
  },
  tech: {
    name: "Tech & Safety", icon: "🔐",
    story: {
      professionals: "For professional tenants, reliable WiFi and a secure smart lock are non-negotiable. The tech setup is often what seals the deal — operators who get this right have much lower turnover.",
      nomads: "Digital nomads will specifically ask about your WiFi setup before signing. Mesh coverage, backup hardware, and the right router are worth the investment if nomads are your tenant profile.",
      default: "The tech and safety layer of a co-living home is invisible when it works and catastrophic when it doesn't. Smart locks, smoke detectors, and reliable WiFi are the backbone of a well-run property."
    }
  },
  common: {
    name: "Common Areas", icon: "🏠",
    story: {
      default: "Common areas set the first impression and daily tone of the home. A well-stocked entryway, clean hallways, and thoughtful shared touches signal to tenants that the operator cares — and that signal translates directly into satisfaction and tenure."
    }
  }
};

// Room-level swatch colors (since CSV has no category column)
const ROOM_SWATCHES = {
  "bedroom":  ["#e8d5c4", "#c4a882"],
  "kitchen":  ["#d8dce4", "#7888a0"],
  "living":   ["#e0d4c4", "#a08060"],
  "bathroom": ["#cce0e4", "#5890a0"],
  "laundry":  ["#dce0e8", "#7880a0"],
  "tech":     ["#d0d8e8", "#6878a8"],
  "common":   ["#dce4e0", "#70a090"],
};

function buildFurnishingsData(rows) {
  const num = (v) => parseFloat((v || "").toString().replace(/[$,\s]/g, "")) || 0;
  const clean = (v) => (v || "").toString().trim();

  // Room order for sidebar display
  const ROOM_ORDER = ["bedroom", "kitchen", "living", "bathroom", "laundry", "tech", "common"];
  const roomMap = {};

  rows.forEach((row, idx) => {
    const rawRoom = clean(row["Room / Area"]);
    if (!rawRoom) return; // skip blank/summary rows

    const roomId = ROOM_ID_MAP[rawRoom.toLowerCase()];
    if (!roomId) return; // skip unknown rooms

    if (!roomMap[roomId]) {
      roomMap[roomId] = { ...ROOM_CONFIG[roomId], id: roomId, items: [] };
    }

    const item = {
      id: `row_${idx}`,
      name: clean(row["Item"]),
      notes: clean(row["Notes"]),
      room: roomId,
      required: clean(row["Required"]).toLowerCase() === "yes",
      link: clean(row["Affiliate URL"]),
      price_low: Math.max(0, num(row["Cost Each"])),
      qty_per_home: num(row["Min Quantity per home"]),
      qty_per_bedroom: num(row["Min Quantity per Bedroom"]),
      qty_per_bath: num(row["Min Quantity per Bath"]),
      qty_per_window: num(row["Quantity per window"]),
      per_window: num(row["Quantity per window"]) > 0,
      tenant_types: parseItemFilters(row["tenant_types"]),
      climate_zones: parseItemFilters(row["climate_zones"]),
      category: roomId, // used by ItemImage for swatch lookup
    };

    if (item.name) roomMap[roomId].items.push(item);
  });

  return {
    rooms: ROOM_ORDER.filter(id => roomMap[id]).map(id => roomMap[id]),
    tenantTypes: [
      { id: "students",      label: "Students / Young Adults",  icon: "🎓" },
      { id: "professionals", label: "Working Professionals",    icon: "💼" },
      { id: "seniors",       label: "55+ / Seniors",            icon: "🌿" },
      { id: "nurses",        label: "Traveling Nurses",         icon: "🏥" },
      { id: "trades",        label: "Construction / Trades",    icon: "🔨" },
      { id: "nomads",        label: "Digital Nomads",           icon: "💻" },
      { id: "sober",         label: "Sober Living",             icon: "🤝" },
    ],
    climateZones: [
      { id: "cold",       label: "Cold / Northern",    description: "Zone 5–8 · Heavy winters, insulation critical", color: "#4a90d9" },
      { id: "temperate",  label: "Temperate / Mixed",  description: "Zone 3–4 · Mild seasons, year-round use",       color: "#5a9e6f" },
      { id: "hot",        label: "Hot / Southern",     description: "Zone 1–2 · Warm year-round, cooling essential", color: "#d97b4a" },
    ]
  };
}
```

- [ ] **Step 6: Update `ItemImage` to use room-level swatches**

Find the `ItemImage` function. Replace the `colors` object lookup with:

```js
function ItemImage({ keyword, size = 56 }) {
  const [bg, stroke] = ROOM_SWATCHES[keyword] || ["#e8e4dc", "#a09880"];
  const initial = keyword ? keyword[0].toUpperCase() : "?";
  return (
    <div style={{
      width: size, height: size, borderRadius: 12, background: bg,
      display: "flex", alignItems: "center", justifyContent: "center",
      flexShrink: 0, border: `1.5px solid ${stroke}30`
    }}>
      <span style={{ fontFamily: "var(--font-display)", fontSize: size * 0.38, fontWeight: 700, color: stroke, opacity: 0.7 }}>{initial}</span>
    </div>
  );
}
```

- [ ] **Step 7: Commit**

```bash
git add colivingfurnish/index.html
git commit -m "feat: CSV parser, filter logic, swatch mapping — all tests passing"
```

---

## Task 4: Wire CSV Into the App

**Files:**
- Modify: `colivingfurnish/index.html` — update `App` component to fetch CSV on mount

- [ ] **Step 1: Add `dataReady` state and loading screen to `App`**

Replace the existing `App` function with:

```js
const STORAGE_KEY = "clf-project-v1";

function App() {
  const [project, setProject] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });
  const [dataReady, setDataReady] = useState(false);
  const [dataError, setDataError] = useState(null);

  useEffect(() => {
    if (project) localStorage.setItem(STORAGE_KEY, JSON.stringify(project));
    else localStorage.removeItem(STORAGE_KEY);
  }, [project]);

  useEffect(() => {
    Papa.parse("furnishings.csv", {
      download: true,
      header: true,
      skipEmptyLines: true,
      transformHeader: h => h.trim(),
      complete: (results) => {
        window.FURNISHINGS_DATA = buildFurnishingsData(results.data);
        setDataReady(true);
      },
      error: (err) => {
        setDataError(err.message);
      }
    });
  }, []);

  function handleComplete(data) { setProject(data); }
  function handleReset() {
    if (window.confirm("Start a new project? Your current checklist will be cleared.")) {
      setProject(null);
    }
  }

  if (dataError) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--cream)", flexDirection: "column", gap: 16 }}>
        <Logo />
        <p style={{ color: "var(--terracotta)", fontSize: 15 }}>Could not load furnishings data: {dataError}</p>
        <p style={{ color: "var(--text-muted)", fontSize: 13 }}>Ensure <code>furnishings.csv</code> is in the same folder as <code>index.html</code> and you're serving via a local server, not opening the file directly.</p>
      </div>
    );
  }

  if (!dataReady) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--cream)", flexDirection: "column", gap: 24 }}>
        <Logo size={32} />
        <div style={{ fontSize: 14, color: "var(--text-muted)" }}>Loading furnishing data…</div>
        <div style={{
          width: 40, height: 40, borderRadius: "50%",
          border: "3px solid var(--cream-dark)",
          borderTop: "3px solid var(--terracotta)",
          animation: "spin 0.8s linear infinite"
        }} />
      </div>
    );
  }

  if (!project) return <Wizard onComplete={handleComplete} />;
  return <Dashboard project={project} onReset={handleReset} />;
}
```

Also add the `spin` keyframe to the `<style>` block:

```css
@keyframes spin {
  to { transform: rotate(360deg); }
}
```

- [ ] **Step 2: Serve the project locally and verify CSV loads**

Since PapaParse's `download: true` uses `fetch()`, you must serve from a local server (not `file://`). From the project root:

```bash
cd colivingfurnish && python -m http.server 8080
```

Open `http://localhost:8080`. Expected:
- Brief loading spinner appears
- Wizard renders with all 4 steps working
- Browser console: no errors; `window.FURNISHINGS_DATA.rooms.length` should be 7

- [ ] **Step 3: Verify wizard completes and dashboard loads with real data**

Walk through all 4 wizard steps (enter any address, pick 3 beds / 2 baths, pick "Students", pick "Cold"). Expected:
- Dashboard renders with rooms from the CSV
- Bedroom accordion shows real items from the CSV (Queen or full bed frame, Mattress, etc.)
- No console errors

- [ ] **Step 4: Commit**

```bash
git add colivingfurnish/index.html
git commit -m "feat: CSV fetch on mount, loading screen, error state"
```

---

## Task 5: Filtering Logic

**Files:**
- Modify: `colivingfurnish/index.html` — update `RoomSection`, `Dashboard` allItems, and sidebar room progress to use `isItemVisible`

- [ ] **Step 1: Update `RoomSection.visibleItems` to use the new filter**

Find `RoomSection`. Replace the `visibleItems` useMemo:

```js
const visibleItems = useMemo(() => {
  return room.items
    .filter(item => isItemVisible(item, tenantType, climate))
    .sort((a, b) => (b.required ? 1 : 0) - (a.required ? 1 : 0));
}, [room.items, tenantType, climate]);
```

- [ ] **Step 2: Update `Dashboard.allItems` to use `isItemVisible` and `computeMultiplier`**

Find `const allItems = useMemo(...)`. Replace with:

```js
const allItems = useMemo(() => {
  const rooms = window.FURNISHINGS_DATA.rooms;
  return rooms.flatMap(r =>
    r.items
      .filter(item => isItemVisible(item, project.tenantType, project.climate))
      .map(item => ({
        ...item,
        _roomId: r.id,
        _multiplier: computeMultiplier(item, project.beds, project.baths)
      }))
  );
}, [project.tenantType, project.climate, project.beds, project.baths]);
```

- [ ] **Step 3: Update sidebar room progress to use `isItemVisible`**

In the sidebar `rooms.map(room => ...)` block, find the `roomItems` filter:

```js
const roomItems = room.items.filter(item =>
  item.climate_zones.includes(project.climate) &&
  (item.tenant_types.includes("all") || item.tenant_types.includes(project.tenantType))
);
```

Replace with:

```js
const roomItems = room.items.filter(item =>
  isItemVisible(item, project.tenantType, project.climate)
);
```

- [ ] **Step 4: Verify filtering works in the browser**

Serve locally. Complete the wizard with:
1. "Students" + "Cold" → optional section in Bedroom should show: Register booster fan, Fabric storage cubes, Under-bed storage, Extra blanket/throw, Draft stopper, Blackout drapes (nurses/trades only — should NOT show for students). Confirm register booster fan appears (cold + no tenant filter) and blackout drapes do NOT appear (nurses,trades only).
2. "Nurses" + "Cold" → Blackout drapes SHOULD appear. Mini fridge SHOULD appear.
3. "Seniors" + "Temperate" → Puzzles and board games SHOULD appear. Draft stopper should NOT.

Fix any mismatches in the CSV `tenant_types`/`climate_zones` columns.

- [ ] **Step 5: Commit**

```bash
git add colivingfurnish/
git commit -m "feat: filtering logic wired — required always shows, optional filtered by tenant/climate"
```

---

## Task 6: Window Item Price Display

**Files:**
- Modify: `colivingfurnish/index.html` — update `ItemRow` and `BudgetBar` for per-window items

- [ ] **Step 1: Update `ItemRow` price display for window items**

Find `ItemRow`. Replace the `priceRange` computation:

```js
const mult = item._multiplier || 1;
const priceLow = item.price_low;
const priceHigh = pH(item);

const priceRange = item.per_window
  ? `$${priceLow}–$${priceHigh} per window`
  : mult > 1
    ? `$${priceLow * mult}–$${priceHigh * mult} (×${mult})`
    : `$${priceLow}–$${priceHigh}`;
```

- [ ] **Step 2: Verify window items show correct price label in browser**

Open the Bedroom room, expand Optional section (with a tenant type that shows curtain items — e.g., "all" tenant). Curtain rod, Blackout drapes, and Blinds should all show:
- `$20–$26 per window`

Other bedroom items (e.g., Queen Mattress for 4 beds) should show:
- `$98–$128 (×4)`

- [ ] **Step 3: Confirm budget bar excludes per-window items from scaling**

Per-window items have `_multiplier = 1` from `computeMultiplier`. The `BudgetBar` already uses `_multiplier` via `pMid(i) * (i._multiplier || 1)`. Since window items use ×1, they contribute their mid-price once to the budget — correct floor behavior.

Open browser, check a window item. Verify the budget bar increases by roughly $23 (mid of $20–$26) when a window item is checked.

- [ ] **Step 4: Commit**

```bash
git add colivingfurnish/index.html
git commit -m "feat: window items show 'per window' price, budget uses floor qty 1"
```

---

## Task 7: Mobile Responsive Layout

**Files:**
- Modify: `colivingfurnish/index.html` — add `@media (max-width: 767px)` CSS rules, update Wizard and Dashboard JSX for mobile

- [ ] **Step 1: Add mobile CSS to the `<style>` block**

Add after the `@keyframes fadeUp` rule:

```css
/* ── Mobile breakpoint ─────────────────────────────── */
@media (max-width: 767px) {
  /* Wizard: hide right panel, go full width */
  .wizard-layout { grid-template-columns: 1fr !important; }
  .wizard-right  { display: none !important; }
  .wizard-left   { padding: 32px 24px !important; max-width: 100% !important; }

  /* Dashboard nav: compact */
  .dash-nav-address { display: none !important; }
  .dash-nav         { padding: 0 16px !important; gap: 10px !important; }

  /* Dashboard layout: single column */
  .dash-layout   { grid-template-columns: 1fr !important; padding: 16px !important; }
  .dash-sidebar  { display: none !important; }
  .dash-tabs     { display: flex !important; }

  /* Hero bar: stack */
  .hero-inner    { flex-direction: column !important; gap: 16px !important; }
  .hero-stats    { flex-wrap: wrap !important; gap: 12px !important; }

  /* Items: make touch targets larger */
  .item-row      { padding: 16px !important; min-height: 56px; }
}
```

- [ ] **Step 2: Add `className` props to Wizard layout divs**

Find the `Wizard` return statement. Add `className="wizard-layout"` to the outer grid div, `className="wizard-left"` to the left panel div, and `className="wizard-right"` to the right panel div:

```jsx
<div className="wizard-layout" style={{ minHeight: "100vh", display: "grid", gridTemplateColumns: "1fr 1fr", background: "var(--cream)" }}>
  <div className="wizard-left" style={{ display: "flex", flexDirection: "column", justifyContent: "center", padding: "48px clamp(32px, 6vw, 80px)", maxWidth: 640, margin: "0 auto", width: "100%" }}>
    {/* ... */}
  </div>
  <div className="wizard-right" style={{ background: "#1e1c18", /* ... */ }}>
    {/* ... */}
  </div>
</div>
```

- [ ] **Step 3: Add class names to Dashboard layout elements**

```jsx
{/* nav */}
<nav className="dash-nav" style={{ ... }}>
  <div className="dash-nav-address" style={{ ... }}>📍 {project.address}</div>
  {/* ... */}
</nav>

{/* hero inner */}
<div className="hero-inner" style={{ maxWidth: 1100, margin: "0 auto", display: "flex", flexWrap: "wrap", gap: 32, alignItems: "center" }}>
  {/* ... */}
  <div className="hero-stats" style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
    {/* ... */}
  </div>
</div>

{/* main grid */}
<div className="dash-layout" style={{ flex: 1, maxWidth: 1100, margin: "0 auto", width: "100%", padding: "32px clamp(16px, 4vw, 48px)", display: "grid", gridTemplateColumns: "240px 1fr", gap: 32, alignItems: "start" }}>
  <div className="dash-sidebar" style={{ position: "sticky", top: 80 }}>
    {/* ... */}
  </div>
  {/* room detail */}
</div>
```

- [ ] **Step 4: Add horizontal room tab strip for mobile (hidden on desktop)**

Inside `Dashboard`, add a `MobileTabs` component rendered just below the hero bar. It is hidden on desktop via `display: none` and shown on mobile via `display: flex`:

```jsx
function MobileTabs({ rooms, activeRoom, onSelect, project, checked }) {
  return (
    <div className="dash-tabs" style={{
      display: "none",  /* shown via CSS on mobile */
      overflowX: "auto", gap: 8, padding: "12px 16px",
      background: "white", borderBottom: "1px solid var(--border)"
    }}>
      {rooms.map(room => {
        const roomItems = room.items.filter(item =>
          isItemVisible(item, project.tenantType, project.climate)
        );
        const roomChecked = roomItems.filter(i => checked[i.id]).length;
        const pct = roomItems.length > 0 ? Math.round((roomChecked / roomItems.length) * 100) : 0;
        const isAct = activeRoom === room.id;
        return (
          <button key={room.id} onClick={() => onSelect(room.id)} style={{
            flexShrink: 0, padding: "8px 14px", borderRadius: 20,
            border: `1.5px solid ${isAct ? "var(--terracotta)" : "var(--border)"}`,
            background: isAct ? "rgba(192,96,58,0.08)" : "white",
            fontFamily: "var(--font-body)", fontSize: 13, fontWeight: 600,
            color: isAct ? "var(--terracotta)" : "var(--charcoal)", cursor: "pointer",
            whiteSpace: "nowrap", minHeight: 44
          }}>
            {room.icon} {room.name} <span style={{ color: "var(--text-muted)", fontWeight: 400, fontSize: 11 }}>{pct}%</span>
          </button>
        );
      })}
    </div>
  );
}
```

Render it in `Dashboard` between the hero bar and main content:

```jsx
<MobileTabs
  rooms={window.FURNISHINGS_DATA.rooms}
  activeRoom={activeRoom}
  onSelect={setActiveRoom}
  project={project}
  checked={checked}
/>
```

Also add the Budget Tracker below the room accordion on mobile. Add inside `dash-layout` after the room detail div:

```jsx
{/* Mobile budget bar — visible below accordion on mobile */}
<div className="mobile-budget" style={{ display: "none" }}>
  <BudgetBar items={allItems} checked={checked} />
</div>
```

Add to CSS: `.mobile-budget { display: none; } @media (max-width: 767px) { .mobile-budget { display: block !important; } }`

- [ ] **Step 5: Verify mobile layout in browser DevTools**

Open `http://localhost:8080` and toggle DevTools mobile emulation (375px width, iPhone). Expected:
- Wizard: single column, no dark right panel
- Dashboard: room tabs visible below hero, no sidebar, accordion full width
- Budget tracker appears below accordion
- All touch targets at least 44px tall
- No horizontal scroll on any screen

Fix any overflow or layout issues.

- [ ] **Step 6: Commit**

```bash
git add colivingfurnish/index.html
git commit -m "feat: mobile responsive — wizard single column, dashboard tab strip"
```

---

## Task 8: Print Checklist

**Files:**
- Modify: `colivingfurnish/index.html` — add print CSS and Print button

- [ ] **Step 1: Add `@media print` CSS to `<style>` block**

```css
/* ── Print styles ──────────────────────────────────── */
@media print {
  .no-print     { display: none !important; }
  .print-header { display: block !important; }
  body          { background: white; font-size: 12px; }
  nav, .dash-sidebar, .dash-tabs, .mobile-budget,
  .wizard-right, .hero-bar, .export-modal-overlay { display: none !important; }
  .dash-layout  { display: block !important; padding: 0 !important; }
  .print-header { margin-bottom: 24px; border-bottom: 2px solid #1e1c18; padding-bottom: 12px; }
  .room-section { page-break-inside: avoid; margin-bottom: 24px; }
  .item-row     { padding: 6px 0 !important; border-bottom: 1px solid #eee !important; background: transparent !important; border-radius: 0 !important; }
  .find-link    { font-size: 10px; color: #555 !important; background: transparent !important; }
  .optional-hidden { display: none !important; }
}
```

- [ ] **Step 2: Add `PrintHeader` component — shown only in print**

```jsx
function PrintHeader({ project }) {
  const tenantLabel = window.FURNISHINGS_DATA.tenantTypes.find(t => t.id === project.tenantType)?.label || project.tenantType;
  const climateLabel = window.FURNISHINGS_DATA.climateZones.find(z => z.id === project.climate)?.label || project.climate;
  const today = new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
  return (
    <div className="print-header" style={{ display: "none" }}>
      <div style={{ fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 700, marginBottom: 6 }}>
        CoLivingFurnish — Furnishing Checklist
      </div>
      <div style={{ fontSize: 13, color: "#555", marginBottom: 4 }}>
        <strong>{project.address}</strong>
      </div>
      <div style={{ fontSize: 12, color: "#777" }}>
        {project.beds} private bedroom{project.beds > 1 ? "s" : ""} · {project.baths} bathroom{project.baths > 1 ? "s" : ""} · {tenantLabel} · {climateLabel} Climate · Generated {today}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Add "Print Checklist" button to nav (next to Export)**

Find the Export button in the `Dashboard` nav. Add the Print button before it:

```jsx
<button
  className="no-print"
  onClick={() => window.print()}
  style={{
    padding: "8px 18px", background: "white",
    color: "var(--charcoal)", border: "1px solid var(--border)",
    borderRadius: 20, fontSize: 13, fontWeight: 600,
    cursor: "pointer", fontFamily: "var(--font-body)"
  }}
>🖨 Print</button>
```

- [ ] **Step 4: Render `PrintHeader` inside `Dashboard` (before main content)**

```jsx
<PrintHeader project={project} />
```

Place immediately after the closing `</nav>` tag in the Dashboard return.

- [ ] **Step 5: Mark unchecked optional items as hidden in print**

In `RoomSection`, the optional items are already toggled by `showOptional`. For print, we want:
- Required items: always print
- Checked optional items: print
- Unchecked optional items: skip

Wrap optional items section in a `no-print-if-unchecked` container and add CSS rule:

In the `optionalItems.map` render, wrap each `ItemRow` with:

```jsx
<div key={item.id} className={!checked[item.id] ? "optional-hidden" : ""}>
  <ItemRow item={item} checked={checked} onToggle={onToggle} />
</div>
```

The `optional-hidden` class is hidden in print (added in Step 1 CSS).

- [ ] **Step 6: Verify print output**

Complete the wizard and check a few items. Click "🖨 Print". Expected print preview:
- Nav, sidebar, hero bar: hidden
- Property header visible at top
- Room sections list with:
  - Required items (all, including unchecked)
  - Only checked optional items
- Affiliate links visible as small text on each item row
- No interactive elements showing

If the browser print dialog opens but preview looks wrong, check the `@media print` CSS class names match what's in the JSX.

- [ ] **Step 7: Commit**

```bash
git add colivingfurnish/index.html
git commit -m "feat: print checklist — @media print layout, print button in nav"
```

---

## Task 9: Smoke Test and Deploy Prep

**Files:**
- Read-only verification — no code changes expected

- [ ] **Step 1: Full wizard flow — Students + Cold**

1. Clear localStorage (`localStorage.clear()` in console)
2. Enter address "123 Test St, Chicago IL"
3. Set 4 beds, 2 baths
4. Select "Students"
5. Select "Cold"
6. Complete wizard

Verify dashboard:
- 7 rooms visible in sidebar/tabs
- Bedroom shows required items including Queen/full bed frame, Mattress, etc.
- Optional section shows: Register booster fan, Fabric storage cubes, Under-bed storage, Extra blanket/throw, Whiteboard/corkboard — but NOT blackout drapes, NOT mini fridge
- Budget tracker shows total required budget range for 4 bedrooms

- [ ] **Step 2: Full wizard flow — Nurses + Hot**

1. Start new project
2. Select "Nurses", "Hot"

Verify:
- Optional bedroom items: Blackout drapes ✓, Mini fridge ✓, White noise machine ✓
- Tower/portable fan ✓, Cooling mattress pad ✓
- Register booster fan should NOT appear (cold climate only)

- [ ] **Step 3: Full wizard flow — Seniors + Temperate**

Verify:
- Puzzles and board games ✓ (living room)
- Reading chair ✓ (living room)
- Grab bar ✓ (bathroom)
- Side tables ✓ (living room)
- Draft stopper should NOT appear (cold only)

- [ ] **Step 4: Check a few items and print**

Check 5–6 items. Click "🖨 Print". Verify:
- Only checked optional items appear in print
- All required items appear in print
- Budget summary at bottom of export modal is accurate

- [ ] **Step 5: Verify restore from localStorage**

Reload the page. The dashboard should restore automatically without showing the wizard. Check that previously checked items are still checked.

- [ ] **Step 6: Verify "New Project" clears state**

Click "New Project" → confirm → wizard should show. Previous checked state should be gone.

- [ ] **Step 7: Prepare for Netlify deploy**

Ensure `colivingfurnish/` folder contains exactly:
- `index.html`
- `furnishings.csv`

To test the Netlify behavior (serving from root), you can run:

```bash
cd colivingfurnish && python -m http.server 8080
```

Then open `http://localhost:8080/index.html` and confirm everything works (PapaParse fetches `furnishings.csv` relative to the HTML file).

- [ ] **Step 8: Final commit**

```bash
git add colivingfurnish/
git commit -m "feat: CoLivingFurnish v1 complete — CSV-driven, mobile, print export"
```

---

## Self-Review Notes

**Spec coverage check:**
- ✅ Standalone deployment (Netlify, 2 files)
- ✅ 4-step wizard (address, beds/baths, tenant type, climate)
- ✅ Required items always show
- ✅ Optional items filter by tenant_types + climate_zones (blank = all)
- ✅ Window items: $20 min, "per window" display, no multiplier
- ✅ Budget tracker: required bar (terracotta) + optional bar (sage)
- ✅ Export: clipboard copy (existing) + print checklist (new)
- ✅ Mobile responsive: wizard single-column, dashboard horizontal tabs
- ✅ Room Notes: prototype stories kept, new stories for Tech & Common
- ✅ Color swatches: room-level (bedroom = sleeping colors, etc.)
- ✅ New optional items: all 7 tenant types + 2 climate zones covered
- ✅ localStorage: project state + checked state keyed by address

**Known limitations (out of scope for v1):**
- Opening `index.html` directly as `file://` will fail (PapaParse fetch requires HTTP server). Must use `python -m http.server` locally or deploy to Netlify.
- Row index IDs (`row_5`) will break checked state if CSV row order changes — acceptable for v1.
