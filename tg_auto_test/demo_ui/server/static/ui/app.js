let se = 0;
const X = /* @__PURE__ */ new Set();
function Te(e) {
  return se += 1, `${e}-${se}`;
}
function B(e) {
  return `[demo ${e}]`;
}
function N(e, t, n = {}) {
  return {
    trace_id: e,
    scope: "ui",
    name: t,
    ts: (/* @__PURE__ */ new Date()).toISOString(),
    payload: n
  };
}
function $e(e) {
  return `${B(e.id)} ${e.action}`;
}
function Se(e) {
  X.has(e.id) || (X.add(e.id), console.groupCollapsed($e(e)));
}
function le(e) {
  X.has(e) && (X.delete(e), console.groupEnd());
}
function P(e, t = {}) {
  const n = { action: e, id: Te(e) };
  return Se(n), console.debug(B(n.id), N(n.id, e, t)), n;
}
function x(e, t = {}, n) {
  if (n) {
    console.debug(B(n), N(n, e, t));
    return;
  }
  console.debug("[demo]", {
    ...N("standalone", e, t),
    trace_id: "standalone"
  });
}
function xe(e) {
  console.debug(B(e.trace_id), e);
}
function Me(e, t) {
  const n = {
    is_edit: !!t.is_edit,
    message_id: t.message_id,
    message_type: t.type
  };
  if (e) {
    console.info(B(e), N(e, "message_rendered", n));
    return;
  }
  console.info("[demo]", N("standalone", "message_rendered", n));
}
function H(e, t = {}) {
  console.debug(B(e.id), N(e.id, "request_completed", t)), le(e.id);
}
function F(e, t, n = {}) {
  console.error(B(e.id), N(e.id, "ui_error", {
    ...n,
    message: t instanceof Error ? t.message : String(t)
  })), le(e.id);
}
async function re(e) {
  return await e.json();
}
async function z(e, t, n) {
  try {
    const s = await n.json();
    if (s.detail)
      return new Error(s.detail);
  } catch {
  }
  return new Error(`${e} ${t} failed: ${n.status} ${n.statusText}`);
}
async function Ne(e) {
  const t = await fetch(e, { method: "GET" });
  if (!t.ok) throw await z("GET", e, t);
  return await re(t);
}
async function Be(e) {
  const t = await fetch(e, { method: "POST" });
  if (!t.ok) throw await z("POST", e, t);
  return await re(t);
}
async function W(e, t, n, s = {}) {
  const i = await fetch(e, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...s },
    body: JSON.stringify(t)
  });
  if (!i.ok) throw await z("POST", e, i);
  await de(i, n);
}
async function Pe(e, t, n, s = {}) {
  const i = await fetch(e, { method: "POST", body: t, headers: s });
  if (!i.ok) throw await z("POST", e, i);
  await de(i, n);
}
async function de(e, t) {
  var o;
  const n = (o = e.body) == null ? void 0 : o.getReader();
  if (!n) return;
  const s = new TextDecoder();
  let i = "", a = "";
  for (; ; ) {
    const { done: c, value: l } = await n.read();
    if (c) break;
    i += s.decode(l, { stream: !0 });
    const d = i.split(`

`);
    i = d.pop() ?? "";
    for (const m of d) {
      const k = m.split(`
`).map((p) => p.trim()).filter(Boolean);
      let b = "message";
      const T = [];
      for (const p of k)
        p.startsWith("event: ") && (b = p.slice(7)), p.startsWith("data: ") && T.push(p.slice(6));
      if (T.length === 0) continue;
      const g = T.join(`
`);
      if (g !== "[DONE]") {
        if (b === "trace") {
          const p = JSON.parse(g);
          if (t.onTrace(p), p.name === "request_failed") {
            const j = p.payload.detail;
            a = typeof j == "string" ? j : "Demo request failed";
          }
          continue;
        }
        t.onMessage(JSON.parse(g));
      }
    }
  }
  if (a) throw new Error(a);
}
async function ue(e, t, n) {
  await W("/api/message", { text: e }, n, { "X-Demo-Trace-Id": t });
}
async function He(e, t, n, s, i) {
  const a = new FormData();
  a.append("file", e), n && a.append("caption", n), await Pe(`/api/${t}`, a, i, { "X-Demo-Trace-Id": s });
}
async function Fe(e, t, n, s) {
  await W(
    "/api/callback",
    { message_id: e, data: t },
    s,
    { "X-Demo-Trace-Id": n }
  );
}
async function Ie(e, t, n) {
  await W(
    "/api/invoice/pay",
    { message_id: e },
    n,
    { "X-Demo-Trace-Id": t }
  );
}
async function De() {
  return await Be("/api/reset");
}
async function Ue() {
  return await Ne("/api/state");
}
async function Oe(e, t, n, s) {
  await W(
    "/api/poll/vote",
    { message_id: e, option_ids: t },
    s,
    { "X-Demo-Trace-Id": n }
  );
}
const u = {
  sending: !1,
  stagedFiles: []
};
let K = null;
function v(e) {
  const t = document.getElementById(e);
  if (!t) throw new Error(`Missing element: #${e}`);
  return t;
}
function r() {
  if (K) return K;
  const e = document.querySelector(".chat-container");
  if (!e) throw new Error("Missing element: .chat-container");
  const t = document.querySelector(".chat-input");
  if (!t) throw new Error("Missing element: .chat-input");
  return K = {
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
    chatContainer: e,
    emptyPlaceholder: v("emptyPlaceholder"),
    startContainer: v("startContainer"),
    startBtn: v("startBtn"),
    chatInputEl: t
  }, K;
}
function L(e) {
  const t = r();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
function Re() {
  K = null;
}
function me() {
  const e = r();
  e.emptyPlaceholder.style.display = "", e.startContainer.style.display = "", e.chatInputEl.style.display = "none";
}
function qe() {
  const e = r();
  e.emptyPlaceholder.style.display = "none", e.startContainer.style.display = "none", e.chatInputEl.style.display = "flex";
}
const S = {
  botCommands: [],
  menuButtonType: "default"
};
let E = !1, $ = "menu", _ = [], C = -1, ee = null;
function Ae(e) {
  ee = e;
  const t = r();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !u.sending && t.menuBtn.classList.contains("visible")) {
      if (E && $ === "menu") {
        w(), te();
        return;
      }
      pe();
    }
  }), t.inputEl.addEventListener("input", () => {
    te();
  }), t.inputEl.addEventListener("keydown", (n) => {
    if (E) {
      if (n.key === "Escape") {
        n.preventDefault(), w();
        return;
      }
      if (_.length > 0) {
        if (n.key === "ArrowDown") {
          n.preventDefault(), ae(1);
          return;
        }
        if (n.key === "ArrowUp") {
          n.preventDefault(), ae(-1);
          return;
        }
      }
      n.key === "Enter" && he() && n.preventDefault();
    }
  }), document.addEventListener("click", (n) => {
    if (!E) return;
    const s = n.target;
    s instanceof Node && (t.commandPanelEl.contains(s) || t.menuBtn.contains(s) || t.inputEl.contains(s) || w());
  });
}
function w() {
  const e = r();
  E = !1, $ = "menu", _ = [], C = -1, e.commandPanelEl.classList.remove("visible"), e.commandPanelEl.innerHTML = "";
}
function pe() {
  fe("menu", S.botCommands, "Commands");
}
function te() {
  if (E && $ === "menu") return;
  const e = Ke();
  if (e === null || S.botCommands.length === 0) {
    E && $ === "slash" && w();
    return;
  }
  const t = [];
  for (const n of S.botCommands)
    n.command && n.command.indexOf(e) === 0 && t.push(n);
  if (t.length === 0) {
    E && $ === "slash" && w();
    return;
  }
  fe("slash", t, e ? `Commands matching "/${e}"` : "Commands");
}
function Ke() {
  const { inputEl: e } = r(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function fe(e, t, n) {
  const s = r();
  $ = e, _ = Array.isArray(t) ? t : [], C = _.length > 0 ? 0 : -1, E = !0, s.commandPanelEl.innerHTML = "";
  const i = document.createElement("div");
  i.className = "cp-card";
  const a = document.createElement("div");
  if (a.className = "cp-header", a.textContent = n, i.appendChild(a), _.length === 0) {
    const o = document.createElement("div");
    o.className = "cp-empty", o.textContent = "No commands.", i.appendChild(o);
  } else
    for (const [o, c] of _.entries()) {
      const l = document.createElement("button");
      l.type = "button", l.className = `cp-item${o === C ? " selected" : ""}`, l.dataset.index = String(o), l.addEventListener("click", () => {
        const m = Number.parseInt(l.dataset.index || "", 10);
        Number.isFinite(m) && (C = m, ge(), he());
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
function ge() {
  const t = r().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, s] of t.entries())
    n === C ? s.classList.add("selected") : s.classList.remove("selected");
}
function ae(e) {
  !E || _.length === 0 || (C = (C + e) % _.length, C < 0 && (C += _.length), ge());
}
function he() {
  if (!E || C < 0 || C >= _.length) return !1;
  const t = _[C].command || "";
  if (!t) return !1;
  const { inputEl: n } = r();
  return $ === "slash" ? (n.value = `/${t} `, w(), n.focus(), !0) : (w(), ee && ee(`/${t}`), !0);
}
function ve() {
  const e = r();
  S.menuButtonType === "commands" && S.botCommands.length > 0 ? e.menuBtn.classList.add("visible") : (e.menuBtn.classList.remove("visible"), E && $ === "menu" && w());
}
async function ye() {
  try {
    const e = await Ue();
    S.botCommands = Array.isArray(e.commands) ? e.commands : [], S.menuButtonType = e.menu_button_type || "default", ve(), E && $ === "menu" ? pe() : E || te();
  } catch {
  }
}
function je() {
  S.botCommands = [], S.menuButtonType = "default", ve(), w();
}
function ie(e) {
  const t = e.type || "";
  return t.startsWith("image/") ? "photo" : t.startsWith("audio/") ? "voice" : t.startsWith("video/") ? "video_note" : "document";
}
function oe(e) {
  const t = URL.createObjectURL(e);
  u.stagedFiles.push({ file: e, type: ie(e), localUrl: t }), x("files_staged", { filename: e.name, size_bytes: e.size, kind: ie(e) }), G();
}
function Je(e) {
  const t = u.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), u.stagedFiles.splice(e, 1), x("files_unstaged", { filename: t.file.name, kind: t.type }), G());
}
function Xe() {
  for (const e of u.stagedFiles) URL.revokeObjectURL(e.localUrl);
  u.stagedFiles.length > 0 && x("files_unstaged", { count: u.stagedFiles.length, mode: "clear_all" }), u.stagedFiles = [], G();
}
function ze() {
  const e = [...u.stagedFiles];
  return u.stagedFiles = [], G(), e;
}
function G() {
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
      Number.isFinite(o) && Je(o);
    }), s.appendChild(a), e.stagedFilesEl.appendChild(s);
  }
}
function We() {
  const e = r();
  e.attachBtn.addEventListener("click", () => {
    u.sending || e.fileInput.click();
  }), e.fileInput.addEventListener("change", () => {
    const t = e.fileInput.files;
    if (t && t.length > 0)
      for (let n = 0; n < t.length; n++) oe(t[n]);
    e.fileInput.value = "", e.inputEl.focus();
  }), e.chatContainer.addEventListener("dragover", (t) => {
    t.preventDefault(), t.stopPropagation();
  }), e.chatContainer.addEventListener("drop", (t) => {
    var s;
    t.preventDefault(), t.stopPropagation();
    const n = (s = t.dataTransfer) == null ? void 0 : s.files;
    if (n && n.length > 0)
      for (let i = 0; i < n.length; i++) oe(n[i]);
  });
}
function O(e, t) {
  return {
    onMessage(n) {
      t(n), Me(e, n);
    },
    onTrace(n) {
      xe(n);
    }
  };
}
function h(e) {
  const t = document.createElement("div");
  return t.textContent = e, t.innerHTML;
}
function Q(e) {
  const t = /\/([a-zA-Z0-9_]{1,32})(?=\s|$)/g;
  let n = "", s = 0, i;
  for (; (i = t.exec(e)) !== null; )
    n += h(e.slice(s, i.index)), n += `<span class="tg-command" data-command="${h(i[0])}">${h(i[0])}</span>`, s = i.index + i[0].length;
  return n += h(e.slice(s)), n;
}
function Ge(e) {
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
      return e.language ? `<pre><code class="language-${h(e.language)}">` : "<pre>";
    case "url":
      return "";
    case "text_url":
      return `<a href="${h(e.url ?? "")}" target="_blank" rel="noopener">`;
    case "spoiler":
      return '<span class="tg-spoiler">';
    default:
      return "";
  }
}
function Ve(e) {
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
function I(e, t) {
  if (t.length === 0) return Q(e);
  const n = [...t].sort(
    (a, o) => a.offset !== o.offset ? a.offset - o.offset : o.length - a.length
  );
  let s = "", i = 0;
  for (const a of n) {
    const o = Math.max(0, Math.min(a.offset, e.length)), c = Math.max(o, Math.min(a.offset + a.length, e.length));
    if (o > i && (s += Q(e.slice(i, o))), c > o) {
      const l = e.slice(o, c);
      a.type === "url" ? s += `<a href="${h(l)}" target="_blank" rel="noopener">${h(l)}</a>` : s += Ge(a) + h(l) + Ve(a), i = c;
    }
  }
  return i < e.length && (s += Q(e.slice(i))), s;
}
function D(e) {
  return e instanceof Error ? e.message : String(e);
}
function V() {
  const e = /* @__PURE__ */ new Date();
  return `${e.getHours().toString().padStart(2, "0")}:${e.getMinutes().toString().padStart(2, "0")}`;
}
function Z(e) {
  if (!Number.isFinite(e) || e < 0) return "0:00";
  const t = Math.floor(e / 60), n = Math.floor(e % 60);
  return `${t}:${n < 10 ? "0" : ""}${n}`;
}
function R() {
  const e = r();
  e.typingEl.classList.add("visible"), e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function f() {
  r().typingEl.classList.remove("visible");
}
function Y(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function Qe(e, t) {
  const n = r(), s = document.createElement("div");
  s.className = `message ${t}`, s.innerHTML = '<div class="sender">Bot</div>', s.appendChild(e);
  const i = document.createElement("span");
  i.className = "meta", i.textContent = V(), s.appendChild(i), n.messagesEl.appendChild(s), n.messagesEl.scrollTop = n.messagesEl.scrollHeight;
}
function Ze(e, t, n) {
  const s = document.createElement("div");
  s.className = "invoice-card";
  const i = document.createElement("div");
  if (i.className = "invoice-title", i.textContent = e.title || "Invoice", s.appendChild(i), e.description) {
    const d = document.createElement("div");
    d.className = "invoice-desc", d.textContent = e.description, s.appendChild(d);
  }
  const a = e.currency || "", o = e.total_amount ?? 0, c = document.createElement("div");
  c.className = "invoice-amount", c.textContent = Y(a, o), s.appendChild(c);
  const l = document.createElement("button");
  l.className = "invoice-pay", l.textContent = `Pay ${Y(a, o)}`, l.addEventListener("click", async () => {
    if (u.sending) return;
    const d = P("invoice_pay_clicked", { message_id: e.message_id });
    u.sending = !0, L(!0), l.disabled = !0, l.textContent = "Paying...", R();
    try {
      await Ie(
        e.message_id,
        d.id,
        O(d.id, (m) => {
          f(), n.onResponse(m);
        })
      ), f(), l.textContent = "Paid", H(d, { status: "ok" });
    } catch (m) {
      f(), l.disabled = !1, l.textContent = `Pay ${Y(a, o)}`, n.onErrorText(`[Payment error: ${D(m)}]`), F(d, m, { message_id: e.message_id });
    }
    u.sending = !1, L(!1), r().inputEl.focus();
  }), s.appendChild(l), Qe(s, t);
}
function Ee(e, t, n, s, i) {
  const a = document.createElement("div");
  a.className = "inline-keyboard";
  for (const o of t) {
    const c = document.createElement("div");
    c.className = "ik-row";
    for (const l of o) {
      const d = document.createElement("button");
      d.className = "ik-btn", d.textContent = l.text || "?", d.dataset.callbackData = l.callback_data || "", d.dataset.messageId = String(n), d.addEventListener("click", async () => {
        const m = d.dataset.callbackData || "", k = Number.parseInt(d.dataset.messageId || "0", 10);
        if (!m || u.sending) return;
        const b = d.closest(".inline-keyboard"), T = b ? b.querySelectorAll(".ik-btn") : [];
        for (const p of T) p.disabled = !0;
        const g = P("callback_clicked", { callback_data: m, message_id: k });
        u.sending = !0, L(!0), R();
        try {
          await Fe(
            k,
            m,
            g.id,
            O(g.id, (p) => {
              f(), s(p);
            })
          ), f(), H(g, { status: "ok" });
        } catch (p) {
          f(), i(`[Callback error: ${D(p)}]`), F(g, p, { callback_data: m, message_id: k });
        }
        u.sending = !1, L(!1), r().inputEl.focus();
      }), c.appendChild(d);
    }
    a.appendChild(c);
  }
  e.appendChild(a);
}
let ne = null;
function Ye(e) {
  ne = e;
}
function et(e) {
  const t = r();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const s = document.createElement("div");
    s.className = "rk-row";
    for (const i of n) {
      const a = document.createElement("button");
      a.className = "rk-btn", a.textContent = i.text || "?", a.addEventListener("click", () => {
        const o = a.textContent || "";
        o && (u.sending || (be(), ne && ne(o)));
      }), s.appendChild(a);
    }
    t.replyKeyboardEl.appendChild(s);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function be() {
  const e = r();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}
function M() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function q(e, t) {
  const n = document.createElement("div");
  return n.className = `message ${e}`, e === "received" && (n.innerHTML = '<div class="sender">Bot</div>'), t !== void 0 && (n.dataset.messageId = String(t)), n;
}
function tt(e) {
  return r().messagesEl.querySelector(
    `.message[data-message-id="${e}"]`
  );
}
function A() {
  return `<span class="meta">${V()}</span>`;
}
function Ce(e, t, n, s) {
  const i = r(), a = q(t), o = document.createElement("img");
  if (o.className = "msg-photo", o.src = e, o.alt = "Photo", a.appendChild(o), n) {
    const c = t === "received" && (s != null && s.length) ? I(n, s) : h(n);
    a.innerHTML += `<span class="caption">${c}</span>`;
  }
  a.innerHTML += A(), i.messagesEl.appendChild(a), o.addEventListener("load", () => M()), M();
}
function _e(e, t, n, s) {
  const i = r(), a = q(t), o = document.createElement("div");
  o.className = "voice-player";
  const c = document.createElement("audio");
  c.src = e, c.preload = "metadata";
  const l = document.createElement("button");
  l.className = "vp-play", l.innerHTML = "&#9654;";
  const d = document.createElement("div");
  d.className = "vp-track";
  const m = document.createElement("div");
  m.className = "vp-bar";
  const k = document.createElement("div");
  k.className = "vp-fill", m.appendChild(k);
  const b = document.createElement("span");
  if (b.className = "vp-time", b.textContent = "0:00", d.appendChild(m), d.appendChild(b), o.appendChild(l), o.appendChild(d), a.appendChild(o), n) {
    const g = document.createElement("span");
    g.className = "caption";
    const p = t === "received" && (s != null && s.length) ? I(n, s) : h(n);
    g.innerHTML = p, a.appendChild(g);
  }
  const T = document.createElement("span");
  T.className = "meta", T.textContent = V(), a.appendChild(T), i.messagesEl.appendChild(a), c.addEventListener("loadedmetadata", () => {
    b.textContent = Z(c.duration);
  }), l.addEventListener("click", () => {
    c.paused ? (c.play(), l.innerHTML = "&#9646;&#9646;") : (c.pause(), l.innerHTML = "&#9654;");
  }), c.addEventListener("timeupdate", () => {
    if (c.duration) {
      const g = c.currentTime / c.duration * 100;
      k.style.width = `${g}%`, b.textContent = Z(c.currentTime);
    }
  }), c.addEventListener("ended", () => {
    l.innerHTML = "&#9654;", k.style.width = "0%", b.textContent = Z(c.duration);
  }), m.addEventListener("click", (g) => {
    if (c.duration) {
      const p = m.getBoundingClientRect(), j = (g.clientX - p.left) / p.width;
      c.currentTime = j * c.duration;
    }
  }), M();
}
function we(e, t, n, s) {
  const i = r(), a = q(t), o = document.createElement("video");
  if (o.className = "msg-video-note", o.src = e, o.controls = !0, o.playsInline = !0, a.appendChild(o), n) {
    const c = t === "received" && (s != null && s.length) ? I(n, s) : h(n);
    a.innerHTML += `<span class="caption">${c}</span>`;
  }
  a.innerHTML += A(), i.messagesEl.appendChild(a), M();
}
function ke(e, t, n, s, i) {
  const a = r(), o = q(n), c = document.createElement("a");
  if (c.className = "doc-attachment", c.href = t ? `${t}?download=1` : "#", c.download = e || "", c.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${h(e)}</span>`, o.appendChild(c), s) {
    const l = n === "received" && (i != null && i.length) ? I(s, i) : h(s);
    o.innerHTML += `<span class="caption">${l}</span>`;
  }
  o.innerHTML += A(), a.messagesEl.appendChild(o), M();
}
function nt() {
  const e = r();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function st(e) {
  const t = document.createElement("div");
  return t.className = `message ${e}`, t.innerHTML = '<div class="sender">Bot</div>', t;
}
function at(e, t) {
  const n = r(), s = st(t);
  if (e.poll_question) {
    const a = document.createElement("h4");
    a.className = "poll-question", a.textContent = e.poll_question, s.appendChild(a);
  }
  if (e.poll_options && e.message_id) {
    const a = document.createElement("div");
    a.className = "poll-options", e.poll_options.forEach((o, c) => {
      const l = document.createElement("button");
      l.className = "poll-option-btn", l.textContent = o.text, l.onclick = () => it(e.message_id, [c]), a.appendChild(l);
    }), s.appendChild(a);
  }
  const i = document.createElement("span");
  i.className = "meta", i.textContent = V(), s.appendChild(i), n.messagesEl.appendChild(s), nt();
}
async function it(e, t) {
  const n = P("poll_vote_submitted", { message_id: e, option_ids: t });
  try {
    L(!0), R(), await Oe(
      e,
      t,
      n.id,
      O(n.id, (s) => {
        f(), s.text && y(s.text, "received");
      })
    ), f(), H(n, { status: "ok" });
  } catch (s) {
    f(), y(`[Poll vote failed: ${D(s)}]`, "received"), F(n, s, { message_id: e });
  } finally {
    L(!1);
  }
}
function y(e, t, n, s) {
  const i = r(), a = q(t, s), o = t === "received" && (n != null && n.length) ? I(e, n) : h(e);
  a.innerHTML += `<span class="text">${o}</span>${A()}`, i.messagesEl.appendChild(a), M();
}
function ot(e, t) {
  const n = I(t.text || "", t.entities ?? []), s = t.reply_markup || null;
  e.innerHTML = '<div class="sender">Bot</div>', e.innerHTML += `<span class="text">${n}</span>${A()}`, s && s.inline_keyboard && Ee(
    e,
    s.inline_keyboard,
    t.message_id,
    U,
    (i) => y(i, "received")
  ), M();
}
function U(e) {
  const t = r(), n = e.reply_markup || null;
  if (e.is_edit && e.type === "text") {
    const s = tt(e.message_id);
    if (s) {
      ot(s, e);
      return;
    }
  }
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const s = q("received", e.message_id), i = I(e.text || "", e.entities ?? []);
      s.innerHTML += `<span class="text">${i}</span>${A()}`, t.messagesEl.appendChild(s), Ee(
        s,
        n.inline_keyboard,
        e.message_id,
        U,
        (a) => y(a, "received")
      ), M();
    } else
      y(e.text || "", "received", e.entities, e.message_id);
    n && n.keyboard && et(n.keyboard);
    return;
  }
  if (e.type === "invoice") {
    Ze(e, "received", {
      onErrorText: (s) => y(s, "received"),
      onResponse: U
    });
    return;
  }
  if (e.type === "photo") {
    Ce(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "voice") {
    _e(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "video_note") {
    we(`/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "document") {
    ke(e.filename || "", `/api/file/${e.file_id || ""}`, "received", e.text || void 0, e.entities);
    return;
  }
  if (e.type === "poll") {
    at(e, "received");
    return;
  }
  y(`[Unknown response type: ${e.type}]`, "received");
}
async function ct() {
  const e = r();
  e.startBtn.disabled = !0, qe(), y("/start", "sent"), R();
  const t = P("start_clicked", { command: "/start" });
  try {
    await ue(
      "/start",
      t.id,
      O(t.id, (n) => {
        f(), U(n);
      })
    ), f(), x("state_refresh_started", {}, t.id), await ye(), x("state_refresh_completed", {}, t.id), H(t, { status: "ok" });
  } catch (n) {
    f(), y(`[Error: ${D(n)}]`, "received"), F(t, n, { command: "/start" });
  } finally {
    e.startBtn.disabled = !1;
  }
}
async function lt() {
  const e = r();
  e.resetBtn.disabled = !0;
  const t = P("reset_clicked");
  try {
    await De(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div><div class="empty-placeholder" id="emptyPlaceholder">No messages here yet...</div>', be(), je(), Xe(), Re(), me(), H(t, { status: "ok" });
  } catch (n) {
    y(`[Reset failed: ${D(n)}]`, "received"), F(t, n);
  }
  e.resetBtn.disabled = !1;
}
async function Le(e) {
  x("state_refresh_started", {}, e), await ye(), x("state_refresh_completed", {}, e);
}
async function J(e, t) {
  const n = r(), s = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!e || u.sending) return;
  w(), u.sending = !0, L(!0), s && (n.inputEl.value = ""), y(e, "sent"), R();
  const i = P("send_text", { text: e });
  try {
    await ue(
      e,
      i.id,
      O(i.id, (a) => {
        f(), U(a);
      })
    ), f(), await Le(i.id), H(i, { status: "ok" });
  } catch (a) {
    f(), y(`[${D(a)}]`, "received"), F(i, a, { text: e });
  }
  u.sending = !1, L(!1), n.inputEl.focus();
}
async function rt(e, t, n, s) {
  await He(
    e,
    t,
    n,
    s,
    O(s, (i) => {
      f(), U(i);
    })
  ), f();
}
async function ce() {
  const e = r(), t = e.inputEl.value.trim(), n = u.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await J(t, { clearInput: !0 });
    return;
  }
  if (u.sending) return;
  w(), u.sending = !0, L(!0), e.inputEl.value = "";
  const s = ze();
  for (const [i, a] of s.entries()) {
    const o = i === 0 ? t : "", c = P("send_file", {
      caption: o,
      filename: a.file.name,
      kind: a.type,
      size_bytes: a.file.size
    });
    switch (a.type) {
      case "photo": {
        Ce(a.localUrl, "sent", o);
        break;
      }
      case "voice": {
        _e(a.localUrl, "sent", o);
        break;
      }
      case "video_note": {
        we(a.localUrl, "sent", o);
        break;
      }
      default:
        ke(a.file.name, a.localUrl, "sent", o);
    }
    R();
    try {
      await rt(a.file, a.type, o, c.id), H(c, { status: "ok" });
    } catch (l) {
      f(), y(`[${D(l)}]`, "received"), F(c, l, { filename: a.file.name });
    }
  }
  u.sending = !1, L(!1), e.inputEl.focus(), await Le("send_file-post");
}
function dt() {
  x("app_initialized");
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = r();
  Ye(async (n) => {
    await J(n, { clearInput: !1 });
  }), Ae(async (n) => {
    await J(n, { clearInput: !1 });
  }), We(), t.sendBtn.addEventListener("click", () => {
    ce();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && ce();
  }), t.resetBtn.addEventListener("click", () => {
    lt();
  }), t.startBtn.addEventListener("click", () => {
    ct();
  }), t.messagesEl.addEventListener("click", (n) => {
    const s = n.target;
    if (s.classList.contains("tg-command")) {
      const i = s.dataset.command;
      i && J(i, { clearInput: !0 });
    }
    s.classList.contains("tg-spoiler") && !s.classList.contains("revealed") && s.classList.add("revealed");
  }), me();
}
dt();
