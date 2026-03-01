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
async function me(e) {
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
async function pe(e) {
  const t = await fetch(e, { method: "POST" });
  if (!t.ok) throw await A("POST", e, t);
  return await U(t);
}
async function fe(e, t) {
  const n = await fetch(e, { method: "POST", body: t });
  if (!n.ok) throw await A("POST", e, n);
  return await U(n);
}
async function Y(e) {
  return await O("/api/message", { text: e });
}
async function ge(e, t, n) {
  const s = new FormData();
  return s.append("file", e), n && s.append("caption", n), await fe(`/api/${t}`, s);
}
async function he(e, t) {
  return await O("/api/callback", { message_id: e, data: t });
}
async function ve(e) {
  return await O("/api/invoice/pay", { message_id: e });
}
async function ye() {
  return await pe("/api/reset");
}
async function Ee() {
  return await me("/api/state");
}
async function be(e, t) {
  return await O("/api/poll/vote", { message_id: e, option_ids: t });
}
const u = {
  sending: !1,
  stagedFiles: []
};
let H = null;
function g(e) {
  const t = document.getElementById(e);
  if (!t) throw new Error(`Missing element: #${e}`);
  return t;
}
function r() {
  if (H) return H;
  const e = document.querySelector(".chat-container");
  if (!e) throw new Error("Missing element: .chat-container");
  const t = document.querySelector(".chat-input");
  if (!t) throw new Error("Missing element: .chat-input");
  return H = {
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
  }, H;
}
function L(e) {
  const t = r();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
function Ce() {
  H = null;
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
let v = !1, T = "menu", E = [], y = -1, W = null;
function Le(e) {
  W = e;
  const t = r();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !u.sending && t.menuBtn.classList.contains("visible")) {
      if (v && T === "menu") {
        b(), V();
        return;
      }
      te();
    }
  }), t.inputEl.addEventListener("input", () => {
    V();
  }), t.inputEl.addEventListener("keydown", (n) => {
    if (v) {
      if (n.key === "Escape") {
        n.preventDefault(), b();
        return;
      }
      if (E.length > 0) {
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
    s instanceof Node && (t.commandPanelEl.contains(s) || t.menuBtn.contains(s) || t.inputEl.contains(s) || b());
  });
}
function b() {
  const e = r();
  v = !1, T = "menu", E = [], y = -1, e.commandPanelEl.classList.remove("visible"), e.commandPanelEl.innerHTML = "";
}
function te() {
  ne("menu", $.botCommands, "Commands");
}
function V() {
  if (v && T === "menu") return;
  const e = ke();
  if (e === null || $.botCommands.length === 0) {
    v && T === "slash" && b();
    return;
  }
  const t = [];
  for (const n of $.botCommands)
    n.command && n.command.indexOf(e) === 0 && t.push(n);
  if (t.length === 0) {
    v && T === "slash" && b();
    return;
  }
  ne("slash", t, e ? `Commands matching "/${e}"` : "Commands");
}
function ke() {
  const { inputEl: e } = r(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function ne(e, t, n) {
  const s = r();
  T = e, E = Array.isArray(t) ? t : [], y = E.length > 0 ? 0 : -1, v = !0, s.commandPanelEl.innerHTML = "";
  const i = document.createElement("div");
  i.className = "cp-card";
  const a = document.createElement("div");
  if (a.className = "cp-header", a.textContent = n, i.appendChild(a), E.length === 0) {
    const o = document.createElement("div");
    o.className = "cp-empty", o.textContent = "No commands.", i.appendChild(o);
  } else
    for (const [o, l] of E.entries()) {
      const c = document.createElement("button");
      c.type = "button", c.className = `cp-item${o === y ? " selected" : ""}`, c.dataset.index = String(o), c.addEventListener("click", () => {
        const m = Number.parseInt(c.dataset.index || "", 10);
        Number.isFinite(m) && (y = m, se(), ae());
      });
      const d = document.createElement("div");
      if (d.className = "cp-cmd", d.textContent = `/${l.command || "?"}`, c.appendChild(d), l.description) {
        const m = document.createElement("div");
        m.className = "cp-desc", m.textContent = l.description, c.appendChild(m);
      }
      i.appendChild(c);
    }
  s.commandPanelEl.appendChild(i), s.commandPanelEl.classList.add("visible");
}
function se() {
  const t = r().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, s] of t.entries())
    n === y ? s.classList.add("selected") : s.classList.remove("selected");
}
function z(e) {
  !v || E.length === 0 || (y = (y + e) % E.length, y < 0 && (y += E.length), se());
}
function ae() {
  if (!v || y < 0 || y >= E.length) return !1;
  const t = E[y].command || "";
  if (!t) return !1;
  const { inputEl: n } = r();
  return T === "slash" ? (n.value = `/${t} `, b(), n.focus(), !0) : (b(), W && W(`/${t}`), !0);
}
function ie() {
  const e = r();
  $.menuButtonType === "commands" && $.botCommands.length > 0 ? e.menuBtn.classList.add("visible") : (e.menuBtn.classList.remove("visible"), v && T === "menu" && b());
}
async function X() {
  try {
    const e = await Ee();
    $.botCommands = Array.isArray(e.commands) ? e.commands : [], $.menuButtonType = e.menu_button_type || "default", ie(), v && T === "menu" ? te() : v || V();
  } catch {
  }
}
function Te() {
  $.botCommands = [], $.menuButtonType = "default", ie(), b();
}
function $e(e) {
  const t = e.type || "";
  return t.startsWith("image/") ? "photo" : t.startsWith("audio/") ? "voice" : t.startsWith("video/") ? "video_note" : "document";
}
function Q(e) {
  const t = URL.createObjectURL(e);
  u.stagedFiles.push({ file: e, type: $e(e), localUrl: t }), R();
}
function xe(e) {
  const t = u.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), u.stagedFiles.splice(e, 1), R());
}
function Ne() {
  for (const e of u.stagedFiles) URL.revokeObjectURL(e.localUrl);
  u.stagedFiles = [], R();
}
function Me() {
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
      const o = document.createElement("img");
      o.src = n.localUrl, o.alt = "Preview", s.appendChild(o);
    } else {
      const o = document.createElement("span");
      o.className = "staged-icon";
      const l = {
        voice: "&#127908;",
        video_note: "&#127909;"
      };
      o.innerHTML = l[n.type] ?? "&#128196;", s.appendChild(o);
    }
    const i = document.createElement("span");
    i.className = "staged-name", i.textContent = n.file.name, s.appendChild(i);
    const a = document.createElement("button");
    a.className = "staged-remove", a.innerHTML = "&times;", a.dataset.index = String(t), a.addEventListener("click", () => {
      const o = Number.parseInt(a.dataset.index || "", 10);
      Number.isFinite(o) && xe(o);
    }), s.appendChild(a), e.stagedFilesEl.appendChild(s);
  }
}
function Be() {
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
function N(e) {
  return e instanceof Error ? e.message : String(e);
}
function p(e) {
  const t = document.createElement("div");
  return t.textContent = e, t.innerHTML;
}
function q(e) {
  const t = /\/([a-zA-Z0-9_]{1,32})(?=\s|$)/g;
  let n = "", s = 0, i;
  for (; (i = t.exec(e)) !== null; )
    n += p(e.slice(s, i.index)), n += `<span class="tg-command" data-command="${p(i[0])}">${p(i[0])}</span>`, s = i.index + i[0].length;
  return n += p(e.slice(s)), n;
}
function Se(e) {
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
function Pe(e) {
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
function B(e, t) {
  if (t.length === 0) return q(e);
  const n = [...t].sort(
    (a, o) => a.offset !== o.offset ? a.offset - o.offset : o.length - a.length
  );
  let s = "", i = 0;
  for (const a of n) {
    const o = Math.max(0, Math.min(a.offset, e.length)), l = Math.max(o, Math.min(a.offset + a.length, e.length));
    if (o > i && (s += q(e.slice(i, o))), l > o) {
      const c = e.slice(o, l);
      a.type === "url" ? s += `<a href="${p(c)}" target="_blank" rel="noopener">${p(c)}</a>` : s += Se(a) + p(c) + Pe(a), i = l;
    }
  }
  return i < e.length && (s += q(e.slice(i))), s;
}
function K() {
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
function w() {
  r().typingEl.classList.remove("visible");
}
function He(e, t, n, s, i) {
  const a = document.createElement("div");
  a.className = "inline-keyboard";
  for (const o of t) {
    const l = document.createElement("div");
    l.className = "ik-row";
    for (const c of o) {
      const d = document.createElement("button");
      d.className = "ik-btn", d.textContent = c.text || "?", d.dataset.callbackData = c.callback_data || "", d.dataset.messageId = String(n), d.addEventListener("click", async () => {
        const m = d.dataset.callbackData || "", f = Number.parseInt(d.dataset.messageId || "0", 10);
        if (!m || u.sending) return;
        const k = d.closest(".inline-keyboard"), P = k ? k.querySelectorAll(".ik-btn") : [];
        for (const h of P) h.disabled = !0;
        u.sending = !0, L(!0), S();
        try {
          const h = await he(f, m);
          w(), s(h);
        } catch (h) {
          w(), i(`[Callback error: ${N(h)}]`);
        }
        u.sending = !1, L(!1), r().inputEl.focus();
      }), l.appendChild(d);
    }
    a.appendChild(l);
  }
  e.appendChild(a);
}
let G = null;
function Ie(e) {
  G = e;
}
function Fe(e) {
  const t = r();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const s = document.createElement("div");
    s.className = "rk-row";
    for (const i of n) {
      const a = document.createElement("button");
      a.className = "rk-btn", a.textContent = i.text || "?", a.addEventListener("click", () => {
        const o = a.textContent || "";
        o && (u.sending || (oe(), G && G(o)));
      }), s.appendChild(a);
    }
    t.replyKeyboardEl.appendChild(s);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function oe() {
  const e = r();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}
function x() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function M(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, e === "received" && (t.innerHTML = '<div class="sender">Bot</div>'), t;
}
function I() {
  return `<span class="meta">${K()}</span>`;
}
function le(e, t, n, s) {
  const i = r(), a = M(t), o = document.createElement("img");
  if (o.className = "msg-photo", o.src = e, o.alt = "Photo", a.appendChild(o), n) {
    const l = t === "received" && (s != null && s.length) ? B(n, s) : p(n);
    a.innerHTML += `<span class="caption">${l}</span>`;
  }
  a.innerHTML += I(), i.messagesEl.appendChild(a), o.addEventListener("load", () => x()), x();
}
function ce(e, t, n, s) {
  const i = r(), a = M(t), o = document.createElement("div");
  o.className = "voice-player";
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
  if (k.className = "vp-time", k.textContent = "0:00", d.appendChild(m), d.appendChild(k), o.appendChild(c), o.appendChild(d), a.appendChild(o), n) {
    const h = document.createElement("span");
    h.className = "caption";
    const _ = t === "received" && (s != null && s.length) ? B(n, s) : p(n);
    h.innerHTML = _, a.appendChild(h);
  }
  const P = document.createElement("span");
  P.className = "meta", P.textContent = K(), a.appendChild(P), i.messagesEl.appendChild(a), l.addEventListener("loadedmetadata", () => {
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
      const _ = m.getBoundingClientRect(), ue = (h.clientX - _.left) / _.width;
      l.currentTime = ue * l.duration;
    }
  }), x();
}
function re(e, t, n, s) {
  const i = r(), a = M(t), o = document.createElement("video");
  if (o.className = "msg-video-note", o.src = e, o.controls = !0, o.playsInline = !0, a.appendChild(o), n) {
    const l = t === "received" && (s != null && s.length) ? B(n, s) : p(n);
    a.innerHTML += `<span class="caption">${l}</span>`;
  }
  a.innerHTML += I(), i.messagesEl.appendChild(a), x();
}
function de(e, t, n, s, i) {
  const a = r(), o = M(n), l = document.createElement("a");
  if (l.className = "doc-attachment", l.href = t ? `${t}?download=1` : "#", l.download = e || "", l.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${p(e)}</span>`, o.appendChild(l), s) {
    const c = n === "received" && (i != null && i.length) ? B(s, i) : p(s);
    o.innerHTML += `<span class="caption">${c}</span>`;
  }
  o.innerHTML += I(), a.messagesEl.appendChild(o), x();
}
function _e() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function De(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, t.innerHTML = '<div class="sender">Bot</div>', t;
}
function Ue(e, t) {
  const n = r(), s = De(t);
  if (e.poll_question) {
    const a = document.createElement("h4");
    a.className = "poll-question", a.textContent = e.poll_question, s.appendChild(a);
  }
  if (e.poll_options && e.message_id) {
    const a = document.createElement("div");
    a.className = "poll-options", e.poll_options.forEach((o, l) => {
      const c = document.createElement("button");
      c.className = "poll-option-btn", c.textContent = o.text, c.onclick = () => Ae(e.message_id, [l]), a.appendChild(c);
    }), s.appendChild(a);
  }
  const i = document.createElement("span");
  i.className = "meta", i.textContent = K(), s.appendChild(i), n.messagesEl.appendChild(s), _e();
}
async function Ae(e, t) {
  try {
    L(!0), S();
    const n = await be(e, t);
    n.text && C(n.text, "received");
  } catch (n) {
    N(`Poll vote failed: ${String(n)}`);
  } finally {
    w(), L(!1);
  }
}
function C(e, t, n) {
  const s = r(), i = M(t), a = t === "received" && (n != null && n.length) ? B(e, n) : p(e);
  i.innerHTML += `<span class="text">${a}</span>${I()}`, s.messagesEl.appendChild(i), x();
}
function J(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function Oe(e, t) {
  const n = r(), s = M(t), i = document.createElement("div");
  i.className = "invoice-card";
  const a = document.createElement("div");
  if (a.className = "invoice-title", a.textContent = e.title || "Invoice", i.appendChild(a), e.description) {
    const f = document.createElement("div");
    f.className = "invoice-desc", f.textContent = e.description, i.appendChild(f);
  }
  const o = e.currency || "", l = e.total_amount ?? 0, c = document.createElement("div");
  c.className = "invoice-amount", c.textContent = J(o, l), i.appendChild(c);
  const d = document.createElement("button");
  d.className = "invoice-pay", d.textContent = `Pay ${J(o, l)}`, d.addEventListener("click", async () => {
    if (!u.sending) {
      u.sending = !0, L(!0), d.disabled = !0, d.textContent = "Paying...", S();
      try {
        const f = await ve(e.message_id);
        w(), d.textContent = "Paid", F(f);
      } catch (f) {
        w(), d.disabled = !1, d.textContent = `Pay ${J(o, l)}`, C(`[Payment error: ${N(f)}]`, "received");
      }
      u.sending = !1, L(!1), n.inputEl.focus();
    }
  }), i.appendChild(d), s.appendChild(i);
  const m = document.createElement("span");
  m.className = "meta", m.textContent = K(), s.appendChild(m), n.messagesEl.appendChild(s), x();
}
function F(e) {
  const t = r(), n = e.reply_markup || null;
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const s = M("received"), i = B(e.text || "", e.entities ?? []);
      s.innerHTML += `<span class="text">${i}</span>${I()}`, t.messagesEl.appendChild(s), He(
        s,
        n.inline_keyboard,
        e.message_id,
        F,
        (a) => C(a, "received")
      ), x();
    } else
      C(e.text || "", "received", e.entities);
    n && n.keyboard && Fe(n.keyboard);
    return;
  }
  if (e.type === "invoice") {
    Oe(e, "received");
    return;
  }
  if (e.type === "photo") {
    le(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "voice") {
    ce(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "video_note") {
    re(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "document") {
    de(e.filename || "", `/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "poll") {
    Ue(e, "received");
    return;
  }
  C(`[Unknown response type: ${e.type}]`, "received");
}
async function Re() {
  const e = r();
  e.startBtn.disabled = !0, we(), C("/start", "sent"), S();
  try {
    const t = await Y("/start");
    w(), F(t), await X();
  } catch (t) {
    w(), C(`[Error: ${N(t)}]`, "received");
  } finally {
    e.startBtn.disabled = !1;
  }
}
async function Ke() {
  const e = r();
  e.resetBtn.disabled = !0;
  try {
    await ye(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div><div class="empty-placeholder" id="emptyPlaceholder">No messages here yet...</div>', oe(), Te(), Ne(), Ce(), ee();
  } catch (t) {
    C(`[Reset failed: ${N(t)}]`, "received");
  }
  e.resetBtn.disabled = !1;
}
async function D(e, t) {
  const n = r(), s = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!(!e || u.sending)) {
    b(), u.sending = !0, L(!0), s && (n.inputEl.value = ""), C(e, "sent"), S();
    try {
      const i = await Y(e);
      w(), F(i), await X();
    } catch (i) {
      w(), C(`[${N(i)}]`, "received");
    }
    u.sending = !1, L(!1), n.inputEl.focus();
  }
}
async function qe(e, t, n) {
  const s = await ge(e, t, n);
  F(s);
}
async function Z() {
  const e = r(), t = e.inputEl.value.trim(), n = u.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await D(t, { clearInput: !0 });
    return;
  }
  if (u.sending) return;
  b(), u.sending = !0, L(!0), e.inputEl.value = "";
  const s = Me();
  for (const [i, a] of s.entries()) {
    const o = i === 0 ? t : "";
    switch (a.type) {
      case "photo": {
        le(a.localUrl, "sent", o);
        break;
      }
      case "voice": {
        ce(a.localUrl, "sent", o);
        break;
      }
      case "video_note": {
        re(a.localUrl, "sent", o);
        break;
      }
      default:
        de(a.file.name, a.localUrl, "sent", o);
    }
    S();
    try {
      await qe(a.file, a.type, o), w();
    } catch (l) {
      w(), C(`[${N(l)}]`, "received");
    }
  }
  u.sending = !1, L(!1), e.inputEl.focus(), await X();
}
function je() {
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = r();
  Ie(async (n) => {
    await D(n, { clearInput: !1 });
  }), Le(async (n) => {
    await D(n, { clearInput: !1 });
  }), Be(), t.sendBtn.addEventListener("click", () => {
    Z();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && Z();
  }), t.resetBtn.addEventListener("click", () => {
    Ke();
  }), t.startBtn.addEventListener("click", () => {
    Re();
  }), t.messagesEl.addEventListener("click", (n) => {
    const s = n.target;
    if (s.classList.contains("tg-command")) {
      const i = s.dataset.command;
      i && D(i, { clearInput: !0 });
    }
    s.classList.contains("tg-spoiler") && !s.classList.contains("revealed") && s.classList.add("revealed");
  }), ee();
}
je();
