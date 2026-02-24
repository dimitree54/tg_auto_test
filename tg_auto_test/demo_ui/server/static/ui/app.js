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
  const s = new FormData();
  return s.append("file", e), n && s.append("caption", n), await ue(`/api/${t}`, s);
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
  return await U("/api/poll/vote", { poll_id: e, option_ids: t });
}
const d = {
  sending: !1,
  stagedFiles: []
};
let F = null;
function v(e) {
  const t = document.getElementById(e);
  if (!t) throw new Error(`Missing element: #${e}`);
  return t;
}
function l() {
  if (F) return F;
  const e = document.querySelector(".chat-container");
  if (!e) throw new Error("Missing element: .chat-container");
  return F = {
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
  }, F;
}
function C(e) {
  const t = l();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
const T = {
  botCommands: [],
  menuButtonType: "default"
};
let f = !1, w = "menu", E = [], g = -1, A = null;
function he(e) {
  A = e;
  const t = l();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !d.sending && t.menuBtn.classList.contains("visible")) {
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
    const s = n.target;
    s instanceof Node && (t.commandPanelEl.contains(s) || t.menuBtn.contains(s) || t.inputEl.contains(s) || h());
  });
}
function h() {
  const e = l();
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
  const { inputEl: e } = l(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function Y(e, t, n) {
  const s = l();
  w = e, E = Array.isArray(t) ? t : [], g = E.length > 0 ? 0 : -1, f = !0, s.commandPanelEl.innerHTML = "";
  const i = document.createElement("div");
  i.className = "cp-card";
  const o = document.createElement("div");
  if (o.className = "cp-header", o.textContent = n, i.appendChild(o), E.length === 0) {
    const a = document.createElement("div");
    a.className = "cp-empty", a.textContent = "No commands.", i.appendChild(a);
  } else
    for (const [a, r] of E.entries()) {
      const u = document.createElement("button");
      u.type = "button", u.className = `cp-item${a === g ? " selected" : ""}`, u.dataset.index = String(a), u.addEventListener("click", () => {
        const m = Number.parseInt(u.dataset.index || "", 10);
        Number.isFinite(m) && (g = m, Z(), ee());
      });
      const c = document.createElement("div");
      if (c.className = "cp-cmd", c.textContent = `/${r.command || "?"}`, u.appendChild(c), r.description) {
        const m = document.createElement("div");
        m.className = "cp-desc", m.textContent = r.description, u.appendChild(m);
      }
      i.appendChild(u);
    }
  s.commandPanelEl.appendChild(i), s.commandPanelEl.classList.add("visible");
}
function Z() {
  const t = l().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, s] of t.entries())
    n === g ? s.classList.add("selected") : s.classList.remove("selected");
}
function V(e) {
  !f || E.length === 0 || (g = (g + e) % E.length, g < 0 && (g += E.length), Z());
}
function ee() {
  if (!f || g < 0 || g >= E.length) return !1;
  const t = E[g].command || "";
  if (!t) return !1;
  const { inputEl: n } = l();
  return w === "slash" ? (n.value = `/${t} `, h(), n.focus(), !0) : (h(), A && A(`/${t}`), !0);
}
function te() {
  const e = l();
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
  d.stagedFiles.push({ file: e, type: Ce(e), localUrl: t }), R();
}
function Le(e) {
  const t = d.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), d.stagedFiles.splice(e, 1), R());
}
function we() {
  for (const e of d.stagedFiles) URL.revokeObjectURL(e.localUrl);
  d.stagedFiles = [], R();
}
function Te() {
  const e = [...d.stagedFiles];
  return d.stagedFiles = [], R(), e;
}
function R() {
  const e = l();
  if (e.stagedFilesEl.innerHTML = "", d.stagedFiles.length === 0) {
    e.stagedFilesEl.classList.remove("visible");
    return;
  }
  e.stagedFilesEl.classList.add("visible");
  for (let t = 0; t < d.stagedFiles.length; t++) {
    const n = d.stagedFiles[t], s = document.createElement("div");
    if (s.className = "staged-item", n.type === "photo") {
      const a = document.createElement("img");
      a.src = n.localUrl, a.alt = "Preview", s.appendChild(a);
    } else {
      const a = document.createElement("span");
      a.className = "staged-icon";
      const r = {
        voice: "&#127908;",
        video_note: "&#127909;"
      };
      a.innerHTML = r[n.type] ?? "&#128196;", s.appendChild(a);
    }
    const i = document.createElement("span");
    i.className = "staged-name", i.textContent = n.file.name, s.appendChild(i);
    const o = document.createElement("button");
    o.className = "staged-remove", o.innerHTML = "&times;", o.dataset.index = String(t), o.addEventListener("click", () => {
      const a = Number.parseInt(o.dataset.index || "", 10);
      Number.isFinite(a) && Le(a);
    }), s.appendChild(o), e.stagedFilesEl.appendChild(s);
  }
}
function ke() {
  const e = l();
  e.attachBtn.addEventListener("click", () => {
    d.sending || e.fileInput.click();
  }), e.fileInput.addEventListener("change", () => {
    const t = e.fileInput.files;
    if (t && t.length > 0)
      for (let n = 0; n < t.length; n++) G(t[n]);
    e.fileInput.value = "", e.inputEl.focus();
  }), e.chatContainer.addEventListener("dragover", (t) => {
    t.preventDefault(), t.stopPropagation();
  }), e.chatContainer.addEventListener("drop", (t) => {
    var s;
    t.preventDefault(), t.stopPropagation();
    const n = (s = t.dataTransfer) == null ? void 0 : s.files;
    if (n && n.length > 0)
      for (let i = 0; i < n.length; i++) G(n[i]);
  });
}
function N(e) {
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
  const e = l();
  e.typingEl.classList.add("visible"), e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function y() {
  l().typingEl.classList.remove("visible");
}
function $e(e, t, n, s, i) {
  const o = document.createElement("div");
  o.className = "inline-keyboard";
  for (const a of t) {
    const r = document.createElement("div");
    r.className = "ik-row";
    for (const u of a) {
      const c = document.createElement("button");
      c.className = "ik-btn", c.textContent = u.text || "?", c.dataset.callbackData = u.callback_data || "", c.dataset.messageId = String(n), c.addEventListener("click", async () => {
        const m = c.dataset.callbackData || "", p = Number.parseInt(c.dataset.messageId || "0", 10);
        if (!m || d.sending) return;
        const M = c.closest(".inline-keyboard"), L = M ? M.querySelectorAll(".ik-btn") : [];
        for (const k of L) k.disabled = !0;
        d.sending = !0, C(!0), B();
        try {
          const k = await pe(p, m);
          y(), s(k);
        } catch (k) {
          y(), i(`[Callback error: ${N(k)}]`);
        }
        d.sending = !1, C(!1), l().inputEl.focus();
      }), r.appendChild(c);
    }
    o.appendChild(r);
  }
  e.appendChild(o);
}
let q = null;
function Ne(e) {
  q = e;
}
function xe(e) {
  const t = l();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const s = document.createElement("div");
    s.className = "rk-row";
    for (const i of n) {
      const o = document.createElement("button");
      o.className = "rk-btn", o.textContent = i.text || "?", o.addEventListener("click", () => {
        const a = o.textContent || "";
        a && (d.sending || (ne(), q && q(a)));
      }), s.appendChild(o);
    }
    t.replyKeyboardEl.appendChild(s);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function ne() {
  const e = l();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}

function Se() {
  const e = l();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function Be(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, t.innerHTML = '<div class="sender">Bot</div>', t;
}
function Pe(e, t) {
  const n = l(), s = Be(t);
  if (e.poll_question) {
    const i = document.createElement("h4");
    i.className = "poll-question", i.textContent = e.poll_question, s.appendChild(i);
  }
  if (e.poll_options && e.poll_id) {
    const i = document.createElement("div");
    i.className = "poll-options", e.poll_options.forEach((o, a) => {
      const r = document.createElement("button");
      r.className = "poll-option-btn", r.textContent = o.text, r.onclick = () => He(e.poll_id, [a]), i.appendChild(r);
    }), s.appendChild(i);
  }
  s.insertAdjacentHTML("beforeend", P()), n.messagesEl.appendChild(s), Se();
}
async function He(e, t) {
  l();
  try {
    C(!0), B();
    const n = await Ee(e, t);
    n.text && b(n.text, "received");
  } catch (n) {
    N(`Poll vote failed: ${String(n)}`);
  } finally {
    y(), C(!1);
  }
}
function $() {
  const e = l();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function x(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, e === "received" && (t.innerHTML = '<div class="sender">Bot</div>'), t;
}
function P() {
  return `<span class="meta">${W()}</span>`;
}
function b(e, t) {
  const n = l(), s = x(t);
  s.innerHTML += `<span class="text">${S(e)}</span>${P()}`, n.messagesEl.appendChild(s), $();
}
function se(e, t, n) {
  const s = l(), i = x(t), o = document.createElement("img");
  o.className = "msg-photo", o.src = e, o.alt = "Photo", i.appendChild(o), n && i.insertAdjacentHTML("beforeend", `<span class="caption">${S(n)}</span>`), i.insertAdjacentHTML("beforeend", P()), s.messagesEl.appendChild(i), o.addEventListener("load", () => $()), $();
}
function ae(e, t, n) {
  const s = l(), i = x(t), o = document.createElement("div");
  o.className = "voice-player";
  const a = document.createElement("audio");
  a.src = e, a.preload = "metadata";
  const r = document.createElement("button");
  r.className = "vp-play", r.innerHTML = "&#9654;";
  const u = document.createElement("div");
  u.className = "vp-track";
  const c = document.createElement("div");
  c.className = "vp-bar";
  const m = document.createElement("div");
  m.className = "vp-fill", c.appendChild(m);
  const p = document.createElement("span");
  if (p.className = "vp-time", p.textContent = "0:00", u.appendChild(c), u.appendChild(p), o.appendChild(r), o.appendChild(u), i.appendChild(o), n) {
    const L = document.createElement("span");
    L.className = "caption", L.textContent = n, i.appendChild(L);
  }
  const M = document.createElement("span");
  M.className = "meta", M.textContent = W(), i.appendChild(M), s.messagesEl.appendChild(i), a.addEventListener("loadedmetadata", () => {
    p.textContent = I(a.duration);
  }), r.addEventListener("click", () => {
    a.paused ? (a.play(), r.innerHTML = "&#9646;&#9646;") : (a.pause(), r.innerHTML = "&#9654;");
  }), a.addEventListener("timeupdate", () => {
    if (a.duration) {
      const L = a.currentTime / a.duration * 100;
      m.style.width = `${L}%`, p.textContent = I(a.currentTime);
    }
  }), a.addEventListener("ended", () => {
    r.innerHTML = "&#9654;", m.style.width = "0%", p.textContent = I(a.duration);
  }), c.addEventListener("click", (L) => {
    if (a.duration) {
      const k = c.getBoundingClientRect(), ce = (L.clientX - k.left) / k.width;
      a.currentTime = ce * a.duration;
    }
  }), $();
}
function ie(e, t, n) {
  const s = l(), i = x(t), o = document.createElement("video");
  o.className = "msg-video-note", o.src = e, o.controls = !0, o.playsInline = !0, i.appendChild(o), n && (i.innerHTML += `<span class="caption">${S(n)}</span>`), i.innerHTML += P(), s.messagesEl.appendChild(i), $();
}
function oe(e, t, n, s) {
  const i = l(), o = x(n), a = document.createElement("a");
  a.className = "doc-attachment", a.href = t ? `${t}?download=1` : "#", a.download = e || "", a.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${S(e)}</span>`, o.appendChild(a), s && (o.innerHTML += `<span class="caption">${S(s)}</span>`), o.innerHTML += P(), i.messagesEl.appendChild(o), $();
}
function O(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function Fe(e, t) {
  const n = l(), s = x(t), i = document.createElement("div");
  i.className = "invoice-card";
  const o = document.createElement("div");
  if (o.className = "invoice-title", o.textContent = e.title || "Invoice", i.appendChild(o), e.description) {
    const p = document.createElement("div");
    p.className = "invoice-desc", p.textContent = e.description, i.appendChild(p);
  }
  const a = e.currency || "", r = e.total_amount ?? 0, u = document.createElement("div");
  u.className = "invoice-amount", u.textContent = O(a, r), i.appendChild(u);
  const c = document.createElement("button");
  c.className = "invoice-pay", c.textContent = `Pay ${O(a, r)}`, c.addEventListener("click", async () => {
    if (!d.sending) {
      d.sending = !0, C(!0), c.disabled = !0, c.textContent = "Paying...", B();
      try {
        const p = await fe(e.message_id);
        y(), c.textContent = "Paid", H(p);
      } catch (p) {
        y(), c.disabled = !1, c.textContent = `Pay ${O(a, r)}`, b(`[Payment error: ${N(p)}]`, "received");
      }
      d.sending = !1, C(!1), n.inputEl.focus();
    }
  }), i.appendChild(c), s.appendChild(i);
  const m = document.createElement("span");
  m.className = "meta", m.textContent = W(), s.appendChild(m), n.messagesEl.appendChild(s), $();
}
function H(e) {
  const t = l(), n = e.reply_markup || null;
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const s = x("received");
      s.innerHTML += `<span class="text">${S(e.text || "")}</span>${P()}`, t.messagesEl.appendChild(s), $e(
        s,
        n.inline_keyboard,
        e.message_id,
        H,
        (i) => b(i, "received")
      ), $();
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
    Pe(e, "received");
    return;
  }
  b(`[Unknown response type: ${e.type}]`, "received");
}
async function le() {
  B();
  try {
    const e = await Q("/start");
    y(), H(e), await J();
  } catch (e) {
    y(), b(`[Error: ${N(e)}]`, "received");
  }
}
async function Ie() {
  const e = l();
  e.resetBtn.disabled = !0;
  try {
    await ge(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div>', ne(), be(), we(), await le();
  } catch (t) {
    b(`[Reset failed: ${N(t)}]`, "received");
  }
  e.resetBtn.disabled = !1;
}
async function j(e, t) {
  const n = l(), s = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!(!e || d.sending)) {
    h(), d.sending = !0, C(!0), s && (n.inputEl.value = ""), b(e, "sent"), B();
    try {
      const i = await Q(e);
      y(), H(i), await J();
    } catch (i) {
      y(), b(`[Error: ${N(i)}]`, "received");
    }
    d.sending = !1, C(!1), n.inputEl.focus();
  }
}
async function _e(e, t, n) {
  const s = await me(e, t, n);
  H(s);
}
async function X() {
  const e = l(), t = e.inputEl.value.trim(), n = d.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await j(t, { clearInput: !0 });
    return;
  }
  if (d.sending) return;
  h(), d.sending = !0, C(!0), e.inputEl.value = "";
  const s = Te();
  for (const [i, o] of s.entries()) {
    const a = i === 0 ? t : "";
    switch (o.type) {
      case "photo": {
        se(o.localUrl, "sent", a);
        break;
      }
      case "voice": {
        ae(o.localUrl, "sent", a);
        break;
      }
      case "video_note": {
        ie(o.localUrl, "sent", a);
        break;
      }
      default:
        oe(o.file.name, o.localUrl, "sent", a);
    }
    B();
    try {
      await _e(o.file, o.type, a), y();
    } catch (r) {
      y(), b(`[Upload error: ${N(r)}]`, "received");
    }
  }
  d.sending = !1, C(!1), e.inputEl.focus(), await J();
}
function De() {
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = l();
  Ne(async (n) => {
    await j(n, { clearInput: !1 });
  }), he(async (n) => {
    await j(n, { clearInput: !1 });
  }), ke(), t.sendBtn.addEventListener("click", () => {
    X();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && X();
  }), t.resetBtn.addEventListener("click", () => {
    Ie();
  }), le();
}
De();
