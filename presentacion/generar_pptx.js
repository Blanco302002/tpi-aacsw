/*
 * generar_pptx.js — builds the pitch deck (English) from presentacion/datos.json.
 *
 *   cd presentacion
 *   npm install          (once: installs pptxgenjs)
 *   node generar_pptx.js
 *
 * Output: presentacion/what-goes-dark.pptx
 * Charts are native PowerPoint charts (editable). Memes come from presentacion/memes/.
 * Slides marked "TO CHANGE" are drafts the presenter wants to redo.
 */
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "datos.json"), "utf8"));
const SALIDA = path.join(__dirname, "what-goes-dark.pptx");

// ---------- Palette (validated: orange/blue pass CVD checks) ----------
const COL = {
  ink: "0B0B0B", ink2: "52514E", muted: "8A8984", grid: "E6E5E1", line: "D9D8D3",
  bg: "FFFFFF", soft: "F4F3EF", accent: "EB6834", accentSoft: "FBE3D8", blue: "2A78D6",
  world: "5F5E5A", gray: "B9B8B2", ok: "1BAF7A", bad: "E34948", off: "2B2B2A",
};
const THEME = {
  name: "What goes dark",
  headFontFace: "Arial", bodyFontFace: "Arial",
  colors: {
    dk1: COL.ink, lt1: COL.bg, dk2: COL.ink2, lt2: COL.soft,
    accent1: COL.accent, accent2: COL.blue, accent3: COL.muted, accent4: COL.ok,
    accent5: COL.bad, accent6: COL.gray, hlink: COL.blue, folHlink: "6250D6",
  },
};
const W = 13.333, H = 7.5, MX = 0.6;
const fmt = (x, d = 0) => Number(x).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "What goes dark when a single company goes down?";
pres.subject = "DATA4QUALITY 2026 — software quality told with data";

// ---------- Layouts ----------
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: COL.bg },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.35, w: W - 2 * MX, h: 0.95,
      fontSize: 34, bold: true, color: COL.ink, align: "left", valign: "middle", margin: 0 }, text: "Slide title" } },
  ],
  slideNumber: { x: W - 1.0, y: H - 0.45, w: 0.6, h: 0.3, fontSize: 10, color: COL.muted, align: "right" },
});
pres.defineSlideMaster({
  title: "CENTER",
  background: { color: COL.bg },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: MX, y: 0.45, w: W - 2 * MX, h: 1.0,
      fontSize: 40, bold: true, color: COL.ink, align: "center", valign: "middle", margin: 0 }, text: "Slide title" } },
  ],
  slideNumber: { x: W - 1.0, y: H - 0.45, w: 0.6, h: 0.3, fontSize: 10, color: COL.muted, align: "right" },
});
pres.defineSlideMaster({ title: "BLANK", background: { color: COL.bg },
  slideNumber: { x: W - 1.0, y: H - 0.45, w: 0.6, h: 0.3, fontSize: 10, color: COL.muted, align: "right" } });

// ---------- Helpers ----------
function txt(slide, text, o) { slide.addText(text, Object.assign({ isTextBox: true, margin: 0, fontFace: "Arial", color: COL.ink }, o)); }
function nota(slide, text, y = H - 0.62) { txt(slide, text, { x: MX, y, w: W - 2 * MX - 0.9, h: 0.4, fontSize: 10, color: COL.muted, valign: "top" }); }
function toChange(slide) {
  slide.addText("TO CHANGE", { isTextBox: true, x: W - 2.2, y: 0.06, w: 1.6, h: 0.3, fontSize: 12, bold: true,
    color: "FFFFFF", align: "center", valign: "middle", margin: 0, fontFace: "Arial",
    shape: pres.ShapeType.roundRect, rectRadius: 0.08, fill: { color: COL.bad }, objectName: "TO CHANGE tag" });
}
const MEMES = {
  cloudflare_this_is_fine: [942, 666], internet_tower_aws_cloudflare: [810, 962], homer_error_500: [937, 582],
  engineers_fixing: [737, 661], chatgpt_caveman: [568, 697], chatgpt_inside_out: [610, 553],
  x_servers: [567, 392], days_since_cloudflare: [605, 606], cloudflare_global_outage: [927, 697],
};
function meme(slide, name, x, y, w, h) {
  const [iw, ih] = MEMES[name]; const k = Math.min(w / iw, h / ih); const ww = iw * k, hh = ih * k;
  slide.addImage({ path: path.join(__dirname, "memes", name + ".png"), x: x + (w - ww) / 2, y: y + (h - hh) / 2, w: ww, h: hh,
    altText: "Meme: " + name.replace(/_/g, " "), objectName: "meme " + name });
}
const S = D.servicios;
const caidos = (c) => S.filter((s) => s.se_cayo[c].afectado !== "no reportado");
const confirmados = (c) => S.filter((s) => s.se_cayo[c].afectado === "confirmado");
const EN = { "X (Twitter)": "X", "Banco Nación (BNA+)": "Banco Nación", "Cuenta DNI (Banco Provincia)": "Cuenta DNI",
  "ARCA (ex AFIP)": "ARCA (tax agency)", "Campus virtual UTN FRRe": "UTN FRRe campus" };
const nombre = (s) => EN[s] || s;
const AXIS = {
  catAxisLabelColor: COL.ink2, valAxisLabelColor: COL.muted, catAxisLabelFontSize: 12, valAxisLabelFontSize: 12,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", valGridLine: { color: COL.grid, size: 1 },
  catGridLine: { style: "none" }, catAxisLineColor: COL.line, valAxisLineShow: false,
};

// =====================================================================
// 1. Title
// =====================================================================
pres.addSection({ title: "Situation" });
let s = pres.addSlide({ masterName: "BLANK", sectionTitle: "Situation" });
txt(s, "DATA4QUALITY 2026 · ADVANCED TOPICS IN SOFTWARE QUALITY · UTN FRRe", { x: MX, y: 0.9, w: W - 2 * MX, h: 0.4, fontSize: 13, bold: true, color: COL.muted, charSpacing: 2 });
txt(s, [{ text: "What goes dark when a ", options: {} }, { text: "single company", options: { color: COL.accent } }, { text: " goes down?", options: {} }],
  { x: MX, y: 1.6, w: W - 2 * MX, h: 2.9, fontSize: 64, bold: true, valign: "middle", lineSpacingMultiple: 0.95 });
txt(s, "A software quality story told with data", { x: MX, y: 4.7, w: W - 2 * MX, h: 0.6, fontSize: 26, color: COL.ink2 });
txt(s, [{ text: "Presented by: ", options: { color: COL.muted } }, { text: "[your name / team]", options: { bold: true, color: COL.ink } },
  { text: "   ·   December 3, 2026", options: { color: COL.muted } }], { x: MX, y: 5.6, w: W - 2 * MX, h: 0.5, fontSize: 20 });
s.addNotes("Open with a question, not a definition. Pause after reading the title.");

// =====================================================================
// 2. The error screen
// =====================================================================
s = pres.addSlide({ masterName: "CENTER", sectionTitle: "Situation" });
s.addText("Tuesday, November 18, 2025 · 10 AM", { placeholder: "title" });
const wx = 2.2, wy = 1.65, ww = W - 4.4, wh = 2.85;
s.addShape(pres.ShapeType.roundRect, { x: wx, y: wy, w: ww, h: wh, rectRadius: 0.12, fill: { color: COL.bg },
  line: { color: COL.line, width: 1 }, shadow: { type: "outer", color: "000000", opacity: 0.12, blur: 12, offset: 4, angle: 90 }, objectName: "browser window" });
s.addShape(pres.ShapeType.rect, { x: wx + 0.05, y: wy + 0.05, w: ww - 0.1, h: 0.45, fill: { color: "F1F0EC" }, line: { color: "F1F0EC" } });
[0, 1, 2].forEach((i) => s.addShape(pres.ShapeType.ellipse, { x: wx + 0.3 + i * 0.28, y: wy + 0.18, w: 0.18, h: 0.18, fill: { color: COL.line }, line: { color: COL.line } }));
txt(s, "ERROR 500 · INTERNAL SERVER ERROR", { x: wx + 0.6, y: wy + 0.8, w: ww - 1.2, h: 0.4, fontSize: 16, color: COL.muted, charSpacing: 2 });
txt(s, "Please unblock challenges.cloudflare.com to proceed.", { x: wx + 0.6, y: wy + 1.25, w: ww - 1.2, h: 1.35, fontSize: 28, bold: true, valign: "top" });
txt(s, "That day, these went down:", { x: MX, y: 4.75, w: W - 2 * MX, h: 0.45, fontSize: 20, color: COL.ink2, align: "center" });
const chips = confirmados("cloudflare").map((x) => [nombre(x.servicio), true])
  .concat(caidos("cloudflare").filter((x) => x.se_cayo.cloudflare.afectado !== "confirmado").slice(0, 4).map((x) => [nombre(x.servicio), false]));
const cw = chips.map(([t]) => 0.45 + t.length * 0.12); const total = cw.reduce((a, b) => a + b, 0) + 0.15 * (chips.length - 1);
let cx = (W - total) / 2;
chips.forEach(([t, fuerte], i) => {
  s.addText(t, { isTextBox: true, x: cx, y: 5.35, w: cw[i], h: 0.5, fontSize: 16, bold: fuerte, color: COL.ink, align: "center", valign: "middle",
    margin: 0, fontFace: "Arial", shape: pres.ShapeType.roundRect, rectRadius: 0.25, fill: { color: COL.bg }, line: { color: fuerte ? COL.ink : COL.line, width: fuerte ? 1.5 : 1 } });
  cx += cw[i] + 0.15;
});
nota(s, "Reconstruction without branding. Argentine users saw it in Spanish: «Por favor, desbloquee challenges.cloudflare.com para continuar». Bold: failure confirmed by the outlet or company; others: reported in the media.", 6.3);
s.addNotes("Everyone in the room probably saw this screen. Nobody knew what Cloudflare was.");

// =====================================================================
// 3. Google Trends
// =====================================================================
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Situation" });
s.addText([{ text: "Argentina asked Google: " }, { text: "“What is Cloudflare?”", options: { color: COL.accent } }], { placeholder: "title" });
const tr = D.trends.serie;
s.addChart(pres.charts.LINE, [{ name: "Search interest for “cloudflare”", labels: tr.map((p) => (+p.d.slice(8, 10)) + ""), values: tr.map((p) => p.v) }], Object.assign({
  x: MX, y: 1.45, w: 9.0, h: 5.0, chartColors: [COL.accent], lineSize: 3, lineDataSymbol: "none", showLegend: false,
  valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 25, catAxisLabelFrequency: 1,
  showCatAxisTitle: true, catAxisTitle: "November 2025 (day)", catAxisTitleColor: COL.muted, catAxisTitleFontSize: 12,
  showValAxisTitle: true, valAxisTitle: "Search interest (100 = peak)", valAxisTitleColor: COL.muted, valAxisTitleFontSize: 12,
  objectName: "chart google trends",
}, AXIS));
const normal = tr.filter((p) => p.d < "2025-11-18").map((p) => p.v); const prom = normal.reduce((a, b) => a + b, 0) / normal.length;
txt(s, Math.floor(100 / prom / 10) * 10 + "+", { x: 9.9, y: 2.0, w: 2.9, h: 1.4, fontSize: 80, bold: true, color: COL.accent });
txt(s, "times more searches on Nov 18 than on a normal day", { x: 9.9, y: 3.4, w: 2.9, h: 1.0, fontSize: 20, color: COL.ink2, valign: "top" });
txt(s, "Top rising search: “que es cloudflare” (what is cloudflare)", { x: 9.9, y: 4.6, w: 2.9, h: 1.0, fontSize: 14, color: COL.muted, valign: "top" });
nota(s, "Source: Google Trends, Argentina, Nov 1–30, 2025, search term “cloudflare”. Relative values (100 = busiest day of the month), not counts.");
s.addNotes("Flat line all month, then a wall on November 18. People learned the name of a company the day it failed.");

// =====================================================================
// 4. Memes (Cloudflare)
// =====================================================================
s = pres.addSlide({ masterName: "CENTER", sectionTitle: "Situation" });
s.addText("Meanwhile, on the internet…", { placeholder: "title" });
[["cloudflare_this_is_fine", 0], ["homer_error_500", 1], ["cloudflare_global_outage", 2]]
  .forEach(([m, i]) => meme(s, m, MX + i * 4.1, 1.6, 3.9, 4.95));
nota(s, "Memes shared on social media during the outages. Drag, resize or replace freely.");
s.addNotes("Let the room laugh. Then: behind the memes, there is data.");

// =====================================================================
// 5. Radar
// =====================================================================
pres.addSection({ title: "Data" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Data" });
const rd = D.radar;
let peor = rd.filter((p) => p.d != null && p.h >= 8.33 && p.h <= 14.1).reduce((m, p) => (p.d < m.d ? p : m));
const hhmm = (h) => { const hh = Math.floor(h), mm = Math.round((h - hh) * 60); return hh + ":" + (mm < 10 ? "0" : "") + mm; };
s.addText([{ text: "At 11 AM, Argentina’s web traffic dropped " }, { text: fmt(-peor.d) + "%", options: { color: COL.accent } }], { placeholder: "title" });
const ymax = Math.max(...rd.map((p) => Math.max(p.v, p.c || 0)));
const labels = rd.map((p) => hhmm(p.h));
s.addChart([
  { type: pres.charts.AREA, data: [{ name: "Cloudflare outage (8:20–14:06)", labels, values: rd.map((p) => (p.h >= 8.33 && p.h <= 14.1 ? +(ymax * 1.05).toFixed(4) : 0)) }],
    options: { chartColors: [COL.accentSoft] } },
  { type: pres.charts.LINE, data: [
      { name: "Previous Tuesday (Nov 11)", labels, values: rd.map((p) => p.c) },
      { name: "Tuesday, Nov 18, 2025", labels, values: rd.map((p) => p.v) }],
    options: { chartColors: [COL.gray, COL.accent], lineSize: 3, lineDataSymbol: "none" } },
], Object.assign({
  x: MX, y: 1.45, w: 9.0, h: 5.0, showLegend: true, legendPos: "t", legendFontSize: 13, legendColor: COL.ink2, legendFontFace: "+mn-lt",
  catAxisLabelFrequency: 12, valAxisMinVal: 0, valAxisMaxVal: +(ymax * 1.05).toFixed(3), valAxisLabelFormatCode: "0.0",
  showValAxisTitle: true, valAxisTitle: "Web traffic (relative scale)", valAxisTitleColor: COL.muted, valAxisTitleFontSize: 12,
  showCatAxisTitle: true, catAxisTitle: "Argentina time", catAxisTitleColor: COL.muted, catAxisTitleFontSize: 12,
  objectName: "chart radar traffic",
}, AXIS));
txt(s, fmt(peor.d) + "%", { x: 9.9, y: 2.0, w: 2.9, h: 1.4, fontSize: 72, bold: true, color: COL.accent });
txt(s, "at " + hhmm(peor.h) + " vs. the same time the previous Tuesday", { x: 9.9, y: 3.4, w: 2.9, h: 1.0, fontSize: 20, color: COL.ink2, valign: "top" });
nota(s, "Source: Cloudflare Radar (CC BY-NC 4.0), Argentina web traffic through Cloudflare, every 15 min. During the outage Cloudflare’s own measurement was also affected: the drop mixes lost and unrecorded traffic.");
s.addNotes("Gray line: a normal Tuesday. Orange: November 18. The shaded band is the outage window from Cloudflare's postmortem.");

// =====================================================================
// 6. Three outages
// =====================================================================
s = pres.addSlide({ masterName: "CENTER", sectionTitle: "Data" });
s.addText("Three outages in 16 months", { placeholder: "title" });
const peorHttp = (ev) => { const r = D.caidas.find((c) => c.evento.startsWith(ev) && c.fuente === "http"); return r ? +r.dif_pct_peor_momento : null; };
[["Cloudflare", "cloudflare", true], ["Amazon (AWS)", "aws", false], ["CrowdStrike", "crowdstrike", false]].forEach(([n, k, acc], i) => {
  const x = MX + i * 4.05;
  txt(s, n, { x, y: 2.2, w: 3.9, h: 0.7, fontSize: 30, bold: true, align: "center" });
  txt(s, fmt(peorHttp(k)) + "%", { x, y: 3.0, w: 3.9, h: 1.9, fontSize: 96, bold: true, align: "center", color: acc ? COL.accent : COL.ink });
});
nota(s, "Argentina’s web traffic at the worst moment vs. the same hour a week earlier (Cloudflare Radar). Cloudflare: Nov 18, 2025 · AWS: Oct 20, 2025 · CrowdStrike: Jul 19, 2024.", 6.2);
s.addNotes("Same question, three answers. Only one of them emptied the Argentine web. The other two hit apps and office computers.");

// =====================================================================
// 7. Memes (ChatGPT / X)
// =====================================================================
s = pres.addSlide({ masterName: "CENTER", sectionTitle: "Data" });
s.addText("How it felt", { placeholder: "title" });
[["chatgpt_caveman", 0], ["chatgpt_inside_out", 1], ["x_servers", 2]]
  .forEach(([m, i]) => meme(s, m, MX + i * 4.1, 1.6, 3.9, 4.95));
nota(s, "Memes shared on social media. Room to add AWS and CrowdStrike memes (more in presentacion/memes/).");

s = pres.addSlide({ masterName: "CENTER", sectionTitle: "Data" });
s.addText("So… who is holding up the internet?", { placeholder: "title" });
meme(s, "internet_tower_aws_cloudflare", MX, 1.55, W - 2 * MX, 5.2);
s.addNotes("Bridge to the discovery: the joke is the data. Next slide measures it.");

// =====================================================================
// 8. Share of sites per company (bars)
// =====================================================================
pres.addSection({ title: "Discovery" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Discovery" });
s.addText([{ text: "Over half of top sites depend on " }, { text: "one company", options: { color: COL.accent } }], { placeholder: "title" });
txt(s, "Share of the " + fmt(D.sitios.con_datos) + " most-visited sites from Argentina that depend on each company", { x: MX, y: 1.3, w: W - 2 * MX, h: 0.5, fontSize: 18, color: COL.ink2 });
const emp = D.empresas.filter((e) => e.empresa !== "Otra").sort((a, b) => b.pct - a.pct).slice(0, 6);
s.addChart(pres.charts.BAR, [{ name: "% of sites", labels: emp.map((e) => e.empresa), values: emp.map((e) => +e.pct.toFixed(1)) }], Object.assign({
  x: MX, y: 1.9, w: W - 2 * MX, h: 4.6, barDir: "bar", catAxisOrientation: "maxMin", barGapWidthPct: 45,
  chartColors: emp.map((e, i) => (i === 0 ? COL.accent : COL.gray)), showLegend: false,
  valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 25, valAxisLabelFormatCode: '0"%"',
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"%"', dataLabelFontSize: 16, dataLabelColor: COL.ink, dataLabelFontFace: "+mn-lt",
  catAxisLabelFontSize: 16, objectName: "chart share by company",
}, AXIS, { catAxisLabelFontSize: 16 }));
nota(s, "Source: Chrome UX Report (most-visited sites from Argentina, Oct 2026) + HTTP Archive (CDN and cloud of each site, Oct 1, 2026). A site can depend on more than one company. Adult sites excluded.");
s.addNotes("This is the main finding. One company sits in front of more than half of the sites we use every day.");

// =====================================================================
// 9. Waffle 7 in 10
// =====================================================================
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Discovery" });
const n = Math.round(D.concentracion.pct_sitios);
s.addText([{ text: fmt(n / 10) + " in 10", options: { color: COL.accent } }, { text: " depend on one of three companies" }], { placeholder: "title" });
const lado = 0.43, gap = 0.07, ox = MX + 0.2, oy = 1.45;
for (let i = 0; i < 100; i++) {
  const f = Math.floor(i / 10), c = i % 10;
  s.addShape(pres.ShapeType.roundRect, { x: ox + c * (lado + gap), y: oy + f * (lado + gap), w: lado, h: lado, rectRadius: 0.05,
    fill: { color: i < n ? COL.accent : COL.grid }, line: { color: i < n ? COL.accent : COL.grid } });
}
const tx = ox + 10 * (lado + gap) + 0.7, tw = W - tx - MX;
txt(s, "Each square = 1% of the most-visited sites from Argentina", { x: tx, y: 1.9, w: tw, h: 0.9, fontSize: 22, color: COL.ink2, valign: "top" });
txt(s, [{ text: n + " of 100", options: { bold: true, color: COL.accent } }, { text: " depend on Cloudflare, Amazon or Google" }], { x: tx, y: 3.0, w: tw, h: 1.0, fontSize: 26, valign: "top" });
txt(s, [{ text: fmt(D.concentracion.pct_sin_cdn) + "%", options: { bold: true } }, { text: " use no detectable provider: many are government and Chaco sites" }], { x: tx, y: 4.3, w: tw, h: 1.0, fontSize: 20, color: COL.ink2, valign: "top" });
nota(s, "Source: Chrome UX Report + HTTP Archive (Oct 2026). Hard dependencies only: CDN, hosting, cloud, proxy.");

// =====================================================================
// 10. Argentina vs. world (dumbbell, drawn with shapes)
// =====================================================================
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Discovery" });
s.addText([{ text: "Not just Argentina: " }, { text: "the world depends even more", options: { color: COL.accent } }], { placeholder: "title" });
const orden = ["Cloudflare", "Amazon (AWS)", "Google", "Akamai", "Fastly", "Microsoft (Azure)"];
const mundo = orden.map((e) => D.mundo.find((m) => m.empresa === e)).filter(Boolean);
const lx = MX + 2.6, rx = W - MX - 0.6, top = 2.15, fila = 0.68;
const X = (v) => lx + (v / 100) * (rx - lx);
s.addShape(pres.ShapeType.ellipse, { x: MX, y: 1.45, w: 0.22, h: 0.22, fill: { color: COL.blue }, line: { color: COL.blue } });
txt(s, "Argentina (top 10,000 from AR)", { x: MX + 0.32, y: 1.38, w: 4, h: 0.36, fontSize: 15, color: COL.ink2 });
s.addShape(pres.ShapeType.ellipse, { x: MX + 4.4, y: 1.45, w: 0.22, h: 0.22, fill: { color: COL.world }, line: { color: COL.world } });
txt(s, "World (global top 10,000)", { x: MX + 4.72, y: 1.38, w: 4, h: 0.36, fontSize: 15, color: COL.ink2 });
[0, 25, 50, 75, 100].forEach((v) => {
  s.addShape(pres.ShapeType.line, { x: X(v), y: top - 0.15, w: 0, h: mundo.length * fila + 0.05, line: { color: COL.grid, width: 1 } });
  txt(s, v + "%", { x: X(v) - 0.4, y: top + mundo.length * fila - 0.02, w: 0.8, h: 0.3, fontSize: 12, color: COL.muted, align: "center" });
});
mundo.forEach((m, i) => {
  const y = top + i * fila + fila / 2 - 0.1;
  txt(s, m.empresa, { x: MX, y: y - 0.2, w: 2.4, h: 0.4, fontSize: 18, align: "right", valign: "middle" });
  const a = Math.min(m.ar, m.mundo), b = Math.max(m.ar, m.mundo);
  s.addShape(pres.ShapeType.line, { x: X(a), y, w: Math.max(X(b) - X(a), 0.001), h: 0, line: { color: COL.line, width: 4 } });
  s.addShape(pres.ShapeType.ellipse, { x: X(m.mundo) - 0.13, y: y - 0.13, w: 0.26, h: 0.26, fill: { color: COL.world }, line: { color: "FFFFFF", width: 1.5 } });
  s.addShape(pres.ShapeType.ellipse, { x: X(m.ar) - 0.13, y: y - 0.13, w: 0.26, h: 0.26, fill: { color: COL.blue }, line: { color: "FFFFFF", width: 1.5 } });
  if (m.empresa === "Cloudflare" || m.empresa === "Akamai") {
    const izq = m.ar < m.mundo;
    const arena = izq && X(m.ar) - 1.45 < lx;   // no room on the left: label above the dot
    txt(s, "AR " + fmt(m.ar) + "%", arena
      ? { x: X(m.ar) - 0.6, y: y - 0.52, w: 1.2, h: 0.32, fontSize: 15, bold: true, align: "center", valign: "middle" }
      : { x: izq ? X(m.ar) - 1.45 : X(m.ar) + 0.2, y: y - 0.2, w: 1.25, h: 0.4, fontSize: 15, bold: true, align: izq ? "right" : "left", valign: "middle" });
    txt(s, "World " + fmt(m.mundo) + "%", { x: izq ? X(m.mundo) + 0.2 : X(m.mundo) - 1.65, y: y - 0.2, w: 1.45, h: 0.4, fontSize: 15, bold: true, align: izq ? "left" : "right", valign: "middle" });
  }
});
nota(s, "Source: HTTP Archive, Oct 1, 2026, same method for both. Argentina uses less Akamai and more local providers than the world average.");
s.addNotes("If you were thinking 'this is an Argentine problem': it isn't. The whole internet is built this way.");

// =====================================================================
// 11. Explore on your phone (QR)
// =====================================================================
pres.addSection({ title: "Explore" });
s = pres.addSlide({ masterName: "CENTER", sectionTitle: "Explore" });
s.addText("What goes dark for you?", { placeholder: "title" });
const QR = path.join(__dirname, "qr.png");
if (fs.existsSync(QR)) {   // made by presentacion/qr.py
  s.addImage({ path: QR, x: (W - 3.6) / 2, y: 1.7, w: 3.6, h: 3.6, altText: "QR code to the explorer", objectName: "QR code" });
  const url = path.join(__dirname, "qr_url.txt");
  if (fs.existsSync(url)) txt(s, fs.readFileSync(url, "utf8").replace(/^https?:\/\//, ""), { x: MX, y: 5.35, w: W - 2 * MX, h: 0.35, fontSize: 14, color: COL.muted, align: "center" });
} else {
  s.addShape(pres.ShapeType.roundRect, { x: (W - 3.6) / 2, y: 1.7, w: 3.6, h: 3.6, rectRadius: 0.1, fill: { color: COL.soft },
    line: { color: COL.muted, width: 1.5, dashType: "dash" }, objectName: "QR placeholder" });
  txt(s, "PASTE THE QR CODE HERE", { x: (W - 3.6) / 2, y: 3.2, w: 3.6, h: 0.6, fontSize: 16, bold: true, color: COL.muted, align: "center" });
}
txt(s, "Scan, pick the apps you use, pick a company… and see what goes dark", { x: MX, y: 5.6, w: W - 2 * MX, h: 0.6, fontSize: 24, color: COL.ink2, align: "center" });
s.addNotes("Give the room 30 seconds to scan. The explorer shows 57 well-known services in Argentina.");

// =====================================================================
// 12. What web data doesn't see (TO CHANGE)
// =====================================================================
pres.addSection({ title: "Quality concept" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Quality concept" });
s.addText("Postmortem findings: what web data doesn’t see", { placeholder: "title" });
toChange(s);
const culpa = caidos("cloudflare").filter((x) => !x.empresas.includes("Cloudflare")).length;
[["Aerolíneas Argentinas", "Its website depends on Google, but on Jul 19, 2024 its systems crashed: CrowdStrike runs inside Windows computers."],
 ["The Nov 18 error screen", "Cloudflare’s anti-bot check sits inside other sites’ logins. It was down 8:30–10:10 and 11:40–12:30 (Argentina time)."],
 [culpa + " services", "were reported down on Nov 18 without depending on Cloudflare. Noise, or hidden dependencies?"]]
  .forEach(([t, b], i) => {
    const x = MX + i * 4.1, y = 1.7;
    s.addShape(pres.ShapeType.roundRect, { x, y, w: 3.85, h: 4.2, rectRadius: 0.12, fill: { color: COL.soft }, line: { color: COL.soft } });
    txt(s, t, { x: x + 0.3, y: y + 0.3, w: 3.25, h: 0.8, fontSize: 22, bold: true, valign: "top" });
    txt(s, b, { x: x + 0.3, y: y + 1.2, w: 3.25, h: 2.8, fontSize: 17, color: COL.ink2, valign: "top" });
  });

// =====================================================================
// 13. Why they went down (TO CHANGE)
// =====================================================================
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Quality concept" });
s.addText([{ text: "Why? Not a hack: " }, { text: "routine changes hit everyone", options: { color: COL.accent } }], { placeholder: "title" });
toChange(s);
const filas = [
  ["Cloudflare", "A database permission change", "An auto-generated file, twice its size, copied to the whole network", "~6 hours"],
  ["AWS", "DNS automation with a latent bug", "One region that half the cloud depends on; other services failed in a chain", "~14.5 hours"],
  ["CrowdStrike", "A routine content update", "Sent to every connected computer, no staged rollout", "78 min to ship; 8.5M PCs fixed by hand"],
];
const cols = [2.0, 3.0, 4.6, 2.5]; const cxs = [MX]; cols.slice(0, -1).forEach((w, i) => cxs.push(cxs[i] + w + 0.1));
["", "The change", "How it spread", "The cost"].forEach((h, j) => txt(s, h.toUpperCase(), { x: cxs[j], y: 1.5, w: cols[j], h: 0.35, fontSize: 12, bold: true, color: COL.muted, charSpacing: 1 }));
filas.forEach((f, i) => {
  const y = 1.95 + i * 1.45;
  f.forEach((c, j) => {
    if (j === 0) { txt(s, c, { x: cxs[j], y, w: cols[j], h: 1.2, fontSize: 20, bold: true, valign: "middle" }); return; }
    s.addText(c, { isTextBox: true, x: cxs[j], y, w: cols[j], h: 1.2, fontSize: 15, color: COL.ink, valign: "middle", margin: 0.12, fontFace: "Arial",
      shape: pres.ShapeType.roundRect, rectRadius: 0.08, fill: { color: COL.bg }, line: { color: j === 2 ? COL.accent : COL.line, width: j === 2 ? 2 : 1 } });
  });
});
nota(s, "Sources: official postmortems — Cloudflare (Nov 18, 2025), AWS (us-east-1, Oct 2025), CrowdStrike (PIR and root cause analysis, 2024); PC count: Microsoft. See docs/postmortems.md.");

// =====================================================================
// 14. All at once vs. gradual (TO CHANGE)
// =====================================================================
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Quality concept" });
s.addText([{ text: "What if the change had rolled out " }, { text: "gradually?", options: { color: COL.accent } }], { placeholder: "title" });
toChange(s);
function grilla(x0, y0, rojos, titulo, pie) {
  const d = 0.22, g = 0.1;
  for (let i = 0; i < 100; i++) {
    const f = Math.floor(i / 10), c = i % 10;
    s.addShape(pres.ShapeType.ellipse, { x: x0 + c * (d + g), y: y0 + f * (d + g), w: d, h: d, fill: { color: rojos(i) ? COL.bad : COL.ok }, line: { color: "FFFFFF", width: 0.5 } });
  }
  txt(s, titulo, { x: x0, y: y0 - 0.55, w: 3.2, h: 0.45, fontSize: 18, bold: true });
  txt(s, pie, { x: x0, y: y0 + 10 * (d + g) + 0.05, w: 3.2, h: 0.7, fontSize: 15, color: COL.ink2, valign: "top" });
}
const cinco = new Set([12, 37, 54, 71, 88]);
grilla(MX, 2.05, () => true, "All at once", "100 of 100 down: a single point of failure");
grilla(MX + 3.6, 2.05, (i) => cinco.has(i), "Gradually (canary)", "5 of 100 fail → error detected, rollout stopped");
[["Product · Reliability", "ISO/IEC 25010:2023: availability, fault tolerance, recoverability. Thousands of sites, one single point of failure."],
 ["Process · Gradual rollout", "Test changes on a few first and stop if they fail. Plus error budgets and blameless postmortems (Site Reliability Engineering)."],
 ["Person · Who pays", "People who never chose the provider, and didn’t know it existed: they couldn’t pay, travel or work."]]
  .forEach(([t, b], i) => {
    const y = 1.55 + i * 1.6, x = MX + 7.4, w = W - x - MX;
    s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 1.45, rectRadius: 0.1, fill: { color: COL.soft }, line: { color: COL.soft } });
    txt(s, t, { x: x + 0.25, y: y + 0.15, w: w - 0.5, h: 0.4, fontSize: 18, bold: true });
    txt(s, b, { x: x + 0.25, y: y + 0.55, w: w - 0.5, h: 0.85, fontSize: 14, color: COL.ink2, valign: "top" });
  });
const legendY = 6.15;
s.addShape(pres.ShapeType.ellipse, { x: MX, y: legendY + 0.07, w: 0.2, h: 0.2, fill: { color: COL.ok }, line: { color: COL.ok } });
txt(s, "working", { x: MX + 0.28, y: legendY, w: 1.2, h: 0.34, fontSize: 13, color: COL.ink2 });
s.addShape(pres.ShapeType.ellipse, { x: MX + 1.5, y: legendY + 0.07, w: 0.2, h: 0.2, fill: { color: COL.bad }, line: { color: COL.bad } });
txt(s, "with the error", { x: MX + 1.78, y: legendY, w: 2, h: 0.34, fontSize: 13, color: COL.ink2 });

// =====================================================================
// 15. Closing quote (TO CHANGE)
// =====================================================================
pres.addSection({ title: "Closing" });
s = pres.addSlide({ masterName: "BLANK", sectionTitle: "Closing" });
toChange(s);
txt(s, [{ text: "The product failed, the cause was in the process, " }, { text: "and people paid for it.", options: { color: COL.accent } }],
  { x: MX, y: 0.9, w: W - 2 * MX, h: 2.6, fontSize: 48, bold: true, valign: "middle" });
[["Sources (public)", "Chrome UX Report · HTTP Archive · Cloudflare Radar · Google Trends · public DNS + Team Cymru · news and official postmortems"],
 ["Unit of analysis", "Most-visited website from Argentina (" + fmt(D.sitios.con_datos) + " with data) · well-known service, app or web (" + S.length + ") · three outages"],
 ["Limitations", "Depending on a company is not going down with it · DNS sees the front door, as of Nov 2026 · “not reported” doesn’t mean it worked"],
 ["Data and code", "github.com/Blanco302002/tpi-aacsw"]]
  .forEach(([t, b], i) => {
    const x = MX + (i % 2) * 6.15, y = 3.9 + Math.floor(i / 2) * 1.45;
    txt(s, t, { x, y, w: 5.9, h: 0.38, fontSize: 16, bold: true });
    txt(s, b, { x, y: y + 0.4, w: 5.9, h: 0.95, fontSize: 14, color: COL.ink2, valign: "top" });
  });

// =====================================================================
// 16. Thank you
// =====================================================================
s = pres.addSlide({ masterName: "BLANK", sectionTitle: "Closing" });
txt(s, "Thank you", { x: MX, y: 2.0, w: W - 2 * MX, h: 1.6, fontSize: 80, bold: true, align: "center", valign: "middle" });
txt(s, "Questions?", { x: MX, y: 3.7, w: W - 2 * MX, h: 0.8, fontSize: 36, color: COL.accent, align: "center", valign: "middle" });
txt(s, "[your name / team]  ·  github.com/Blanco302002/tpi-aacsw", { x: MX, y: 5.2, w: W - 2 * MX, h: 0.5, fontSize: 18, color: COL.muted, align: "center" });

// ---------- Write + theme ----------
(async () => {
  await pres.writeFile({ fileName: SALIDA });
  // Optional: writes the palette into the deck theme (needs the pptx skill's helper).
  if (process.env.PPTX_SKILL) {
    const { applyTheme } = require(path.join(process.env.PPTX_SKILL, "scripts", "apply_theme.js"));
    await applyTheme(SALIDA, THEME);
  }
  console.log("OK " + path.basename(SALIDA));
})();
