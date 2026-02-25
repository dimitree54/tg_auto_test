async function _(e) {
  return await e.json();
}
function D(e, t, n) {
  return new Error(`${e} ${t} failed: ${n.status} ${n.statusText}`);
}
async function re(e) {
  const t = await fetch(e, { method: "GET" });
  if (!t.ok) throw D("GET", e, t);
  return await _(t);
}
async function U(e, t) {
  const n = await fetch(e, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(t)
  });
  if (!n.ok) throw D("POST", e, n);
  return await _(n);
}
async function de(e) {
  const t = await fetch(e, { method: "POST" });
  if (!t.ok) throw D("POST", e, t);
  return await _(t);
}
async function ue(e, t) {
  const n = await fetch(e, { method: "POST", body: t });
  if (!n.ok) throw D("POST", e, n);
  return await _(n);
}
async function Q(e) {
  return await U("/api/message", { text: e });
}
async function me(e, t, n) {
  const a = new FormData();
  return a.append("file", e), n && a.append("caption", n), await ue(`/api/${t}`, a);
}
async function pe(e, t) {
  return await U("/api/callback", { message_id: e, data: t });
}
async function fe(e) {
  return await U("/api/invoice/pay", { message_id: e });
}
async function ge() {
  return await de("/api/reset");
}
async function ve() {
  return await re("/api/state");
}
async function Ee(e, t) {
  return await U("/api/poll/vote", { message_id: e, option_ids: t });
}
const r = {
  sending: !1,
  stagedFiles: []
};
let H = null;
function v(e) {
  const t = document.getElementById(e);
  if (!t) throw new Error(`Missing element: #${e}`);
  return t;
}
function c() {
  if (H) return H;
  const e = document.querySelector(".chat-container");
  if (!e) throw new Error("Missing element: .chat-container");
  return H = {
    messagesEl: v("messages"),
    inputEl: v("msgInput"),
    sendBtn: v("sendBtn"),
    resetBtn: v("resetBtn"),
    typingEl: v("typing"),
    attachBtn: v("attachBtn"),
    fileInput: v("fileInput"),
    stagedFilesEl: v("stagedFiles"),
    replyKeyboardEl: v("replyKeyboard"),
    menuBtn: v("menuBtn"),
    commandPanelEl: v("commandPanel"),
    chatContainer: e
  }, H;
}
function C(e) {
  const t = c();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
const T = {
  botCommands: [],
  menuButtonType: "default"
};
let f = !1, w = "menu", E = [], g = -1, A = null;
function he(e) {
  A = e;
  const t = c();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !r.sending && t.menuBtn.classList.contains("visible")) {
      if (f && w === "menu") {
        h(), K();
        return;
      }
      z();
    }
  }), t.inputEl.addEventListener("input", () => {
    K();
  }), t.inputEl.addEventListener("keydown", (n) => {
    if (f) {
      if (n.key === "Escape") {
        n.preventDefault(), h();
        return;
      }
      if (E.length > 0) {
        if (n.key === "ArrowDown") {
          n.preventDefault(), V(1);
          return;
        }
        if (n.key === "ArrowUp") {
          n.preventDefault(), V(-1);
          return;
        }
      }
      n.key === "Enter" && ee() && n.preventDefault();
    }
  }), document.addEventListener("click", (n) => {
    if (!f) return;
    const a = n.target;
    a instanceof Node && (t.commandPanelEl.contains(a) || t.menuBtn.contains(a) || t.inputEl.contains(a) || h());
  });
}
function h() {
  const e = c();
  f = !1, w = "menu", E = [], g = -1, e.commandPanelEl.classList.remove("visible"), e.commandPanelEl.innerHTML = "";
}
function z() {
  Y("menu", T.botCommands, "Commands");
}
function K() {
  if (f && w === "menu") return;
  const e = ye();
  if (e === null || T.botCommands.length === 0) {
    f && w === "slash" && h();
    return;
  }
  const t = [];
  for (const n of T.botCommands)
    n.command && n.command.indexOf(e) === 0 && t.push(n);
  if (t.length === 0) {
    f && w === "slash" && h();
    return;
  }
  Y("slash", t, e ? `Commands matching "/${e}"` : "Commands");
}
function ye() {
  const { inputEl: e } = c(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function Y(e, t, n) {
  const a = c();
  w = e, E = Array.isArray(t) ? t : [], g = E.length > 0 ? 0 : -1, f = !0, a.commandPanelEl.innerHTML = "";
  const o = document.createElement("div");
  o.className = "cp-card";
  const s = document.createElement("div");
  if (s.className = "cp-header", s.textContent = n, o.appendChild(s), E.length === 0) {
    const i = document.createElement("div");
    i.className = "cp-empty", i.textContent = "No commands.", o.appendChild(i);
  } else
    for (const [i, d] of E.entries()) {
      const u = document.createElement("button");
      u.type = "button", u.className = `cp-item${i === g ? " selected" : ""}`, u.dataset.index = String(i), u.addEventListener("click", () => {
        const m = Number.parseInt(u.dataset.index || "", 10);
        Number.isFinite(m) && (g = m, Z(), ee());
      });
      const l = document.createElement("div");
      if (l.className = "cp-cmd", l.textContent = `/${d.command || "?"}`, u.appendChild(l), d.description) {
        const m = document.createElement("div");
        m.className = "cp-desc", m.textContent = d.description, u.appendChild(m);
      }
      o.appendChild(u);
    }
  a.commandPanelEl.appendChild(o), a.commandPanelEl.classList.add("visible");
}
function Z() {
  const t = c().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, a] of t.entries())
    n === g ? a.classList.add("selected") : a.classList.remove("selected");
}
function V(e) {
  !f || E.length === 0 || (g = (g + e) % E.length, g < 0 && (g += E.length), Z());
}
function ee() {
  if (!f || g < 0 || g >= E.length) return !1;
  const t = E[g].command || "";
  if (!t) return !1;
  const { inputEl: n } = c();
  return w === "slash" ? (n.value = `/${t} `, h(), n.focus(), !0) : (h(), A && A(`/${t}`), !0);
}
function te() {
  const e = c();
  T.menuButtonType === "commands" && T.botCommands.length > 0 ? e.menuBtn.classList.add("visible") : (e.menuBtn.classList.remove("visible"), f && w === "menu" && h());
}
async function J() {
  try {
    const e = await ve();
    T.botCommands = Array.isArray(e.commands) ? e.commands : [], T.menuButtonType = e.menu_button_type || "default", te(), f && w === "menu" ? z() : f || K();
  } catch {
  }
}
function be() {
  T.botCommands = [], T.menuButtonType = "default", te(), h();
}
function Ce(e) {
  const t = e.type || "";
  return t.startsWith("image/") ? "photo" : t.startsWith("audio/") ? "voice" : t.startsWith("video/") ? "video_note" : "document";
}
function G(e) {
  const t = URL.createObjectURL(e);
  r.stagedFiles.push({ file: e, type: Ce(e), localUrl: t }), R();
}
function Le(e) {
  const t = r.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), r.stagedFiles.splice(e, 1), R());
}
function we() {
  for (const e of r.stagedFiles) URL.revokeObjectURL(e.localUrl);
  r.stagedFiles = [], R();
}
function Te() {
  const e = [...r.stagedFiles];
  return r.stagedFiles = [], R(), e;
}
function R() {
  const e = c();
  if (e.stagedFilesEl.innerHTML = "", r.stagedFiles.length === 0) {
    e.stagedFilesEl.classList.remove("visible");
    return;
  }
  e.stagedFilesEl.classList.add("visible");
  for (let t = 0; t < r.stagedFiles.length; t++) {
    const n = r.stagedFiles[t], a = document.createElement("div");
    if (a.className = "staged-item", n.type === "photo") {
      const i = document.createElement("img");
      i.src = n.localUrl, i.alt = "Preview", a.appendChild(i);
    } else {
      const i = document.createElement("span");
      i.className = "staged-icon";
      const d = {
        voice: "&#127908;",
        video_note: "&#127909;"
      };
      i.innerHTML = d[n.type] ?? "&#128196;", a.appendChild(i);
    }
    const o = document.createElement("span");
    o.className = "staged-name", o.textContent = n.file.name, a.appendChild(o);
    const s = document.createElement("button");
    s.className = "staged-remove", s.innerHTML = "&times;", s.dataset.index = String(t), s.addEventListener("click", () => {
      const i = Number.parseInt(s.dataset.index || "", 10);
      Number.isFinite(i) && Le(i);
    }), a.appendChild(s), e.stagedFilesEl.appendChild(a);
  }
}
function ke() {
  const e = c();
  e.attachBtn.addEventListener("click", () => {
    r.sending || e.fileInput.click();
  }), e.fileInput.addEventListener("change", () => {
    const t = e.fileInput.files;
    if (t && t.length > 0)
      for (let n = 0; n < t.length; n++) G(t[n]);
    e.fileInput.value = "", e.inputEl.focus();
  }), e.chatContainer.addEventListener("dragover", (t) => {
    t.preventDefault(), t.stopPropagation();
  }), e.chatContainer.addEventListener("drop", (t) => {
    var a;
    t.preventDefault(), t.stopPropagation();
    const n = (a = t.dataTransfer) == null ? void 0 : a.files;
    if (n && n.length > 0)
      for (let o = 0; o < n.length; o++) G(n[o]);
  });
}
function $(e) {
  return e instanceof Error ? e.message : String(e);
}
function S(e) {
  const t = document.createElement("div");
  return t.textContent = e, t.innerHTML;
}
function W() {
  const e = /* @__PURE__ */ new Date();
  return `${e.getHours().toString().padStart(2, "0")}:${e.getMinutes().toString().padStart(2, "0")}`;
}
function I(e) {
  if (!Number.isFinite(e) || e < 0) return "0:00";
  const t = Math.floor(e / 60), n = Math.floor(e % 60);
  return `${t}:${n < 10 ? "0" : ""}${n}`;
}
function B() {
  const e = c();
  e.typingEl.classList.add("visible"), e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function y() {
  c().typingEl.classList.remove("visible");
}
function Ne(e, t, n, a, o) {
  const s = document.createElement("div");
  s.className = "inline-keyboard";
  for (const i of t) {
    const d = document.createElement("div");
    d.className = "ik-row";
    for (const u of i) {
      const l = document.createElement("button");
      l.className = "ik-btn", l.textContent = u.text || "?", l.dataset.callbackData = u.callback_data || "", l.dataset.messageId = String(n), l.addEventListener("click", async () => {
        const m = l.dataset.callbackData || "", p = Number.parseInt(l.dataset.messageId || "0", 10);
        if (!m || r.sending) return;
        const M = l.closest(".inline-keyboard"), L = M ? M.querySelectorAll(".ik-btn") : [];
        for (const k of L) k.disabled = !0;
        r.sending = !0, C(!0), B();
        try {
          const k = await pe(p, m);
          y(), a(k);
        } catch (k) {
          y(), o(`[Callback error: ${$(k)}]`);
        }
        r.sending = !1, C(!1), c().inputEl.focus();
      }), d.appendChild(l);
    }
    s.appendChild(d);
  }
  e.appendChild(s);
}
let q = null;
function $e(e) {
  q = e;
}
function xe(e) {
  const t = c();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const a = document.createElement("div");
    a.className = "rk-row";
    for (const o of n) {
      const s = document.createElement("button");
      s.className = "rk-btn", s.textContent = o.text || "?", s.addEventListener("click", () => {
        const i = s.textContent || "";
        i && (r.sending || (ne(), q && q(i)));
      }), a.appendChild(s);
    }
    t.replyKeyboardEl.appendChild(a);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function ne() {
  const e = c();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}
function N() {
  const e = c();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function x(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, e === "received" && (t.innerHTML = '<div class="sender">Bot</div>'), t;
}
function P() {
  return `<span class="meta">${W()}</span>`;
}
function se(e, t, n) {
  const a = c(), o = x(t), s = document.createElement("img");
  s.className = "msg-photo", s.src = e, s.alt = "Photo", o.appendChild(s), n && (o.innerHTML += `<span class="caption">${S(n)}</span>`), o.innerHTML += P(), a.messagesEl.appendChild(o), s.addEventListener("load", () => N()), N();
}
function ae(e, t, n) {
  const a = c(), o = x(t), s = document.createElement("div");
  s.className = "voice-player";
  const i = document.createElement("audio");
  i.src = e, i.preload = "metadata";
  const d = document.createElement("button");
  d.className = "vp-play", d.innerHTML = "&#9654;";
  const u = document.createElement("div");
  u.className = "vp-track";
  const l = document.createElement("div");
  l.className = "vp-bar";
  const m = document.createElement("div");
  m.className = "vp-fill", l.appendChild(m);
  const p = document.createElement("span");
  if (p.className = "vp-time", p.textContent = "0:00", u.appendChild(l), u.appendChild(p), s.appendChild(d), s.appendChild(u), o.appendChild(s), n) {
    const L = document.createElement("span");
    L.className = "caption", L.textContent = n, o.appendChild(L);
  }
  const M = document.createElement("span");
  M.className = "meta", M.textContent = W(), o.appendChild(M), a.messagesEl.appendChild(o), i.addEventListener("loadedmetadata", () => {
    p.textContent = I(i.duration);
  }), d.addEventListener("click", () => {
    i.paused ? (i.play(), d.innerHTML = "&#9646;&#9646;") : (i.pause(), d.innerHTML = "&#9654;");
  }), i.addEventListener("timeupdate", () => {
    if (i.duration) {
      const L = i.currentTime / i.duration * 100;
      m.style.width = `${L}%`, p.textContent = I(i.currentTime);
    }
  }), i.addEventListener("ended", () => {
    d.innerHTML = "&#9654;", m.style.width = "0%", p.textContent = I(i.duration);
  }), l.addEventListener("click", (L) => {
    if (i.duration) {
      const k = l.getBoundingClientRect(), le = (L.clientX - k.left) / k.width;
      i.currentTime = le * i.duration;
    }
  }), N();
}
function ie(e, t, n) {
  const a = c(), o = x(t), s = document.createElement("video");
  s.className = "msg-video-note", s.src = e, s.controls = !0, s.playsInline = !0, o.appendChild(s), n && (o.innerHTML += `<span class="caption">${S(n)}</span>`), o.innerHTML += P(), a.messagesEl.appendChild(o), N();
}
function oe(e, t, n, a) {
  const o = c(), s = x(n), i = document.createElement("a");
  i.className = "doc-attachment", i.href = t ? `${t}?download=1` : "#", i.download = e || "", i.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${S(e)}</span>`, s.appendChild(i), a && (s.innerHTML += `<span class="caption">${S(a)}</span>`), s.innerHTML += P(), o.messagesEl.appendChild(s), N();
}
function Me() {
  const e = c();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function Se(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, t.innerHTML = '<div class="sender">Bot</div>', t;
}
function Be(e, t) {
  const n = c(), a = Se(t);
  if (e.poll_question) {
    const s = document.createElement("h4");
    s.className = "poll-question", s.textContent = e.poll_question, a.appendChild(s);
  }
  if (e.poll_options && e.message_id) {
    const s = document.createElement("div");
    s.className = "poll-options", e.poll_options.forEach((i, d) => {
      const u = document.createElement("button");
      u.className = "poll-option-btn", u.textContent = i.text, u.onclick = () => Pe(e.message_id, [d]), s.appendChild(u);
    }), a.appendChild(s);
  }
  const o = document.createElement("span");
  o.className = "meta", o.textContent = I(/* @__PURE__ */ new Date()), a.appendChild(o), n.messagesEl.appendChild(a), Me();
}
async function Pe(e, t) {
  c();
  try {
    C(!0), B();
    const n = await Ee(e, t);
    n.text && b(n.text, "received");
  } catch (n) {
    $(`Poll vote failed: ${String(n)}`);
  } finally {
    y(), C(!1);
  }
}
function b(e, t) {
  const n = c(), a = x(t);
  a.innerHTML += `<span class="text">${S(e)}</span>${P()}`, n.messagesEl.appendChild(a), N();
}
function O(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function Fe(e, t) {
  const n = c(), a = x(t), o = document.createElement("div");
  o.className = "invoice-card";
  const s = document.createElement("div");
  if (s.className = "invoice-title", s.textContent = e.title || "Invoice", o.appendChild(s), e.description) {
    const p = document.createElement("div");
    p.className = "invoice-desc", p.textContent = e.description, o.appendChild(p);
  }
  const i = e.currency || "", d = e.total_amount ?? 0, u = document.createElement("div");
  u.className = "invoice-amount", u.textContent = O(i, d), o.appendChild(u);
  const l = document.createElement("button");
  l.className = "invoice-pay", l.textContent = `Pay ${O(i, d)}`, l.addEventListener("click", async () => {
    if (!r.sending) {
      r.sending = !0, C(!0), l.disabled = !0, l.textContent = "Paying...", B();
      try {
        const p = await fe(e.message_id);
        y(), l.textContent = "Paid", F(p);
      } catch (p) {
        y(), l.disabled = !1, l.textContent = `Pay ${O(i, d)}`, b(`[Payment error: ${$(p)}]`, "received");
      }
      r.sending = !1, C(!1), n.inputEl.focus();
    }
  }), o.appendChild(l), a.appendChild(o);
  const m = document.createElement("span");
  m.className = "meta", m.textContent = W(), a.appendChild(m), n.messagesEl.appendChild(a), N();
}
function F(e) {
  const t = c(), n = e.reply_markup || null;
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const a = x("received");
      a.innerHTML += `<span class="text">${S(e.text || "")}</span>${P()}`, t.messagesEl.appendChild(a), Ne(
        a,
        n.inline_keyboard,
        e.message_id,
        F,
        (o) => b(o, "received")
      ), N();
    } else
      b(e.text || "", "received");
    n && n.keyboard && xe(n.keyboard);
    return;
  }
  if (e.type === "invoice") {
    Fe(e, "received");
    return;
  }
  if (e.type === "photo") {
    se(`/api/file/${e.file_id || ""}`, "received");
    return;
  }
  if (e.type === "voice") {
    ae(`/api/file/${e.file_id || ""}`, "received");
    return;
  }
  if (e.type === "video_note") {
    ie(`/api/file/${e.file_id || ""}`, "received");
    return;
  }
  if (e.type === "document") {
    oe(e.filename || "", `/api/file/${e.file_id || ""}`, "received");
    return;
  }
  if (e.type === "poll") {
    Be(e, "received");
    return;
  }
  b(`[Unknown response type: ${e.type}]`, "received");
}
async function ce() {
  B();
  try {
    const e = await Q("/start");
    y(), F(e), await J();
  } catch (e) {
    y(), b(`[Error: ${$(e)}]`, "received");
  }
}
async function He() {
  const e = c();
  e.resetBtn.disabled = !0;
  try {
    await ge(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div>', ne(), be(), we(), await ce();
  } catch (t) {
    b(`[Reset failed: ${$(t)}]`, "received");
  }
  e.resetBtn.disabled = !1;
}
async function j(e, t) {
  const n = c(), a = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!(!e || r.sending)) {
    h(), r.sending = !0, C(!0), a && (n.inputEl.value = ""), b(e, "sent"), B();
    try {
      const o = await Q(e);
      y(), F(o), await J();
    } catch (o) {
      y(), b(`[Error: ${$(o)}]`, "received");
    }
    r.sending = !1, C(!1), n.inputEl.focus();
  }
}
async function Ie(e, t, n) {
  const a = await me(e, t, n);
  F(a);
}
async function X() {
  const e = c(), t = e.inputEl.value.trim(), n = r.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await j(t, { clearInput: !0 });
    return;
  }
  if (r.sending) return;
  h(), r.sending = !0, C(!0), e.inputEl.value = "";
  const a = Te();
  for (const [o, s] of a.entries()) {
    const i = o === 0 ? t : "";
    switch (s.type) {
      case "photo": {
        se(s.localUrl, "sent", i);
        break;
      }
      case "voice": {
        ae(s.localUrl, "sent", i);
        break;
      }
      case "video_note": {
        ie(s.localUrl, "sent", i);
        break;
      }
      default:
        oe(s.file.name, s.localUrl, "sent", i);
    }
    B();
    try {
      await Ie(s.file, s.type, i), y();
    } catch (d) {
      y(), b(`[Upload error: ${$(d)}]`, "received");
    }
  }
  r.sending = !1, C(!1), e.inputEl.focus(), await J();
}
function _e() {
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = c();
  $e(async (n) => {
    await j(n, { clearInput: !1 });
  }), he(async (n) => {
    await j(n, { clearInput: !1 });
  }), ke(), t.sendBtn.addEventListener("click", () => {
    X();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && X();
  }), t.resetBtn.addEventListener("click", () => {
    He();
  }), ce();
}
_e();
