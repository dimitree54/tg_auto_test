async function U(e) {
  return await e.json();
}
function O(e, t, n) {
  return new Error(`${e} ${t} failed: ${n.status} ${n.statusText}`);
}
async function ue(e) {
  const t = await fetch(e, { method: "GET" });
  if (!t.ok) throw O("GET", e, t);
  return await U(t);
}
async function R(e, t) {
  const n = await fetch(e, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(t)
  });
  if (!n.ok) throw O("POST", e, n);
  return await U(n);
}
async function me(e) {
  const t = await fetch(e, { method: "POST" });
  if (!t.ok) throw O("POST", e, t);
  return await U(t);
}
async function pe(e, t) {
  const n = await fetch(e, { method: "POST", body: t });
  if (!n.ok) throw O("POST", e, n);
  return await U(n);
}
async function Y(e) {
  return await R("/api/message", { text: e });
}
async function fe(e, t, n) {
  const s = new FormData();
  return s.append("file", e), n && s.append("caption", n), await pe(`/api/${t}`, s);
}
async function ge(e, t) {
  return await R("/api/callback", { message_id: e, data: t });
}
async function he(e) {
  return await R("/api/invoice/pay", { message_id: e });
}
async function ve() {
  return await me("/api/reset");
}
async function Ee() {
  return await ue("/api/state");
}
async function ye(e, t) {
  return await R("/api/poll/vote", { message_id: e, option_ids: t });
}
const u = {
  sending: !1,
  stagedFiles: []
};
let I = null;
function E(e) {
  const t = document.getElementById(e);
  if (!t) throw new Error(`Missing element: #${e}`);
  return t;
}
function r() {
  if (I) return I;
  const e = document.querySelector(".chat-container");
  if (!e) throw new Error("Missing element: .chat-container");
  return I = {
    messagesEl: E("messages"),
    inputEl: E("msgInput"),
    sendBtn: E("sendBtn"),
    resetBtn: E("resetBtn"),
    typingEl: E("typing"),
    attachBtn: E("attachBtn"),
    fileInput: E("fileInput"),
    stagedFilesEl: E("stagedFiles"),
    replyKeyboardEl: E("replyKeyboard"),
    menuBtn: E("menuBtn"),
    commandPanelEl: E("commandPanel"),
    chatContainer: e
  }, I;
}
function w(e) {
  const t = r();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
const $ = {
  botCommands: [],
  menuButtonType: "default"
};
let h = !1, k = "menu", y = [], v = -1, q = null;
function be(e) {
  q = e;
  const t = r();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !u.sending && t.menuBtn.classList.contains("visible")) {
      if (h && k === "menu") {
        b(), j();
        return;
      }
      Z();
    }
  }), t.inputEl.addEventListener("input", () => {
    j();
  }), t.inputEl.addEventListener("keydown", (n) => {
    if (h) {
      if (n.key === "Escape") {
        n.preventDefault(), b();
        return;
      }
      if (y.length > 0) {
        if (n.key === "ArrowDown") {
          n.preventDefault(), X(1);
          return;
        }
        if (n.key === "ArrowUp") {
          n.preventDefault(), X(-1);
          return;
        }
      }
      n.key === "Enter" && ne() && n.preventDefault();
    }
  }), document.addEventListener("click", (n) => {
    if (!h) return;
    const s = n.target;
    s instanceof Node && (t.commandPanelEl.contains(s) || t.menuBtn.contains(s) || t.inputEl.contains(s) || b());
  });
}
function b() {
  const e = r();
  h = !1, k = "menu", y = [], v = -1, e.commandPanelEl.classList.remove("visible"), e.commandPanelEl.innerHTML = "";
}
function Z() {
  ee("menu", $.botCommands, "Commands");
}
function j() {
  if (h && k === "menu") return;
  const e = Ce();
  if (e === null || $.botCommands.length === 0) {
    h && k === "slash" && b();
    return;
  }
  const t = [];
  for (const n of $.botCommands)
    n.command && n.command.indexOf(e) === 0 && t.push(n);
  if (t.length === 0) {
    h && k === "slash" && b();
    return;
  }
  ee("slash", t, e ? `Commands matching "/${e}"` : "Commands");
}
function Ce() {
  const { inputEl: e } = r(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function ee(e, t, n) {
  const s = r();
  k = e, y = Array.isArray(t) ? t : [], v = y.length > 0 ? 0 : -1, h = !0, s.commandPanelEl.innerHTML = "";
  const i = document.createElement("div");
  i.className = "cp-card";
  const a = document.createElement("div");
  if (a.className = "cp-header", a.textContent = n, i.appendChild(a), y.length === 0) {
    const o = document.createElement("div");
    o.className = "cp-empty", o.textContent = "No commands.", i.appendChild(o);
  } else
    for (const [o, c] of y.entries()) {
      const l = document.createElement("button");
      l.type = "button", l.className = `cp-item${o === v ? " selected" : ""}`, l.dataset.index = String(o), l.addEventListener("click", () => {
        const m = Number.parseInt(l.dataset.index || "", 10);
        Number.isFinite(m) && (v = m, te(), ne());
      });
      const d = document.createElement("div");
      if (d.className = "cp-cmd", d.textContent = `/${c.command || "?"}`, l.appendChild(d), c.description) {
        const m = document.createElement("div");
        m.className = "cp-desc", m.textContent = c.description, l.appendChild(m);
      }
      i.appendChild(l);
    }
  s.commandPanelEl.appendChild(i), s.commandPanelEl.classList.add("visible");
}
function te() {
  const t = r().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, s] of t.entries())
    n === v ? s.classList.add("selected") : s.classList.remove("selected");
}
function X(e) {
  !h || y.length === 0 || (v = (v + e) % y.length, v < 0 && (v += y.length), te());
}
function ne() {
  if (!h || v < 0 || v >= y.length) return !1;
  const t = y[v].command || "";
  if (!t) return !1;
  const { inputEl: n } = r();
  return k === "slash" ? (n.value = `/${t} `, b(), n.focus(), !0) : (b(), q && q(`/${t}`), !0);
}
function se() {
  const e = r();
  $.menuButtonType === "commands" && $.botCommands.length > 0 ? e.menuBtn.classList.add("visible") : (e.menuBtn.classList.remove("visible"), h && k === "menu" && b());
}
async function V() {
  try {
    const e = await Ee();
    $.botCommands = Array.isArray(e.commands) ? e.commands : [], $.menuButtonType = e.menu_button_type || "default", se(), h && k === "menu" ? Z() : h || j();
  } catch {
  }
}
function Le() {
  $.botCommands = [], $.menuButtonType = "default", se(), b();
}
function we(e) {
  const t = e.type || "";
  return t.startsWith("image/") ? "photo" : t.startsWith("audio/") ? "voice" : t.startsWith("video/") ? "video_note" : "document";
}
function Q(e) {
  const t = URL.createObjectURL(e);
  u.stagedFiles.push({ file: e, type: we(e), localUrl: t }), A();
}
function Te(e) {
  const t = u.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), u.stagedFiles.splice(e, 1), A());
}
function ke() {
  for (const e of u.stagedFiles) URL.revokeObjectURL(e.localUrl);
  u.stagedFiles = [], A();
}
function $e() {
  const e = [...u.stagedFiles];
  return u.stagedFiles = [], A(), e;
}
function A() {
  const e = r();
  if (e.stagedFilesEl.innerHTML = "", u.stagedFiles.length === 0) {
    e.stagedFilesEl.classList.remove("visible");
    return;
  }
  e.stagedFilesEl.classList.add("visible");
  for (let t = 0; t < u.stagedFiles.length; t++) {
    const n = u.stagedFiles[t], s = document.createElement("div");
    if (s.className = "staged-item", n.type === "photo") {
      const o = document.createElement("img");
      o.src = n.localUrl, o.alt = "Preview", s.appendChild(o);
    } else {
      const o = document.createElement("span");
      o.className = "staged-icon";
      const c = {
        voice: "&#127908;",
        video_note: "&#127909;"
      };
      o.innerHTML = c[n.type] ?? "&#128196;", s.appendChild(o);
    }
    const i = document.createElement("span");
    i.className = "staged-name", i.textContent = n.file.name, s.appendChild(i);
    const a = document.createElement("button");
    a.className = "staged-remove", a.innerHTML = "&times;", a.dataset.index = String(t), a.addEventListener("click", () => {
      const o = Number.parseInt(a.dataset.index || "", 10);
      Number.isFinite(o) && Te(o);
    }), s.appendChild(a), e.stagedFilesEl.appendChild(s);
  }
}
function Ne() {
  const e = r();
  e.attachBtn.addEventListener("click", () => {
    u.sending || e.fileInput.click();
  }), e.fileInput.addEventListener("change", () => {
    const t = e.fileInput.files;
    if (t && t.length > 0)
      for (let n = 0; n < t.length; n++) Q(t[n]);
    e.fileInput.value = "", e.inputEl.focus();
  }), e.chatContainer.addEventListener("dragover", (t) => {
    t.preventDefault(), t.stopPropagation();
  }), e.chatContainer.addEventListener("drop", (t) => {
    var s;
    t.preventDefault(), t.stopPropagation();
    const n = (s = t.dataTransfer) == null ? void 0 : s.files;
    if (n && n.length > 0)
      for (let i = 0; i < n.length; i++) Q(n[i]);
  });
}
function x(e) {
  return e instanceof Error ? e.message : String(e);
}
function f(e) {
  const t = document.createElement("div");
  return t.textContent = e, t.innerHTML;
}
function xe(e) {
  switch (e.type) {
    case "bold":
      return "<strong>";
    case "italic":
      return "<em>";
    case "underline":
      return "<u>";
    case "strikethrough":
      return "<s>";
    case "code":
      return "<code>";
    case "pre":
      return e.language ? `<pre><code class="language-${f(e.language)}">` : "<pre>";
    case "url":
      return "";
    case "text_url":
      return `<a href="${f(e.url ?? "")}" target="_blank" rel="noopener">`;
    case "spoiler":
      return '<span class="tg-spoiler">';
    default:
      return "";
  }
}
function Me(e) {
  switch (e.type) {
    case "bold":
      return "</strong>";
    case "italic":
      return "</em>";
    case "underline":
      return "</u>";
    case "strikethrough":
      return "</s>";
    case "code":
      return "</code>";
    case "pre":
      return e.language ? "</code></pre>" : "</pre>";
    case "url":
      return "";
    case "text_url":
      return "</a>";
    case "spoiler":
      return "</span>";
    default:
      return "";
  }
}
function S(e, t) {
  if (t.length === 0) return f(e);
  const n = [...t].sort(
    (a, o) => a.offset !== o.offset ? a.offset - o.offset : o.length - a.length
  );
  let s = "", i = 0;
  for (const a of n) {
    const o = Math.max(0, Math.min(a.offset, e.length)), c = Math.max(o, Math.min(a.offset + a.length, e.length));
    if (o > i && (s += f(e.slice(i, o))), c > o) {
      const l = e.slice(o, c);
      a.type === "url" ? s += `<a href="${f(l)}" target="_blank" rel="noopener">${f(l)}</a>` : s += xe(a) + f(l) + Me(a), i = c;
    }
  }
  return i < e.length && (s += f(e.slice(i))), s;
}
function G() {
  const e = /* @__PURE__ */ new Date();
  return `${e.getHours().toString().padStart(2, "0")}:${e.getMinutes().toString().padStart(2, "0")}`;
}
function D(e) {
  if (!Number.isFinite(e) || e < 0) return "0:00";
  const t = Math.floor(e / 60), n = Math.floor(e % 60);
  return `${t}:${n < 10 ? "0" : ""}${n}`;
}
function B() {
  const e = r();
  e.typingEl.classList.add("visible"), e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function C() {
  r().typingEl.classList.remove("visible");
}
function Se(e, t, n, s, i) {
  const a = document.createElement("div");
  a.className = "inline-keyboard";
  for (const o of t) {
    const c = document.createElement("div");
    c.className = "ik-row";
    for (const l of o) {
      const d = document.createElement("button");
      d.className = "ik-btn", d.textContent = l.text || "?", d.dataset.callbackData = l.callback_data || "", d.dataset.messageId = String(n), d.addEventListener("click", async () => {
        const m = d.dataset.callbackData || "", p = Number.parseInt(d.dataset.messageId || "0", 10);
        if (!m || u.sending) return;
        const T = d.closest(".inline-keyboard"), H = T ? T.querySelectorAll(".ik-btn") : [];
        for (const g of H) g.disabled = !0;
        u.sending = !0, w(!0), B();
        try {
          const g = await ge(p, m);
          C(), s(g);
        } catch (g) {
          C(), i(`[Callback error: ${x(g)}]`);
        }
        u.sending = !1, w(!1), r().inputEl.focus();
      }), c.appendChild(d);
    }
    a.appendChild(c);
  }
  e.appendChild(a);
}
let J = null;
function Be(e) {
  J = e;
}
function He(e) {
  const t = r();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const s = document.createElement("div");
    s.className = "rk-row";
    for (const i of n) {
      const a = document.createElement("button");
      a.className = "rk-btn", a.textContent = i.text || "?", a.addEventListener("click", () => {
        const o = a.textContent || "";
        o && (u.sending || (ae(), J && J(o)));
      }), s.appendChild(a);
    }
    t.replyKeyboardEl.appendChild(s);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function ae() {
  const e = r();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}
function N() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function M(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, e === "received" && (t.innerHTML = '<div class="sender">Bot</div>'), t;
}
function P() {
  return `<span class="meta">${G()}</span>`;
}
function oe(e, t, n, s) {
  const i = r(), a = M(t), o = document.createElement("img");
  if (o.className = "msg-photo", o.src = e, o.alt = "Photo", a.appendChild(o), n) {
    const c = t === "received" && (s != null && s.length) ? S(n, s) : f(n);
    a.innerHTML += `<span class="caption">${c}</span>`;
  }
  a.innerHTML += P(), i.messagesEl.appendChild(a), o.addEventListener("load", () => N()), N();
}
function ie(e, t, n, s) {
  const i = r(), a = M(t), o = document.createElement("div");
  o.className = "voice-player";
  const c = document.createElement("audio");
  c.src = e, c.preload = "metadata";
  const l = document.createElement("button");
  l.className = "vp-play", l.innerHTML = "&#9654;";
  const d = document.createElement("div");
  d.className = "vp-track";
  const m = document.createElement("div");
  m.className = "vp-bar";
  const p = document.createElement("div");
  p.className = "vp-fill", m.appendChild(p);
  const T = document.createElement("span");
  if (T.className = "vp-time", T.textContent = "0:00", d.appendChild(m), d.appendChild(T), o.appendChild(l), o.appendChild(d), a.appendChild(o), n) {
    const g = document.createElement("span");
    g.className = "caption";
    const _ = t === "received" && (s != null && s.length) ? S(n, s) : f(n);
    g.innerHTML = _, a.appendChild(g);
  }
  const H = document.createElement("span");
  H.className = "meta", H.textContent = G(), a.appendChild(H), i.messagesEl.appendChild(a), c.addEventListener("loadedmetadata", () => {
    T.textContent = D(c.duration);
  }), l.addEventListener("click", () => {
    c.paused ? (c.play(), l.innerHTML = "&#9646;&#9646;") : (c.pause(), l.innerHTML = "&#9654;");
  }), c.addEventListener("timeupdate", () => {
    if (c.duration) {
      const g = c.currentTime / c.duration * 100;
      p.style.width = `${g}%`, T.textContent = D(c.currentTime);
    }
  }), c.addEventListener("ended", () => {
    l.innerHTML = "&#9654;", p.style.width = "0%", T.textContent = D(c.duration);
  }), m.addEventListener("click", (g) => {
    if (c.duration) {
      const _ = m.getBoundingClientRect(), de = (g.clientX - _.left) / _.width;
      c.currentTime = de * c.duration;
    }
  }), N();
}
function ce(e, t, n, s) {
  const i = r(), a = M(t), o = document.createElement("video");
  if (o.className = "msg-video-note", o.src = e, o.controls = !0, o.playsInline = !0, a.appendChild(o), n) {
    const c = t === "received" && (s != null && s.length) ? S(n, s) : f(n);
    a.innerHTML += `<span class="caption">${c}</span>`;
  }
  a.innerHTML += P(), i.messagesEl.appendChild(a), N();
}
function le(e, t, n, s, i) {
  const a = r(), o = M(n), c = document.createElement("a");
  if (c.className = "doc-attachment", c.href = t ? `${t}?download=1` : "#", c.download = e || "", c.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${f(e)}</span>`, o.appendChild(c), s) {
    const l = n === "received" && (i != null && i.length) ? S(s, i) : f(s);
    o.innerHTML += `<span class="caption">${l}</span>`;
  }
  o.innerHTML += P(), a.messagesEl.appendChild(o), N();
}
function Pe() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function Fe(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, t.innerHTML = '<div class="sender">Bot</div>', t;
}
function _e(e, t) {
  const n = r(), s = Fe(t);
  if (e.poll_question) {
    const a = document.createElement("h4");
    a.className = "poll-question", a.textContent = e.poll_question, s.appendChild(a);
  }
  if (e.poll_options && e.message_id) {
    const a = document.createElement("div");
    a.className = "poll-options", e.poll_options.forEach((o, c) => {
      const l = document.createElement("button");
      l.className = "poll-option-btn", l.textContent = o.text, l.onclick = () => Ie(e.message_id, [c]), a.appendChild(l);
    }), s.appendChild(a);
  }
  const i = document.createElement("span");
  i.className = "meta", i.textContent = D(/* @__PURE__ */ new Date()), s.appendChild(i), n.messagesEl.appendChild(s), Pe();
}
async function Ie(e, t) {
  r();
  try {
    w(!0), B();
    const n = await ye(e, t);
    n.text && L(n.text, "received");
  } catch (n) {
    x(`Poll vote failed: ${String(n)}`);
  } finally {
    C(), w(!1);
  }
}
function L(e, t, n) {
  const s = r(), i = M(t), a = t === "received" && (n != null && n.length) ? S(e, n) : f(e);
  i.innerHTML += `<span class="text">${a}</span>${P()}`, s.messagesEl.appendChild(i), N();
}
function K(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function De(e, t) {
  const n = r(), s = M(t), i = document.createElement("div");
  i.className = "invoice-card";
  const a = document.createElement("div");
  if (a.className = "invoice-title", a.textContent = e.title || "Invoice", i.appendChild(a), e.description) {
    const p = document.createElement("div");
    p.className = "invoice-desc", p.textContent = e.description, i.appendChild(p);
  }
  const o = e.currency || "", c = e.total_amount ?? 0, l = document.createElement("div");
  l.className = "invoice-amount", l.textContent = K(o, c), i.appendChild(l);
  const d = document.createElement("button");
  d.className = "invoice-pay", d.textContent = `Pay ${K(o, c)}`, d.addEventListener("click", async () => {
    if (!u.sending) {
      u.sending = !0, w(!0), d.disabled = !0, d.textContent = "Paying...", B();
      try {
        const p = await he(e.message_id);
        C(), d.textContent = "Paid", F(p);
      } catch (p) {
        C(), d.disabled = !1, d.textContent = `Pay ${K(o, c)}`, L(`[Payment error: ${x(p)}]`, "received");
      }
      u.sending = !1, w(!1), n.inputEl.focus();
    }
  }), i.appendChild(d), s.appendChild(i);
  const m = document.createElement("span");
  m.className = "meta", m.textContent = G(), s.appendChild(m), n.messagesEl.appendChild(s), N();
}
function F(e) {
  const t = r(), n = e.reply_markup || null;
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const s = M("received"), i = S(e.text || "", e.entities ?? []);
      s.innerHTML += `<span class="text">${i}</span>${P()}`, t.messagesEl.appendChild(s), Se(
        s,
        n.inline_keyboard,
        e.message_id,
        F,
        (a) => L(a, "received")
      ), N();
    } else
      L(e.text || "", "received", e.entities);
    n && n.keyboard && He(n.keyboard);
    return;
  }
  if (e.type === "invoice") {
    De(e, "received");
    return;
  }
  if (e.type === "photo") {
    oe(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "voice") {
    ie(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "video_note") {
    ce(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "document") {
    le(e.filename || "", `/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "poll") {
    _e(e, "received");
    return;
  }
  L(`[Unknown response type: ${e.type}]`, "received");
}
async function re() {
  B();
  try {
    const e = await Y("/start");
    C(), F(e), await V();
  } catch (e) {
    C(), L(`[Error: ${x(e)}]`, "received");
  }
}
async function Ue() {
  const e = r();
  e.resetBtn.disabled = !0;
  try {
    await ve(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div>', ae(), Le(), ke(), await re();
  } catch (t) {
    L(`[Reset failed: ${x(t)}]`, "received");
  }
  e.resetBtn.disabled = !1;
}
async function W(e, t) {
  const n = r(), s = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!(!e || u.sending)) {
    b(), u.sending = !0, w(!0), s && (n.inputEl.value = ""), L(e, "sent"), B();
    try {
      const i = await Y(e);
      C(), F(i), await V();
    } catch (i) {
      C(), L(`[Error: ${x(i)}]`, "received");
    }
    u.sending = !1, w(!1), n.inputEl.focus();
  }
}
async function Oe(e, t, n) {
  const s = await fe(e, t, n);
  F(s);
}
async function z() {
  const e = r(), t = e.inputEl.value.trim(), n = u.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await W(t, { clearInput: !0 });
    return;
  }
  if (u.sending) return;
  b(), u.sending = !0, w(!0), e.inputEl.value = "";
  const s = $e();
  for (const [i, a] of s.entries()) {
    const o = i === 0 ? t : "";
    switch (a.type) {
      case "photo": {
        oe(a.localUrl, "sent", o);
        break;
      }
      case "voice": {
        ie(a.localUrl, "sent", o);
        break;
      }
      case "video_note": {
        ce(a.localUrl, "sent", o);
        break;
      }
      default:
        le(a.file.name, a.localUrl, "sent", o);
    }
    B();
    try {
      await Oe(a.file, a.type, o), C();
    } catch (c) {
      C(), L(`[Upload error: ${x(c)}]`, "received");
    }
  }
  u.sending = !1, w(!1), e.inputEl.focus(), await V();
}
function Re() {
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = r();
  Be(async (n) => {
    await W(n, { clearInput: !1 });
  }), be(async (n) => {
    await W(n, { clearInput: !1 });
  }), Ne(), t.sendBtn.addEventListener("click", () => {
    z();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && z();
  }), t.resetBtn.addEventListener("click", () => {
    Ue();
  }), re();
}
Re();
