async function V(e) {
  return await e.json();
}
async function I(e, t, n) {
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
  if (!t.ok) throw await I("GET", e, t);
  return await V(t);
}
async function ge(e, t) {
  const n = await fetch(e, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(t)
  });
  if (!n.ok) throw await I("POST", e, n);
  return await V(n);
}
async function he(e) {
  const t = await fetch(e, { method: "POST" });
  if (!t.ok) throw await I("POST", e, t);
  return await V(t);
}
async function G(e, t, n) {
  const s = await fetch(e, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(t)
  });
  if (!s.ok) throw await I("POST", e, s);
  await Y(s, n);
}
async function ye(e, t, n) {
  const s = await fetch(e, { method: "POST", body: t });
  if (!s.ok) throw await I("POST", e, s);
  await Y(s, n);
}
async function Y(e, t) {
  var i;
  const n = (i = e.body) == null ? void 0 : i.getReader();
  if (!n) return;
  const s = new TextDecoder();
  let a = "";
  for (; ; ) {
    const { done: o, value: l } = await n.read();
    if (o) break;
    a += s.decode(l, { stream: !0 });
    const c = a.split(`

`);
    a = c.pop() ?? "";
    for (const d of c) {
      const m = d.trim();
      if (!m.startsWith("data: ")) continue;
      const p = m.slice(6);
      p !== "[DONE]" && t(JSON.parse(p));
    }
  }
}
async function ee(e, t) {
  await G("/api/message", { text: e }, t);
}
async function ve(e, t, n, s) {
  const a = new FormData();
  a.append("file", e), n && a.append("caption", n), await ye(`/api/${t}`, a, s);
}
async function Ee(e, t) {
  return await ge("/api/callback", { message_id: e, data: t });
}
async function be(e, t) {
  await G("/api/invoice/pay", { message_id: e }, t);
}
async function Ce() {
  return await he("/api/reset");
}
async function we() {
  return await fe("/api/state");
}
async function Le(e, t, n) {
  await G(
    "/api/poll/vote",
    { message_id: e, option_ids: t },
    n
  );
}
const u = {
  sending: !1,
  stagedFiles: []
};
let F = null;
function h(e) {
  const t = document.getElementById(e);
  if (!t) throw new Error(`Missing element: #${e}`);
  return t;
}
function r() {
  if (F) return F;
  const e = document.querySelector(".chat-container");
  if (!e) throw new Error("Missing element: .chat-container");
  const t = document.querySelector(".chat-input");
  if (!t) throw new Error("Missing element: .chat-input");
  return F = {
    messagesEl: h("messages"),
    inputEl: h("msgInput"),
    sendBtn: h("sendBtn"),
    resetBtn: h("resetBtn"),
    typingEl: h("typing"),
    attachBtn: h("attachBtn"),
    fileInput: h("fileInput"),
    stagedFilesEl: h("stagedFiles"),
    replyKeyboardEl: h("replyKeyboard"),
    menuBtn: h("menuBtn"),
    commandPanelEl: h("commandPanel"),
    chatContainer: e,
    emptyPlaceholder: h("emptyPlaceholder"),
    startContainer: h("startContainer"),
    startBtn: h("startBtn"),
    chatInputEl: t
  }, F;
}
function k(e) {
  const t = r();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
function ke() {
  F = null;
}
function te() {
  const e = r();
  e.emptyPlaceholder.style.display = "", e.startContainer.style.display = "", e.chatInputEl.style.display = "none";
}
function Te() {
  const e = r();
  e.emptyPlaceholder.style.display = "none", e.startContainer.style.display = "none", e.chatInputEl.style.display = "flex";
}
const $ = {
  botCommands: [],
  menuButtonType: "default"
};
let v = !1, T = "menu", w = [], E = -1, J = null;
function $e(e) {
  J = e;
  const t = r();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !u.sending && t.menuBtn.classList.contains("visible")) {
      if (v && T === "menu") {
        L(), j();
        return;
      }
      ne();
    }
  }), t.inputEl.addEventListener("input", () => {
    j();
  }), t.inputEl.addEventListener("keydown", (n) => {
    if (v) {
      if (n.key === "Escape") {
        n.preventDefault(), L();
        return;
      }
      if (w.length > 0) {
        if (n.key === "ArrowDown") {
          n.preventDefault(), z(1);
          return;
        }
        if (n.key === "ArrowUp") {
          n.preventDefault(), z(-1);
          return;
        }
      }
      n.key === "Enter" && ie() && n.preventDefault();
    }
  }), document.addEventListener("click", (n) => {
    if (!v) return;
    const s = n.target;
    s instanceof Node && (t.commandPanelEl.contains(s) || t.menuBtn.contains(s) || t.inputEl.contains(s) || L());
  });
}
function L() {
  const e = r();
  v = !1, T = "menu", w = [], E = -1, e.commandPanelEl.classList.remove("visible"), e.commandPanelEl.innerHTML = "";
}
function ne() {
  se("menu", $.botCommands, "Commands");
}
function j() {
  if (v && T === "menu") return;
  const e = Se();
  if (e === null || $.botCommands.length === 0) {
    v && T === "slash" && L();
    return;
  }
  const t = [];
  for (const n of $.botCommands)
    n.command && n.command.indexOf(e) === 0 && t.push(n);
  if (t.length === 0) {
    v && T === "slash" && L();
    return;
  }
  se("slash", t, e ? `Commands matching "/${e}"` : "Commands");
}
function Se() {
  const { inputEl: e } = r(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function se(e, t, n) {
  const s = r();
  T = e, w = Array.isArray(t) ? t : [], E = w.length > 0 ? 0 : -1, v = !0, s.commandPanelEl.innerHTML = "";
  const a = document.createElement("div");
  a.className = "cp-card";
  const i = document.createElement("div");
  if (i.className = "cp-header", i.textContent = n, a.appendChild(i), w.length === 0) {
    const o = document.createElement("div");
    o.className = "cp-empty", o.textContent = "No commands.", a.appendChild(o);
  } else
    for (const [o, l] of w.entries()) {
      const c = document.createElement("button");
      c.type = "button", c.className = `cp-item${o === E ? " selected" : ""}`, c.dataset.index = String(o), c.addEventListener("click", () => {
        const m = Number.parseInt(c.dataset.index || "", 10);
        Number.isFinite(m) && (E = m, ae(), ie());
      });
      const d = document.createElement("div");
      if (d.className = "cp-cmd", d.textContent = `/${l.command || "?"}`, c.appendChild(d), l.description) {
        const m = document.createElement("div");
        m.className = "cp-desc", m.textContent = l.description, c.appendChild(m);
      }
      a.appendChild(c);
    }
  s.commandPanelEl.appendChild(a), s.commandPanelEl.classList.add("visible");
}
function ae() {
  const t = r().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, s] of t.entries())
    n === E ? s.classList.add("selected") : s.classList.remove("selected");
}
function z(e) {
  !v || w.length === 0 || (E = (E + e) % w.length, E < 0 && (E += w.length), ae());
}
function ie() {
  if (!v || E < 0 || E >= w.length) return !1;
  const t = w[E].command || "";
  if (!t) return !1;
  const { inputEl: n } = r();
  return T === "slash" ? (n.value = `/${t} `, L(), n.focus(), !0) : (L(), J && J(`/${t}`), !0);
}
function oe() {
  const e = r();
  $.menuButtonType === "commands" && $.botCommands.length > 0 ? e.menuBtn.classList.add("visible") : (e.menuBtn.classList.remove("visible"), v && T === "menu" && L());
}
async function X() {
  try {
    const e = await we();
    $.botCommands = Array.isArray(e.commands) ? e.commands : [], $.menuButtonType = e.menu_button_type || "default", oe(), v && T === "menu" ? ne() : v || j();
  } catch {
  }
}
function xe() {
  $.botCommands = [], $.menuButtonType = "default", oe(), L();
}
function Ne(e) {
  const t = e.type || "";
  return t.startsWith("image/") ? "photo" : t.startsWith("audio/") ? "voice" : t.startsWith("video/") ? "video_note" : "document";
}
function Q(e) {
  const t = URL.createObjectURL(e);
  u.stagedFiles.push({ file: e, type: Ne(e), localUrl: t }), U();
}
function Me(e) {
  const t = u.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), u.stagedFiles.splice(e, 1), U());
}
function Be() {
  for (const e of u.stagedFiles) URL.revokeObjectURL(e.localUrl);
  u.stagedFiles = [], U();
}
function Pe() {
  const e = [...u.stagedFiles];
  return u.stagedFiles = [], U(), e;
}
function U() {
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
    const a = document.createElement("span");
    a.className = "staged-name", a.textContent = n.file.name, s.appendChild(a);
    const i = document.createElement("button");
    i.className = "staged-remove", i.innerHTML = "&times;", i.dataset.index = String(t), i.addEventListener("click", () => {
      const o = Number.parseInt(i.dataset.index || "", 10);
      Number.isFinite(o) && Me(o);
    }), s.appendChild(i), e.stagedFilesEl.appendChild(s);
  }
}
function _e() {
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
      for (let a = 0; a < n.length; a++) Q(n[a]);
  });
}
function x(e) {
  return e instanceof Error ? e.message : String(e);
}
function g(e) {
  const t = document.createElement("div");
  return t.textContent = e, t.innerHTML;
}
function R(e) {
  const t = /\/([a-zA-Z0-9_]{1,32})(?=\s|$)/g;
  let n = "", s = 0, a;
  for (; (a = t.exec(e)) !== null; )
    n += g(e.slice(s, a.index)), n += `<span class="tg-command" data-command="${g(a[0])}">${g(a[0])}</span>`, s = a.index + a[0].length;
  return n += g(e.slice(s)), n;
}
function He(e) {
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
      return e.language ? `<pre><code class="language-${g(e.language)}">` : "<pre>";
    case "url":
      return "";
    case "text_url":
      return `<a href="${g(e.url ?? "")}" target="_blank" rel="noopener">`;
    case "spoiler":
      return '<span class="tg-spoiler">';
    default:
      return "";
  }
}
function Fe(e) {
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
  if (t.length === 0) return R(e);
  const n = [...t].sort(
    (i, o) => i.offset !== o.offset ? i.offset - o.offset : o.length - i.length
  );
  let s = "", a = 0;
  for (const i of n) {
    const o = Math.max(0, Math.min(i.offset, e.length)), l = Math.max(o, Math.min(i.offset + i.length, e.length));
    if (o > a && (s += R(e.slice(a, o))), l > o) {
      const c = e.slice(o, l);
      i.type === "url" ? s += `<a href="${g(c)}" target="_blank" rel="noopener">${g(c)}</a>` : s += He(i) + g(c) + Fe(i), a = l;
    }
  }
  return a < e.length && (s += R(e.slice(a))), s;
}
function A() {
  const e = /* @__PURE__ */ new Date();
  return `${e.getHours().toString().padStart(2, "0")}:${e.getMinutes().toString().padStart(2, "0")}`;
}
function q(e) {
  if (!Number.isFinite(e) || e < 0) return "0:00";
  const t = Math.floor(e / 60), n = Math.floor(e % 60);
  return `${t}:${n < 10 ? "0" : ""}${n}`;
}
function B() {
  const e = r();
  e.typingEl.classList.add("visible"), e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function f() {
  r().typingEl.classList.remove("visible");
}
function le(e, t, n, s, a) {
  const i = document.createElement("div");
  i.className = "inline-keyboard";
  for (const o of t) {
    const l = document.createElement("div");
    l.className = "ik-row";
    for (const c of o) {
      const d = document.createElement("button");
      d.className = "ik-btn", d.textContent = c.text || "?", d.dataset.callbackData = c.callback_data || "", d.dataset.messageId = String(n), d.addEventListener("click", async () => {
        const m = d.dataset.callbackData || "", p = Number.parseInt(d.dataset.messageId || "0", 10);
        if (!m || u.sending) return;
        const C = d.closest(".inline-keyboard"), H = C ? C.querySelectorAll(".ik-btn") : [];
        for (const y of H) y.disabled = !0;
        u.sending = !0, k(!0), B();
        try {
          const y = await Ee(p, m);
          f(), s(y);
        } catch (y) {
          f(), a(`[Callback error: ${x(y)}]`);
        }
        u.sending = !1, k(!1), r().inputEl.focus();
      }), l.appendChild(d);
    }
    i.appendChild(l);
  }
  e.appendChild(i);
}
let W = null;
function Ie(e) {
  W = e;
}
function De(e) {
  const t = r();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const s = document.createElement("div");
    s.className = "rk-row";
    for (const a of n) {
      const i = document.createElement("button");
      i.className = "rk-btn", i.textContent = a.text || "?", i.addEventListener("click", () => {
        const o = i.textContent || "";
        o && (u.sending || (ce(), W && W(o)));
      }), s.appendChild(i);
    }
    t.replyKeyboardEl.appendChild(s);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function ce() {
  const e = r();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}
function S() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function M(e, t) {
  const n = document.createElement("div");
  return n.className = `message ${e}`, e === "received" && (n.innerHTML = '<div class="sender">Bot</div>'), t !== void 0 && (n.dataset.messageId = String(t)), n;
}
function Oe(e) {
  return r().messagesEl.querySelector(
    `.message[data-message-id="${e}"]`
  );
}
function P() {
  return `<span class="meta">${A()}</span>`;
}
function re(e, t, n, s) {
  const a = r(), i = M(t), o = document.createElement("img");
  if (o.className = "msg-photo", o.src = e, o.alt = "Photo", i.appendChild(o), n) {
    const l = t === "received" && (s != null && s.length) ? N(n, s) : g(n);
    i.innerHTML += `<span class="caption">${l}</span>`;
  }
  i.innerHTML += P(), a.messagesEl.appendChild(i), o.addEventListener("load", () => S()), S();
}
function de(e, t, n, s) {
  const a = r(), i = M(t), o = document.createElement("div");
  o.className = "voice-player";
  const l = document.createElement("audio");
  l.src = e, l.preload = "metadata";
  const c = document.createElement("button");
  c.className = "vp-play", c.innerHTML = "&#9654;";
  const d = document.createElement("div");
  d.className = "vp-track";
  const m = document.createElement("div");
  m.className = "vp-bar";
  const p = document.createElement("div");
  p.className = "vp-fill", m.appendChild(p);
  const C = document.createElement("span");
  if (C.className = "vp-time", C.textContent = "0:00", d.appendChild(m), d.appendChild(C), o.appendChild(c), o.appendChild(d), i.appendChild(o), n) {
    const y = document.createElement("span");
    y.className = "caption";
    const D = t === "received" && (s != null && s.length) ? N(n, s) : g(n);
    y.innerHTML = D, i.appendChild(y);
  }
  const H = document.createElement("span");
  H.className = "meta", H.textContent = A(), i.appendChild(H), a.messagesEl.appendChild(i), l.addEventListener("loadedmetadata", () => {
    C.textContent = q(l.duration);
  }), c.addEventListener("click", () => {
    l.paused ? (l.play(), c.innerHTML = "&#9646;&#9646;") : (l.pause(), c.innerHTML = "&#9654;");
  }), l.addEventListener("timeupdate", () => {
    if (l.duration) {
      const y = l.currentTime / l.duration * 100;
      p.style.width = `${y}%`, C.textContent = q(l.currentTime);
    }
  }), l.addEventListener("ended", () => {
    c.innerHTML = "&#9654;", p.style.width = "0%", C.textContent = q(l.duration);
  }), m.addEventListener("click", (y) => {
    if (l.duration) {
      const D = m.getBoundingClientRect(), pe = (y.clientX - D.left) / D.width;
      l.currentTime = pe * l.duration;
    }
  }), S();
}
function ue(e, t, n, s) {
  const a = r(), i = M(t), o = document.createElement("video");
  if (o.className = "msg-video-note", o.src = e, o.controls = !0, o.playsInline = !0, i.appendChild(o), n) {
    const l = t === "received" && (s != null && s.length) ? N(n, s) : g(n);
    i.innerHTML += `<span class="caption">${l}</span>`;
  }
  i.innerHTML += P(), a.messagesEl.appendChild(i), S();
}
function me(e, t, n, s, a) {
  const i = r(), o = M(n), l = document.createElement("a");
  if (l.className = "doc-attachment", l.href = t ? `${t}?download=1` : "#", l.download = e || "", l.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${g(e)}</span>`, o.appendChild(l), s) {
    const c = n === "received" && (a != null && a.length) ? N(s, a) : g(s);
    o.innerHTML += `<span class="caption">${c}</span>`;
  }
  o.innerHTML += P(), i.messagesEl.appendChild(o), S();
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
    const i = document.createElement("h4");
    i.className = "poll-question", i.textContent = e.poll_question, s.appendChild(i);
  }
  if (e.poll_options && e.message_id) {
    const i = document.createElement("div");
    i.className = "poll-options", e.poll_options.forEach((o, l) => {
      const c = document.createElement("button");
      c.className = "poll-option-btn", c.textContent = o.text, c.onclick = () => qe(e.message_id, [l]), i.appendChild(c);
    }), s.appendChild(i);
  }
  const a = document.createElement("span");
  a.className = "meta", a.textContent = A(), s.appendChild(a), n.messagesEl.appendChild(s), Ue();
}
async function qe(e, t) {
  try {
    k(!0), B();
    let n = !1;
    await Le(e, t, (s) => {
      n || (f(), n = !0), s.text && b(s.text, "received");
    }), n || f();
  } catch (n) {
    f(), x(`Poll vote failed: ${String(n)}`);
  } finally {
    k(!1);
  }
}
function b(e, t, n, s) {
  const a = r(), i = M(t, s), o = t === "received" && (n != null && n.length) ? N(e, n) : g(e);
  i.innerHTML += `<span class="text">${o}</span>${P()}`, a.messagesEl.appendChild(i), S();
}
function K(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function Ke(e, t) {
  const n = r(), s = M(t), a = document.createElement("div");
  a.className = "invoice-card";
  const i = document.createElement("div");
  if (i.className = "invoice-title", i.textContent = e.title || "Invoice", a.appendChild(i), e.description) {
    const p = document.createElement("div");
    p.className = "invoice-desc", p.textContent = e.description, a.appendChild(p);
  }
  const o = e.currency || "", l = e.total_amount ?? 0, c = document.createElement("div");
  c.className = "invoice-amount", c.textContent = K(o, l), a.appendChild(c);
  const d = document.createElement("button");
  d.className = "invoice-pay", d.textContent = `Pay ${K(o, l)}`, d.addEventListener("click", async () => {
    if (!u.sending) {
      u.sending = !0, k(!0), d.disabled = !0, d.textContent = "Paying...", B();
      try {
        let p = !1;
        await be(e.message_id, (C) => {
          p || (f(), p = !0), _(C);
        }), p || f(), d.textContent = "Paid";
      } catch (p) {
        f(), d.disabled = !1, d.textContent = `Pay ${K(o, l)}`, b(`[Payment error: ${x(p)}]`, "received");
      }
      u.sending = !1, k(!1), n.inputEl.focus();
    }
  }), a.appendChild(d), s.appendChild(a);
  const m = document.createElement("span");
  m.className = "meta", m.textContent = A(), s.appendChild(m), n.messagesEl.appendChild(s), S();
}
function Je(e, t) {
  const n = N(t.text || "", t.entities ?? []), s = t.reply_markup || null;
  e.innerHTML = '<div class="sender">Bot</div>', e.innerHTML += `<span class="text">${n}</span>${P()}`, s && s.inline_keyboard && le(
    e,
    s.inline_keyboard,
    t.message_id,
    _,
    (a) => b(a, "received")
  ), S();
}
function _(e) {
  const t = r(), n = e.reply_markup || null;
  if (e.is_edit && e.type === "text") {
    const s = Oe(e.message_id);
    if (s) {
      Je(s, e);
      return;
    }
  }
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const s = M("received", e.message_id), a = N(e.text || "", e.entities ?? []);
      s.innerHTML += `<span class="text">${a}</span>${P()}`, t.messagesEl.appendChild(s), le(
        s,
        n.inline_keyboard,
        e.message_id,
        _,
        (i) => b(i, "received")
      ), S();
    } else
      b(e.text || "", "received", e.entities, e.message_id);
    n && n.keyboard && De(n.keyboard);
    return;
  }
  if (e.type === "invoice") {
    Ke(e, "received");
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
  b(`[Unknown response type: ${e.type}]`, "received");
}
async function je() {
  const e = r();
  e.startBtn.disabled = !0, Te(), b("/start", "sent"), B();
  try {
    let t = !1;
    await ee("/start", (n) => {
      t || (f(), t = !0), _(n);
    }), t || f(), await X();
  } catch (t) {
    f(), b(`[Error: ${x(t)}]`, "received");
  } finally {
    e.startBtn.disabled = !1;
  }
}
async function We() {
  const e = r();
  e.resetBtn.disabled = !0;
  try {
    await Ce(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div><div class="empty-placeholder" id="emptyPlaceholder">No messages here yet...</div>', ce(), xe(), Be(), ke(), te();
  } catch (t) {
    b(`[Reset failed: ${x(t)}]`, "received");
  }
  e.resetBtn.disabled = !1;
}
async function O(e, t) {
  const n = r(), s = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!(!e || u.sending)) {
    L(), u.sending = !0, k(!0), s && (n.inputEl.value = ""), b(e, "sent"), B();
    try {
      let a = !1;
      await ee(e, (i) => {
        a || (f(), a = !0), _(i);
      }), a || f(), await X();
    } catch (a) {
      f(), b(`[${x(a)}]`, "received");
    }
    u.sending = !1, k(!1), n.inputEl.focus();
  }
}
async function Ve(e, t, n) {
  let s = !1;
  await ve(e, t, n, (a) => {
    s || (f(), s = !0), _(a);
  }), s || f();
}
async function Z() {
  const e = r(), t = e.inputEl.value.trim(), n = u.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await O(t, { clearInput: !0 });
    return;
  }
  if (u.sending) return;
  L(), u.sending = !0, k(!0), e.inputEl.value = "";
  const s = Pe();
  for (const [a, i] of s.entries()) {
    const o = a === 0 ? t : "";
    switch (i.type) {
      case "photo": {
        re(i.localUrl, "sent", o);
        break;
      }
      case "voice": {
        de(i.localUrl, "sent", o);
        break;
      }
      case "video_note": {
        ue(i.localUrl, "sent", o);
        break;
      }
      default:
        me(i.file.name, i.localUrl, "sent", o);
    }
    B();
    try {
      await Ve(i.file, i.type, o);
    } catch (l) {
      f(), b(`[${x(l)}]`, "received");
    }
  }
  u.sending = !1, k(!1), e.inputEl.focus(), await X();
}
function Ge() {
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = r();
  Ie(async (n) => {
    await O(n, { clearInput: !1 });
  }), $e(async (n) => {
    await O(n, { clearInput: !1 });
  }), _e(), t.sendBtn.addEventListener("click", () => {
    Z();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && Z();
  }), t.resetBtn.addEventListener("click", () => {
    We();
  }), t.startBtn.addEventListener("click", () => {
    je();
  }), t.messagesEl.addEventListener("click", (n) => {
    const s = n.target;
    if (s.classList.contains("tg-command")) {
      const a = s.dataset.command;
      a && O(a, { clearInput: !0 });
    }
    s.classList.contains("tg-spoiler") && !s.classList.contains("revealed") && s.classList.add("revealed");
  }), te();
}
Ge();
