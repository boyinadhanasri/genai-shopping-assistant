/* ============================================================
   Shelfie — GenAI Shopping Assistant frontend
   This file is a working PROTOTYPE: it runs entirely on mock
   catalog data so the UI is demoable with no backend running.

   Where your real backend plugs in is marked clearly below with
   "BACKEND HOOK". Swap MOCK_CATALOG + fakeAssistantTurn() for a
   fetch() call to your FastAPI/Flask endpoint and everything else
   (rendering, compare tray, history) keeps working unchanged.
   ============================================================ */

// ---------- MOCK CATALOG (stand-in for OpenSearch + FAISS results) ----------
const MOCK_CATALOG = {
  "Electronics": [
    {
      "id": "FKP0000156",
      "brand": "Adidas",
      "title": "Adidas Prime 262",
      "price": 16670.28,
      "rating": 5.0,
      "specs": {
        "color": "Silver",
        "size": "XL",
        "warranty_months": 0,
        "weight_g": 425.72
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000226",
      "brand": "Boat",
      "title": "Boat Series 871",
      "price": 28444.06,
      "rating": 5.0,
      "specs": {
        "color": "Black",
        "size": "S",
        "warranty_months": 24,
        "weight_g": 623.43
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000622",
      "brand": "LG",
      "title": "LG Ultra 912",
      "price": 13546.27,
      "rating": 5.0,
      "specs": {
        "color": "Black",
        "warranty_months": 6,
        "weight_g": 3294.67,
        "delivery_days": 4
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    }
  ],
  "Mobiles": [
    {
      "id": "FKP0000140",
      "brand": "Sony",
      "title": "Sony Series 975",
      "price": 13828.71,
      "rating": 5.0,
      "specs": {
        "color": "White",
        "size": "One Size",
        "warranty_months": 6,
        "weight_g": 364.84
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000249",
      "brand": "Reebok",
      "title": "Reebok Ultra 909",
      "price": 37354.42,
      "rating": 5.0,
      "specs": {
        "color": "Grey",
        "size": "One Size",
        "warranty_months": 6,
        "weight_g": 3614.79
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000293",
      "brand": "Samsung",
      "title": "Samsung Model 392",
      "price": 9284.59,
      "rating": 5.0,
      "specs": {
        "color": "Red",
        "size": "One Size",
        "warranty_months": 24,
        "weight_g": 1968.04
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    }
  ],
  "Appliances": [
    {
      "id": "FKP0000268",
      "brand": "LG",
      "title": "LG Ultra 138",
      "price": 51948.52,
      "rating": 5.0,
      "specs": {
        "color": "Black",
        "size": "XL",
        "warranty_months": 0,
        "weight_g": 720.41
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000734",
      "brand": "Dell",
      "title": "Dell Prime 529",
      "price": 32523.22,
      "rating": 5.0,
      "specs": {
        "color": "White",
        "size": "L",
        "warranty_months": 24,
        "weight_g": 3284.2
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000412",
      "brand": "LG",
      "title": "LG Model 443",
      "price": 10703.58,
      "rating": 4.9,
      "specs": {
        "color": "White",
        "size": "One Size",
        "warranty_months": 0,
        "weight_g": 2769.87
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    }
  ],
  "Home & Kitchen": [
    {
      "id": "FKP0000260",
      "brand": "Prestige",
      "title": "Prestige Ultra 97",
      "price": 444.01,
      "rating": 5.0,
      "specs": {
        "color": "Silver",
        "warranty_months": 12,
        "weight_g": 1762.44,
        "delivery_days": 7
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000535",
      "brand": "Dell",
      "title": "Dell Edition 169",
      "price": 17495.57,
      "rating": 4.9,
      "specs": {
        "color": "Grey",
        "size": "L",
        "warranty_months": 24,
        "weight_g": 158.36
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000148",
      "brand": "Prestige",
      "title": "Prestige Series 415",
      "price": 3623.8,
      "rating": 4.8,
      "specs": {
        "color": "Blue",
        "size": "L",
        "warranty_months": 0,
        "weight_g": 4163.95
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    }
  ],
  "Fashion": [
    {
      "id": "FKP0000677",
      "brand": "LG",
      "title": "LG Prime 349",
      "price": 19921.74,
      "rating": 5.0,
      "specs": {
        "color": "Green",
        "size": "S",
        "warranty_months": 36,
        "weight_g": 559.08
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000975",
      "brand": "Sony",
      "title": "Sony Edition 688",
      "price": 10194.98,
      "rating": 5.0,
      "specs": {
        "color": "Green",
        "size": "XL",
        "warranty_months": 6,
        "weight_g": 288.97
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000017",
      "brand": "Samsung",
      "title": "Samsung Series 442",
      "price": 2430.58,
      "rating": 4.9,
      "specs": {
        "color": "Red",
        "size": "XL",
        "warranty_months": 36,
        "weight_g": 4206.14
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    }
  ],
  "Beauty": [
    {
      "id": "FKP0001008",
      "brand": "Dell",
      "title": "Dell Series 984",
      "price": 6058.67,
      "rating": 5.0,
      "specs": {
        "color": "Grey",
        "size": "XL",
        "warranty_months": 0,
        "weight_g": 3483.17
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000492",
      "brand": "Apple",
      "title": "Apple Model 586",
      "price": 35377.46,
      "rating": 4.9,
      "specs": {
        "color": "Blue",
        "size": "XL",
        "warranty_months": 36,
        "weight_g": 158.62
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000676",
      "brand": "Boat",
      "title": "Boat Model 559",
      "price": 12884.95,
      "rating": 4.9,
      "specs": {
        "color": "Grey",
        "size": "S",
        "warranty_months": 6,
        "weight_g": 1308.22
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    }
  ],
  "Sports": [
    {
      "id": "FKP0000514",
      "brand": "Apple",
      "title": "Apple Model 636",
      "price": 26984.67,
      "rating": 5.0,
      "specs": {
        "color": "Blue",
        "size": "M",
        "warranty_months": 36,
        "weight_g": 2676.06
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0001129",
      "brand": "LG",
      "title": "LG Series 261",
      "price": 9579.48,
      "rating": 5.0,
      "specs": {
        "color": "White",
        "warranty_months": 36,
        "weight_g": 4056.84,
        "delivery_days": 1
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000251",
      "brand": "HP",
      "title": "HP Edition 836",
      "price": 24210.87,
      "rating": 4.9,
      "specs": {
        "color": "Red",
        "size": "XL",
        "warranty_months": 24,
        "weight_g": 4268.83
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    }
  ],
  "Toys": [
    {
      "id": "FKP0000257",
      "brand": "Sony",
      "title": "Sony Edition 590",
      "price": 39133.41,
      "rating": 5.0,
      "specs": {
        "color": "Black",
        "size": "XL",
        "warranty_months": 0,
        "weight_g": 1172.67
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000922",
      "brand": "LG",
      "title": "LG Prime 978",
      "price": 12072.37,
      "rating": 5.0,
      "specs": {
        "color": "Green",
        "size": "L",
        "warranty_months": 12,
        "weight_g": 1412.05
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    },
    {
      "id": "FKP0000112",
      "brand": "Whirlpool",
      "title": "Whirlpool Prime 556",
      "price": 29311.58,
      "rating": 4.9,
      "specs": {
        "color": "White",
        "warranty_months": 24,
        "weight_g": 667.12,
        "delivery_days": 1
      },
      "availability": "In stock",
      "source": "Flipkart (sample dataset)"
    }
  ]
};

// ---------- STATE ----------
let activeCategory = "Electronics";
let compareSet = new Map(); // id -> product
let historyTurns = [];

// ---------- DOM ----------
const threadEl = document.getElementById("thread");
const composerForm = document.getElementById("composerForm");
const composerInput = document.getElementById("composerInput");
const categoryChips = document.getElementById("categoryChips");
const historyList = document.getElementById("historyList");
const trayEmpty = document.getElementById("trayEmpty");
const trayTableWrap = document.getElementById("trayTableWrap");
const trayTable = document.getElementById("trayTable");
const trayCount = document.getElementById("trayCount");
const trayClear = document.getElementById("trayClear");
const newSearchBtn = document.getElementById("newSearchBtn");

// ---------- CATEGORY SWITCHING ----------
categoryChips.addEventListener("click", (e) => {
  const btn = e.target.closest(".chip");
  if (!btn) return;
  [...categoryChips.children].forEach((c) => c.classList.remove("is-active"));
  btn.classList.add("is-active");
  activeCategory = btn.dataset.category;
});

// ---------- NEW SEARCH ----------
newSearchBtn.addEventListener("click", () => {
  threadEl.innerHTML = "";
  compareSet.clear();
  renderTray();
});

// ---------- COMPOSER ----------
composerForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const query = composerInput.value.trim();
  if (!query) return;
  addUserMessage(query);
  composerInput.value = "";
  addHistoryEntry(query);

  runQuery(query, activeCategory);
});

const API_BASE = window.location.protocol.startsWith("http")
  ? window.location.origin
  : "http://127.0.0.1:8000";

async function runQuery(query, category) {
  try {
    const res = await fetch(`${API_BASE}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, category }),
    });
    if (!res.ok) throw new Error(`API returned ${res.status}`);
    const data = await res.json();
    renderAssistantTurn(
      { category: data.slots.category, budget: data.slots.budget_max ? `under ₹${data.slots.budget_max.toLocaleString("en-IN")}` : "not specified" },
      data.products
    );
  } catch (err) {
    // Backend not running (yet) — fall back to local mock data so the
    // UI stays demoable on its own. Remove this catch once the API
    // is always available.
    console.warn("Backend unavailable, using mock data:", err.message);
    const { slots, products } = fakeAssistantTurn(query, category);
    renderAssistantTurn(slots, products);
  }
}

function addUserMessage(text) {
  const div = document.createElement("div");
  div.className = "msg msg--user";
  div.textContent = text;
  threadEl.appendChild(div);
  threadEl.scrollTop = threadEl.scrollHeight;
}

function addHistoryEntry(query) {
  historyTurns.unshift(query);
  historyList.innerHTML = "";
  historyTurns.slice(0, 12).forEach((q, i) => {
    const li = document.createElement("li");
    li.textContent = q;
    if (i === 0) li.classList.add("is-current");
    historyList.appendChild(li);
  });
}

// ---------- FAKE INTENT EXTRACTION (stand-in for LLM function-calling) ----------
function fakeAssistantTurn(query, category) {
  const budgetMatch = query.match(/(\d[\d,]{2,})/);
  const budget = budgetMatch ? parseInt(budgetMatch[1].replace(/,/g, ""), 10) : null;
  const slots = {
    category,
    budget: budget ? `under ₹${budget.toLocaleString("en-IN")}` : "not specified",
  };

  let products = MOCK_CATALOG[category] || [];
  if (budget) products = products.filter((p) => p.price <= budget);
  if (products.length === 0) products = MOCK_CATALOG[category] || [];

  return { slots, products };
}

// ---------- RENDER ASSISTANT TURN ----------
function renderAssistantTurn(slots, products) {
  const wrap = document.createElement("div");
  wrap.className = "msg msg--assistant";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = `Here's what matches in <strong>${slots.category}</strong> right now.
    <span class="slot-line">slots → category: ${slots.category} · budget: ${slots.budget}</span>`;
  wrap.appendChild(bubble);

  const strip = document.createElement("div");
  strip.className = "result-strip";
  products.forEach((p) => strip.appendChild(renderProductCard(p)));
  wrap.appendChild(strip);

  threadEl.appendChild(wrap);
  threadEl.scrollTop = threadEl.scrollHeight;
}

function renderProductCard(p) {
  const card = document.createElement("div");
  card.className = "pcard";

  const tag = document.createElement("span");
  tag.className = "pcard-tag" + (p.availability !== "In stock" ? " is-alert" : "");
  tag.textContent = p.availability;
  card.appendChild(tag);

  const specsHtml = Object.entries(p.specs)
    .map(([k, v]) => `${k}: ${v}`)
    .join(" · ");

  card.innerHTML += `
    <div class="pcard-brand">${p.brand}</div>
    <div class="pcard-title">${p.title}</div>
    <div class="pcard-price">₹${p.price.toLocaleString("en-IN")}</div>
    <div class="pcard-specs">${specsHtml}</div>
    <div class="pcard-source">${p.source} · ★ ${p.rating}</div>
  `;

  const compareRow = document.createElement("label");
  compareRow.className = "pcard-compare";
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = compareSet.has(p.id);
  checkbox.addEventListener("change", () => {
    if (checkbox.checked) compareSet.set(p.id, p);
    else compareSet.delete(p.id);
    renderTray();
  });
  compareRow.appendChild(checkbox);
  compareRow.appendChild(document.createTextNode(" Compare"));
  card.appendChild(compareRow);

  return card;
}

// ---------- COMPARE TRAY ----------
function renderTray() {
  trayCount.textContent = compareSet.size;

  if (compareSet.size < 2) {
    trayEmpty.hidden = false;
    trayTableWrap.hidden = true;
    trayClear.hidden = true;
    return;
  }

  trayEmpty.hidden = true;
  trayTableWrap.hidden = false;
  trayClear.hidden = false;

  const items = [...compareSet.values()];
  // schema-first: union of spec keys actually present, grounded per product
  const allKeys = [...new Set(items.flatMap((p) => Object.keys(p.specs)))];

  let html = "<tr><th>Product</th>" + items.map((p) => `<th>${p.brand}</th>`).join("") + "</tr>";
  html += "<tr><td>Price</td>" + items.map((p) => `<td class="price-cell">₹${p.price.toLocaleString("en-IN")}</td>`).join("") + "</tr>";
  allKeys.forEach((key) => {
    html += `<tr><td>${key}</td>` + items.map((p) => {
      const val = p.specs[key];
      return val ? `<td>${val}</td>` : `<td class="not-specified">not specified</td>`;
    }).join("") + "</tr>";
  });

  trayTable.innerHTML = html;
}

trayClear.addEventListener("click", () => {
  compareSet.clear();
  document.querySelectorAll(".pcard-compare input").forEach((cb) => (cb.checked = false));
  renderTray();
});

// ---------- INITIAL GREETING ----------
renderAssistantTurn(
  { category: "Electronics", budget: "not specified" },
  MOCK_CATALOG.Electronics
);
