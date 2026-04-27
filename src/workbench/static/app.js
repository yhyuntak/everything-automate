"use strict";

const state = {
  source: "custom",
  path: "",
  graph: null,
  cy: null,
  mini: null,
  selectedId: null,
  hoveredId: null,
  hubId: null,
  graphMode: "small",
  importantLabelIds: new Set(),
  filters: {
    skill: true,
    agent: true,
  },
};

const els = {};

function $(selector) {
  return document.querySelector(selector);
}

function all(selector) {
  return Array.from(document.querySelectorAll(selector));
}

function init() {
  bindElements();
  bindEvents();
  applyUrlState();
  updateSourceUi();
  updateFilterLists();
  updatePreview();
  if (state.source && (state.source !== "custom" || state.path)) {
    loadGraph();
  }
}

function bindElements() {
  els.sourcesPanel = $("#sourcesPanel");
  els.inspectorPanel = $("#inspectorPanel");
  els.drawerBackdrop = $("#drawerBackdrop");
  els.graphCanvas = $("#graphCanvas");
  els.nodeOverlayLayer = $("#nodeOverlayLayer");
  els.emptyState = $("#emptyState");
  els.minimap = $("#minimap");
  els.customPath = $("#customPath");
  els.sourceName = $("#sourceName");
  els.sourceSummary = $("#sourceSummary");
  els.sourceStatus = $("#sourceStatus");
  els.skillFilter = $("#skillFilter");
  els.agentFilter = $("#agentFilter");
  els.skillList = $("#skillList");
  els.agentList = $("#agentList");
  els.skillCount = $("#skillCount");
  els.agentCount = $("#agentCount");
  els.zoomReadout = $("#zoomReadout");
  els.inspectorEmpty = $("#inspectorEmpty");
  els.inspectorCard = $("#inspectorCard");
  els.selectedIcon = $("#selectedIcon");
  els.selectedName = $("#selectedName");
  els.selectedKind = $("#selectedKind");
  els.selectedId = $("#selectedId");
  els.detailSelectionId = $("#detailSelectionId");
  els.detailPath = $("#detailPath");
  els.detailAliases = $("#detailAliases");
  els.detailDegree = $("#detailDegree");
  els.incomingEdges = $("#incomingEdges");
  els.outgoingEdges = $("#outgoingEdges");
  els.previewSource = $("#previewSource");
  els.previewNodes = $("#previewNodes");
  els.previewEdges = $("#previewEdges");
}

function bindEvents() {
  all(".source-tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.source = button.dataset.source;
      updateSourceUi();
    });
  });

  $("#loadButton").addEventListener("click", loadGraph);
  $("#reloadSourceButton").addEventListener("click", loadGraph);
  $("#clearButton").addEventListener("click", clearGraph);
  $("#clearFiltersButton").addEventListener("click", () => {
    state.filters.skill = false;
    state.filters.agent = false;
    updateFilterLists();
    renderGraph();
  });
  $("#sourcesToggle").addEventListener("click", () => openDrawer("sources"));
  $("#closeSourcesButton").addEventListener("click", () => closeDrawers());
  $("#closeInspectorButton").addEventListener("click", () => closeDrawers());
  $("#drawerBackdrop").addEventListener("click", closeDrawers);
  $("#fitButton").addEventListener("click", fitGraph);
  $("#fitCanvasButton").addEventListener("click", fitGraph);
  $("#layoutButton").addEventListener("click", resetLayout);
  $("#zoomInButton").addEventListener("click", () => zoomBy(1.18));
  $("#zoomOutButton").addEventListener("click", () => zoomBy(0.84));
  $("#selectModeButton").addEventListener("click", () => setMode("select"));
  $("#panModeButton").addEventListener("click", () => setMode("pan"));
  $("#helpButton").addEventListener("click", () => togglePopover("helpPopover"));
  $("#menuButton").addEventListener("click", () => togglePopover("menuPopover"));
  $("#reloadButton").addEventListener("click", loadGraph);
  $("#resetButton").addEventListener("click", resetLayout);
  $("#clearSelectionButton").addEventListener("click", clearSelection);
  els.inspectorPanel.addEventListener("click", (event) => {
    const edgeButton = event.target.closest("[data-node-id]");
    if (!edgeButton) return;
    selectNode(edgeButton.dataset.nodeId);
  });

  all("[data-close-popover]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.closePopover;
      document.getElementById(id).hidden = true;
    });
  });

  els.skillFilter.addEventListener("change", () => {
    state.filters.skill = els.skillFilter.checked;
    updateFilterLists();
    renderGraph();
  });
  els.agentFilter.addEventListener("change", () => {
    state.filters.agent = els.agentFilter.checked;
    updateFilterLists();
    renderGraph();
  });

  window.addEventListener("resize", () => {
    if (state.cy) {
      state.cy.resize();
      fitGraph();
    }
  });
}

function applyUrlState() {
  const params = new URLSearchParams(window.location.search);
  const source = params.get("source");
  const path = params.get("path");
  if (source && ["global", "local", "custom"].includes(source)) {
    state.source = source;
  }
  if (path) {
    state.path = path;
    els.customPath.value = path;
  }
}

function updateSourceUi() {
  all(".source-tab").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.source === state.source);
  });
  const labels = {
    global: ["codex_global", "Uses ~/.codex"],
    local: ["codex_local", "Uses repo-root .codex"],
    custom: ["custom", "Load a Codex home-like path"],
  };
  const [name, summary] = labels[state.source];
  els.sourceName.textContent = name;
  els.sourceSummary.textContent = summary;
  els.customPath.disabled = state.source !== "custom";
}

function syncFilterInputs() {
  els.skillFilter.checked = state.filters.skill;
  els.agentFilter.checked = state.filters.agent;
}

async function loadGraph() {
  state.path = els.customPath.value.trim();
  setStatus("Loading graph...");
  const params = new URLSearchParams({ source: state.source });
  if (state.source === "custom") {
    if (!state.path) {
      setStatus("Custom source requires a path.", true);
      return;
    }
    params.set("path", state.path);
  }

  try {
    const response = await fetch(`/api/graph?${params.toString()}`);
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.message || "Graph load failed");
    }
    state.graph = payload;
    state.selectedId = null;
    state.hoveredId = null;
    setStatus(`${sourceLabel()} loaded`);
    updateUrl(params);
    updateFilterLists();
    renderGraph();
    updateInspector();
    updatePreview();
  } catch (error) {
    clearGraph(false);
    setStatus(error.message, true);
  }
}

function clearGraph(clearStatus = true) {
  state.graph = null;
  state.selectedId = null;
  state.hoveredId = null;
  destroyGraphs();
  els.emptyState.hidden = false;
  els.emptyState.querySelector("h2").textContent = "No graph loaded";
  els.emptyState.querySelector("p").textContent = "Load a global, local, or custom Codex source to inspect the map.";
  updateFilterLists();
  updateInspector();
  updatePreview();
  if (clearStatus) {
    setStatus("Choose a source and load the graph.");
  }
}

function setStatus(message, isError = false) {
  els.sourceStatus.textContent = message;
  els.sourceStatus.classList.toggle("is-error", isError);
}

function updateUrl(params) {
  const next = `${window.location.pathname}?${params.toString()}`;
  window.history.replaceState({}, "", next);
}

function sourceLabel() {
  if (!state.graph) return "No source";
  return state.graph.source.source_id.replaceAll("-", "_");
}

function visibleNodes() {
  if (!state.graph) return [];
  return state.graph.nodes.filter((node) => state.filters[node.surface_type]);
}

function visibleNodeIds() {
  return new Set(visibleNodes().map((node) => node.selection_id));
}

function visibleEdges() {
  if (!state.graph) return [];
  const ids = visibleNodeIds();
  return state.graph.edges.filter(
    (edge) => ids.has(edge.from_selection_id) && ids.has(edge.to_selection_id),
  );
}

function updateFilterLists() {
  const nodes = state.graph ? state.graph.nodes : [];
  const skills = nodes.filter((node) => node.surface_type === "skill");
  const agents = nodes.filter((node) => node.surface_type === "agent");
  els.skillCount.textContent = `${state.filters.skill ? skills.length : 0} selected`;
  els.agentCount.textContent = `${state.filters.agent ? agents.length : 0} selected`;
  els.skillList.innerHTML = skills.map(renderCompactNode).join("");
  els.agentList.innerHTML = agents.map(renderCompactNode).join("");
  syncFilterInputs();
}

function renderCompactNode(node) {
  return `
    <div class="compact-item">
      <span class="compact-name">${escapeHtml(node.name)}</span>
      <span class="compact-degree">${node.degree}</span>
    </div>
  `;
}

function renderGraph() {
  if (!state.graph) {
    clearGraph(false);
    return;
  }
  const nodes = visibleNodes();
  const edges = visibleEdges();
  if (state.selectedId && !nodes.some((node) => node.selection_id === state.selectedId)) {
    state.selectedId = null;
    updateInspector();
  }
  if (!nodes.length) {
    destroyGraphs();
    els.emptyState.hidden = false;
    els.emptyState.querySelector("h2").textContent = "No visible nodes";
    els.emptyState.querySelector("p").textContent = "Turn on Skills or Agents to show the graph.";
    updatePreview();
    return;
  }

  els.emptyState.hidden = true;
  const viewPolicy = graphViewPolicy(nodes, edges);
  state.graphMode = viewPolicy.mode;
  state.importantLabelIds = viewPolicy.importantLabelIds;
  const positioned = applyClientLayout(nodes, edges, viewPolicy);
  const hub = positioned.find((node) => node.isHub);
  state.hubId = hub ? hub.selection_id : null;
  const elements = [
    ...positioned.map((node) => ({
      group: "nodes",
      data: {
        id: node.selection_id,
        kind: node.surface_type,
        size: node.renderSize,
        degree: node.degree,
      },
      position: { x: node.cx, y: node.cy },
      classes: `${node.surface_type} ${viewPolicy.mode}`,
    })),
    ...edges.map((edge, index) => ({
      group: "edges",
      data: {
        id: `edge-${index}-${edge.from_selection_id}-${edge.to_selection_id}`,
        source: edge.from_selection_id,
        target: edge.to_selection_id,
        match: edge.match_text,
      },
      classes: viewPolicy.mode,
    })),
  ];

  destroyGraphs();
  state.cy = cytoscape({
    container: els.graphCanvas,
    elements,
    minZoom: 0.22,
    maxZoom: 2.4,
    style: graphStyle(),
    layout: { name: "preset", fit: false },
  });

  state.cy.on("select", "node", (event) => {
    state.selectedId = event.target.id();
    updateFocusClasses();
    updateInspector();
    if (window.innerWidth <= 1220) openDrawer("inspector");
  });
  state.cy.on("unselect", "node", () => {
    state.selectedId = null;
    updateFocusClasses();
    updateInspector();
  });
  state.cy.on("mouseover", "node", (event) => {
    state.hoveredId = event.target.id();
    updateFocusClasses();
  });
  state.cy.on("mouseout", "node", () => {
    state.hoveredId = null;
    updateFocusClasses();
  });
  state.cy.on("zoom pan", updateZoomReadout);
  state.cy.on("render zoom pan", updateNodeOverlays);

  renderNodeOverlays(positioned);
  makeMiniMap(elements);
  fitGraph();
  updateFocusClasses();
  updatePreview();
}

function graphStyle() {
  return [
    {
      selector: "node",
      style: {
        width: "data(size)",
        height: "data(size)",
        shape: "ellipse",
        "background-color": "#e8f8ef",
        "border-width": 2,
        "border-color": "#25b96f",
        "overlay-padding": 4,
      },
    },
    {
      selector: "node.agent",
      style: {
        "background-color": "#e7f1ff",
        "border-color": "#0b72f0",
      },
    },
    {
      selector: "node:selected",
      style: {
        width: (node) => Number(node.data("size")) + 22,
        height: (node) => Number(node.data("size")) + 22,
        "border-width": 6,
        "border-color": "#25b96f",
        "background-color": "#34c77a",
      },
    },
    {
      selector: "node.agent:selected",
      style: {
        "border-color": "#0b72f0",
        "background-color": "#57a4ff",
      },
    },
    {
      selector: "node.dim",
      style: {
        opacity: 0.22,
      },
    },
    {
      selector: "edge",
      style: {
        width: 1.4,
        "curve-style": "bezier",
        "line-color": "#8b96a8",
        "target-arrow-color": "#8b96a8",
        "target-arrow-shape": "triangle",
        "arrow-scale": 0.7,
        opacity: 0.48,
      },
    },
    {
      selector: "edge.dense",
      style: {
        width: 0.9,
        "line-color": "#9aa6b6",
        "target-arrow-color": "#9aa6b6",
        "arrow-scale": 0.48,
        opacity: 0.16,
      },
    },
    {
      selector: "edge.active",
      style: {
        width: 2.2,
        "line-color": "#536173",
        "target-arrow-color": "#536173",
        "arrow-scale": 0.75,
        opacity: 0.95,
      },
    },
    {
      selector: "edge.dim",
      style: {
        opacity: 0.08,
      },
    },
  ];
}

function graphViewPolicy(nodes, edges) {
  const dense = nodes.length > 12 || edges.length > 35;
  const importantCount = dense ? Math.min(8, nodes.length) : nodes.length;
  const importantLabelIds = new Set(
    [...nodes]
      .sort((a, b) => {
        if (b.degree !== a.degree) return b.degree - a.degree;
        return a.selection_id.localeCompare(b.selection_id);
      })
      .slice(0, importantCount)
      .map((node) => node.selection_id),
  );
  return {
    dense,
    mode: dense ? "dense" : "small",
    importantLabelIds,
    minGap: dense ? 176 : 150,
  };
}

function applyClientLayout(nodes, edges, viewPolicy) {
  const incident = new Map(nodes.map((node) => [node.selection_id, new Set()]));
  edges.forEach((edge) => {
    incident.get(edge.from_selection_id)?.add(edge.to_selection_id);
    incident.get(edge.to_selection_id)?.add(edge.from_selection_id);
  });

  const sorted = [...nodes].sort((a, b) => {
    if (b.degree !== a.degree) return b.degree - a.degree;
    if (a.surface_type !== b.surface_type) {
      return a.surface_type === "skill" ? -1 : 1;
    }
    return a.selection_id.localeCompare(b.selection_id);
  });
  if (viewPolicy.dense) {
    return applyDenseRingLayout(sorted, viewPolicy);
  }
  const hub = sorted[0];
  const hubNeighbors = new Set(incident.get(hub.selection_id) || []);
  const nearSlots = [-172, -110, -38, 22, 78, 134, 188, 238, 302].map(toRadians);
  const farSlots = [-135, -72, -8, 54, 118, 176, 230, 286, 338].map(toRadians);
  const result = [];
  let nearIndex = 0;
  let farIndex = 0;

  sorted.forEach((node) => {
    const isHub = node.selection_id === hub.selection_id;
    const ring = isHub ? 0 : hubNeighbors.has(node.selection_id) ? 1 : 2;
    const radius = ring === 0 ? 0 : ring === 1 ? 255 : 400;
    const angle = ring === 0
      ? 0
      : ring === 1
        ? nearSlots[nearIndex++ % nearSlots.length]
        : farSlots[farIndex++ % farSlots.length];
    const size = nodeRenderSize(node, viewPolicy, isHub);
    result.push({
      ...node,
      isHub,
      renderSize: size,
      cx: Math.cos(angle) * radius,
      cy: Math.sin(angle) * radius,
    });
  });
  return result;
}

function applyDenseRingLayout(sorted, viewPolicy) {
  const result = [];
  const hub = sorted[0];
  sorted.forEach((node, index) => {
    const isHub = index === 0;
    if (isHub) {
      result.push({
        ...node,
        isHub,
        renderSize: nodeRenderSize(node, viewPolicy, true),
        cx: 0,
        cy: 0,
      });
      return;
    }
    const ringPlacement = denseRingPlacement(index - 1, viewPolicy.minGap);
    result.push({
      ...node,
      isHub,
      renderSize: nodeRenderSize(node, viewPolicy, false),
      cx: Math.cos(ringPlacement.angle) * ringPlacement.radius,
      cy: Math.sin(ringPlacement.angle) * ringPlacement.radius,
    });
  });
  return result;
}

function denseRingPlacement(index, minGap) {
  let remaining = index;
  let ring = 1;
  let radius = 330;
  while (true) {
    const capacity = Math.max(8, Math.floor(2 * Math.PI * radius / minGap));
    if (remaining < capacity) {
      const offset = ring % 2 === 0 ? Math.PI / capacity : 0;
      return {
        radius,
        angle: -Math.PI / 2 + offset + remaining / capacity * 2 * Math.PI,
      };
    }
    remaining -= capacity;
    ring += 1;
    radius += 230;
  }
}

function nodeRenderSize(node, viewPolicy, isHub) {
  if (viewPolicy.dense) {
    return Math.min(76, 42 + Math.sqrt(Math.max(node.degree, 1)) * 8 + (isHub ? 8 : 0));
  }
  return Math.min(94, 48 + node.degree * 8 + (isHub ? 18 : 0));
}

function toRadians(degrees) {
  return degrees * Math.PI / 180;
}

function makeMiniMap(elements) {
  state.mini = cytoscape({
    container: els.minimap,
    elements,
    userZoomingEnabled: false,
    userPanningEnabled: false,
    autoungrabify: true,
    style: [
      {
        selector: "node",
        style: {
          width: 8,
          height: 8,
          "background-color": "#8ca3bd",
          "border-width": 0,
        },
      },
      {
        selector: "node.skill",
        style: { "background-color": "#25b96f" },
      },
      {
        selector: "node.agent",
        style: { "background-color": "#0b72f0" },
      },
      {
        selector: "edge",
        style: {
          width: 1,
          "line-color": "#b6c1ce",
          "curve-style": "bezier",
          "target-arrow-shape": "none",
        },
      },
    ],
    layout: { name: "preset", fit: true, padding: 16 },
  });
}

function destroyGraphs() {
  if (state.cy) {
    state.cy.destroy();
    state.cy = null;
  }
  if (state.mini) {
    state.mini.destroy();
    state.mini = null;
  }
  if (els.nodeOverlayLayer) {
    els.nodeOverlayLayer.innerHTML = "";
  }
}

function fitGraph() {
  if (!state.cy) return;
  state.cy.resize();
  state.cy.fit(state.cy.elements(), 92);
  centerFocusNode();
  updateZoomReadout();
}

function centerFocusNode() {
  if (!state.cy) return;
  const focusId = state.selectedId;
  if (!focusId) return;
  const focus = state.cy.getElementById(focusId);
  if (!focus || focus.empty()) return;
  const rendered = focus.renderedPosition();
  const target = {
    x: els.graphCanvas.clientWidth / 2,
    y: els.graphCanvas.clientHeight / 2,
  };
  const pan = state.cy.pan();
  state.cy.pan({
    x: pan.x + (target.x - rendered.x) * 0.72,
    y: pan.y + (target.y - rendered.y) * 0.72,
  });
}

function resetLayout() {
  if (!state.graph) return;
  renderGraph();
}

function zoomBy(factor) {
  if (!state.cy) return;
  const next = state.cy.zoom() * factor;
  state.cy.zoom({
    level: Math.max(state.cy.minZoom(), Math.min(state.cy.maxZoom(), next)),
    renderedPosition: {
      x: els.graphCanvas.clientWidth / 2,
      y: els.graphCanvas.clientHeight / 2,
    },
  });
  updateZoomReadout();
}

function updateZoomReadout() {
  if (!state.cy) {
    els.zoomReadout.textContent = "100%";
    return;
  }
  els.zoomReadout.textContent = `${Math.round(state.cy.zoom() * 100)}%`;
}

function setMode(mode) {
  if (!state.cy) return;
  const isPan = mode === "pan";
  state.cy.nodes().grabify();
  state.cy.userPanningEnabled(true);
  $("#selectModeButton").classList.toggle("is-active", !isPan);
  $("#panModeButton").classList.toggle("is-active", isPan);
  state.cy.autounselectify(isPan);
}

function updateFocusClasses() {
  if (!state.cy) return;
  const focusId = state.hoveredId || state.selectedId;
  state.cy.elements().removeClass("active dim");
  if (!focusId) {
    updateNodeOverlays();
    return;
  }
  const focus = state.cy.getElementById(focusId);
  const neighborhood = focus.closedNeighborhood();
  state.cy.elements().not(neighborhood).addClass("dim");
  neighborhood.addClass("active");
  updateNodeOverlays();
}

function updateInspector() {
  if (!state.graph || !state.selectedId) {
    els.inspectorEmpty.hidden = false;
    els.inspectorCard.hidden = true;
    return;
  }
  const node = state.graph.nodes.find((item) => item.selection_id === state.selectedId);
  if (!node) {
    clearSelection();
    return;
  }
  const incoming = state.graph.edges.filter((edge) => edge.to_selection_id === node.selection_id);
  const outgoing = state.graph.edges.filter((edge) => edge.from_selection_id === node.selection_id);
  els.inspectorEmpty.hidden = true;
  els.inspectorCard.hidden = false;
  els.selectedIcon.classList.toggle("is-agent", node.surface_type === "agent");
  els.selectedName.textContent = node.name;
  els.selectedKind.textContent = node.surface_type;
  els.selectedId.textContent = node.display_id;
  els.detailSelectionId.textContent = node.selection_id;
  els.detailPath.textContent = node.relative_path;
  els.detailAliases.textContent = node.aliases.length ? node.aliases.join(", ") : "None";
  els.detailDegree.textContent = String(node.degree);
  els.incomingEdges.innerHTML = edgeListHtml(incoming, "from_selection_id");
  els.outgoingEdges.innerHTML = edgeListHtml(outgoing, "to_selection_id");
}

function edgeListHtml(edges, peerKey) {
  if (!edges.length) return `<p class="muted">No detected edges.</p>`;
  return edges.map((edge) => {
    const peer = state.graph.nodes.find((node) => node.selection_id === edge[peerKey]);
    return `
      <button class="edge-line" type="button" data-node-id="${escapeAttr(edge[peerKey])}">
        <strong>${escapeHtml(peer ? peer.name : edge[peerKey])}</strong>
        <span>${escapeHtml(edge.match_kind)}: ${escapeHtml(edge.match_text)}</span>
      </button>
    `;
  }).join("");
}

function clearSelection() {
  state.selectedId = null;
  if (state.cy) state.cy.nodes().unselect();
  updateFocusClasses();
  updateInspector();
}

function selectNode(nodeId) {
  if (!state.cy || !nodeId) return;
  const node = state.cy.getElementById(nodeId);
  if (!node || node.empty()) return;
  state.cy.nodes().unselect();
  node.select();
  state.selectedId = nodeId;
  state.cy.animate({
    center: { eles: node },
    duration: 220,
  });
  updateFocusClasses();
  updateInspector();
}

function updatePreview() {
  const nodes = visibleNodes();
  const edges = visibleEdges();
  els.previewSource.textContent = state.graph ? sourceLabel() : "None";
  els.previewNodes.textContent = String(nodes.length);
  els.previewEdges.textContent = String(edges.length);
}

function renderNodeOverlays(nodes) {
  els.nodeOverlayLayer.innerHTML = nodes.map((node) => `
    <div class="node-overlay is-${escapeAttr(node.surface_type)}" data-node-id="${escapeAttr(node.selection_id)}">
      <div class="node-mark"></div>
      <div class="node-label">${escapeHtml(node.name)}</div>
    </div>
  `).join("");
  updateNodeOverlays();
}

function updateNodeOverlays() {
  if (!state.cy || !els.nodeOverlayLayer) return;
  const focusId = state.hoveredId || state.selectedId;
  const visibleLabelIds = focusId ? focusNeighborhoodIds(focusId) : state.importantLabelIds;
  const overlayItems = all(".node-overlay").map((overlay) => {
    const id = overlay.dataset.nodeId;
    const node = state.cy.getElementById(id);
    if (!node || node.empty()) {
      overlay.hidden = true;
      return null;
    }
    const position = node.renderedPosition();
    const size = Math.max(42, node.renderedWidth());
    return { overlay, node, id, position, size };
  }).filter(Boolean);
  const readableLabelIds = readableDenseLabelIds(overlayItems, visibleLabelIds, focusId);

  overlayItems.forEach((item) => {
    const { overlay, node, id, position, size } = item;
    overlay.hidden = false;
    overlay.style.left = `${position.x}px`;
    overlay.style.top = `${position.y}px`;
    overlay.style.setProperty("--node-size", `${size}px`);
    overlay.classList.toggle("is-selected", node.selected());
    overlay.classList.toggle("is-dim", node.hasClass("dim"));
    overlay.classList.toggle("is-dense", state.graphMode === "dense");
    overlay.classList.toggle("is-label-hidden", state.graphMode === "dense" && !readableLabelIds.has(id));
  });
}

function focusNeighborhoodIds(focusId) {
  const ids = new Set(state.importantLabelIds);
  if (!state.cy || !focusId) return ids;
  const focus = state.cy.getElementById(focusId);
  if (!focus || focus.empty()) return ids;
  focus.closedNeighborhood("node").forEach((node) => ids.add(node.id()));
  return ids;
}

function readableDenseLabelIds(items, candidateIds, focusId) {
  if (state.graphMode !== "dense") {
    return new Set(items.map((item) => item.id));
  }
  const kept = [];
  const labels = new Set();
  const sorted = [...items]
    .filter((item) => candidateIds.has(item.id))
    .sort((a, b) => labelPriority(b, focusId) - labelPriority(a, focusId));

  sorted.forEach((item) => {
    const forced = item.id === state.selectedId || item.id === state.hoveredId;
    const box = {
      x1: item.position.x - 58,
      x2: item.position.x + 58,
      y1: item.position.y + item.size / 2 + 6,
      y2: item.position.y + item.size / 2 + 34,
    };
    if (!forced && kept.some((other) => rectsOverlap(box, other, 8))) return;
    kept.push(box);
    labels.add(item.id);
  });
  return labels;
}

function labelPriority(item, focusId) {
  if (item.id === state.selectedId) return 10000;
  if (item.id === state.hoveredId) return 9000;
  if (item.id === focusId) return 8000;
  const degree = Number(item.node.data("degree")) || 0;
  return (state.importantLabelIds.has(item.id) ? 1000 : 0) + degree;
}

function rectsOverlap(a, b, padding) {
  return !(
    a.x2 + padding < b.x1
    || a.x1 - padding > b.x2
    || a.y2 + padding < b.y1
    || a.y1 - padding > b.y2
  );
}

function openDrawer(kind) {
  if (kind === "sources") {
    document.body.classList.add("sources-open");
  }
  if (kind === "inspector") {
    document.body.classList.add("inspector-open");
  }
  els.drawerBackdrop.hidden = false;
}

function closeDrawers() {
  document.body.classList.remove("sources-open", "inspector-open");
  els.drawerBackdrop.hidden = true;
}

function togglePopover(id) {
  const popover = document.getElementById(id);
  popover.hidden = !popover.hidden;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

window.addEventListener("DOMContentLoaded", init);
