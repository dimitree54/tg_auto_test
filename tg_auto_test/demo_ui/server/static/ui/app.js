async function U(e) {
  return await e.json();
}
async function A(e, t, n) {
  try {
    const s = await n.json();
    if (s.detail)
      return new Error(s.detail);
  } catch {
  }
  return new Error(`${e} ${t} failed: ${n.status} ${n.statusText}`);
}
async function pe(e) {
  const t = await fetch(e, { method: "GET" });
  if (!t.ok) throw await A("GET", e, t);
  return await U(t);
}
async function O(e, t) {
  const n = await fetch(e, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(t)
  });
  if (!n.ok) throw await A("POST", e, n);
  return await U(n);
}
async function fe(e) {
  const t = await fetch(e, { method: "POST" });
  if (!t.ok) throw await A("POST", e, t);
  return await U(t);
}
async function ge(e, t) {
  const n = await fetch(e, { method: "POST", body: t });
  if (!n.ok) throw await A("POST", e, n);
  return await U(n);
}
async function Y(e) {
  return await O("/api/message", { text: e });
}
async function he(e, t, n) {
  const s = new FormData();
  return s.append("file", e), n && s.append("caption", n), await ge(`/api/${t}`, s);
}
async function ve(e, t) {
  return await O("/api/callback", { message_id: e, data: t });
}
async function ye(e) {
  return await O("/api/invoice/pay", { message_id: e });
}
async function Ee() {
  return await fe("/api/reset");
}
async function be() {
  return await pe("/api/state");
}
async function Ce(e, t) {
  return await O("/api/poll/vote", { message_id: e, option_ids: t });
}
const u = {
  sending: !1,
  stagedFiles: []
};
let I = null;
function g(e) {
  const t = document.getElementById(e);
  if (!t) throw new Error(`Missing element: #${e}`);
  return t;
}
function r() {
  if (I) return I;
  const e = document.querySelector(".chat-container");
  if (!e) throw new Error("Missing element: .chat-container");
  const t = document.querySelector(".chat-input");
  if (!t) throw new Error("Missing element: .chat-input");
  return I = {
    messagesEl: g("messages"),
    inputEl: g("msgInput"),
    sendBtn: g("sendBtn"),
    resetBtn: g("resetBtn"),
    typingEl: g("typing"),
    attachBtn: g("attachBtn"),
    fileInput: g("fileInput"),
    stagedFilesEl: g("stagedFiles"),
    replyKeyboardEl: g("replyKeyboard"),
    menuBtn: g("menuBtn"),
    commandPanelEl: g("commandPanel"),
    chatContainer: e,
    emptyPlaceholder: g("emptyPlaceholder"),
    startContainer: g("startContainer"),
    startBtn: g("startBtn"),
    chatInputEl: t
  }, I;
}
function w(e) {
  const t = r();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
function Le() {
  I = null;
}
function ee() {
  const e = r();
  e.emptyPlaceholder.style.display = "", e.startContainer.style.display = "", e.chatInputEl.style.display = "none";
}
function we() {
  const e = r();
  e.emptyPlaceholder.style.display = "none", e.startContainer.style.display = "none", e.chatInputEl.style.display = "flex";
}
const $ = {
  botCommands: [],
  menuButtonType: "default"
};
let v = !1, T = "menu", b = [], y = -1, W = null;
function ke(e) {
  W = e;
  const t = r();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !u.sending && t.menuBtn.classList.contains("visible")) {
      if (v && T === "menu") {
        C(), V();
        return;
      }
      te();
    }
  }), t.inputEl.addEventListener("input", () => {
    V();
  }), t.inputEl.addEventListener("keydown", (n) => {
    if (v) {
      if (n.key === "Escape") {
        n.preventDefault(), C();
        return;
      }
      if (b.length > 0) {
        if (n.key === "ArrowDown") {
          n.preventDefault(), z(1);
          return;
        }
        if (n.key === "ArrowUp") {
          n.preventDefault(), z(-1);
          return;
        }
      }
      n.key === "Enter" && ae() && n.preventDefault();
    }
  }), document.addEventListener("click", (n) => {
    if (!v) return;
    const s = n.target;
    s instanceof Node && (t.commandPanelEl.contains(s) || t.menuBtn.contains(s) || t.inputEl.contains(s) || C());
  });
}
function C() {
  const e = r();
  v = !1, T = "menu", b = [], y = -1, e.commandPanelEl.classList.remove("visible"), e.commandPanelEl.innerHTML = "";
}
function te() {
  ne("menu", $.botCommands, "Commands");
}
function V() {
  if (v && T === "menu") return;
  const e = Te();
  if (e === null || $.botCommands.length === 0) {
    v && T === "slash" && C();
    return;
  }
  const t = [];
  for (const n of $.botCommands)
    n.command && n.command.indexOf(e) === 0 && t.push(n);
  if (t.length === 0) {
    v && T === "slash" && C();
    return;
  }
  ne("slash", t, e ? `Commands matching "/${e}"` : "Commands");
}
function Te() {
  const { inputEl: e } = r(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function ne(e, t, n) {
  const s = r();
  T = e, b = Array.isArray(t) ? t : [], y = b.length > 0 ? 0 : -1, v = !0, s.commandPanelEl.innerHTML = "";
  const o = document.createElement("div");
  o.className = "cp-card";
  const a = document.createElement("div");
  if (a.className = "cp-header", a.textContent = n, o.appendChild(a), b.length === 0) {
    const i = document.createElement("div");
    i.className = "cp-empty", i.textContent = "No commands.", o.appendChild(i);
  } else
    for (const [i, l] of b.entries()) {
      const c = document.createElement("button");
      c.type = "button", c.className = `cp-item${i === y ? " selected" : ""}`, c.dataset.index = String(i), c.addEventListener("click", () => {
        const m = Number.parseInt(c.dataset.index || "", 10);
        Number.isFinite(m) && (y = m, se(), ae());
      });
      const d = document.createElement("div");
      if (d.className = "cp-cmd", d.textContent = `/${l.command || "?"}`, c.appendChild(d), l.description) {
        const m = document.createElement("div");
        m.className = "cp-desc", m.textContent = l.description, c.appendChild(m);
      }
      o.appendChild(c);
    }
  s.commandPanelEl.appendChild(o), s.commandPanelEl.classList.add("visible");
}
function se() {
  const t = r().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, s] of t.entries())
    n === y ? s.classList.add("selected") : s.classList.remove("selected");
}
function z(e) {
  !v || b.length === 0 || (y = (y + e) % b.length, y < 0 && (y += b.length), se());
}
function ae() {
  if (!v || y < 0 || y >= b.length) return !1;
  const t = b[y].command || "";
  if (!t) return !1;
  const { inputEl: n } = r();
  return T === "slash" ? (n.value = `/${t} `, C(), n.focus(), !0) : (C(), W && W(`/${t}`), !0);
}
function ie() {
  const e = r();
  $.menuButtonType === "commands" && $.botCommands.length > 0 ? e.menuBtn.classList.add("visible") : (e.menuBtn.classList.remove("visible"), v && T === "menu" && C());
}
async function X() {
  try {
    const e = await be();
    $.botCommands = Array.isArray(e.commands) ? e.commands : [], $.menuButtonType = e.menu_button_type || "default", ie(), v && T === "menu" ? te() : v || V();
  } catch {
  }
}
function $e() {
  $.botCommands = [], $.menuButtonType = "default", ie(), C();
}
function xe(e) {
  const t = e.type || "";
  return t.startsWith("image/") ? "photo" : t.startsWith("audio/") ? "voice" : t.startsWith("video/") ? "video_note" : "document";
}
function Q(e) {
  const t = URL.createObjectURL(e);
  u.stagedFiles.push({ file: e, type: xe(e), localUrl: t }), R();
}
function Me(e) {
  const t = u.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), u.stagedFiles.splice(e, 1), R());
}
function Ne() {
  for (const e of u.stagedFiles) URL.revokeObjectURL(e.localUrl);
  u.stagedFiles = [], R();
}
function Be() {
  const e = [...u.stagedFiles];
  return u.stagedFiles = [], R(), e;
}
function R() {
  const e = r();
  if (e.stagedFilesEl.innerHTML = "", u.stagedFiles.length === 0) {
    e.stagedFilesEl.classList.remove("visible");
    return;
  }
  e.stagedFilesEl.classList.add("visible");
  for (let t = 0; t < u.stagedFiles.length; t++) {
    const n = u.stagedFiles[t], s = document.createElement("div");
    if (s.className = "staged-item", n.type === "photo") {
      const i = document.createElement("img");
      i.src = n.localUrl, i.alt = "Preview", s.appendChild(i);
    } else {
      const i = document.createElement("span");
      i.className = "staged-icon";
      const l = {
        voice: "&#127908;",
        video_note: "&#127909;"
      };
      i.innerHTML = l[n.type] ?? "&#128196;", s.appendChild(i);
    }
    const o = document.createElement("span");
    o.className = "staged-name", o.textContent = n.file.name, s.appendChild(o);
    const a = document.createElement("button");
    a.className = "staged-remove", a.innerHTML = "&times;", a.dataset.index = String(t), a.addEventListener("click", () => {
      const i = Number.parseInt(a.dataset.index || "", 10);
      Number.isFinite(i) && Me(i);
    }), s.appendChild(a), e.stagedFilesEl.appendChild(s);
  }
}
function Se() {
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
      for (let o = 0; o < n.length; o++) Q(n[o]);
  });
}
function M(e) {
  return e instanceof Error ? e.message : String(e);
}
function p(e) {
  const t = document.createElement("div");
  return t.textContent = e, t.innerHTML;
}
function K(e) {
  const t = /\/([a-zA-Z0-9_]{1,32})(?=\s|$)/g;
  let n = "", s = 0, o;
  for (; (o = t.exec(e)) !== null; )
    n += p(e.slice(s, o.index)), n += `<span class="tg-command" data-command="${p(o[0])}">${p(o[0])}</span>`, s = o.index + o[0].length;
  return n += p(e.slice(s)), n;
}
function Pe(e) {
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
      return e.language ? `<pre><code class="language-${p(e.language)}">` : "<pre>";
    case "url":
      return "";
    case "text_url":
      return `<a href="${p(e.url ?? "")}" target="_blank" rel="noopener">`;
    case "spoiler":
      return '<span class="tg-spoiler">';
    default:
      return "";
  }
}
function _e(e) {
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
function N(e, t) {
  if (t.length === 0) return K(e);
  const n = [...t].sort(
    (a, i) => a.offset !== i.offset ? a.offset - i.offset : i.length - a.length
  );
  let s = "", o = 0;
  for (const a of n) {
    const i = Math.max(0, Math.min(a.offset, e.length)), l = Math.max(i, Math.min(a.offset + a.length, e.length));
    if (i > o && (s += K(e.slice(o, i))), l > i) {
      const c = e.slice(i, l);
      a.type === "url" ? s += `<a href="${p(c)}" target="_blank" rel="noopener">${p(c)}</a>` : s += Pe(a) + p(c) + _e(a), o = l;
    }
  }
  return o < e.length && (s += K(e.slice(o))), s;
}
function q() {
  const e = /* @__PURE__ */ new Date();
  return `${e.getHours().toString().padStart(2, "0")}:${e.getMinutes().toString().padStart(2, "0")}`;
}
function j(e) {
  if (!Number.isFinite(e) || e < 0) return "0:00";
  const t = Math.floor(e / 60), n = Math.floor(e % 60);
  return `${t}:${n < 10 ? "0" : ""}${n}`;
}
function S() {
  const e = r();
  e.typingEl.classList.add("visible"), e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function L() {
  r().typingEl.classList.remove("visible");
}
function oe(e, t, n, s, o) {
  const a = document.createElement("div");
  a.className = "inline-keyboard";
  for (const i of t) {
    const l = document.createElement("div");
    l.className = "ik-row";
    for (const c of i) {
      const d = document.createElement("button");
      d.className = "ik-btn", d.textContent = c.text || "?", d.dataset.callbackData = c.callback_data || "", d.dataset.messageId = String(n), d.addEventListener("click", async () => {
        const m = d.dataset.callbackData || "", f = Number.parseInt(d.dataset.messageId || "0", 10);
        if (!m || u.sending) return;
        const k = d.closest(".inline-keyboard"), H = k ? k.querySelectorAll(".ik-btn") : [];
        for (const h of H) h.disabled = !0;
        u.sending = !0, w(!0), S();
        try {
          const h = await ve(f, m);
          L(), s(h);
        } catch (h) {
          L(), o(`[Callback error: ${M(h)}]`);
        }
        u.sending = !1, w(!1), r().inputEl.focus();
      }), l.appendChild(d);
    }
    a.appendChild(l);
  }
  e.appendChild(a);
}
let G = null;
function He(e) {
  G = e;
}
function Ie(e) {
  const t = r();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const s = document.createElement("div");
    s.className = "rk-row";
    for (const o of n) {
      const a = document.createElement("button");
      a.className = "rk-btn", a.textContent = o.text || "?", a.addEventListener("click", () => {
        const i = a.textContent || "";
        i && (u.sending || (le(), G && G(i)));
      }), s.appendChild(a);
    }
    t.replyKeyboardEl.appendChild(s);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function le() {
  const e = r();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}
function x() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function B(e, t) {
  const n = document.createElement("div");
  return n.className = `message ${e}`, e === "received" && (n.innerHTML = '<div class="sender">Bot</div>'), t !== void 0 && (n.dataset.messageId = String(t)), n;
}
function Fe(e) {
  return r().messagesEl.querySelector(
    `.message[data-message-id="${e}"]`
  );
}
function P() {
  return `<span class="meta">${q()}</span>`;
}
function ce(e, t, n, s) {
  const o = r(), a = B(t), i = document.createElement("img");
  if (i.className = "msg-photo", i.src = e, i.alt = "Photo", a.appendChild(i), n) {
    const l = t === "received" && (s != null && s.length) ? N(n, s) : p(n);
    a.innerHTML += `<span class="caption">${l}</span>`;
  }
  a.innerHTML += P(), o.messagesEl.appendChild(a), i.addEventListener("load", () => x()), x();
}
function re(e, t, n, s) {
  const o = r(), a = B(t), i = document.createElement("div");
  i.className = "voice-player";
  const l = document.createElement("audio");
  l.src = e, l.preload = "metadata";
  const c = document.createElement("button");
  c.className = "vp-play", c.innerHTML = "&#9654;";
  const d = document.createElement("div");
  d.className = "vp-track";
  const m = document.createElement("div");
  m.className = "vp-bar";
  const f = document.createElement("div");
  f.className = "vp-fill", m.appendChild(f);
  const k = document.createElement("span");
  if (k.className = "vp-time", k.textContent = "0:00", d.appendChild(m), d.appendChild(k), i.appendChild(c), i.appendChild(d), a.appendChild(i), n) {
    const h = document.createElement("span");
    h.className = "caption";
    const F = t === "received" && (s != null && s.length) ? N(n, s) : p(n);
    h.innerHTML = F, a.appendChild(h);
  }
  const H = document.createElement("span");
  H.className = "meta", H.textContent = q(), a.appendChild(H), o.messagesEl.appendChild(a), l.addEventListener("loadedmetadata", () => {
    k.textContent = j(l.duration);
  }), c.addEventListener("click", () => {
    l.paused ? (l.play(), c.innerHTML = "&#9646;&#9646;") : (l.pause(), c.innerHTML = "&#9654;");
  }), l.addEventListener("timeupdate", () => {
    if (l.duration) {
      const h = l.currentTime / l.duration * 100;
      f.style.width = `${h}%`, k.textContent = j(l.currentTime);
    }
  }), l.addEventListener("ended", () => {
    c.innerHTML = "&#9654;", f.style.width = "0%", k.textContent = j(l.duration);
  }), m.addEventListener("click", (h) => {
    if (l.duration) {
      const F = m.getBoundingClientRect(), me = (h.clientX - F.left) / F.width;
      l.currentTime = me * l.duration;
    }
  }), x();
}
function de(e, t, n, s) {
  const o = r(), a = B(t), i = document.createElement("video");
  if (i.className = "msg-video-note", i.src = e, i.controls = !0, i.playsInline = !0, a.appendChild(i), n) {
    const l = t === "received" && (s != null && s.length) ? N(n, s) : p(n);
    a.innerHTML += `<span class="caption">${l}</span>`;
  }
  a.innerHTML += P(), o.messagesEl.appendChild(a), x();
}
function ue(e, t, n, s, o) {
  const a = r(), i = B(n), l = document.createElement("a");
  if (l.className = "doc-attachment", l.href = t ? `${t}?download=1` : "#", l.download = e || "", l.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${p(e)}</span>`, i.appendChild(l), s) {
    const c = n === "received" && (o != null && o.length) ? N(s, o) : p(s);
    i.innerHTML += `<span class="caption">${c}</span>`;
  }
  i.innerHTML += P(), a.messagesEl.appendChild(i), x();
}
function De() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function Ue(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, t.innerHTML = '<div class="sender">Bot</div>', t;
}
function Ae(e, t) {
  const n = r(), s = Ue(t);
  if (e.poll_question) {
    const a = document.createElement("h4");
    a.className = "poll-question", a.textContent = e.poll_question, s.appendChild(a);
  }
  if (e.poll_options && e.message_id) {
    const a = document.createElement("div");
    a.className = "poll-options", e.poll_options.forEach((i, l) => {
      const c = document.createElement("button");
      c.className = "poll-option-btn", c.textContent = i.text, c.onclick = () => Oe(e.message_id, [l]), a.appendChild(c);
    }), s.appendChild(a);
  }
  const o = document.createElement("span");
  o.className = "meta", o.textContent = q(), s.appendChild(o), n.messagesEl.appendChild(s), De();
}
async function Oe(e, t) {
  try {
    w(!0), S();
    const n = await Ce(e, t);
    n.text && E(n.text, "received");
  } catch (n) {
    M(`Poll vote failed: ${String(n)}`);
  } finally {
    L(), w(!1);
  }
}
function E(e, t, n, s) {
  const o = r(), a = B(t, s), i = t === "received" && (n != null && n.length) ? N(e, n) : p(e);
  a.innerHTML += `<span class="text">${i}</span>${P()}`, o.messagesEl.appendChild(a), x();
}
function J(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function Re(e, t) {
  const n = r(), s = B(t), o = document.createElement("div");
  o.className = "invoice-card";
  const a = document.createElement("div");
  if (a.className = "invoice-title", a.textContent = e.title || "Invoice", o.appendChild(a), e.description) {
    const f = document.createElement("div");
    f.className = "invoice-desc", f.textContent = e.description, o.appendChild(f);
  }
  const i = e.currency || "", l = e.total_amount ?? 0, c = document.createElement("div");
  c.className = "invoice-amount", c.textContent = J(i, l), o.appendChild(c);
  const d = document.createElement("button");
  d.className = "invoice-pay", d.textContent = `Pay ${J(i, l)}`, d.addEventListener("click", async () => {
    if (!u.sending) {
      u.sending = !0, w(!0), d.disabled = !0, d.textContent = "Paying...", S();
      try {
        const f = await ye(e.message_id);
        L(), d.textContent = "Paid", _(f);
      } catch (f) {
        L(), d.disabled = !1, d.textContent = `Pay ${J(i, l)}`, E(`[Payment error: ${M(f)}]`, "received");
      }
      u.sending = !1, w(!1), n.inputEl.focus();
    }
  }), o.appendChild(d), s.appendChild(o);
  const m = document.createElement("span");
  m.className = "meta", m.textContent = q(), s.appendChild(m), n.messagesEl.appendChild(s), x();
}
function qe(e, t) {
  const n = N(t.text || "", t.entities ?? []), s = t.reply_markup || null;
  e.innerHTML = '<div class="sender">Bot</div>', e.innerHTML += `<span class="text">${n}</span>${P()}`, s && s.inline_keyboard && oe(
    e,
    s.inline_keyboard,
    t.message_id,
    _,
    (o) => E(o, "received")
  ), x();
}
function _(e) {
  const t = r(), n = e.reply_markup || null;
  if (e.is_edit && e.type === "text") {
    const s = Fe(e.message_id);
    if (s) {
      qe(s, e);
      return;
    }
  }
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const s = B("received", e.message_id), o = N(e.text || "", e.entities ?? []);
      s.innerHTML += `<span class="text">${o}</span>${P()}`, t.messagesEl.appendChild(s), oe(
        s,
        n.inline_keyboard,
        e.message_id,
        _,
        (a) => E(a, "received")
      ), x();
    } else
      E(e.text || "", "received", e.entities, e.message_id);
    n && n.keyboard && Ie(n.keyboard);
    return;
  }
  if (e.type === "invoice") {
    Re(e, "received");
    return;
  }
  if (e.type === "photo") {
    ce(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "voice") {
    re(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "video_note") {
    de(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "document") {
    ue(e.filename || "", `/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "poll") {
    Ae(e, "received");
    return;
  }
  E(`[Unknown response type: ${e.type}]`, "received");
}
async function Ke() {
  const e = r();
  e.startBtn.disabled = !0, we(), E("/start", "sent"), S();
  try {
    const t = await Y("/start");
    L(), _(t), await X();
  } catch (t) {
    L(), E(`[Error: ${M(t)}]`, "received");
  } finally {
    e.startBtn.disabled = !1;
  }
}
async function je() {
  const e = r();
  e.resetBtn.disabled = !0;
  try {
    await Ee(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div><div class="empty-placeholder" id="emptyPlaceholder">No messages here yet...</div>', le(), $e(), Ne(), Le(), ee();
  } catch (t) {
    E(`[Reset failed: ${M(t)}]`, "received");
  }
  e.resetBtn.disabled = !1;
}
async function D(e, t) {
  const n = r(), s = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!(!e || u.sending)) {
    C(), u.sending = !0, w(!0), s && (n.inputEl.value = ""), E(e, "sent"), S();
    try {
      const o = await Y(e);
      L(), _(o), await X();
    } catch (o) {
      L(), E(`[${M(o)}]`, "received");
    }
    u.sending = !1, w(!1), n.inputEl.focus();
  }
}
async function Je(e, t, n) {
  const s = await he(e, t, n);
  _(s);
}
async function Z() {
  const e = r(), t = e.inputEl.value.trim(), n = u.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await D(t, { clearInput: !0 });
    return;
  }
  if (u.sending) return;
  C(), u.sending = !0, w(!0), e.inputEl.value = "";
  const s = Be();
  for (const [o, a] of s.entries()) {
    const i = o === 0 ? t : "";
    switch (a.type) {
      case "photo": {
        ce(a.localUrl, "sent", i);
        break;
      }
      case "voice": {
        re(a.localUrl, "sent", i);
        break;
      }
      case "video_note": {
        de(a.localUrl, "sent", i);
        break;
      }
      default:
        ue(a.file.name, a.localUrl, "sent", i);
    }
    S();
    try {
      await Je(a.file, a.type, i), L();
    } catch (l) {
      L(), E(`[${M(l)}]`, "received");
    }
  }
  u.sending = !1, w(!1), e.inputEl.focus(), await X();
}
function We() {
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = r();
  He(async (n) => {
    await D(n, { clearInput: !1 });
  }), ke(async (n) => {
    await D(n, { clearInput: !1 });
  }), Se(), t.sendBtn.addEventListener("click", () => {
    Z();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && Z();
  }), t.resetBtn.addEventListener("click", () => {
    je();
  }), t.startBtn.addEventListener("click", () => {
    Ke();
  }), t.messagesEl.addEventListener("click", (n) => {
    const s = n.target;
    if (s.classList.contains("tg-command")) {
      const o = s.dataset.command;
      o && D(o, { clearInput: !0 });
    }
    s.classList.contains("tg-spoiler") && !s.classList.contains("revealed") && s.classList.add("revealed");
  }), ee();
}
We();
