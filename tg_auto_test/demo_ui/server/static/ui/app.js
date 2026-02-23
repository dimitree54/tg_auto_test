async function I(e) {
  return await e.json();
}
function D(e, t, n) {
  return new Error(`${e} ${t} failed: ${n.status} ${n.statusText}`);
}
async function le(e) {
  const t = await fetch(e, { method: "GET" });
  if (!t.ok) throw D("GET", e, t);
  return await I(t);
}
async function q(e, t) {
  const n = await fetch(e, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(t)
  });
  if (!n.ok) throw D("POST", e, n);
  return await I(n);
}
async function de(e) {
  const t = await fetch(e, { method: "POST" });
  if (!t.ok) throw D("POST", e, t);
  return await I(t);
}
async function ue(e, t) {
  const n = await fetch(e, { method: "POST", body: t });
  if (!n.ok) throw D("POST", e, n);
  return await I(n);
}
async function Q(e) {
  return await q("/api/message", { text: e });
}
async function me(e, t, n) {
  const s = new FormData();
  return s.append("file", e), n && s.append("caption", n), await ue(`/api/${t}`, s);
}
async function pe(e, t) {
  return await q("/api/callback", { message_id: e, data: t });
}
async function fe(e) {
  return await q("/api/invoice/pay", { message_id: e });
}
async function ge() {
  return await de("/api/reset");
}
async function ve() {
  return await le("/api/state");
}
const l = {
  sending: !1,
  stagedFiles: []
};
let H = null;
function v(e) {
  const t = document.getElementById(e);
  if (!t) throw new Error(`Missing element: #${e}`);
  return t;
}
function r() {
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
function k(e) {
  const t = r();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
const w = {
  botCommands: [],
  menuButtonType: "default"
};
let f = !1, C = "menu", y = [], g = -1, O = null;
function ye(e) {
  O = e;
  const t = r();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !l.sending && t.menuBtn.classList.contains("visible")) {
      if (f && C === "menu") {
        E(), A();
        return;
      }
      z();
    }
  }), t.inputEl.addEventListener("input", () => {
    A();
  }), t.inputEl.addEventListener("keydown", (n) => {
    if (f) {
      if (n.key === "Escape") {
        n.preventDefault(), E();
        return;
      }
      if (y.length > 0) {
        if (n.key === "ArrowDown") {
          n.preventDefault(), G(1);
          return;
        }
        if (n.key === "ArrowUp") {
          n.preventDefault(), G(-1);
          return;
        }
      }
      n.key === "Enter" && ee() && n.preventDefault();
    }
  }), document.addEventListener("click", (n) => {
    if (!f) return;
    const s = n.target;
    s instanceof Node && (t.commandPanelEl.contains(s) || t.menuBtn.contains(s) || t.inputEl.contains(s) || E());
  });
}
function E() {
  const e = r();
  f = !1, C = "menu", y = [], g = -1, e.commandPanelEl.classList.remove("visible"), e.commandPanelEl.innerHTML = "";
}
function z() {
  Y("menu", w.botCommands, "Commands");
}
function A() {
  if (f && C === "menu") return;
  const e = Ee();
  if (e === null || w.botCommands.length === 0) {
    f && C === "slash" && E();
    return;
  }
  const t = [];
  for (const n of w.botCommands)
    n.command && n.command.indexOf(e) === 0 && t.push(n);
  if (t.length === 0) {
    f && C === "slash" && E();
    return;
  }
  Y("slash", t, e ? `Commands matching "/${e}"` : "Commands");
}
function Ee() {
  const { inputEl: e } = r(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function Y(e, t, n) {
  const s = r();
  C = e, y = Array.isArray(t) ? t : [], g = y.length > 0 ? 0 : -1, f = !0, s.commandPanelEl.innerHTML = "";
  const o = document.createElement("div");
  o.className = "cp-card";
  const i = document.createElement("div");
  if (i.className = "cp-header", i.textContent = n, o.appendChild(i), y.length === 0) {
    const a = document.createElement("div");
    a.className = "cp-empty", a.textContent = "No commands.", o.appendChild(a);
  } else
    for (const [a, d] of y.entries()) {
      const u = document.createElement("button");
      u.type = "button", u.className = `cp-item${a === g ? " selected" : ""}`, u.dataset.index = String(a), u.addEventListener("click", () => {
        const m = Number.parseInt(u.dataset.index || "", 10);
        Number.isFinite(m) && (g = m, Z(), ee());
      });
      const c = document.createElement("div");
      if (c.className = "cp-cmd", c.textContent = `/${d.command || "?"}`, u.appendChild(c), d.description) {
        const m = document.createElement("div");
        m.className = "cp-desc", m.textContent = d.description, u.appendChild(m);
      }
      o.appendChild(u);
    }
  s.commandPanelEl.appendChild(o), s.commandPanelEl.classList.add("visible");
}
function Z() {
  const t = r().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, s] of t.entries())
    n === g ? s.classList.add("selected") : s.classList.remove("selected");
}
function G(e) {
  !f || y.length === 0 || (g = (g + e) % y.length, g < 0 && (g += y.length), Z());
}
function ee() {
  if (!f || g < 0 || g >= y.length) return !1;
  const t = y[g].command || "";
  if (!t) return !1;
  const { inputEl: n } = r();
  return C === "slash" ? (n.value = `/${t} `, E(), n.focus(), !0) : (E(), O && O(`/${t}`), !0);
}
function te() {
  const e = r();
  w.menuButtonType === "commands" && w.botCommands.length > 0 ? e.menuBtn.classList.add("visible") : (e.menuBtn.classList.remove("visible"), f && C === "menu" && E());
}
async function J() {
  try {
    const e = await ve();
    w.botCommands = Array.isArray(e.commands) ? e.commands : [], w.menuButtonType = e.menu_button_type || "default", te(), f && C === "menu" ? z() : f || A();
  } catch {
  }
}
function he() {
  w.botCommands = [], w.menuButtonType = "default", te(), E();
}
function be(e) {
  const t = e.type || "";
  return t.startsWith("image/") ? "photo" : t.startsWith("audio/") ? "voice" : t.startsWith("video/") ? "video_note" : "document";
}
function V(e) {
  const t = URL.createObjectURL(e);
  l.stagedFiles.push({ file: e, type: be(e), localUrl: t }), _();
}
function Ce(e) {
  const t = l.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), l.stagedFiles.splice(e, 1), _());
}
function Le() {
  for (const e of l.stagedFiles) URL.revokeObjectURL(e.localUrl);
  l.stagedFiles = [], _();
}
function we() {
  const e = [...l.stagedFiles];
  return l.stagedFiles = [], _(), e;
}
function _() {
  const e = r();
  if (e.stagedFilesEl.innerHTML = "", l.stagedFiles.length === 0) {
    e.stagedFilesEl.classList.remove("visible");
    return;
  }
  e.stagedFilesEl.classList.add("visible");
  for (let t = 0; t < l.stagedFiles.length; t++) {
    const n = l.stagedFiles[t], s = document.createElement("div");
    if (s.className = "staged-item", n.type === "photo") {
      const a = document.createElement("img");
      a.src = n.localUrl, a.alt = "Preview", s.appendChild(a);
    } else {
      const a = document.createElement("span");
      a.className = "staged-icon";
      const d = {
        voice: "&#127908;",
        video_note: "&#127909;"
      };
      a.innerHTML = d[n.type] ?? "&#128196;", s.appendChild(a);
    }
    const o = document.createElement("span");
    o.className = "staged-name", o.textContent = n.file.name, s.appendChild(o);
    const i = document.createElement("button");
    i.className = "staged-remove", i.innerHTML = "&times;", i.dataset.index = String(t), i.addEventListener("click", () => {
      const a = Number.parseInt(i.dataset.index || "", 10);
      Number.isFinite(a) && Ce(a);
    }), s.appendChild(i), e.stagedFilesEl.appendChild(s);
  }
}
function Te() {
  const e = r();
  e.attachBtn.addEventListener("click", () => {
    l.sending || e.fileInput.click();
  }), e.fileInput.addEventListener("change", () => {
    const t = e.fileInput.files;
    if (t && t.length > 0)
      for (let n = 0; n < t.length; n++) V(t[n]);
    e.fileInput.value = "", e.inputEl.focus();
  }), e.chatContainer.addEventListener("dragover", (t) => {
    t.preventDefault(), t.stopPropagation();
  }), e.chatContainer.addEventListener("drop", (t) => {
    var s;
    t.preventDefault(), t.stopPropagation();
    const n = (s = t.dataTransfer) == null ? void 0 : s.files;
    if (n && n.length > 0)
      for (let o = 0; o < n.length; o++) V(n[o]);
  });
}
function S(e) {
  return e instanceof Error ? e.message : String(e);
}
function M(e) {
  const t = document.createElement("div");
  return t.textContent = e, t.innerHTML;
}
function W() {
  const e = /* @__PURE__ */ new Date();
  return `${e.getHours().toString().padStart(2, "0")}:${e.getMinutes().toString().padStart(2, "0")}`;
}
function U(e) {
  if (!Number.isFinite(e) || e < 0) return "0:00";
  const t = Math.floor(e / 60), n = Math.floor(e % 60);
  return `${t}:${n < 10 ? "0" : ""}${n}`;
}
function B() {
  const e = r();
  e.typingEl.classList.add("visible"), e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function h() {
  r().typingEl.classList.remove("visible");
}
function ke(e, t, n, s, o) {
  const i = document.createElement("div");
  i.className = "inline-keyboard";
  for (const a of t) {
    const d = document.createElement("div");
    d.className = "ik-row";
    for (const u of a) {
      const c = document.createElement("button");
      c.className = "ik-btn", c.textContent = u.text || "?", c.dataset.callbackData = u.callback_data || "", c.dataset.messageId = String(n), c.addEventListener("click", async () => {
        const m = c.dataset.callbackData || "", p = Number.parseInt(c.dataset.messageId || "0", 10);
        if (!m || l.sending) return;
        const x = c.closest(".inline-keyboard"), b = x ? x.querySelectorAll(".ik-btn") : [];
        for (const T of b) T.disabled = !0;
        l.sending = !0, k(!0), B();
        try {
          const T = await pe(p, m);
          h(), s(T);
        } catch (T) {
          h(), o(`[Callback error: ${S(T)}]`);
        }
        l.sending = !1, k(!1), r().inputEl.focus();
      }), d.appendChild(c);
    }
    i.appendChild(d);
  }
  e.appendChild(i);
}
let K = null;
function $e(e) {
  K = e;
}
function Ne(e) {
  const t = r();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const s = document.createElement("div");
    s.className = "rk-row";
    for (const o of n) {
      const i = document.createElement("button");
      i.className = "rk-btn", i.textContent = o.text || "?", i.addEventListener("click", () => {
        const a = i.textContent || "";
        a && (l.sending || (ne(), K && K(a)));
      }), s.appendChild(i);
    }
    t.replyKeyboardEl.appendChild(s);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function ne() {
  const e = r();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}
function $() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function N(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, e === "received" && (t.innerHTML = '<div class="sender">Bot</div>'), t;
}
function F() {
  return `<span class="meta">${W()}</span>`;
}
function L(e, t) {
  const n = r(), s = N(t);
  s.innerHTML += `<span class="text">${M(e)}</span>${F()}`, n.messagesEl.appendChild(s), $();
}
function se(e, t, n) {
  const s = r(), o = N(t), i = document.createElement("img");
  i.className = "msg-photo", i.src = e, i.alt = "Photo", o.appendChild(i), n && (o.innerHTML += `<span class="caption">${M(n)}</span>`), o.innerHTML += F(), s.messagesEl.appendChild(o), i.addEventListener("load", () => $()), $();
}
function ae(e, t, n) {
  const s = r(), o = N(t), i = document.createElement("div");
  i.className = "voice-player";
  const a = document.createElement("audio");
  a.src = e, a.preload = "metadata";
  const d = document.createElement("button");
  d.className = "vp-play", d.innerHTML = "&#9654;";
  const u = document.createElement("div");
  u.className = "vp-track";
  const c = document.createElement("div");
  c.className = "vp-bar";
  const m = document.createElement("div");
  m.className = "vp-fill", c.appendChild(m);
  const p = document.createElement("span");
  if (p.className = "vp-time", p.textContent = "0:00", u.appendChild(c), u.appendChild(p), i.appendChild(d), i.appendChild(u), o.appendChild(i), n) {
    const b = document.createElement("span");
    b.className = "caption", b.textContent = n, o.appendChild(b);
  }
  const x = document.createElement("span");
  x.className = "meta", x.textContent = W(), o.appendChild(x), s.messagesEl.appendChild(o), a.addEventListener("loadedmetadata", () => {
    p.textContent = U(a.duration);
  }), d.addEventListener("click", () => {
    a.paused ? (a.play(), d.innerHTML = "&#9646;&#9646;") : (a.pause(), d.innerHTML = "&#9654;");
  }), a.addEventListener("timeupdate", () => {
    if (a.duration) {
      const b = a.currentTime / a.duration * 100;
      m.style.width = `${b}%`, p.textContent = U(a.currentTime);
    }
  }), a.addEventListener("ended", () => {
    d.innerHTML = "&#9654;", m.style.width = "0%", p.textContent = U(a.duration);
  }), c.addEventListener("click", (b) => {
    if (a.duration) {
      const T = c.getBoundingClientRect(), re = (b.clientX - T.left) / T.width;
      a.currentTime = re * a.duration;
    }
  }), $();
}
function ie(e, t, n) {
  const s = r(), o = N(t), i = document.createElement("video");
  i.className = "msg-video-note", i.src = e, i.controls = !0, i.playsInline = !0, o.appendChild(i), n && (o.innerHTML += `<span class="caption">${M(n)}</span>`), o.innerHTML += F(), s.messagesEl.appendChild(o), $();
}
function oe(e, t, n, s) {
  const o = r(), i = N(n), a = document.createElement("a");
  a.className = "doc-attachment", a.href = t ? `${t}?download=1` : "#", a.download = e || "", a.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${M(e)}</span>`, i.appendChild(a), s && (i.innerHTML += `<span class="caption">${M(s)}</span>`), i.innerHTML += F(), o.messagesEl.appendChild(i), $();
}
function R(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function xe(e, t) {
  const n = r(), s = N(t), o = document.createElement("div");
  o.className = "invoice-card";
  const i = document.createElement("div");
  if (i.className = "invoice-title", i.textContent = e.title || "Invoice", o.appendChild(i), e.description) {
    const p = document.createElement("div");
    p.className = "invoice-desc", p.textContent = e.description, o.appendChild(p);
  }
  const a = e.currency || "", d = e.total_amount ?? 0, u = document.createElement("div");
  u.className = "invoice-amount", u.textContent = R(a, d), o.appendChild(u);
  const c = document.createElement("button");
  c.className = "invoice-pay", c.textContent = `Pay ${R(a, d)}`, c.addEventListener("click", async () => {
    if (!l.sending) {
      l.sending = !0, k(!0), c.disabled = !0, c.textContent = "Paying...", B();
      try {
        const p = await fe(e.message_id);
        h(), c.textContent = "Paid", P(p);
      } catch (p) {
        h(), c.disabled = !1, c.textContent = `Pay ${R(a, d)}`, L(`[Payment error: ${S(p)}]`, "received");
      }
      l.sending = !1, k(!1), n.inputEl.focus();
    }
  }), o.appendChild(c), s.appendChild(o);
  const m = document.createElement("span");
  m.className = "meta", m.textContent = W(), s.appendChild(m), n.messagesEl.appendChild(s), $();
}
function P(e) {
  const t = r(), n = e.reply_markup || null;
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const s = N("received");
      s.innerHTML += `<span class="text">${M(e.text || "")}</span>${F()}`, t.messagesEl.appendChild(s), ke(
        s,
        n.inline_keyboard,
        e.message_id,
        P,
        (o) => L(o, "received")
      ), $();
    } else
      L(e.text || "", "received");
    n && n.keyboard && Ne(n.keyboard);
    return;
  }
  if (e.type === "invoice") {
    xe(e, "received");
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
  L(`[Unknown response type: ${e.type}]`, "received");
}
async function ce() {
  B();
  try {
    const e = await Q("/start");
    h(), P(e), await J();
  } catch (e) {
    h(), L(`[Error: ${S(e)}]`, "received");
  }
}
async function Me() {
  const e = r();
  e.resetBtn.disabled = !0;
  try {
    await ge(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div>', ne(), he(), Le(), await ce();
  } catch (t) {
    L(`[Reset failed: ${S(t)}]`, "received");
  }
  e.resetBtn.disabled = !1;
}
async function j(e, t) {
  const n = r(), s = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!(!e || l.sending)) {
    E(), l.sending = !0, k(!0), s && (n.inputEl.value = ""), L(e, "sent"), B();
    try {
      const o = await Q(e);
      h(), P(o), await J();
    } catch (o) {
      h(), L(`[Error: ${S(o)}]`, "received");
    }
    l.sending = !1, k(!1), n.inputEl.focus();
  }
}
async function Se(e, t, n) {
  const s = await me(e, t, n);
  P(s);
}
async function X() {
  const e = r(), t = e.inputEl.value.trim(), n = l.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await j(t, { clearInput: !0 });
    return;
  }
  if (l.sending) return;
  E(), l.sending = !0, k(!0), e.inputEl.value = "";
  const s = we();
  for (const [o, i] of s.entries()) {
    const a = o === 0 ? t : "";
    switch (i.type) {
      case "photo": {
        se(i.localUrl, "sent", a);
        break;
      }
      case "voice": {
        ae(i.localUrl, "sent", a);
        break;
      }
      case "video_note": {
        ie(i.localUrl, "sent", a);
        break;
      }
      default:
        oe(i.file.name, i.localUrl, "sent", a);
    }
    B();
    try {
      await Se(i.file, i.type, a), h();
    } catch (d) {
      h(), L(`[Upload error: ${S(d)}]`, "received");
    }
  }
  l.sending = !1, k(!1), e.inputEl.focus(), await J();
}
function Be() {
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = r();
  $e(async (n) => {
    await j(n, { clearInput: !1 });
  }), ye(async (n) => {
    await j(n, { clearInput: !1 });
  }), Te(), t.sendBtn.addEventListener("click", () => {
    X();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && X();
  }), t.resetBtn.addEventListener("click", () => {
    Me();
  }), ce();
}
Be();
