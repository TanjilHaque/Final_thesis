const pptxgen = require("pptxgenjs");
let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "IT2-TrFTP Thesis Presentation";

// ─── THEME ───────────────────────────────────────────────────────────────────
const CLR = {
  navy: "1B2A4A", // primary dark
  teal: "0D7C8F", // accent
  white: "FFFFFF",
  offwhite: "F5F8FA",
  light: "DDE6EE",
  text: "1A1A2E",
  muted: "5B6E8A",
  green: "1D7A4A",
  amber: "C27A00",
  red: "B52B2B",
};

const FONT = "Arial";
const TITLE_SZ = 26;
const BODY_SZ = 15;
const SMALL_SZ = 12;
const LABEL_SZ = 11;
const TOTAL_SLIDES = 22; // cover + 20 content + thank you

// ─── HELPERS ─────────────────────────────────────────────────────────────────
function slideNum(n) {
  // n = content slide number (1-20), displayed as n / 20
  return `${n} / 20`;
}

function addPageNum(slide, n) {
  slide.addText(slideNum(n), {
    x: 8.8,
    y: 5.25,
    w: 1.0,
    h: 0.28,
    fontFace: FONT,
    fontSize: LABEL_SZ,
    color: CLR.muted,
    align: "right",
    margin: 0,
  });
}

function addTitle(slide, text, dark = false) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0,
    y: 0,
    w: 10,
    h: 0.72,
    fill: { color: dark ? CLR.navy : CLR.teal },
  });
  slide.addText(text, {
    x: 0.3,
    y: 0,
    w: 9.4,
    h: 0.72,
    fontFace: FONT,
    fontSize: TITLE_SZ,
    bold: true,
    color: CLR.white,
    valign: "middle",
    margin: 0,
  });
}

function addBody(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x,
    y,
    w,
    h,
    fontFace: FONT,
    fontSize: opts.sz || BODY_SZ,
    color: opts.color || CLR.text,
    bold: opts.bold || false,
    italic: opts.italic || false,
    align: opts.align || "left",
    valign: opts.valign || "top",
    margin: opts.margin !== undefined ? opts.margin : 4,
    wrap: true,
  });
}

function card(slide, x, y, w, h, fillColor, shadow = true) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x,
    y,
    w,
    h,
    fill: { color: fillColor },
    rectRadius: 0.08,
    shadow: shadow
      ? {
          type: "outer",
          color: "000000",
          blur: 5,
          offset: 2,
          angle: 45,
          opacity: 0.12,
        }
      : undefined,
  });
}

function makeShadow() {
  return {
    type: "outer",
    color: "000000",
    blur: 5,
    offset: 2,
    angle: 45,
    opacity: 0.12,
  };
}

function placeholder(slide, x, y, w, h, label) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x,
    y,
    w,
    h,
    fill: { color: CLR.light },
    line: { color: CLR.teal, width: 1, dashType: "dash" },
  });
  slide.addText(`[ ${label} ]`, {
    x,
    y,
    w,
    h,
    fontFace: FONT,
    fontSize: LABEL_SZ,
    color: CLR.teal,
    bold: true,
    align: "center",
    valign: "middle",
    margin: 0,
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 0 — COVER
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.navy };

  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0,
    y: 0,
    w: 10,
    h: 1.1,
    fill: { color: CLR.teal },
  });
  sl.addText("DEPARTMENT OF INDUSTRIAL AND PRODUCTION ENGINEERING | BUET", {
    x: 0.3,
    y: 0.1,
    w: 9.4,
    h: 0.9,
    fontFace: FONT,
    fontSize: 11,
    color: CLR.white,
    bold: true,
    align: "center",
    valign: "middle",
  });

  sl.addText(
    "Comparative Performance and Robustness Analysis of\nModified Vogel's and Modified Russell's Approximation Methods\nunder Interval Type-2 Trapezoidal Fuzzy Uncertainty",
    {
      x: 0.5,
      y: 1.35,
      w: 9,
      h: 2.0,
      fontFace: FONT,
      fontSize: 20,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
    },
  );

  sl.addShape(pres.shapes.LINE, {
    x: 1,
    y: 3.45,
    w: 8,
    h: 0,
    line: { color: CLR.teal, width: 2 },
  });

  sl.addText(
    "Md Sadiqul Haque  (ID: 2008082)     |     Md Tanjil Haque  (ID: 2008094)",
    {
      x: 0.5,
      y: 3.6,
      w: 9,
      h: 0.4,
      fontFace: FONT,
      fontSize: 13,
      color: CLR.light,
      align: "center",
    },
  );
  sl.addText("Supervised by: Dr. Kais Bin Zaman, Professor, IPE, BUET", {
    x: 0.5,
    y: 4.08,
    w: 9,
    h: 0.35,
    fontFace: FONT,
    fontSize: 13,
    color: CLR.light,
    align: "center",
  });
  sl.addText("B.Sc. in Industrial & Production Engineering  |  June 2026", {
    x: 0.5,
    y: 4.5,
    w: 9,
    h: 0.35,
    fontFace: FONT,
    fontSize: 12,
    color: CLR.muted,
    align: "center",
  });

  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0,
    y: 5.3,
    w: 10,
    h: 0.32,
    fill: { color: "0A1A2E" },
  });
  sl.addText("BUET — Bangladesh University of Engineering and Technology", {
    x: 0.3,
    y: 5.3,
    w: 9.4,
    h: 0.32,
    fontFace: FONT,
    fontSize: 10,
    color: CLR.muted,
    align: "center",
    valign: "middle",
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 1 — PRESENTATION OUTLINE
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Presentation Outline");

  const items = [
    ["01", "Transportation Problem Background"],
    ["02", "Uncertainty Modeling: T1 vs IT2 Fuzzy Sets"],
    ["03", "Research Gap & Problem Statement"],
    ["04", "Research Objectives & Scope"],
    ["05", "IT2 Fuzzy Framework: Fuzzification"],
    ["06", "IT2 Fuzzy Framework: KM & Defuzzification"],
    ["07", "Balance-Preserving Normalization"],
    ["08", "MVAM: Modified Vogel's Approx. Method"],
    ["09", "MRAM: Modified Russell's Approx. Method"],
    ["10", "MODI Optimization & Performance Metrics"],
    ["11", "Structural Regimes: Penalty-Sharp vs Diffuse"],
    ["12", "Synthetic Dataset Design"],
    ["13", "Results: Small & Medium Scale"],
    ["14", "Results: Large & Extended Scale"],
    ["15", "Statistical Benchmarking Summary"],
    ["16", "Problem Structure vs Problem Size"],
    ["17", "Cost Sensitivity Analysis"],
    ["18", "Footprint of Uncertainty (FOU) Sensitivity"],
    ["19", "Joint Robustness Assessment"],
    ["20", "Contributions, Limitations & Future Work"],
  ];

  const cols = [items.slice(0, 10), items.slice(10, 20)];
  cols.forEach((col, ci) => {
    col.forEach(([num, label], ri) => {
      const x = 0.3 + ci * 4.85;
      const y = 0.88 + ri * 0.44;
      card(sl, x, y, 4.55, 0.38, CLR.white, false);
      sl.addText(num, {
        x: x + 0.08,
        y,
        w: 0.45,
        h: 0.38,
        fontFace: FONT,
        fontSize: 12,
        bold: true,
        color: CLR.teal,
        align: "center",
        valign: "middle",
        margin: 0,
      });
      sl.addShape(pres.shapes.LINE, {
        x: x + 0.53,
        y: y + 0.07,
        w: 0,
        h: 0.24,
        line: { color: CLR.light, width: 1 },
      });
      sl.addText(label, {
        x: x + 0.6,
        y,
        w: 3.85,
        h: 0.38,
        fontFace: FONT,
        fontSize: 12,
        color: CLR.text,
        valign: "middle",
        margin: 0,
      });
    });
  });
  addPageNum(sl, 1);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 2 — TRANSPORTATION PROBLEM BACKGROUND
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "The Transportation Problem (TP) — Background");

  // Left column: text
  addBody(
    sl,
    "Introduced by Hitchcock [1] (1941) & Koopmans [2] (1947)",
    0.3,
    0.88,
    4.4,
    0.38,
    { bold: true, sz: 14 },
  );

  const lines = [
    "Minimize total shipping cost from m sources → n destinations",
    "Decision variable: x_ij = units shipped from source i to destination j",
    "Subject to: supply & demand constraints + non-negativity",
  ];
  lines.forEach((t, i) => {
    sl.addShape(pres.shapes.OVAL, {
      x: 0.35,
      y: 1.37 + i * 0.52,
      w: 0.14,
      h: 0.14,
      fill: { color: CLR.teal },
    });
    addBody(sl, t, 0.57, 1.3 + i * 0.52, 4.1, 0.4, { sz: 13 });
  });

  // Formula card
  card(sl, 0.3, 2.92, 4.4, 1.12, CLR.white);
  sl.addText("Objective Function:", {
    x: 0.45,
    y: 2.98,
    w: 4.1,
    h: 0.28,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.teal,
    margin: 0,
  });
  sl.addText("Minimize  Z  =  Σᵢ Σⱼ  cᵢⱼ · xᵢⱼ", {
    x: 0.45,
    y: 3.28,
    w: 4.1,
    h: 0.32,
    fontFace: FONT,
    fontSize: 15,
    italic: true,
    bold: true,
    color: CLR.navy,
    align: "center",
    margin: 0,
  });
  sl.addText(
    "cᵢⱼ = unit cost (i→j)   |   xᵢⱼ = units shipped   |   Σᵢ sᵢ = Σⱼ dⱼ  (balance)",
    {
      x: 0.45,
      y: 3.63,
      w: 4.1,
      h: 0.33,
      fontFace: FONT,
      fontSize: 11,
      color: CLR.muted,
      align: "center",
      margin: 0,
    },
  );

  // Right: placeholder for supply-demand network diagram
  placeholder(
    sl,
    4.9,
    0.85,
    4.8,
    3.25,
    "Figure: Supply-Demand Network Diagram\n(Insert Figure 4.4 — Simplified Workflow)",
  );

  addPageNum(sl, 2);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 3 — UNCERTAINTY IN TRANSPORTATION: T1 vs IT2
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(
    sl,
    "Uncertainty Modeling: Type-1 (T1FS) vs Interval Type-2 (IT2FS)",
  );

  const cols = [
    {
      hdr: "Type-1 Fuzzy Set (T1FS)",
      ref: "Zadeh [6], 1965",
      color: CLR.teal,
      pts: [
        "Membership grade: precise number ∈ [0,1]",
        "Suitable for simple linguistic uncertainty",
        "Cannot model uncertainty in the membership function itself",
        "Limitation: assumes membership perfectly known",
      ],
    },
    {
      hdr: "Interval Type-2 Fuzzy Set (IT2FS)",
      ref: "Mendel & John [8]",
      color: CLR.navy,
      pts: [
        "Membership grade: interval — models higher-order uncertainty",
        "Bounded by Upper MF (UMF) and Lower MF (LMF)",
        "Footprint of Uncertainty (FOU) = area between UMF & LMF",
        "Captures expert disagreement, noise, incomplete data",
      ],
    },
  ];

  cols.forEach((c, ci) => {
    const x = 0.3 + ci * 4.85;
    card(sl, x, 0.85, 4.55, 3.6, CLR.white);
    sl.addShape(pres.shapes.RECTANGLE, {
      x,
      y: 0.85,
      w: 4.55,
      h: 0.48,
      fill: { color: c.color },
      rectRadius: 0,
    });
    sl.addText(c.hdr, {
      x: x + 0.1,
      y: 0.85,
      w: 4.35,
      h: 0.32,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.white,
      valign: "middle",
      margin: 0,
    });
    sl.addText(`(${c.ref})`, {
      x: x + 0.1,
      y: 1.13,
      w: 4.35,
      h: 0.22,
      fontFace: FONT,
      fontSize: 10,
      color: CLR.white,
      italic: true,
      margin: 0,
    });
    c.pts.forEach((pt, pi) => {
      sl.addShape(pres.shapes.OVAL, {
        x: x + 0.1,
        y: 1.5 + pi * 0.55,
        w: 0.12,
        h: 0.12,
        fill: { color: c.color },
      });
      addBody(sl, pt, x + 0.28, 1.44 + pi * 0.55, 4.1, 0.48, { sz: 13 });
    });
  });

  card(sl, 0.3, 4.54, 9.4, 0.55, CLR.navy, false);
  sl.addText(
    "Key Insight: IT2FS has a second layer of uncertainty — uncertainty about the membership function itself. This is critical for real-world transportation.",
    {
      x: 0.5,
      y: 4.54,
      w: 9.0,
      h: 0.55,
      fontFace: FONT,
      fontSize: 13,
      color: CLR.white,
      bold: true,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 3);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 4 — RESEARCH GAP & PROBLEM STATEMENT
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Research Gaps & Problem Statement");

  const gaps = [
    ["Gap 1", "No comparative study of MVAM vs MRAM under IT2 uncertainty"],
    [
      "Gap 2",
      "Pratihar et al. [14] introduced MVAM — but no alternative heuristic tested",
    ],
    ["Gap 3", "No systematic benchmarking across multiple scales"],
    [
      "Gap 4",
      "Transportation problem structure not studied as performance predictor",
    ],
    ["Gap 5", "FOU sensitivity not analyzed in IT2 transportation literature"],
    ["Gap 6", "No balance-restoration mechanism after KM defuzzification"],
  ];

  gaps.forEach(([lbl, txt], i) => {
    const row = Math.floor(i / 2);
    const col = i % 2;
    const x = 0.3 + col * 4.85;
    const y = 0.88 + row * 0.88;
    card(sl, x, y, 4.55, 0.76, CLR.white);
    sl.addText(lbl, {
      x: x + 0.1,
      y: y + 0.05,
      w: 0.9,
      h: 0.3,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: CLR.teal,
      margin: 0,
    });
    addBody(sl, txt, x + 0.1, y + 0.32, 4.25, 0.38, { sz: 12 });
  });

  card(sl, 0.3, 3.58, 9.4, 0.56, CLR.navy, false);
  sl.addText(
    "→ This thesis fills all six gaps by building a complete IT2-TrFTP pipeline and comparing MVAM vs MRAM at scale.",
    {
      x: 0.5,
      y: 3.58,
      w: 9.0,
      h: 0.56,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 4);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 5 — RESEARCH OBJECTIVES & SCOPE
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Research Objectives & Scope");

  // Left: Objectives
  card(sl, 0.3, 0.85, 5.5, 3.85, CLR.white);
  sl.addText("Research Objectives", {
    x: 0.45,
    y: 0.9,
    w: 5.2,
    h: 0.32,
    fontFace: FONT,
    fontSize: 14,
    bold: true,
    color: CLR.teal,
    margin: 0,
  });
  const objs = [
    "Develop an IT2 trapezoidal fuzzification pipeline",
    "Implement KM type-reduction & defuzzification",
    "Design a balance-preserving normalization layer",
    "Compare MVAM vs MRAM under IT2 uncertainty",
    "Benchmark across multiple problem scales",
    "Conduct Cost Magnitude & FOU Sensitivity Analysis",
  ];
  objs.forEach((o, i) => {
    sl.addText(`${i + 1}.`, {
      x: 0.45,
      y: 1.3 + i * 0.52,
      w: 0.3,
      h: 0.4,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.teal,
      margin: 0,
    });
    addBody(sl, o, 0.8, 1.3 + i * 0.52, 4.8, 0.4, { sz: 13 });
  });

  // Right: Scope & Delimitations
  card(sl, 6.0, 0.85, 3.7, 3.85, CLR.white);
  sl.addText("Scope", {
    x: 6.15,
    y: 0.9,
    w: 3.4,
    h: 0.32,
    fontFace: FONT,
    fontSize: 14,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  const scope = [
    "Balanced TP only",
    "IT2 trapezoidal fuzzy",
    "MVAM & MRAM (IBFS)",
    "MODI (optimization)",
    "Synthetic datasets",
    "Cost & FOU sensitivity",
  ];
  const noScope = [
    "General T2FS",
    "Multi-objective TP",
    "Metaheuristics",
    "Real-time networks",
  ];
  sl.addText("Included:", {
    x: 6.15,
    y: 1.28,
    w: 3.4,
    h: 0.28,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.green,
    margin: 0,
  });
  scope.forEach((s, i) =>
    addBody(sl, `✓  ${s}`, 6.15, 1.58 + i * 0.36, 3.4, 0.3, { sz: 12 }),
  );
  sl.addText("Excluded:", {
    x: 6.15,
    y: 3.78,
    w: 3.4,
    h: 0.28,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.red,
    margin: 0,
  });

  addPageNum(sl, 5);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 6 — IT2-TrFTP FRAMEWORK: FUZZIFICATION
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "IT2-TrFTP Framework: Three-Dimensional Fuzzification");

  // 3 dimension cards
  const dims = [
    {
      lbl: "Geometric Uncertainty",
      sym: "αg",
      desc: "Controls UMF spread/shape\nWider αg → wider trapezoid\nModels spatial ambiguity",
      color: CLR.teal,
    },
    {
      lbl: "Epistemic Uncertainty",
      sym: "ρ",
      desc: "Controls LMF contraction\nρ close to 1 → narrow FOU\nModels knowledge gap",
      color: CLR.navy,
    },
    {
      lbl: "Confidence/Variability",
      sym: "γ",
      desc: "Controls LMF height\nModels membership certainty\nOrthogonal degree of freedom",
      color: "2D6A4F",
    },
  ];
  dims.forEach((d, i) => {
    const x = 0.3 + i * 3.2;
    card(sl, x, 0.85, 3.0, 1.7, CLR.white);
    sl.addShape(pres.shapes.RECTANGLE, {
      x,
      y: 0.85,
      w: 3.0,
      h: 0.38,
      fill: { color: d.color },
    });
    sl.addText(d.lbl, {
      x: x + 0.08,
      y: 0.85,
      w: 2.84,
      h: 0.38,
      fontFace: FONT,
      fontSize: 12,
      bold: true,
      color: CLR.white,
      valign: "middle",
      margin: 0,
    });
    sl.addText(`Symbol: ${d.sym}`, {
      x: x + 0.12,
      y: 1.28,
      w: 2.76,
      h: 0.28,
      fontFace: FONT,
      fontSize: 12,
      bold: true,
      italic: true,
      color: d.color,
      margin: 0,
    });
    d.desc
      .split("\n")
      .forEach((ln, li) =>
        addBody(sl, ln, x + 0.12, 1.56 + li * 0.3, 2.76, 0.28, { sz: 11 }),
      );
  });

  // Formula for UMF
  card(sl, 0.3, 2.68, 5.5, 1.55, CLR.white);
  sl.addText("UMF Trapezoid Construction:", {
    x: 0.45,
    y: 2.73,
    w: 5.2,
    h: 0.28,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.teal,
    margin: 0,
  });
  sl.addText("Ã_UMF  =  (a, b, c, d)  where:", {
    x: 0.45,
    y: 3.03,
    w: 5.2,
    h: 0.28,
    fontFace: FONT,
    fontSize: 14,
    italic: true,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  sl.addText(
    "a = x·(1 − αg)   b = x·(1 − αg/2)   c = x·(1 + αg/2)   d = x·(1 + αg)",
    {
      x: 0.45,
      y: 3.33,
      w: 5.2,
      h: 0.28,
      fontFace: FONT,
      fontSize: 12,
      italic: true,
      color: CLR.text,
      margin: 0,
    },
  );
  sl.addText("x = crisp parameter   αg = geometric uncertainty coefficient", {
    x: 0.45,
    y: 3.64,
    w: 5.2,
    h: 0.28,
    fontFace: FONT,
    fontSize: 11,
    color: CLR.muted,
    margin: 0,
  });

  // Right: IT2FS figure placeholder
  placeholder(
    sl,
    6.0,
    2.68,
    3.7,
    1.55,
    "Figure 3.3: IT2FS with FOU\n(Insert from Thesis — UMF/LMF trapezoid diagram)",
  );

  // Fuzzification applies to:
  card(sl, 0.3, 4.32, 9.4, 0.5, CLR.light, false);
  sl.addText(
    "Fuzzification applies to:  (1) Transportation Costs  cᵢⱼ   |   (2) Supply Values  sᵢ   |   (3) Demand Values  dⱼ",
    {
      x: 0.5,
      y: 4.32,
      w: 9.0,
      h: 0.5,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.navy,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 6);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 7 — KM TYPE-REDUCTION & DEFUZZIFICATION
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "KM Type-Reduction & Centroid Defuzzification");

  // Left: Steps
  const steps = [
    [
      "Step 1: Type-Reduction",
      "Karnik–Mendel (KM) Algorithm [9][10]\nComputes centroid interval [y_l, y_r]\nIterative switch-point procedure — guaranteed convergence",
    ],
    [
      "Step 2: Centroid Formula",
      "y_l = left centroid\ny_r = right centroid\n(computed separately)",
    ],
    [
      "Step 3: Defuzzification",
      "y* = (y_l + y_r) / 2\ny* = crisp scalar value\nUsed as input to transportation algorithms",
    ],
  ];

  steps.forEach(([hdr, body], i) => {
    card(sl, 0.3, 0.85 + i * 1.42, 5.0, 1.28, CLR.white);
    sl.addText(hdr, {
      x: 0.45,
      y: 0.88 + i * 1.42,
      w: 4.7,
      h: 0.3,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.teal,
      margin: 0,
    });
    body.split("\n").forEach((ln, li) => {
      const isFormula =
        ln.includes("=") &&
        !ln.includes("computed") &&
        !ln.includes("Iterative");
      addBody(sl, ln, 0.45, 1.22 + i * 1.42 + li * 0.3, 4.7, 0.28, {
        sz: isFormula ? 13 : 12,
        italic: isFormula,
        color: isFormula ? CLR.navy : CLR.text,
      });
    });
  });

  // Right: centroid formula card
  card(sl, 5.5, 0.85, 4.2, 2.6, CLR.white);
  sl.addText("Centroid Type-Reduction (KM):", {
    x: 5.65,
    y: 0.92,
    w: 3.9,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  sl.addText("C(Ã) = [y_l, y_r]", {
    x: 5.65,
    y: 1.26,
    w: 3.9,
    h: 0.36,
    fontFace: FONT,
    fontSize: 18,
    italic: true,
    bold: true,
    color: CLR.teal,
    align: "center",
    margin: 0,
  });
  const defs = [
    "y_l  = left endpoint of centroid interval",
    "y_r  = right endpoint of centroid interval",
    "Ã    = IT2 trapezoidal fuzzy number",
  ];
  defs.forEach((d, i) =>
    addBody(sl, d, 5.65, 1.68 + i * 0.38, 3.9, 0.32, { sz: 12, italic: true }),
  );

  sl.addShape(pres.shapes.LINE, {
    x: 5.65,
    y: 2.88,
    w: 3.9,
    h: 0,
    line: { color: CLR.light, width: 1 },
  });
  sl.addText("Crisp Output:", {
    x: 5.65,
    y: 2.95,
    w: 3.9,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  sl.addText("y* = (y_l + y_r) / 2", {
    x: 5.65,
    y: 3.26,
    w: 3.9,
    h: 0.36,
    fontFace: FONT,
    fontSize: 18,
    italic: true,
    bold: true,
    color: CLR.teal,
    align: "center",
    margin: 0,
  });

  // KM flowchart placeholder
  placeholder(
    sl,
    5.5,
    3.6,
    4.2,
    0.62,
    "Figure 3.4 / 3.5: KM Algorithm Flowchart (Insert from Thesis)",
  );

  // Note
  card(sl, 0.3, 4.32, 9.4, 0.5, CLR.navy, false);
  sl.addText(
    "N = 1000 discretization points | Convergence tolerance = 10⁻⁸ | Applied to every cost, supply & demand IT2 parameter",
    {
      x: 0.5,
      y: 4.32,
      w: 9.0,
      h: 0.5,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 7);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 8 — BALANCE-PRESERVING NORMALIZATION
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Balance-Preserving Normalization Layer (Novel Contribution)");

  // Problem
  card(sl, 0.3, 0.85, 4.3, 1.6, CLR.white);
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0.3,
    y: 0.85,
    w: 4.3,
    h: 0.38,
    fill: { color: CLR.red },
  });
  sl.addText("The Problem: Post-Defuzzification Imbalance", {
    x: 0.42,
    y: 0.85,
    w: 4.1,
    h: 0.38,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.white,
    valign: "middle",
    margin: 0,
  });
  sl.addText(
    "Supply & demand fuzzified independently\n→ KM centroids diverge slightly\n→ Σsᵢ ≠ Σdⱼ after defuzzification\n→ Transportation problem becomes infeasible!",
    {
      x: 0.42,
      y: 1.28,
      w: 4.1,
      h: 1.1,
      fontFace: FONT,
      fontSize: 13,
      color: CLR.text,
      margin: 4,
    },
  );

  // Solution
  card(sl, 4.9, 0.85, 4.8, 1.6, CLR.white);
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 4.9,
    y: 0.85,
    w: 4.8,
    h: 0.38,
    fill: { color: CLR.green },
  });
  sl.addText("The Solution: Proportional Normalization", {
    x: 5.02,
    y: 0.85,
    w: 4.6,
    h: 0.38,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.white,
    valign: "middle",
    margin: 0,
  });
  sl.addText(
    "Compute anchor:  T = (Σs_KM + Σd_KM) / 2\nScale demand:  dⱼ* = dⱼ · (T / Σdⱼ)\nResult:  Σsᵢ = Σdⱼ* exactly",
    {
      x: 5.02,
      y: 1.28,
      w: 4.6,
      h: 0.82,
      fontFace: FONT,
      fontSize: 13,
      italic: true,
      color: CLR.navy,
      margin: 4,
    },
  );

  // Formula card
  card(sl, 0.3, 2.55, 9.4, 0.85, CLR.white);
  sl.addText("Normalization Formula:", {
    x: 0.5,
    y: 2.6,
    w: 2.5,
    h: 0.28,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.teal,
    margin: 0,
  });
  sl.addText(
    "dⱼ*  =  dⱼ  ·  ( T / Σⱼ dⱼ )     where   T = ( Σᵢ sᵢ_KM + Σⱼ dⱼ_KM ) / 2",
    {
      x: 3.0,
      y: 2.6,
      w: 6.5,
      h: 0.35,
      fontFace: FONT,
      fontSize: 15,
      italic: true,
      bold: true,
      color: CLR.navy,
      align: "center",
      margin: 0,
    },
  );
  sl.addText(
    "dⱼ = raw defuzzified demand   |   T = symmetric anchor   |   Result: exact balance Σsᵢ = Σdⱼ*",
    {
      x: 0.5,
      y: 2.97,
      w: 9.0,
      h: 0.28,
      fontFace: FONT,
      fontSize: 11,
      color: CLR.muted,
      align: "center",
      margin: 0,
    },
  );

  // 4 guarantees
  sl.addText("4 Mathematical Guarantees:", {
    x: 0.3,
    y: 3.5,
    w: 4.0,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  const gs = [
    ["Exact balance restoration", "Σsᵢ = Σdⱼ always"],
    ["Ratio preservation", "Proportional structure kept"],
    ["Full determinism", "No randomness"],
    ["Minimal distortion", "Correction < 0.02% per element"],
  ];
  gs.forEach(([g1, g2], i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.3 + col * 4.85;
    const y = 3.84 + row * 0.48;
    card(sl, x, y, 4.55, 0.42, CLR.light, false);
    sl.addText("✓", {
      x: x + 0.08,
      y,
      w: 0.32,
      h: 0.42,
      fontFace: FONT,
      fontSize: 14,
      bold: true,
      color: CLR.green,
      align: "center",
      valign: "middle",
      margin: 0,
    });
    addBody(sl, `${g1}  —  ${g2}`, x + 0.42, y, 4.0, 0.42, { sz: 12 });
  });

  addPageNum(sl, 8);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 9 — MVAM
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "MVAM — Modified Vogel's Approximation Method");

  // Left: procedure
  card(sl, 0.3, 0.85, 5.1, 3.5, CLR.white);
  sl.addText("Algorithm Steps:", {
    x: 0.45,
    y: 0.92,
    w: 4.8,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.teal,
    margin: 0,
  });
  const steps = [
    "Compute row penalty:  Pᵢ = c_i(1) − c_i(2)",
    "Compute column penalty:  Pⱼ = c_j(1) − c_j(2)",
    "Select row/column with largest penalty",
    "Allocate max to minimum-cost cell in that row/col",
    "Update supply & demand; remove exhausted row/col",
    "Repeat until all supplies & demands are satisfied",
  ];
  steps.forEach((s, i) => {
    sl.addShape(pres.shapes.OVAL, {
      x: 0.42,
      y: 1.3 + i * 0.4,
      w: 0.22,
      h: 0.22,
      fill: { color: CLR.teal },
    });
    sl.addText(`${i + 1}`, {
      x: 0.42,
      y: 1.3 + i * 0.4,
      w: 0.22,
      h: 0.22,
      fontFace: FONT,
      fontSize: 9,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    });
    addBody(sl, s, 0.72, 1.28 + i * 0.4, 4.5, 0.36, {
      sz: 12,
      italic: s.includes("="),
    });
  });

  // Formula box
  card(sl, 0.3, 4.4, 5.1, 0.4, CLR.navy, false);
  sl.addText(
    "Pᵢ = c_i(1) − c_i(2)   where  c_i(1) = min cost in row i,   c_i(2) = 2nd min cost in row i",
    {
      x: 0.45,
      y: 4.4,
      w: 4.9,
      h: 0.4,
      fontFace: FONT,
      fontSize: 11,
      italic: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  // Right: characteristics
  card(sl, 5.6, 0.85, 4.1, 1.7, CLR.white);
  sl.addText("When MVAM Excels:", {
    x: 5.75,
    y: 0.92,
    w: 3.8,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.teal,
    margin: 0,
  });
  sl.addText(
    "✓  Wide cost range (cₘₐₓ − cₘᵢₙ large)\n✓  Low noise in cost matrix\n✓  Penalty-Sharp regime: clear differentiation",
    {
      x: 5.75,
      y: 1.25,
      w: 3.8,
      h: 1.15,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.text,
      margin: 4,
    },
  );

  card(sl, 5.6, 2.65, 4.1, 1.65, CLR.white);
  sl.addText("When MVAM Struggles:", {
    x: 5.75,
    y: 2.72,
    w: 3.8,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.red,
    margin: 0,
  });
  sl.addText(
    "✗  Narrow cost range\n✗  High noise (penalties become indistinguishable)\n✗  Penalty-Diffuse regime",
    {
      x: 5.75,
      y: 3.05,
      w: 3.8,
      h: 1.1,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.text,
      margin: 4,
    },
  );

  placeholder(
    sl,
    5.6,
    4.38,
    4.1,
    0.45,
    "Operates on defuzzified crisp cost matrix C* from KM pipeline",
  );

  addPageNum(sl, 9);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 10 — MRAM
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "MRAM — Modified Russell's Approximation Method");

  // Left: procedure
  card(sl, 0.3, 0.85, 5.1, 3.5, CLR.white);
  sl.addText("Algorithm Steps:", {
    x: 0.45,
    y: 0.92,
    w: 4.8,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  const steps = [
    "Compute row reference value:  uᵢ = max_j (cᵢⱼ)  for each row i",
    "Compute col reference value:  vⱼ = max_i (cᵢⱼ)  for each col j",
    "Compute Russell measure:  Rᵢⱼ = cᵢⱼ − uᵢ − vⱼ",
    "Select cell with most negative Rᵢⱼ (highest opportunity)",
    "Allocate max to that cell; update supply & demand",
    "Repeat until all allocations satisfied",
  ];
  steps.forEach((s, i) => {
    sl.addShape(pres.shapes.OVAL, {
      x: 0.42,
      y: 1.3 + i * 0.4,
      w: 0.22,
      h: 0.22,
      fill: { color: CLR.navy },
    });
    sl.addText(`${i + 1}`, {
      x: 0.42,
      y: 1.3 + i * 0.4,
      w: 0.22,
      h: 0.22,
      fontFace: FONT,
      fontSize: 9,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    });
    addBody(sl, s, 0.72, 1.28 + i * 0.4, 4.5, 0.36, {
      sz: 12,
      italic: s.includes("="),
    });
  });

  // Formula box
  card(sl, 0.3, 4.4, 5.1, 0.4, CLR.navy, false);
  sl.addText(
    "Rᵢⱼ = cᵢⱼ − uᵢ − vⱼ   where  uᵢ = max row cost,   vⱼ = max col cost",
    {
      x: 0.45,
      y: 4.4,
      w: 4.9,
      h: 0.4,
      fontFace: FONT,
      fontSize: 11,
      italic: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  // Right: key difference
  card(sl, 5.6, 0.85, 4.1, 1.65, CLR.white);
  sl.addText("Key Difference from MVAM:", {
    x: 5.75,
    y: 0.92,
    w: 3.8,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  sl.addText(
    "MVAM uses local penalty (row/col min diff)\nMRAM uses global cost structure (max references)\nMRAM estimates opportunity cost relative to entire row/col landscape",
    {
      x: 5.75,
      y: 1.25,
      w: 3.8,
      h: 1.1,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.text,
      margin: 4,
    },
  );

  card(sl, 5.6, 2.62, 4.1, 1.65, CLR.white);
  sl.addText("When MRAM Excels:", {
    x: 5.75,
    y: 2.69,
    w: 3.8,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.green,
    margin: 0,
  });
  sl.addText(
    "✓  Narrow cost range (homogeneous matrix)\n✓  High noise (penalty signals weak)\n✓  Penalty-Diffuse regime\n✓  Global topology still informative",
    {
      x: 5.75,
      y: 3.02,
      w: 3.8,
      h: 1.1,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.text,
      margin: 4,
    },
  );

  placeholder(
    sl,
    5.6,
    4.38,
    4.1,
    0.45,
    "Figure 4.1: RAM Allocation Flowchart (Insert from Thesis)",
  );

  addPageNum(sl, 10);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 11 — MODI & PERFORMANCE METRICS
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "MODI Optimization & Performance Evaluation Metrics");

  // MODI left
  card(sl, 0.3, 0.85, 4.7, 3.2, CLR.white);
  sl.addText("Modified Distribution Method (MODI) [5][13]", {
    x: 0.45,
    y: 0.92,
    w: 4.4,
    h: 0.32,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.teal,
    margin: 0,
  });
  sl.addText("Dual variables for occupied cells:", {
    x: 0.45,
    y: 1.3,
    w: 4.4,
    h: 0.26,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  sl.addText("uᵢ + vⱼ = cᵢⱼ   for all basic cells", {
    x: 0.45,
    y: 1.6,
    w: 4.4,
    h: 0.3,
    fontFace: FONT,
    fontSize: 14,
    italic: true,
    bold: true,
    color: CLR.navy,
    align: "center",
    margin: 0,
  });
  sl.addText(
    "uᵢ = row potential   vⱼ = col potential   cᵢⱼ = cost of basic cell",
    {
      x: 0.45,
      y: 1.93,
      w: 4.4,
      h: 0.26,
      fontFace: FONT,
      fontSize: 11,
      color: CLR.muted,
      align: "center",
      margin: 0,
    },
  );
  sl.addText("Opportunity cost for non-basic cells:", {
    x: 0.45,
    y: 2.25,
    w: 4.4,
    h: 0.26,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  sl.addText("Δᵢⱼ = cᵢⱼ − uᵢ − vⱼ", {
    x: 0.45,
    y: 2.54,
    w: 4.4,
    h: 0.3,
    fontFace: FONT,
    fontSize: 14,
    italic: true,
    bold: true,
    color: CLR.navy,
    align: "center",
    margin: 0,
  });
  sl.addText("Δᵢⱼ = opportunity cost   If all Δᵢⱼ ≥ 0: OPTIMAL", {
    x: 0.45,
    y: 2.87,
    w: 4.4,
    h: 0.26,
    fontFace: FONT,
    fontSize: 11,
    color: CLR.muted,
    align: "center",
    margin: 0,
  });
  sl.addText(
    "If any Δᵢⱼ < 0: loop-shift to reduce cost. Repeat until optimal.",
    {
      x: 0.45,
      y: 3.18,
      w: 4.4,
      h: 0.6,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.text,
      margin: 4,
    },
  );

  // Metrics right
  card(sl, 5.2, 0.85, 4.5, 3.2, CLR.white);
  sl.addText("Performance Metrics", {
    x: 5.35,
    y: 0.92,
    w: 4.2,
    h: 0.32,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  const metrics = [
    ["IBFS Cost", "Z_IBFS = Σᵢ Σⱼ cᵢⱼ · xᵢⱼ⁽⁰⁾", "Initial solution quality"],
    ["MODI Cost", "Z_OPT = Σᵢ Σⱼ cᵢⱼ · xᵢⱼ*", "Final optimized cost"],
    [
      "% Improvement",
      "Δ% = (Z_IBFS − Z_OPT)/Z_IBFS × 100",
      "IBFS closeness to optimum",
    ],
    [
      "Runtime T",
      "30 repetitions, 95% CI (t-dist.)",
      "Computational efficiency",
    ],
    ["MODI Iterations", "Count until Δᵢⱼ ≥ 0", "Convergence behavior"],
  ];
  metrics.forEach(([name, form, note], i) => {
    card(sl, 5.35, 1.33 + i * 0.53, 4.2, 0.47, CLR.offwhite, false);
    sl.addText(name, {
      x: 5.45,
      y: 1.36 + i * 0.53,
      w: 1.3,
      h: 0.24,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: CLR.teal,
      margin: 0,
    });
    sl.addText(form, {
      x: 5.45,
      y: 1.6 + i * 0.53,
      w: 4.0,
      h: 0.2,
      fontFace: FONT,
      fontSize: 10,
      italic: true,
      color: CLR.navy,
      margin: 0,
    });
  });

  card(sl, 0.3, 4.16, 9.4, 0.42, CLR.navy, false);
  sl.addText(
    "Both MVAM and MRAM are followed by the SAME MODI optimizer → isolates initialization quality from final cost comparison",
    {
      x: 0.5,
      y: 4.16,
      w: 9.0,
      h: 0.42,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.white,
      bold: true,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 11);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 12 — STRUCTURAL REGIMES
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Structural Regimes: Penalty-Sharp vs Penalty-Diffuse");

  const regimes = [
    {
      name: "Penalty-Sharp Regime",
      color: CLR.teal,
      winner: "MVAM Favored",
      conds: [
        "Wide cost range: cₘᵢₙ=1, cₘₐₓ=40",
        "Low noise: σ ≤ 0.5",
        "Strong cost differentiation",
        "Penalty signals clearly distinct",
      ],
      instances: "Instances: 40×60, 90×90, 110×110, 150×150, 200×180",
    },
    {
      name: "Penalty-Diffuse Regime",
      color: CLR.navy,
      winner: "MRAM Favored",
      conds: [
        "Narrow cost range: cₘᵢₙ=10, cₘₐₓ=16",
        "High noise: σ ≥ 2.0",
        "Column-cluster structure",
        "Penalty signals nearly equal",
      ],
      instances: "Instances: 60×60, 100×100, 120×120, 200×200",
    },
    {
      name: "Parity Zone",
      color: CLR.amber,
      winner: "Statistical Tie",
      conds: [
        "Moderate cost range & noise",
        "No strong cluster bias",
        "Both methods converge similarly",
        "No structural advantage exists",
      ],
      instances: "Instances: 3×4, 6×8, 150×150 (borderline)",
    },
  ];

  regimes.forEach((r, i) => {
    const x = 0.3 + i * 3.2;
    card(sl, x, 0.85, 3.0, 3.95, CLR.white);
    sl.addShape(pres.shapes.RECTANGLE, {
      x,
      y: 0.85,
      w: 3.0,
      h: 0.46,
      fill: { color: r.color },
    });
    sl.addText(r.name, {
      x: x + 0.08,
      y: 0.85,
      w: 2.84,
      h: 0.28,
      fontFace: FONT,
      fontSize: 12,
      bold: true,
      color: CLR.white,
      valign: "middle",
      margin: 0,
    });
    sl.addText(r.winner, {
      x: x + 0.08,
      y: 1.11,
      w: 2.84,
      h: 0.2,
      fontFace: FONT,
      fontSize: 10,
      color: CLR.white,
      italic: true,
      margin: 0,
    });
    sl.addText("Conditions:", {
      x: x + 0.12,
      y: 1.37,
      w: 2.76,
      h: 0.24,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: r.color,
      margin: 0,
    });
    r.conds.forEach((c, ci) => {
      sl.addShape(pres.shapes.OVAL, {
        x: x + 0.12,
        y: 1.66 + ci * 0.42,
        w: 0.1,
        h: 0.1,
        fill: { color: r.color },
      });
      addBody(sl, c, x + 0.28, 1.6 + ci * 0.42, 2.6, 0.38, { sz: 11 });
    });
    card(sl, x + 0.08, 3.88, 2.84, 0.72, CLR.light, false);
    addBody(sl, r.instances, x + 0.14, 3.92, 2.76, 0.64, {
      sz: 10,
      color: r.color,
      bold: true,
    });
  });

  card(sl, 0.3, 4.72, 9.4, 0.46, CLR.navy, false);
  sl.addText(
    "100% Predictive Accuracy on all 9 non-parity instances — Structure, not size, determines the winner.",
    {
      x: 0.5,
      y: 4.72,
      w: 9.0,
      h: 0.46,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 12);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 13 — SYNTHETIC DATASET DESIGN
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Synthetic Dataset Design & Experimental Protocol");

  // Left: why synthetic
  card(sl, 0.3, 0.85, 4.5, 1.72, CLR.white);
  sl.addText("Why Synthetic Datasets?", {
    x: 0.45,
    y: 0.92,
    w: 4.2,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.teal,
    margin: 0,
  });
  sl.addText(
    "No public IT2 fuzzy TP benchmark exists\nSmall instances only in Pratihar et al. [14]\nNeed to isolate structural regime effects\nFully reproducible via fixed seeds (NumPy PCG64)",
    {
      x: 0.45,
      y: 1.24,
      w: 4.2,
      h: 1.2,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.text,
      margin: 4,
    },
  );

  // Dataset table
  card(sl, 5.0, 0.85, 4.7, 1.72, CLR.white);
  sl.addText("Dataset Inventory", {
    x: 5.15,
    y: 0.92,
    w: 4.4,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  const scales = [
    ["Small", "3×4, 6×8"],
    ["Medium", "40×60, 60×60, 90×90"],
    ["Large", "90×90, 100×100, 110×110, 120×120"],
    ["Extended", "150×150, 200×180, 200×200"],
  ];
  scales.forEach(([sc, inst], i) => {
    card(sl, 5.1, 1.27 + i * 0.32, 4.4, 0.28, CLR.offwhite, false);
    sl.addText(sc, {
      x: 5.18,
      y: 1.29 + i * 0.32,
      w: 1.1,
      h: 0.24,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: CLR.teal,
      margin: 0,
    });
    addBody(sl, inst, 6.35, 1.29 + i * 0.32, 3.1, 0.24, { sz: 11 });
  });

  // Perturbation design
  const prows = [
    {
      lbl: "Supply/Demand Range",
      small: "(5,15)",
      med: "(50,120)",
      large: "(80,200)",
    },
    {
      lbl: "Cost Range (Sharp)",
      small: "(1,40)",
      med: "(1,40)",
      large: "(1,40)",
    },
    {
      lbl: "Cost Range (Diffuse)",
      small: "(10,16)",
      med: "(10,16)",
      large: "(10,16)",
    },
    { lbl: "Noise Level", small: "σ=0.5", med: "σ=2.0", large: "σ=5.0" },
  ];

  sl.addText("Generation Parameters:", {
    x: 0.3,
    y: 2.7,
    w: 4.5,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  const hdr = [
    ["Parameter", "#1E2761"],
    ["Small", "#0D7C8F"],
    ["Medium", "#2D6A4F"],
    ["Large", "#1A1A2E"],
  ];
  hdr.forEach(([h, c], i) => {
    sl.addShape(pres.shapes.RECTANGLE, {
      x: 0.3 + i * 2.35,
      y: 3.0,
      w: 2.25,
      h: 0.28,
      fill: { color: c },
    });
    sl.addText(h, {
      x: 0.3 + i * 2.35,
      y: 3.0,
      w: 2.25,
      h: 0.28,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    });
  });
  prows.forEach((r, ri) => {
    const bg = ri % 2 === 0 ? CLR.offwhite : CLR.white;
    [
      [r.lbl, 0],
      [r.small, 1],
      [r.med, 2],
      [r.large, 3],
    ].forEach(([v, ci]) => {
      sl.addShape(pres.shapes.RECTANGLE, {
        x: 0.3 + ci * 2.35,
        y: 3.3 + ri * 0.32,
        w: 2.25,
        h: 0.3,
        fill: { color: bg },
      });
      sl.addText(v, {
        x: 0.3 + ci * 2.35,
        y: 3.3 + ri * 0.32,
        w: 2.25,
        h: 0.3,
        fontFace: FONT,
        fontSize: 11,
        color: CLR.text,
        align: "center",
        valign: "middle",
        margin: 0,
      });
    });
  });

  // Right bottom: experimental stats
  card(sl, 5.0, 2.68, 4.7, 2.1, CLR.white);
  sl.addText("Benchmarking Protocol", {
    x: 5.15,
    y: 2.75,
    w: 4.4,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  const stats = [
    "30 repetitions per (instance, method) pair",
    "95% CI using Student's t-distribution (ν=29)",
    "CV < 10% required for valid measurement",
    "timer: Python time.perf_counter()",
    "JSON datasets — seed-controlled, fully reproducible",
  ];
  stats.forEach((s, i) => {
    sl.addShape(pres.shapes.OVAL, {
      x: 5.18,
      y: 3.13 + i * 0.38,
      w: 0.11,
      h: 0.11,
      fill: { color: CLR.teal },
    });
    addBody(sl, s, 5.36, 3.08 + i * 0.38, 4.2, 0.32, { sz: 12 });
  });

  addPageNum(sl, 13);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 14 — RESULTS: SMALL & MEDIUM SCALE
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Results: Small & Medium Scale (3×4 and 40×60 / 60×60)");

  // 3×4 card
  card(sl, 0.3, 0.85, 4.55, 3.45, CLR.white);
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0.3,
    y: 0.85,
    w: 4.55,
    h: 0.36,
    fill: { color: CLR.teal },
  });
  sl.addText("3×4 Instance (Parity Zone | Pratihar et al. [14])", {
    x: 0.42,
    y: 0.85,
    w: 4.35,
    h: 0.36,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.white,
    valign: "middle",
    margin: 0,
  });
  const r3x4 = [
    ["", "MVAM", "MRAM"],
    ["IBFS Cost", "69.1461", "67.0683 ✓"],
    ["MODI Cost", "67.0683", "67.0683"],
    ["MODI Iters", "3", "1 ✓"],
    ["Regime", "Parity", "-"],
  ];
  r3x4.forEach(([a, b, c], ri) => {
    const bg = ri === 0 ? CLR.navy : ri % 2 === 0 ? CLR.offwhite : CLR.white;
    const tc = ri === 0 ? CLR.white : CLR.text;
    [
      [a, 0],
      [b, 1],
      [c, 2],
    ].forEach(([v, ci]) => {
      sl.addShape(pres.shapes.RECTANGLE, {
        x: 0.38 + ci * 1.45,
        y: 1.26 + ri * 0.37,
        w: 1.4,
        h: 0.35,
        fill: { color: bg },
      });
      sl.addText(v, {
        x: 0.38 + ci * 1.45,
        y: 1.26 + ri * 0.37,
        w: 1.4,
        h: 0.35,
        fontFace: FONT,
        fontSize: 11,
        bold: ri === 0,
        color: tc,
        align: "center",
        valign: "middle",
        margin: 0,
      });
    });
  });
  addBody(
    sl,
    "Both converge to identical optimal cost.\nRAM uses 1 MODI iteration vs VAM's 3.\nSource: Table 6.2",
    0.42,
    3.2,
    4.25,
    0.72,
    { sz: 12, color: CLR.muted },
  );

  // 40×60 card (penalty-sharp)
  card(sl, 5.05, 0.85, 4.55, 1.62, CLR.white);
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 5.05,
    y: 0.85,
    w: 4.55,
    h: 0.36,
    fill: { color: CLR.teal },
  });
  sl.addText("40×60 — Penalty-Sharp (VAM wins)", {
    x: 5.17,
    y: 0.85,
    w: 4.35,
    h: 0.36,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.white,
    valign: "middle",
    margin: 0,
  });
  const r40 = [
    ["IBFS Cost", "2,776,524 ✓", "3,487,971"],
    ["MODI Iters", "77 ✓", "161"],
    ["MODI Cost", "1,452,634", "1,452,634"],
    ["Pipeline", "1.75× faster ✓", "—"],
  ];
  r40.forEach(([a, b, c], ri) => {
    const bg = ri % 2 === 0 ? CLR.offwhite : CLR.white;
    [
      [a, 0],
      [b, 1],
      [c, 2],
    ].forEach(([v, ci]) => {
      sl.addShape(pres.shapes.RECTANGLE, {
        x: 5.1 + ci * 1.45,
        y: 1.26 + ri * 0.3,
        w: 1.4,
        h: 0.28,
        fill: { color: bg },
      });
      sl.addText(v, {
        x: 5.1 + ci * 1.45,
        y: 1.26 + ri * 0.3,
        w: 1.4,
        h: 0.28,
        fontFace: FONT,
        fontSize: 10,
        color: CLR.text,
        align: "center",
        valign: "middle",
        margin: 0,
      });
    });
  });

  // 60×60 card (penalty-diffuse)
  card(sl, 5.05, 2.56, 4.55, 1.62, CLR.white);
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 5.05,
    y: 2.56,
    w: 4.55,
    h: 0.36,
    fill: { color: CLR.navy },
  });
  sl.addText("60×60 — Penalty-Diffuse (RAM wins)", {
    x: 5.17,
    y: 2.56,
    w: 4.35,
    h: 0.36,
    fontFace: FONT,
    fontSize: 12,
    bold: true,
    color: CLR.white,
    valign: "middle",
    margin: 0,
  });
  const r60 = [
    ["IBFS Cost", "40,943 ✗", "29,547 ✓"],
    ["MODI Iters", "102", "40 ✓"],
    ["MODI Cost", "28,983", "28,983"],
    ["Pipeline", "—", "1.48× faster ✓"],
  ];
  r60.forEach(([a, b, c], ri) => {
    const bg = ri % 2 === 0 ? CLR.offwhite : CLR.white;
    [
      [a, 0],
      [b, 1],
      [c, 2],
    ].forEach(([v, ci]) => {
      sl.addShape(pres.shapes.RECTANGLE, {
        x: 5.1 + ci * 1.45,
        y: 2.97 + ri * 0.3,
        w: 1.4,
        h: 0.28,
        fill: { color: bg },
      });
      sl.addText(v, {
        x: 5.1 + ci * 1.45,
        y: 2.97 + ri * 0.3,
        w: 1.4,
        h: 0.28,
        fontFace: FONT,
        fontSize: 10,
        color: CLR.text,
        align: "center",
        valign: "middle",
        margin: 0,
      });
    });
  });

  card(sl, 0.3, 4.38, 9.4, 0.44, CLR.navy, false);
  sl.addText(
    "40×60 vs 60×60: Same scale, opposite winners — proof that STRUCTURE, not SIZE, determines outcome.",
    {
      x: 0.5,
      y: 4.38,
      w: 9.0,
      h: 0.44,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 14);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 15 — RESULTS: LARGE & EXTENDED SCALE
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Results: Large & Extended Scale (90×90 to 200×200)");

  // Table header
  const headers = [
    "Instance",
    "Regime",
    "IBFS Winner",
    "MODI Iters (VAM/RAM)",
    "Pipeline Winner",
    "Speed Ratio",
  ];
  headers.forEach((h, i) => {
    const ws = [1.2, 1.4, 1.2, 1.8, 1.4, 1.2];
    const xs = [0.3, 1.52, 2.94, 4.16, 5.98, 7.4];
    sl.addShape(pres.shapes.RECTANGLE, {
      x: xs[i],
      y: 0.85,
      w: ws[i],
      h: 0.34,
      fill: { color: CLR.navy },
    });
    sl.addText(h, {
      x: xs[i],
      y: 0.85,
      w: ws[i],
      h: 0.34,
      fontFace: FONT,
      fontSize: 10,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    });
  });

  const rows = [
    ["90×90", "Sharp", "VAM", "127 / 171", "VAM+MODI", "1.24×"],
    ["100×100", "Diffuse", "RAM", "172 / 65", "RAM+MODI", "1.51×"],
    ["110×110", "Sharp", "VAM", "197 / 277", "VAM+MODI", "1.30×"],
    ["120×120", "Diffuse", "RAM", "—  / —  ", "RAM+MODI", "1.42×"],
    ["150×150", "Parity", "Tie", "77  / 137", "VAM+MODI*", "1.33×"],
    ["200×180", "Sharp", "VAM", "118 / 148", "VAM+MODI", "1.16×"],
    ["200×200", "Diffuse", "RAM", "449 / 207", "RAM+MODI", "1.50×"],
  ];

  const colWs = [1.2, 1.4, 1.2, 1.8, 1.4, 1.2];
  const colXs = [0.3, 1.52, 2.94, 4.16, 5.98, 7.4];

  rows.forEach((r, ri) => {
    const bg = ri % 2 === 0 ? CLR.offwhite : CLR.white;
    r.forEach((v, ci) => {
      const hilite =
        ci === 2 && v === "VAM"
          ? CLR.teal
          : ci === 2 && v === "RAM"
            ? CLR.navy
            : ci === 2 && v === "Tie"
              ? CLR.amber
              : null;
      const hiliteP =
        ci === 4 && v.includes("VAM")
          ? CLR.teal
          : ci === 4 && v.includes("RAM")
            ? CLR.navy
            : null;
      const useBg = hilite || hiliteP || bg;
      const useTc = hilite || hiliteP ? CLR.white : CLR.text;
      sl.addShape(pres.shapes.RECTANGLE, {
        x: colXs[ci],
        y: 1.22 + ri * 0.38,
        w: colWs[ci],
        h: 0.36,
        fill: { color: useBg },
      });
      sl.addText(v, {
        x: colXs[ci],
        y: 1.22 + ri * 0.38,
        w: colWs[ci],
        h: 0.36,
        fontFace: FONT,
        fontSize: 10,
        bold: !!(hilite || hiliteP),
        color: useTc,
        align: "center",
        valign: "middle",
        margin: 0,
      });
    });
  });

  card(sl, 0.3, 4.0, 9.4, 0.44, CLR.navy, false);
  sl.addText(
    "Within large scale: 90×90 (Sharp→VAM), 100×100 (Diffuse→RAM), 110×110 (Sharp→VAM) — alternating despite increasing size.",
    {
      x: 0.5,
      y: 4.0,
      w: 9.0,
      h: 0.44,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  sl.addText(
    "Source: Tables 6.6, 6.8, 6.10 | *VAM faster despite parity due to simpler internals",
    {
      x: 0.3,
      y: 4.52,
      w: 9.4,
      h: 0.26,
      fontFace: FONT,
      fontSize: 10,
      color: CLR.muted,
      align: "center",
      margin: 0,
    },
  );

  addPageNum(sl, 15);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 16 — STATISTICAL BENCHMARKING SUMMARY
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Statistical Benchmarking Summary — All 11 Instances");

  // 6 findings
  const findings = [
    {
      num: "F1",
      hdr: "Structural Determinism of IBFS",
      txt: "VAM wins all 5 sharp instances\nRAM wins all 4 diffuse instances\n100% structural prediction rate",
    },
    {
      num: "F2",
      hdr: "MODI Equalizes Final Cost",
      txt: "7 of 11 instances: identical post-MODI cost\nRemaining 4: difference < 0.20 units\n(<0.003% relative difference)",
    },
    {
      num: "F3",
      hdr: "Pipeline Speed Follows MODI Iters",
      txt: "Dominant cost = MODI refinement\nVAM: 1.05–1.18× faster at IBFS only\nMODI overhead reverses advantage",
    },
    {
      num: "F4",
      hdr: "Scale Amplifies, Not Determines",
      txt: "200×200: largest gaps observed\nBut direction determined by structure\n3 consecutive large sizes → alternating winner",
    },
    {
      num: "F5",
      hdr: "Statistical Reliability Increases",
      txt: "3×4: CV > 50% (noise dominated)\n6×8: CV < 10% (reproducible)\n60×60+: CV < 4% (highly reliable)",
    },
    {
      num: "F6",
      hdr: "No Universal Winner",
      txt: "VAM+MODI faster: 6 instances\nRAM+MODI faster: 4 instances\nN/S tie: 1 instance (3×4)",
    },
  ];

  findings.forEach((f, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.3 + col * 4.85;
    const y = 0.88 + row * 1.42;
    card(sl, x, y, 4.55, 1.28, CLR.white);
    sl.addText(f.num, {
      x: x + 0.1,
      y: y + 0.1,
      w: 0.45,
      h: 0.45,
      fontFace: FONT,
      fontSize: 16,
      bold: true,
      color: CLR.teal,
      align: "center",
      valign: "middle",
      margin: 0,
    });
    sl.addText(f.hdr, {
      x: x + 0.65,
      y: y + 0.1,
      w: 3.75,
      h: 0.36,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.navy,
      valign: "middle",
      margin: 0,
    });
    f.txt.split("\n").forEach((ln, li) =>
      addBody(sl, ln, x + 0.65, y + 0.52 + li * 0.27, 3.75, 0.26, {
        sz: 11,
        color: CLR.muted,
      }),
    );
  });

  placeholder(
    sl,
    3.0,
    4.42,
    4.0,
    0.38,
    "Figure 6.1: Complete Timing Benchmark Summary (Insert from Thesis)",
  );

  addPageNum(sl, 16);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 17 — PROBLEM STRUCTURE vs PROBLEM SIZE
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Problem Structure vs Problem Size as Performance Determinant");

  // Central message
  card(sl, 0.3, 0.85, 9.4, 0.62, CLR.navy, false);
  sl.addText(
    "Central Thesis Hypothesis: Transportation problem structure (penalty topology) is a STRONGER predictor than problem size.",
    {
      x: 0.5,
      y: 0.85,
      w: 9.0,
      h: 0.62,
      fontFace: FONT,
      fontSize: 14,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  // 3 observations
  const obs = [
    {
      num: "Observation 1",
      hdr: "Within-Group Size Alternation",
      txt: "90×90 → VAM wins (Sharp)\n100×100 → RAM wins (Diffuse)\n110×110 → VAM wins (Sharp)\nSame scale class, 3 different structural regimes → 3 different winners",
    },
    {
      num: "Observation 2",
      hdr: "Cross-Group Structure Consistency",
      txt: "All Sharp instances (any size) → VAM wins\nAll Diffuse instances (any size) → RAM wins\nStructure predicts direction at EVERY scale",
    },
    {
      num: "Observation 3",
      hdr: "Scale Modulates Magnitude",
      txt: "200×200 penalty-diffuse: VAM gap = 15.1%\n(larger than 60×60 gap of 28.2%)\nPenalty diffuseness compounds with size\nbut DIRECTION is always structure-determined",
    },
  ];

  obs.forEach((o, i) => {
    card(sl, 0.3 + i * 3.2, 1.6, 3.0, 2.95, CLR.white);
    sl.addShape(pres.shapes.RECTANGLE, {
      x: 0.3 + i * 3.2,
      y: 1.6,
      w: 3.0,
      h: 0.36,
      fill: { color: CLR.teal },
    });
    sl.addText(o.num, {
      x: 0.38 + i * 3.2,
      y: 1.6,
      w: 2.84,
      h: 0.36,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: CLR.white,
      valign: "middle",
      margin: 0,
    });
    sl.addText(o.hdr, {
      x: 0.38 + i * 3.2,
      y: 2.02,
      w: 2.84,
      h: 0.3,
      fontFace: FONT,
      fontSize: 12,
      bold: true,
      color: CLR.navy,
      margin: 0,
    });
    o.txt.split("\n").forEach((ln, li) =>
      addBody(sl, ln, 0.38 + i * 3.2, 2.38 + li * 0.36, 2.84, 0.32, {
        sz: 11,
      }),
    );
  });

  card(sl, 0.3, 4.64, 9.4, 0.52, CLR.teal, false);
  sl.addText(
    "Conclusion: Structural classification (penalty-sharp / penalty-diffuse) achieves 100% predictive accuracy on 9 non-parity instances.",
    {
      x: 0.5,
      y: 4.64,
      w: 9.0,
      h: 0.52,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 17);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 18 — COST SENSITIVITY ANALYSIS
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Cost Magnitude Sensitivity Analysis");

  // Design card
  card(sl, 0.3, 0.85, 4.5, 1.62, CLR.white);
  sl.addText("Perturbation Design:", {
    x: 0.45,
    y: 0.92,
    w: 4.2,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.teal,
    margin: 0,
  });
  sl.addText(
    "All UMF & LMF vertices scaled by M ∈ {0.80, 0.90, 1.10, 1.20}\nFOU gap ratios preserved (uncertainty structure unchanged)\nKM type-reduction re-run on each perturbed dataset\nSupply & demand unchanged",
    {
      x: 0.45,
      y: 1.24,
      w: 4.2,
      h: 1.15,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.text,
      margin: 4,
    },
  );

  // Perturbation table
  card(sl, 5.0, 0.85, 4.7, 1.62, CLR.white);
  sl.addText("Perturbation Levels (Table 7.1):", {
    x: 5.15,
    y: 0.92,
    w: 4.4,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  const levels = [
    ["C1", "×0.80", "−20% (cost reduction)"],
    ["C2", "×0.90", "−10%"],
    ["Baseline", "×1.00", "Baseline (Chapter 6)"],
    ["C3", "×1.10", "+10%"],
    ["C4", "×1.20", "+20% (cost increase)"],
  ];
  levels.forEach(([l, m, d], i) => {
    const bg = l === "Baseline" ? CLR.teal : CLR.offwhite;
    const tc = l === "Baseline" ? CLR.white : CLR.text;
    card(sl, 5.08, 1.28 + i * 0.24, 4.5, 0.22, bg, false);
    sl.addText(`${l}  ${m}  —  ${d}`, {
      x: 5.15,
      y: 1.3 + i * 0.24,
      w: 4.38,
      h: 0.2,
      fontFace: FONT,
      fontSize: 10,
      color: tc,
      margin: 0,
      align: "center",
    });
  });

  // Results
  const scaleRes = [
    [
      "3×4 (Parity)",
      "RAM IBFS superior in all 5 scenarios",
      "Both converge to same MODI cost",
      "VAM improvement % = 3.00% (exact constant)",
    ],
    [
      "40×60 (Sharp)",
      "VAM IBFS superior in all 5 scenarios",
      "VAM+MODI 1.69–1.86× faster",
      "Final costs within 0.003%",
    ],
    [
      "100×100 (Diffuse)",
      "RAM IBFS superior in all 5 scenarios",
      "RAM+MODI 1.52–1.71× faster",
      "RAM improvement ≈ 1.01–1.02%",
    ],
  ];
  scaleRes.forEach(([sc, ...pts], i) => {
    card(sl, 0.3 + i * 3.2, 2.58, 3.0, 1.75, CLR.white);
    sl.addShape(pres.shapes.RECTANGLE, {
      x: 0.3 + i * 3.2,
      y: 2.58,
      w: 3.0,
      h: 0.32,
      fill: { color: i === 0 ? CLR.amber : i === 1 ? CLR.teal : CLR.navy },
    });
    sl.addText(sc, {
      x: 0.38 + i * 3.2,
      y: 2.58,
      w: 2.84,
      h: 0.32,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: CLR.white,
      valign: "middle",
      margin: 0,
    });
    pts.forEach((p, pi) =>
      addBody(sl, `→ ${p}`, 0.38 + i * 3.2, 2.96 + pi * 0.36, 2.84, 0.32, {
        sz: 11,
      }),
    );
  });

  // Key finding
  card(sl, 0.3, 4.43, 9.4, 0.42, CLR.teal, false);
  sl.addText(
    "Key Finding: IBFS ranking, pipeline speed, and final cost equality — ALL stable across ±20% cost perturbation.",
    {
      x: 0.5,
      y: 4.43,
      w: 9.0,
      h: 0.42,
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 18);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 19 — FOU SENSITIVITY ANALYSIS
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Footprint of Uncertainty (FOU) Sensitivity Analysis");

  // FOU definition
  card(sl, 0.3, 0.85, 4.5, 1.42, CLR.white);
  sl.addText("FOU Perturbation Design:", {
    x: 0.45,
    y: 0.92,
    w: 4.2,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  sl.addText(
    "Gap quantities: G1 = b₁−a₁   G2 = b₂−a₂\nG3 = a₃−b₃   G4 = a₄−b₄\nNew LMF: b₁ᴺ = a₁ + G1×M  (and similarly for b₂,b₃,b₄)\nM<1 → narrow FOU   M>1 → wide FOU",
    {
      x: 0.45,
      y: 1.24,
      w: 4.2,
      h: 0.95,
      fontFace: FONT,
      fontSize: 12,
      italic: true,
      color: CLR.text,
      margin: 4,
    },
  );

  // Perturbation levels
  card(sl, 5.0, 0.85, 4.7, 1.42, CLR.white);
  sl.addText("FOU Perturbation Levels (Table 7.8):", {
    x: 5.15,
    y: 0.92,
    w: 4.4,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.navy,
    margin: 0,
  });
  const flevels = [
    ["F1", "×0.80", "FOU narrows by 20%"],
    ["F2", "×0.90", "FOU narrows by 10%"],
    ["Baseline", "×1.00", "Baseline"],
    ["F3", "×1.10", "FOU widens by 10%"],
    ["F4", "×1.20", "FOU widens by 20%"],
  ];
  flevels.forEach(([l, m, d], i) => {
    const bg = l === "Baseline" ? CLR.navy : CLR.offwhite;
    const tc = l === "Baseline" ? CLR.white : CLR.text;
    card(sl, 5.08, 1.28 + i * 0.2, 4.5, 0.18, bg, false);
    sl.addText(`${l}  ${m}  —  ${d}`, {
      x: 5.15,
      y: 1.3 + i * 0.2,
      w: 4.38,
      h: 0.17,
      fontFace: FONT,
      fontSize: 10,
      color: tc,
      margin: 0,
      align: "center",
    });
  });

  // Key findings per scale
  const fouRes = [
    [
      "3×4",
      "RAM IBFS superior in all FOU scenarios",
      "VAM improvement ≈ 3.00% (stable)",
      "Wider FOU → slight cost decrease (KM centroid effect)",
    ],
    [
      "40×60",
      "VAM IBFS advantage maintained",
      "VAM+MODI 1.69–1.87× faster",
      "MODI costs within 0.002%",
    ],
    [
      "100×100",
      "RAM IBFS advantage maintained",
      "RAM+MODI 1.60–1.65× faster",
      "Monotone cost decrease as FOU widens",
    ],
  ];
  fouRes.forEach(([sc, ...pts], i) => {
    card(sl, 0.3 + i * 3.2, 2.38, 3.0, 1.9, CLR.white);
    sl.addShape(pres.shapes.RECTANGLE, {
      x: 0.3 + i * 3.2,
      y: 2.38,
      w: 3.0,
      h: 0.32,
      fill: { color: i === 0 ? CLR.amber : i === 1 ? CLR.teal : CLR.navy },
    });
    sl.addText(sc, {
      x: 0.38 + i * 3.2,
      y: 2.38,
      w: 2.84,
      h: 0.32,
      fontFace: FONT,
      fontSize: 11,
      bold: true,
      color: CLR.white,
      valign: "middle",
      margin: 0,
    });
    pts.forEach((p, pi) =>
      addBody(sl, `→ ${p}`, 0.38 + i * 3.2, 2.76 + pi * 0.36, 2.84, 0.32, {
        sz: 11,
      }),
    );
  });

  // FOU insight
  card(sl, 0.3, 4.38, 9.4, 0.44, CLR.navy, false);
  sl.addText(
    "FOU Effect: Wider FOU → slightly lower defuzzified costs (KM centroid shifts). Does NOT change algorithm rankings.",
    {
      x: 0.5,
      y: 4.38,
      w: 9.0,
      h: 0.44,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.white,
      align: "center",
      valign: "middle",
      bold: true,
      margin: 0,
    },
  );

  placeholder(
    sl,
    3.5,
    4.9,
    3.0,
    0.38,
    "Figure 7.11: Complete Sensitivity Analysis Overview (Insert from Thesis)",
  );

  addPageNum(sl, 19);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 20 — JOINT ROBUSTNESS
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Joint Robustness Assessment — 24 Perturbation Experiments");

  // Central metric
  card(sl, 2.5, 0.85, 5.0, 1.02, CLR.teal, false);
  sl.addText("0 Ranking Reversals", {
    x: 2.6,
    y: 0.85,
    w: 4.8,
    h: 0.55,
    fontFace: FONT,
    fontSize: 28,
    bold: true,
    color: CLR.white,
    align: "center",
    valign: "middle",
    margin: 0,
  });
  sl.addText(
    "across 24 independent perturbation experiments (3 scales × 2 types × 4 levels)",
    {
      x: 2.6,
      y: 1.42,
      w: 4.8,
      h: 0.32,
      fontFace: FONT,
      fontSize: 11,
      color: CLR.white,
      align: "center",
      margin: 0,
    },
  );

  // Robustness map
  const bgs = [
    CLR.teal,
    CLR.teal,
    CLR.teal,
    CLR.teal,
    CLR.navy,
    CLR.navy,
    CLR.navy,
    CLR.navy,
    CLR.amber,
    CLR.amber,
    CLR.amber,
    CLR.amber,
  ];
  const labels = [
    ["3×4", "Cost -20", "RAM"],
    ["3×4", "Cost -10", "RAM"],
    ["3×4", "Cost +10", "RAM"],
    ["3×4", "Cost +20", "RAM"],
    ["40×60", "Cost -20", "VAM"],
    ["40×60", "Cost -10", "VAM"],
    ["40×60", "Cost +10", "VAM"],
    ["40×60", "Cost +20", "VAM"],
    ["100×100", "FOU -20", "RAM"],
    ["100×100", "FOU -10", "RAM"],
    ["100×100", "FOU +10", "RAM"],
    ["100×100", "FOU +20", "RAM"],
  ];

  sl.addText(
    "Robustness Map — IBFS Winner by Scenario (all identical = stable):",
    {
      x: 0.3,
      y: 2.0,
      w: 9.4,
      h: 0.28,
      fontFace: FONT,
      fontSize: 12,
      bold: true,
      color: CLR.navy,
      margin: 0,
    },
  );
  labels.forEach(([inst, scen, winner], i) => {
    const col = i % 4;
    const row = Math.floor(i / 4);
    const x = 0.3 + col * 2.38;
    const y = 2.32 + row * 0.62;
    card(sl, x, y, 2.28, 0.56, bgs[i], false);
    sl.addText(`${inst}\n${scen}\nWinner: ${winner}`, {
      x: x + 0.05,
      y,
      w: 2.18,
      h: 0.56,
      fontFace: FONT,
      fontSize: 9,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    });
  });

  // Findings S
  const sfinds = [
    "S1: Perfect ranking stability under cost perturbation",
    "S2: Perfect ranking stability under FOU perturbation",
    "S3: MODI final cost equal across all scenarios",
    "S4: Improvement rate invariance (LP basis invariance theorem)",
    "S5: FOU perturbation produces monotone cost shifts only",
    "S6: Structural classification is perturbation-invariant",
  ];
  sfinds.forEach((s, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    addBody(sl, s, 0.3 + col * 4.85, 4.18 + row * 0.3, 4.55, 0.28, {
      sz: 12,
      color: CLR.muted,
    });
  });

  addPageNum(sl, 20);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SLIDE 21 — CONTRIBUTIONS, LIMITATIONS & FUTURE WORK
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.offwhite };
  addTitle(sl, "Contributions, Limitations & Future Research Directions");

  // 4 contributions
  const contribs = [
    [
      "C1",
      "Complete IT2-TrFTP Pipeline",
      "First end-to-end: 3D fuzzification + KM + normalization + dual IBFS + MODI",
    ],
    [
      "C2",
      "Structural Classification",
      "Penalty-sharp / Penalty-diffuse framework — 100% predictive accuracy on non-parity instances",
    ],
    [
      "C3",
      "Balance-Enforcement Layer",
      "Novel normalization restoring Σsᵢ = Σdⱼ after asymmetric KM defuzzification",
    ],
    [
      "C4",
      "2D Sensitivity Analysis",
      "Cost + FOU robustness — new result: FOU does not cause ranking reversals",
    ],
  ];
  contribs.forEach(([num, hdr, txt], i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.3 + col * 4.85;
    const y = 0.85 + row * 1.0;
    card(sl, x, y, 4.55, 0.88, CLR.white);
    sl.addShape(pres.shapes.RECTANGLE, {
      x,
      y,
      w: 0.5,
      h: 0.88,
      fill: { color: CLR.teal },
    });
    sl.addText(num, {
      x,
      y,
      w: 0.5,
      h: 0.88,
      fontFace: FONT,
      fontSize: 12,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    });
    sl.addText(hdr, {
      x: x + 0.6,
      y: y + 0.08,
      w: 3.82,
      h: 0.28,
      fontFace: FONT,
      fontSize: 12,
      bold: true,
      color: CLR.navy,
      margin: 0,
    });
    addBody(sl, txt, x + 0.6, y + 0.38, 3.82, 0.42, {
      sz: 11,
      color: CLR.muted,
    });
  });

  // Limitations & Future
  card(sl, 0.3, 2.92, 4.55, 1.28, CLR.white);
  sl.addText("Limitations", {
    x: 0.45,
    y: 2.97,
    w: 4.2,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.red,
    margin: 0,
  });
  const lims = [
    "Synthetic datasets only — no real-world validation",
    "Only MVAM vs MRAM compared (other heuristics excluded)",
    "Fuzzification parameters (δ, α, β, γ) not varied systematically",
  ];
  lims.forEach((l, i) =>
    addBody(sl, `• ${l}`, 0.45, 3.3 + i * 0.3, 4.2, 0.28, { sz: 12 }),
  );

  card(sl, 5.15, 2.92, 4.55, 1.28, CLR.white);
  sl.addText("Future Research Directions", {
    x: 5.3,
    y: 2.97,
    w: 4.2,
    h: 0.28,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.green,
    margin: 0,
  });
  const fut = [
    "Pre-computation structural diagnostic (CV-based)",
    "Replace KM with Nie–Tan [44] approximation at large scale",
    "Validate on real logistics datasets",
    "Extend to multi-objective IT2-TrFTP",
  ];
  fut.forEach((f, i) =>
    addBody(sl, `→ ${f}`, 5.3, 3.3 + i * 0.3, 4.2, 0.28, { sz: 12 }),
  );

  card(sl, 0.3, 4.3, 9.4, 0.42, CLR.navy, false);
  sl.addText(
    "Algorithm performance is structurally determined — understanding cost topology is the key to principled deployment decisions.",
    {
      x: 0.5,
      y: 4.3,
      w: 9.0,
      h: 0.42,
      fontFace: FONT,
      fontSize: 12,
      bold: true,
      color: CLR.white,
      align: "center",
      valign: "middle",
      margin: 0,
    },
  );

  addPageNum(sl, 20);
}

// ═══════════════════════════════════════════════════════════════════════════════
// THANK YOU
// ═══════════════════════════════════════════════════════════════════════════════
{
  let sl = pres.addSlide();
  sl.background = { color: CLR.navy };
  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0,
    y: 0,
    w: 10,
    h: 1.0,
    fill: { color: CLR.teal },
  });
  sl.addText("BANGLADESH UNIVERSITY OF ENGINEERING AND TECHNOLOGY", {
    x: 0.3,
    y: 0,
    w: 9.4,
    h: 1.0,
    fontFace: FONT,
    fontSize: 13,
    bold: true,
    color: CLR.white,
    align: "center",
    valign: "middle",
  });

  sl.addText("Thank You", {
    x: 1,
    y: 1.55,
    w: 8,
    h: 1.0,
    fontFace: FONT,
    fontSize: 42,
    bold: true,
    color: CLR.white,
    align: "center",
  });
  sl.addShape(pres.shapes.LINE, {
    x: 1.5,
    y: 2.65,
    w: 7,
    h: 0,
    line: { color: CLR.teal, width: 2 },
  });

  sl.addText(
    "Comparative Performance and Robustness Analysis of\nModified Vogel's and Modified Russell's Approximation Methods\nunder Interval Type-2 Trapezoidal Fuzzy Uncertainty",
    {
      x: 0.5,
      y: 2.82,
      w: 9,
      h: 1.1,
      fontFace: FONT,
      fontSize: 15,
      color: CLR.light,
      align: "center",
    },
  );

  sl.addText(
    "Md Sadiqul Haque  (2008082)     |     Md Tanjil Haque  (2008094)",
    {
      x: 0.5,
      y: 4.05,
      w: 9,
      h: 0.35,
      fontFace: FONT,
      fontSize: 13,
      color: CLR.light,
      align: "center",
    },
  );
  sl.addText(
    "Supervisor: Dr. Kais Bin Zaman, Professor, IPE, BUET  |  June 2026",
    {
      x: 0.5,
      y: 4.42,
      w: 9,
      h: 0.32,
      fontFace: FONT,
      fontSize: 12,
      color: CLR.muted,
      align: "center",
    },
  );

  sl.addShape(pres.shapes.RECTANGLE, {
    x: 0,
    y: 5.28,
    w: 10,
    h: 0.34,
    fill: { color: "0A1A2E" },
  });
  sl.addText("Questions & Discussion Welcome", {
    x: 0.3,
    y: 5.28,
    w: 9.4,
    h: 0.34,
    fontFace: FONT,
    fontSize: 11,
    color: CLR.muted,
    align: "center",
    valign: "middle",
  });
}

pres
  .writeFile({ fileName: "IT2_TrFTP_Thesis_Presentation.pptx" })
  .then(() => console.log("PPTX created successfully"))
  .catch((e) => console.error("Error:", e));
