async function D(e) {
  return await e.json();
}
async function U(e, t, n) {
  try {
    const s = await n.json();
    if (s.detail)
      return new Error(s.detail);
  } catch {
  }
  return new Error(`${e} ${t} failed: ${n.status} ${n.statusText}`);
}
async function fe(e) {
  const t = await fetch(e, { method: "GET" });
  if (!t.ok) throw await U("GET", e, t);
  return await D(t);
}
async function A(e, t) {
  const n = await fetch(e, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(t)
  });
  if (!n.ok) throw await U("POST", e, n);
  return await D(n);
}
async function ge(e) {
  const t = await fetch(e, { method: "POST" });
  if (!t.ok) throw await U("POST", e, t);
  return await D(t);
}
async function he(e, t) {
  const n = await fetch(e, { method: "POST", body: t });
  if (!n.ok) throw await U("POST", e, n);
  return await D(n);
}
async function ee(e) {
  return await A("/api/message", { text: e });
}
async function ve(e, t, n) {
  const s = new FormData();
  return s.append("file", e), n && s.append("caption", n), await he(`/api/${t}`, s);
}
async function ye(e, t) {
  return await A("/api/callback", { message_id: e, data: t });
}
async function Ee(e) {
  return await A("/api/invoice/pay", { message_id: e });
}
async function be() {
  return await ge("/api/reset");
}
async function Ce() {
  return await fe("/api/state");
}
async function Le(e, t) {
  return await A("/api/poll/vote", { message_id: e, option_ids: t });
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
function w(e) {
  const t = r();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
function we() {
  H = null;
}
function te() {
  const e = r();
  e.emptyPlaceholder.style.display = "", e.startContainer.style.display = "", e.chatInputEl.style.display = "none";
}
function ke() {
  const e = r();
  e.emptyPlaceholder.style.display = "none", e.startContainer.style.display = "none", e.chatInputEl.style.display = "flex";
}
const $ = {
  botCommands: [],
  menuButtonType: "default"
};
let v = !1, T = "menu", b = [], y = -1, W = null;
function Te(e) {
  W = e;
  const t = r();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !u.sending && t.menuBtn.classList.contains("visible")) {
      if (v && T === "menu") {
        C(), V();
        return;
      }
      ne();
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
          n.preventDefault(), Q(1);
          return;
        }
        if (n.key === "ArrowUp") {
          n.preventDefault(), Q(-1);
          return;
        }
      }
      n.key === "Enter" && ie() && n.preventDefault();
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
function ne() {
  se("menu", $.botCommands, "Commands");
}
function V() {
  if (v && T === "menu") return;
  const e = $e();
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
  se("slash", t, e ? `Commands matching "/${e}"` : "Commands");
}
function $e() {
  const { inputEl: e } = r(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function se(e, t, n) {
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
        Number.isFinite(m) && (y = m, ae(), ie());
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
function ae() {
  const t = r().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, s] of t.entries())
    n === y ? s.classList.add("selected") : s.classList.remove("selected");
}
function Q(e) {
  !v || b.length === 0 || (y = (y + e) % b.length, y < 0 && (y += b.length), ae());
}
function ie() {
  if (!v || y < 0 || y >= b.length) return !1;
  const t = b[y].command || "";
  if (!t) return !1;
  const { inputEl: n } = r();
  return T === "slash" ? (n.value = `/${t} `, C(), n.focus(), !0) : (C(), W && W(`/${t}`), !0);
}
function oe() {
  const e = r();
  $.menuButtonType === "commands" && $.botCommands.length > 0 ? e.menuBtn.classList.add("visible") : (e.menuBtn.classList.remove("visible"), v && T === "menu" && C());
}
async function X() {
  try {
    const e = await Ce();
    $.botCommands = Array.isArray(e.commands) ? e.commands : [], $.menuButtonType = e.menu_button_type || "default", oe(), v && T === "menu" ? ne() : v || V();
  } catch {
  }
}
function xe() {
  $.botCommands = [], $.menuButtonType = "default", oe(), C();
}
function Me(e) {
  const t = e.type || "";
  return t.startsWith("image/") ? "photo" : t.startsWith("audio/") ? "voice" : t.startsWith("video/") ? "video_note" : "document";
}
function Z(e) {
  const t = URL.createObjectURL(e);
  u.stagedFiles.push({ file: e, type: Me(e), localUrl: t }), R();
}
function Be(e) {
  const t = u.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), u.stagedFiles.splice(e, 1), R());
}
function Ne() {
  for (const e of u.stagedFiles) URL.revokeObjectURL(e.localUrl);
  u.stagedFiles = [], R();
}
function Se() {
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
      Number.isFinite(i) && Be(i);
    }), s.appendChild(a), e.stagedFilesEl.appendChild(s);
  }
}
function Pe() {
  const e = r();
  e.attachBtn.addEventListener("click", () => {
    u.sending || e.fileInput.click();
  }), e.fileInput.addEventListener("change", () => {
    const t = e.fileInput.files;
    if (t && t.length > 0)
      for (let n = 0; n < t.length; n++) Z(t[n]);
    e.fileInput.value = "", e.inputEl.focus();
  }), e.chatContainer.addEventListener("dragover", (t) => {
    t.preventDefault(), t.stopPropagation();
  }), e.chatContainer.addEventListener("drop", (t) => {
    var s;
    t.preventDefault(), t.stopPropagation();
    const n = (s = t.dataTransfer) == null ? void 0 : s.files;
    if (n && n.length > 0)
      for (let o = 0; o < n.length; o++) Z(n[o]);
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
function _e(e) {
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
function He(e) {
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
  if (t.length === 0) return K(e);
  const n = [...t].sort(
    (a, i) => a.offset !== i.offset ? a.offset - i.offset : i.length - a.length
  );
  let s = "", o = 0;
  for (const a of n) {
    const i = Math.max(0, Math.min(a.offset, e.length)), l = Math.max(i, Math.min(a.offset + a.length, e.length));
    if (i > o && (s += K(e.slice(o, i))), l > i) {
      const c = e.slice(i, l);
      a.type === "url" ? s += `<a href="${p(c)}" target="_blank" rel="noopener">${p(c)}</a>` : s += _e(a) + p(c) + He(a), o = l;
    }
  }
  return o < e.length && (s += K(e.slice(o))), s;
}
function O() {
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
function le(e, t, n, s, o) {
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
        const k = d.closest(".inline-keyboard"), _ = k ? k.querySelectorAll(".ik-btn") : [];
        for (const h of _) h.disabled = !0;
        u.sending = !0, w(!0), S();
        try {
          const h = await ye(f, m);
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
function Ie(e) {
  G = e;
}
function Fe(e) {
  const t = r();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const s = document.createElement("div");
    s.className = "rk-row";
    for (const o of n) {
      const a = document.createElement("button");
      a.className = "rk-btn", a.textContent = o.text || "?", a.addEventListener("click", () => {
        const i = a.textContent || "";
        i && (u.sending || (ce(), G && G(i)));
      }), s.appendChild(a);
    }
    t.replyKeyboardEl.appendChild(s);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function ce() {
  const e = r();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}
function x() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function N(e, t) {
  const n = document.createElement("div");
  return n.className = `message ${e}`, e === "received" && (n.innerHTML = '<div class="sender">Bot</div>'), t !== void 0 && (n.dataset.messageId = String(t)), n;
}
function De(e) {
  return r().messagesEl.querySelector(
    `.message[data-message-id="${e}"]`
  );
}
function P() {
  return `<span class="meta">${O()}</span>`;
}
function re(e, t, n, s) {
  const o = r(), a = N(t), i = document.createElement("img");
  if (i.className = "msg-photo", i.src = e, i.alt = "Photo", a.appendChild(i), n) {
    const l = t === "received" && (s != null && s.length) ? B(n, s) : p(n);
    a.innerHTML += `<span class="caption">${l}</span>`;
  }
  a.innerHTML += P(), o.messagesEl.appendChild(a), i.addEventListener("load", () => x()), x();
}
function de(e, t, n, s) {
  const o = r(), a = N(t), i = document.createElement("div");
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
    const I = t === "received" && (s != null && s.length) ? B(n, s) : p(n);
    h.innerHTML = I, a.appendChild(h);
  }
  const _ = document.createElement("span");
  _.className = "meta", _.textContent = O(), a.appendChild(_), o.messagesEl.appendChild(a), l.addEventListener("loadedmetadata", () => {
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
      const I = m.getBoundingClientRect(), pe = (h.clientX - I.left) / I.width;
      l.currentTime = pe * l.duration;
    }
  }), x();
}
function ue(e, t, n, s) {
  const o = r(), a = N(t), i = document.createElement("video");
  if (i.className = "msg-video-note", i.src = e, i.controls = !0, i.playsInline = !0, a.appendChild(i), n) {
    const l = t === "received" && (s != null && s.length) ? B(n, s) : p(n);
    a.innerHTML += `<span class="caption">${l}</span>`;
  }
  a.innerHTML += P(), o.messagesEl.appendChild(a), x();
}
function me(e, t, n, s, o) {
  const a = r(), i = N(n), l = document.createElement("a");
  if (l.className = "doc-attachment", l.href = t ? `${t}?download=1` : "#", l.download = e || "", l.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${p(e)}</span>`, i.appendChild(l), s) {
    const c = n === "received" && (o != null && o.length) ? B(s, o) : p(s);
    i.innerHTML += `<span class="caption">${c}</span>`;
  }
  i.innerHTML += P(), a.messagesEl.appendChild(i), x();
}
function Ue() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function Ae(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, t.innerHTML = '<div class="sender">Bot</div>', t;
}
function Re(e, t) {
  const n = r(), s = Ae(t);
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
  o.className = "meta", o.textContent = O(), s.appendChild(o), n.messagesEl.appendChild(s), Ue();
}
async function Oe(e, t) {
  try {
    w(!0), S();
    const n = await Le(e, t);
    for (const s of n)
      s.text && E(s.text, "received");
  } catch (n) {
    M(`Poll vote failed: ${String(n)}`);
  } finally {
    L(), w(!1);
  }
}
function E(e, t, n, s) {
  const o = r(), a = N(t, s), i = t === "received" && (n != null && n.length) ? B(e, n) : p(e);
  a.innerHTML += `<span class="text">${i}</span>${P()}`, o.messagesEl.appendChild(a), x();
}
function J(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function qe(e, t) {
  const n = r(), s = N(t), o = document.createElement("div");
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
        const f = await Ee(e.message_id);
        L(), d.textContent = "Paid", q(f);
      } catch (f) {
        L(), d.disabled = !1, d.textContent = `Pay ${J(i, l)}`, E(`[Payment error: ${M(f)}]`, "received");
      }
      u.sending = !1, w(!1), n.inputEl.focus();
    }
  }), o.appendChild(d), s.appendChild(o);
  const m = document.createElement("span");
  m.className = "meta", m.textContent = O(), s.appendChild(m), n.messagesEl.appendChild(s), x();
}
function Ke(e, t) {
  const n = B(t.text || "", t.entities ?? []), s = t.reply_markup || null;
  e.innerHTML = '<div class="sender">Bot</div>', e.innerHTML += `<span class="text">${n}</span>${P()}`, s && s.inline_keyboard && le(
    e,
    s.inline_keyboard,
    t.message_id,
    z,
    (o) => E(o, "received")
  ), x();
}
function q(e) {
  for (const t of e)
    z(t);
}
function z(e) {
  const t = r(), n = e.reply_markup || null;
  if (e.is_edit && e.type === "text") {
    const s = De(e.message_id);
    if (s) {
      Ke(s, e);
      return;
    }
  }
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const s = N("received", e.message_id), o = B(e.text || "", e.entities ?? []);
      s.innerHTML += `<span class="text">${o}</span>${P()}`, t.messagesEl.appendChild(s), le(
        s,
        n.inline_keyboard,
        e.message_id,
        z,
        (a) => E(a, "received")
      ), x();
    } else
      E(e.text || "", "received", e.entities, e.message_id);
    n && n.keyboard && Fe(n.keyboard);
    return;
  }
  if (e.type === "invoice") {
    qe(e, "received");
    return;
  }
  if (e.type === "photo") {
    re(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "voice") {
    de(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "video_note") {
    ue(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "document") {
    me(e.filename || "", `/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "poll") {
    Re(e, "received");
    return;
  }
  E(`[Unknown response type: ${e.type}]`, "received");
}
async function je() {
  const e = r();
  e.startBtn.disabled = !0, ke(), E("/start", "sent"), S();
  try {
    const t = await ee("/start");
    L(), q(t), await X();
  } catch (t) {
    L(), E(`[Error: ${M(t)}]`, "received");
  } finally {
    e.startBtn.disabled = !1;
  }
}
async function Je() {
  const e = r();
  e.resetBtn.disabled = !0;
  try {
    await be(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div><div class="empty-placeholder" id="emptyPlaceholder">No messages here yet...</div>', ce(), xe(), Ne(), we(), te();
  } catch (t) {
    E(`[Reset failed: ${M(t)}]`, "received");
  }
  e.resetBtn.disabled = !1;
}
async function F(e, t) {
  const n = r(), s = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!(!e || u.sending)) {
    C(), u.sending = !0, w(!0), s && (n.inputEl.value = ""), E(e, "sent"), S();
    try {
      const o = await ee(e);
      L(), q(o), await X();
    } catch (o) {
      L(), E(`[${M(o)}]`, "received");
    }
    u.sending = !1, w(!1), n.inputEl.focus();
  }
}
async function We(e, t, n) {
  const s = await ve(e, t, n);
  q(s);
}
async function Y() {
  const e = r(), t = e.inputEl.value.trim(), n = u.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await F(t, { clearInput: !0 });
    return;
  }
  if (u.sending) return;
  C(), u.sending = !0, w(!0), e.inputEl.value = "";
  const s = Se();
  for (const [o, a] of s.entries()) {
    const i = o === 0 ? t : "";
    switch (a.type) {
      case "photo": {
        re(a.localUrl, "sent", i);
        break;
      }
      case "voice": {
        de(a.localUrl, "sent", i);
        break;
      }
      case "video_note": {
        ue(a.localUrl, "sent", i);
        break;
      }
      default:
        me(a.file.name, a.localUrl, "sent", i);
    }
    S();
    try {
      await We(a.file, a.type, i), L();
    } catch (l) {
      L(), E(`[${M(l)}]`, "received");
    }
  }
  u.sending = !1, w(!1), e.inputEl.focus(), await X();
}
function Ve() {
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = r();
  Ie(async (n) => {
    await F(n, { clearInput: !1 });
  }), Te(async (n) => {
    await F(n, { clearInput: !1 });
  }), Pe(), t.sendBtn.addEventListener("click", () => {
    Y();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && Y();
  }), t.resetBtn.addEventListener("click", () => {
    Je();
  }), t.startBtn.addEventListener("click", () => {
    je();
  }), t.messagesEl.addEventListener("click", (n) => {
    const s = n.target;
    if (s.classList.contains("tg-command")) {
      const o = s.dataset.command;
      o && F(o, { clearInput: !0 });
    }
    s.classList.contains("tg-spoiler") && !s.classList.contains("revealed") && s.classList.add("revealed");
  }), te();
}
Ve();
