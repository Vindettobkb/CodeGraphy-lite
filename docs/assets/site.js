/* CodeGraphy v2.2.0 landing page — no build step, no dependencies. */
(function () {
  "use strict";

  /* Single checkout configuration point. A URL opens in a new tab; a "#"
     placeholder opens the manual Pro-key modal. */
  var PRO_CHECKOUT_URL = "#get-pro";

  var $ = function (sel, root) {
    return (root || document).querySelector(sel);
  };
  var $$ = function (sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  };

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /* ------------------------------------------------------------
     Toast
     ------------------------------------------------------------ */

  var toast = $("#toast");
  var toastMsg = $("#toast-msg");
  var toastTimer = null;

  function showToast(message) {
    if (!toast || !toastMsg) return;
    toastMsg.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () {
      toast.classList.remove("is-visible");
    }, 2200);
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () {
        return legacyCopy(text);
      });
    }
    return Promise.resolve(legacyCopy(text));
  }

  function legacyCopy(text) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (_) {
      ok = false;
    }
    document.body.removeChild(area);
    return ok;
  }

  /* ------------------------------------------------------------
     Mobile navigation
     ------------------------------------------------------------ */

  var navToggle = $("#nav-toggle");
  var mobileMenu = $("#mobile-menu");

  function setMenu(open) {
    if (!navToggle || !mobileMenu) return;
    mobileMenu.hidden = !open;
    navToggle.setAttribute("aria-expanded", String(open));
    navToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }

  if (navToggle && mobileMenu) {
    navToggle.addEventListener("click", function () {
      setMenu(mobileMenu.hidden);
    });

    $$("a", mobileMenu).forEach(function (link) {
      link.addEventListener("click", function () {
        setMenu(false);
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !mobileMenu.hidden) setMenu(false);
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 860 && !mobileMenu.hidden) setMenu(false);
    });
  }

  /* ------------------------------------------------------------
     Active section in the desktop navigation
     ------------------------------------------------------------ */

  var navLinks = $$(".nav-links a");
  var navSections = navLinks
    .map(function (link) {
      var id = link.getAttribute("href");
      if (!id || id.charAt(0) !== "#") return null;
      var el = document.getElementById(id.slice(1));
      return el ? { link: link, el: el } : null;
    })
    .filter(Boolean)
    .sort(function (a, b) {
      return a.el.offsetTop - b.el.offsetTop;
    });

  function paintActiveLink() {
    if (!navSections.length) return;
    var marker = window.scrollY + 96;
    var current = null;
    navSections.forEach(function (item) {
      if (item.el.offsetTop <= marker) current = item;
    });
    navSections.forEach(function (item) {
      if (item === current) item.link.setAttribute("aria-current", "true");
      else item.link.removeAttribute("aria-current");
    });
  }

  if (navSections.length) {
    window.addEventListener("scroll", paintActiveLink, { passive: true });
    paintActiveLink();
  }

  /* ------------------------------------------------------------
     Copy buttons
     ------------------------------------------------------------ */

  $$("[data-copy-text]").forEach(function (button) {
    button.addEventListener("click", function () {
      var text = button.getAttribute("data-copy-text");
      copyText(text).then(function () {
        showToast("Copied: " + text);
      });
    });
  });

  $$("[data-copy-target]").forEach(function (button) {
    button.addEventListener("click", function () {
      var target = document.getElementById(button.getAttribute("data-copy-target"));
      if (!target) return;
      copyText(target.textContent).then(function () {
        showToast("Copied to clipboard");
      });
    });
  });

  /* ------------------------------------------------------------
     CI linter tabs
     ------------------------------------------------------------ */

  var codeTabs = $$("[data-code-tab]");

  function selectCodeTab(key) {
    codeTabs.forEach(function (tab) {
      var selected = tab.getAttribute("data-code-tab") === key;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      var panel = document.getElementById(tab.getAttribute("aria-controls"));
      if (panel) panel.hidden = !selected;
    });

    var copyButton = $(".code-window [data-copy-target]");
    if (copyButton) copyButton.setAttribute("data-copy-target", "ci-code-" + key);
  }

  codeTabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      selectCodeTab(tab.getAttribute("data-code-tab"));
    });
  });

  /* ------------------------------------------------------------
     Compression inspector (real 225-token sample)
     ------------------------------------------------------------ */

  var LEVELS = {
    full: {
      tokens: 225,
      saved: 0,
      dynamic: "3 calls",
      description:
        '<strong>Original source.</strong> Nothing is removed. This is the 225-token baseline every other level is measured against.',
      content: [
        '"""Load and validate service credentials."""',
        "import logging",
        "import os",
        "from dataclasses import dataclass",
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "",
        "@dataclass",
        "class Credentials:",
        "    token: str",
        "    timeout: float",
        "    retries: int = 3",
        "",
        "",
        "class CredentialLoader:",
        "    def __init__(self) -> None:",
        "        self.last_profile: str | None = None",
        "",
        '    def load(self, profile: str = "default") -> Credentials:',
        '        """Build credentials from the environment for the selected profile."""',
        '        print(f"loading profile: {profile}")',
        '        logger.info("resolving credentials for %s", profile)',
        '        token = os.getenv("SERVICE_TOKEN")',
        "        if not token:",
        '            raise RuntimeError("SERVICE_TOKEN is not set")',
        '        timeout = float(os.getenv("SERVICE_TIMEOUT", "5"))',
        '        retries = int(os.getenv("SERVICE_RETRIES", "3"))',
        "        self.last_profile = profile",
        "        if retries < 1:",
        '            logger.warning("invalid retry count, using 1")',
        "            retries = 1",
        "        return Credentials(token=token, timeout=timeout, retries=retries)"
      ].join("\n"),
      source: "original source"
    },
    behavioral: {
      tokens: 131,
      saved: 41.8,
      dynamic: "flagged",
      description:
        "<strong>Prints and logger calls are removed.</strong> Branches, <code>raise</code>, <code>return</code>, calls and " +
        "state mutations like <code>self.last_profile = profile</code> stay. Dynamic lookups are marked.",
      content: [
        "# [DYNAMIC_LOOKUP: os.getenv — static skeleton may miss runtime behavior; inspect full file or get_symbol_body]",
        "# ...",
        "class Credentials:",
        "    # ...",
        "class CredentialLoader:",
        "    def __init__(self) -> None:",
        "        self.last_profile: str | None = None",
        '    def load(self, profile: str = "default") -> Credentials:',
        "        # ...",
        "        if not token:",
        '            raise RuntimeError("SERVICE_TOKEN is not set")',
        "        # ...",
        "        self.last_profile = profile",
        "        if retries < 1:",
        "            # ...",
        "            retries = 1",
        "        return Credentials(token=token, timeout=timeout, retries=retries)"
      ].join("\n"),
      source: "generated by backend.app.context_levels.compress_context"
    },
    structural: {
      tokens: 98,
      saved: 56.4,
      dynamic: "flagged",
      description:
        "<strong>Imports, types, signatures and the first docstring line.</strong> Bodies are collapsed. " +
        "The smallest useful view when the budget is tight — and still marked when a dynamic lookup exists.",
      content: [
        "# [DYNAMIC_LOOKUP: os.getenv — static skeleton may miss runtime behavior; inspect full file or get_symbol_body]",
        "# ...",
        "import logging",
        "import os",
        "from dataclasses import dataclass",
        "# ...",
        "@dataclass",
        "class Credentials:",
        "    # ...",
        "class CredentialLoader:",
        "    def __init__(self) -> None:",
        "        # ...",
        '    def load(self, profile: str = "default") -> Credentials:',
        '        """Build credentials from the environment for the selected profile."""',
        "        # ..."
      ].join("\n"),
      source: "generated by backend.app.context_levels.compress_context"
    }
  };

  var levelTabs = $$(".level-tab");
  var levelCode = $("#level-code");

  function codeToHtml(source) {
    return source
      .split("\n")
      .map(function (line) {
        var html = escapeHtml(line);
        if (line.indexOf("# [DYNAMIC_LOOKUP") === 0) {
          return '<span class="ln-marker">' + html + "</span>";
        }
        if (line === "# ...") {
          return '<span class="ln-omitted">' + html + "</span>";
        }
        return html;
      })
      .join("\n");
  }

  function selectLevel(key) {
    var data = LEVELS[key];
    if (!data) return;

    levelTabs.forEach(function (tab) {
      var selected = tab.getAttribute("data-level") === key;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });

    var description = $("#level-desc");
    var tokens = $("#level-tokens");
    var saved = $("#level-saved");
    var dynamic = $("#level-dynamic");
    var badge = $("#level-badge");
    var foot = $("#level-code-foot");
    var progress = $("#level-progress-bar");

    if (description) description.innerHTML = data.description;
    if (tokens) tokens.textContent = String(data.tokens);
    if (saved) saved.textContent = data.saved === 0 ? "0%" : data.saved.toFixed(1) + "%";
    if (dynamic) {
      dynamic.textContent = data.dynamic;
      dynamic.classList.toggle("warn", key !== "full");
    }
    if (badge) badge.textContent = key;
    if (levelCode) levelCode.innerHTML = codeToHtml(data.content);
    if (progress) progress.style.setProperty("--pct", data.saved + "%");
    if (foot) {
      foot.innerHTML =
        '<span class="ok">' +
        key +
        "</span> · " +
        data.tokens +
        " tokens · " +
        escapeHtml(data.source);
    }
  }

  levelTabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      selectLevel(tab.getAttribute("data-level"));
    });
  });

  /* ------------------------------------------------------------
     Pro key modal
     ------------------------------------------------------------ */

  var proModal = $("#pro-modal");
  var proButtons = $$("[data-pro-checkout]");
  var modalClose = $("[data-close-modal]");
  var bodyOverflow = "";

  function openProModal() {
    if (!proModal) return;
    bodyOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    if (typeof proModal.showModal === "function") proModal.showModal();
    else proModal.setAttribute("open", "");
  }

  function closeProModal() {
    if (!proModal) return;
    if (typeof proModal.close === "function") proModal.close();
    else proModal.removeAttribute("open");
    document.body.style.overflow = bodyOverflow;
  }

  proButtons.forEach(function (button) {
    button.addEventListener("click", function (event) {
      if (PRO_CHECKOUT_URL.charAt(0) === "#") {
        event.preventDefault();
        openProModal();
      } else {
        window.open(PRO_CHECKOUT_URL, "_blank", "noopener");
      }
    });
  });

  if (proModal) {
    if (modalClose) modalClose.addEventListener("click", closeProModal);

    proModal.addEventListener("click", function (event) {
      if (event.target === proModal) closeProModal();
    });

    proModal.addEventListener("cancel", function (event) {
      event.preventDefault();
      closeProModal();
    });

    proModal.addEventListener("close", function () {
      document.body.style.overflow = bodyOverflow;
    });
  }

  /* ------------------------------------------------------------
     Playground — preserved novapay-checkout sandbox
     ------------------------------------------------------------ */

  var NODES = [
    {
      id: "ui_checkout",
      name: "CheckoutForm.tsx",
      layer: "UI",
      rawTokens: 8420,
      astTokens: 1310,
      mode: "ast",
      unified: { x: 5, y: 80 },
      layers: { x: 4, y: 75 },
      fullCode:
        "export function CheckoutForm({ cartId, onPaid }: Props) {\n  const [card, setCard] = useState<CardPayload | null>(null);\n  const submit = () => api.post('/v1/checkout', { cartId, card });\n  return <form onSubmit={submit}>...</form>;\n}",
      astCode:
        "export interface Props { cartId: string; onPaid: (txId: string) => void; }\nexport function CheckoutForm(props: Props): JSX.Element;"
    },
    {
      id: "ui_modal",
      name: "3DSModal.tsx",
      layer: "UI",
      rawTokens: 4890,
      astTokens: 760,
      mode: "off",
      unified: { x: 5, y: 290 },
      layers: { x: 4, y: 270 },
      fullCode:
        "export function ThreeDSModal({ challengeUrl, onVerify }: Props) {\n  return <iframe src={challengeUrl} className='w-full h-96' />;\n}",
      astCode:
        "export function ThreeDSModal(props: { challengeUrl: string; onVerify: () => void }): JSX.Element;"
    },
    {
      id: "api_auth",
      name: "auth_guard.py",
      layer: "API",
      rawTokens: 5120,
      astTokens: 840,
      mode: "ast",
      unified: { x: 38, y: 40 },
      layers: { x: 38, y: 45 },
      fullCode:
        "async def verify_jwt(token: str = Depends(oauth2)) -> Merchant:\n    payload = jwt.decode(token, settings.JWT_SECRET)\n    return await repo.get_merchant(payload['sub'])",
      astCode: "async def verify_jwt(token: str) -> Merchant: ..."
    },
    {
      id: "api_checkout",
      name: "checkout_api.py",
      layer: "API",
      rawTokens: 9640,
      astTokens: 1620,
      mode: "full",
      unified: { x: 38, y: 205 },
      layers: { x: 38, y: 210 },
      fullCode:
        "@router.post('/v1/checkout')\nasync def process_payment(req: PayReq, m: Merchant = Depends(verify_jwt)):\n    score = fraud.evaluate(req.ip, req.amount)\n    if score > 0.85: raise HTTPException(403, 'Blocked')\n    return stripe.charge(req.token, req.amount)",
      astCode:
        "@router.post('/v1/checkout')\nasync def process_payment(req: PayReq, m: Merchant) -> Receipt: ..."
    },
    {
      id: "core_fraud",
      name: "fraud_engine.py",
      layer: "CORE",
      rawTokens: 7850,
      astTokens: 1290,
      mode: "ast",
      unified: { x: 71, y: 40 },
      layers: { x: 71, y: 40 },
      fullCode:
        "class FraudEngine:\n    def evaluate(self, ip: str, amount: Decimal) -> float:\n        velocity = self.ledger.recent_tx_count(ip)\n        return min(1.0, velocity * 0.15 + float(amount) / 10000)",
      astCode: "class FraudEngine:\n    def evaluate(self, ip: str, amount: Decimal) -> float: ..."
    },
    {
      id: "core_stripe",
      name: "stripe_gateway.py",
      layer: "CORE",
      rawTokens: 6910,
      astTokens: 1180,
      mode: "ast",
      unified: { x: 71, y: 205 },
      layers: { x: 71, y: 205 },
      fullCode:
        "class StripeGateway:\n    def charge(self, token: str, amount: Decimal) -> Receipt:\n        res = stripe.PaymentIntent.create(amount=int(amount * 100))\n        return self.ledger.record(res.id, amount)",
      astCode: "class StripeGateway:\n    def charge(self, token: str, amount: Decimal) -> Receipt: ..."
    },
    {
      id: "core_ledger",
      name: "ledger_repo.py",
      layer: "CORE",
      rawTokens: 5340,
      astTokens: 910,
      mode: "ast",
      unified: { x: 71, y: 370 },
      layers: { x: 71, y: 365 },
      fullCode:
        "class LedgerRepo:\n    def record(self, tx_id: str, amount: Decimal) -> Receipt:\n        # Atomic PostgreSQL double-entry insert\n        return Receipt(id=tx_id, status='settled')",
      astCode:
        "class LedgerRepo:\n    def record(self, tx_id: str, amount: Decimal) -> Receipt: ...\n    def recent_tx_count(self, ip: str) -> int: ..."
    }
  ];

  var EDGES = [
    { from: "ui_checkout", to: "api_checkout", fromSide: "right", toSide: "left", cycle: false },
    { from: "ui_modal", to: "api_checkout", fromSide: "right", toSide: "left", cycle: false },
    { from: "api_auth", to: "api_checkout", fromSide: "bottom", toSide: "top", cycle: false },
    { from: "api_checkout", to: "core_fraud", fromSide: "right", toSide: "left", cycle: false },
    { from: "api_checkout", to: "core_stripe", fromSide: "right", toSide: "left", cycle: true },
    { from: "core_stripe", to: "api_checkout", fromSide: "left", toSide: "right", cycle: true },
    { from: "core_fraud", to: "core_ledger", fromSide: "bottom", toSide: "top", cycle: false },
    { from: "core_stripe", to: "core_ledger", fromSide: "bottom", toSide: "top", cycle: false }
  ];

  var INITIAL_POSITIONS = NODES.map(function (node) {
    return {
      id: node.id,
      unified: { x: node.unified.x, y: node.unified.y },
      layers: { x: node.layers.x, y: node.layers.y }
    };
  });

  var INITIAL_EDGES = EDGES.map(function (edge) {
    return {
      from: edge.from,
      to: edge.to,
      fromSide: edge.fromSide,
      toSide: edge.toSide,
      cycle: edge.cycle
    };
  });

  var BASE_STAGE_HEIGHT = 450;
  var COMPACT_STAGE = 560;
  var currentView = "unified";
  var selectedNodeId = "api_checkout";
  var nodeElements = {};
  var dragState = null;
  var connectState = null;

  function stageEl() {
    return document.getElementById("graph-stage");
  }

  function getUpstream(targetId) {
    var impacted = {};
    impacted[targetId] = true;
    var added = true;
    while (added) {
      added = false;
      EDGES.forEach(function (edge) {
        if (impacted[edge.to] && !impacted[edge.from]) {
          impacted[edge.from] = true;
          added = true;
        }
      });
    }
    return impacted;
  }

  function upstreamSize(set) {
    return Object.keys(set).length;
  }

  function getPortCoords(el, side) {
    var x = el.offsetLeft;
    var y = el.offsetTop;
    var w = el.offsetWidth;
    var h = el.offsetHeight;
    if (side === "left") return { x: x, y: y + h / 2 };
    if (side === "right") return { x: x + w, y: y + h / 2 };
    if (side === "top") return { x: x + w / 2, y: y };
    return { x: x + w / 2, y: y + h };
  }

  function drawEdges() {
    var edgesSvg = document.getElementById("graph-edges");
    var stage = stageEl();
    if (!edgesSvg || !stage) return;

    edgesSvg.setAttribute("viewBox", "0 0 " + stage.clientWidth + " " + stage.clientHeight);
    edgesSvg.innerHTML = "";

    var blastSet = currentView === "blast" ? getUpstream(selectedNodeId) : null;

    EDGES.forEach(function (edge) {
      var el1 = nodeElements[edge.from];
      var el2 = nodeElements[edge.to];
      if (!el1 || !el2) return;

      var p1 = getPortCoords(el1, edge.fromSide);
      var p2 = getPortCoords(el2, edge.toSide);
      var isCycle = currentView === "linter" && edge.cycle;
      var isHighlighted =
        isCycle ||
        (currentView === "blast" && blastSet[edge.from] && blastSet[edge.to]) ||
        (currentView !== "linter" &&
          currentView !== "blast" &&
          (edge.from === selectedNodeId || edge.to === selectedNodeId));

      var d = "";
      if (edge.fromSide === "right" && edge.toSide === "left") {
        var dx = Math.max(36, Math.abs(p2.x - p1.x) * 0.5);
        d =
          "M " + p1.x + " " + p1.y +
          " C " + (p1.x + dx) + " " + p1.y +
          ", " + (p2.x - dx) + " " + p2.y +
          ", " + p2.x + " " + p2.y;
      } else if (edge.fromSide === "left" && edge.toSide === "right") {
        var dx2 = Math.max(36, Math.abs(p1.x - p2.x) * 0.5);
        d =
          "M " + p1.x + " " + p1.y +
          " C " + (p1.x - dx2) + " " + (p1.y - 26) +
          ", " + (p2.x + dx2) + " " + (p2.y - 26) +
          ", " + p2.x + " " + p2.y;
      } else {
        var dy = Math.max(24, Math.abs(p2.y - p1.y) * 0.5);
        d =
          "M " + p1.x + " " + p1.y +
          " C " + p1.x + " " + (p1.y + dy) +
          ", " + p2.x + " " + (p2.y - dy) +
          ", " + p2.x + " " + p2.y;
      }

      var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", d);
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", isCycle ? "#c98b8b" : isHighlighted ? "#d9dee8" : "#2b303a");
      path.setAttribute("stroke-width", isCycle || isHighlighted ? "2.2" : "1.4");
      path.setAttribute("stroke-linecap", "round");
      if (isCycle) path.setAttribute("class", "edge-cycle");
      edgesSvg.appendChild(path);
    });

    if (connectState) {
      var fromEl = nodeElements[connectState.fromId];
      if (fromEl) {
        var start = getPortCoords(fromEl, connectState.fromSide);
        var end = { x: connectState.curX, y: connectState.curY };
        var cdx = Math.max(30, Math.abs(end.x - start.x) * 0.45);
        var preview =
          "M " + start.x + " " + start.y +
          " C " + (start.x + cdx) + " " + start.y +
          ", " + (end.x - cdx) + " " + end.y +
          ", " + end.x + " " + end.y;
        var tempPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
        tempPath.setAttribute("d", preview);
        tempPath.setAttribute("fill", "none");
        tempPath.setAttribute("stroke", "#d9dee8");
        tempPath.setAttribute("stroke-width", "2");
        tempPath.setAttribute("stroke-dasharray", "4 4");
        edgesSvg.appendChild(tempPath);
      }
    }
  }

  function layerIndex(layer) {
    if (layer === "API") return 1;
    if (layer === "CORE") return 2;
    return 0;
  }

  function layoutNode(el, node) {
    var stage = stageEl();
    if (!stage) return;
    var pos = currentView === "layers" ? node.layers : node.unified;
    var maxLeft = Math.max(0, stage.clientWidth - el.offsetWidth);
    var scaleY = stage.clientHeight / BASE_STAGE_HEIGHT;
    var compact = stage.clientWidth < COMPACT_STAGE;

    if (compact && typeof node.mobileX !== "number") {
      node.mobileX = 2 + layerIndex(node.layer) * 48;
    }

    var xPercent = compact ? node.mobileX : pos.x;
    el.style.left = ((xPercent / 100) * maxLeft) + "px";
    el.style.top = (pos.y * scaleY) + "px";
  }

  function renderPlayground() {
    var fileList = document.getElementById("file-list");
    var nodesEl = document.getElementById("graph-nodes");
    var stage = stageEl();
    var layerHeaders = document.getElementById("layer-headers");
    var linterBadge = document.getElementById("linter-badge");
    if (!fileList || !nodesEl || !stage) return;

    if (layerHeaders) layerHeaders.classList.toggle("is-visible", currentView === "layers");
    if (linterBadge) linterBadge.hidden = currentView !== "linter";

    var blastSet = currentView === "blast" ? getUpstream(selectedNodeId) : null;

    fileList.innerHTML = "";
    var totalRaw = 0;
    var totalCompiled = 0;

    NODES.forEach(function (node) {
      totalRaw += node.rawTokens;
      if (node.mode === "full") totalCompiled += node.rawTokens;
      else if (node.mode === "ast") totalCompiled += node.astTokens;

      var isSelected = node.id === selectedNodeId;
      var row = document.createElement("div");
      row.className = "pg-file" + (isSelected ? " is-selected" : "");

      var label = document.createElement("div");
      label.style.minWidth = "0";

      var name = document.createElement("div");
      name.className = "pg-file-name";
      name.textContent = node.name;

      var meta = document.createElement("div");
      meta.className = "pg-file-meta";
      meta.textContent =
        (node.mode === "full" ? node.rawTokens : node.mode === "ast" ? node.astTokens : 0) + " tok";

      var mode = document.createElement("button");
      mode.type = "button";
      mode.className = "pg-mode";
      mode.setAttribute("data-mode", node.mode);
      mode.textContent = node.mode;
      mode.title = "Click to cycle Full / AST / Off";

      mode.addEventListener("click", function (event) {
        event.stopPropagation();
        var order = ["full", "ast", "off"];
        node.mode = order[(order.indexOf(node.mode) + 1) % order.length];
        renderPlayground();
      });

      row.addEventListener("click", function (event) {
        if (event.target.closest("button")) return;
        selectedNodeId = node.id;
        renderPlayground();
      });

      label.appendChild(name);
      label.appendChild(meta);
      row.appendChild(label);
      row.appendChild(mode);
      fileList.appendChild(row);
    });

    nodesEl.innerHTML = "";
    nodeElements = {};

    NODES.forEach(function (node) {
      var isSelected = node.id === selectedNodeId;
      var isCycleNode =
        currentView === "linter" && (node.id === "api_checkout" || node.id === "core_stripe");
      var isDimmed = blastSet ? !blastSet[node.id] : false;

      var el = document.createElement("div");
      el.dataset.nodeId = node.id;
      el.title = node.name;
      el.className =
        "pg-node" +
        (isSelected ? " is-selected" : "") +
        (isCycleNode ? " is-cycle" : "") +
        (isDimmed ? " is-dimmed" : "");

      el.innerHTML =
        '<span class="pg-handle" data-port="top" data-node="' + node.id + '" title="Drag to connect"></span>' +
        '<span class="pg-handle" data-port="bottom" data-node="' + node.id + '" title="Drag to connect"></span>' +
        '<span class="pg-handle" data-port="left" data-node="' + node.id + '" title="Drag to connect"></span>' +
        '<span class="pg-handle" data-port="right" data-node="' + node.id + '" title="Drag to connect"></span>' +
        '<div class="pg-node-top"><span class="pg-layer" data-layer="' + node.layer + '">' +
        node.layer +
        '</span><span class="pg-node-mode">' +
        node.mode.toUpperCase() +
        "</span></div>" +
        '<div class="pg-node-name">' +
        node.name +
        "</div>";

      $$(".pg-handle", el).forEach(function (handle) {
        handle.addEventListener("pointerdown", function (event) {
          event.stopPropagation();
          event.preventDefault();
          var rect = stage.getBoundingClientRect();
          connectState = {
            fromId: node.id,
            fromSide: handle.getAttribute("data-port"),
            curX: event.clientX - rect.left,
            curY: event.clientY - rect.top
          };
          drawEdges();
        });
      });

      el.addEventListener("pointerdown", function (event) {
        if (event.target.closest(".pg-handle")) return;
        event.preventDefault();
        selectedNodeId = node.id;
        dragState = {
          node: node,
          el: el,
          startX: event.clientX,
          startY: event.clientY,
          origLeftPx: el.offsetLeft,
          origTopPx: el.offsetTop,
          moved: false
        };
      });

      nodesEl.appendChild(el);
      nodeElements[node.id] = el;
      layoutNode(el, node);
    });

    drawEdges();
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(drawEdges);
    }

    var selected = NODES.find(function (node) {
      return node.id === selectedNodeId;
    });
    var savings = Math.max(0, Math.round((1 - totalCompiled / totalRaw) * 1000) / 10);

    var compiledEl = document.getElementById("live-compiled");
    var rawEl = document.getElementById("live-raw");
    var savingsBadge = document.getElementById("inspector-savings-badge");
    if (compiledEl) compiledEl.textContent = totalCompiled.toLocaleString();
    if (rawEl) rawEl.textContent = totalRaw.toLocaleString();
    if (savingsBadge) savingsBadge.textContent = "-" + savings + "% saved";

    if (selected) {
      var fileName = document.getElementById("preview-file-name");
      var fileMode = document.getElementById("preview-file-mode");
      var code = document.getElementById("preview-code");
      if (fileName) fileName.textContent = selected.name;
      if (fileMode) fileMode.textContent = selected.mode.toUpperCase();
      if (code) {
        code.textContent =
          selected.mode === "full"
            ? selected.fullCode
            : selected.mode === "ast"
              ? selected.astCode
              : "// Excluded from prompt context (OFF)";
      }

      var banner = document.getElementById("banner-text");
      if (banner) {
        if (currentView === "linter") {
          banner.innerHTML =
            '<span class="danger">Cycle detected:</span> checkout_api.py &harr; stripe_gateway.py';
        } else if (currentView === "blast") {
          banner.innerHTML =
            'Blast radius for <span class="sel">' +
            selected.name +
            "</span>: " +
            upstreamSize(blastSet) +
            " modules impacted";
        } else {
          banner.innerHTML =
            'Selected: <span class="sel">' +
            selected.name +
            "</span> &middot; Drag nodes or connect ports";
        }
      }
    }
  }

  window.addEventListener("pointermove", function (event) {
    var stage = stageEl();
    if (!stage) return;

    if (dragState) {
      var dx = event.clientX - dragState.startX;
      var dy = event.clientY - dragState.startY;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) dragState.moved = true;

      var maxLeft = Math.max(1, stage.clientWidth - dragState.el.offsetWidth);
      var scaleY = stage.clientHeight / BASE_STAGE_HEIGHT;
      var newLeft = Math.max(0, Math.min(maxLeft, dragState.origLeftPx + dx));
      var newTop = Math.max(0, Math.min(stage.clientHeight - dragState.el.offsetHeight, dragState.origTopPx + dy));

      var targetPos = currentView === "layers" ? dragState.node.layers : dragState.node.unified;
      var xPercent = (newLeft / maxLeft) * 100;
      targetPos.x = xPercent;
      targetPos.y = newTop / scaleY;
      if (stage.clientWidth < COMPACT_STAGE) dragState.node.mobileX = xPercent;

      dragState.el.style.left = newLeft + "px";
      dragState.el.style.top = newTop + "px";
      drawEdges();
    } else if (connectState) {
      var rect = stage.getBoundingClientRect();
      connectState.curX = event.clientX - rect.left;
      connectState.curY = event.clientY - rect.top;
      drawEdges();
    }
  });

  window.addEventListener("pointerup", function (event) {
    if (dragState) {
      var wasMoved = dragState.moved;
      dragState = null;
      if (!wasMoved) renderPlayground();
    }

    if (connectState) {
      var targetEl = document.elementFromPoint(event.clientX, event.clientY);
      var portEl = targetEl && targetEl.closest(".pg-handle");
      var nodeEl = targetEl && targetEl.closest("[data-node-id]");
      var toId = portEl ? portEl.getAttribute("data-node") : nodeEl ? nodeEl.getAttribute("data-node-id") : null;
      var toSide = portEl ? portEl.getAttribute("data-port") : "left";

      if (toId && toId !== connectState.fromId) {
        var exists = EDGES.some(function (edge) {
          return (
            edge.from === connectState.fromId &&
            edge.to === toId &&
            edge.fromSide === connectState.fromSide &&
            edge.toSide === toSide
          );
        });
        if (!exists) {
          EDGES.push({
            from: connectState.fromId,
            to: toId,
            fromSide: connectState.fromSide,
            toSide: toSide,
            cycle: false
          });
          showToast("Connected module edge");
        }
      }
      connectState = null;
      renderPlayground();
    }
  });

  var resetButton = document.getElementById("reset-graph-btn");
  if (resetButton) {
    resetButton.addEventListener("click", function () {
      INITIAL_POSITIONS.forEach(function (position) {
        var node = NODES.find(function (item) {
          return item.id === position.id;
        });
        if (node) {
          node.unified = { x: position.unified.x, y: position.unified.y };
          node.layers = { x: position.layers.x, y: position.layers.y };
          delete node.mobileX;
        }
      });
      EDGES.length = 0;
      INITIAL_EDGES.forEach(function (edge) {
        EDGES.push({
          from: edge.from,
          to: edge.to,
          fromSide: edge.fromSide,
          toSide: edge.toSide,
          cycle: edge.cycle
        });
      });
      renderPlayground();
      showToast("Graph layout reset");
    });
  }

  $$(".pg-tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      currentView = tab.getAttribute("data-view");
      $$(".pg-tab").forEach(function (item) {
        item.setAttribute("aria-selected", String(item === tab));
      });
      var labels = {
        unified: "Unified Graph",
        layers: "Split Layers",
        linter: "Architecture Linter",
        blast: "Blast Radius"
      };
      var pill = document.getElementById("status-pill");
      if (pill) pill.textContent = labels[currentView];
      renderPlayground();
    });
  });

  var resizeTimer = null;
  window.addEventListener("resize", function () {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(function () {
      if (!dragState && !connectState) renderPlayground();
    }, 120);
  });

  var copyMcp = document.getElementById("copy-mcp-btn");
  if (copyMcp) {
    copyMcp.addEventListener("click", function () {
      var payload = NODES.filter(function (node) {
        return node.mode !== "off";
      })
        .map(function (node) {
          return (
            "# " +
            node.name +
            " [" +
            node.mode.toUpperCase() +
            "]\n" +
            (node.mode === "full" ? node.fullCode : node.astCode)
          );
        })
        .join("\n\n");

      copyText(payload).then(function () {
        showToast("Compiled context copied to clipboard");
      });
    });
  }

  /* Initial paint. */
  if (document.getElementById("graph-stage")) renderPlayground();
  else selectLevel("behavioral");

  if (levelCode) selectLevel("behavioral");
})();
