let se = 0;
const X = /* @__PURE__ */ new Set();
function Te(e) {
  return se += 1, `${e}-${se}`;
}
function P(e) {
  return `[demo ${e}]`;
}
function M(e, t, n = {}) {
  return {
    trace_id: e,
    scope: "ui",
    name: t,
    ts: (/* @__PURE__ */ new Date()).toISOString(),
    payload: n
  };
}
function $e(e) {
  return `${P(e.id)} ${e.action}`;
}
function Ne(e) {
  X.has(e.id) || (X.add(e.id), console.groupCollapsed($e(e)));
}
function ce(e) {
  X.has(e) && (X.delete(e), console.groupEnd());
}
function H(e, t = {}) {
  const n = { action: e, id: Te(e) };
  return Ne(n), console.debug(P(n.id), M(n.id, e, t)), n;
}
function x(e, t = {}, n) {
  if (n) {
    console.debug(P(n), M(n, e, t));
    return;
  }
  console.debug("[demo]", {
    ...M("standalone", e, t),
    trace_id: "standalone"
  });
}
function Se(e) {
  console.debug(P(e.trace_id), e);
}
function xe(e, t) {
  const n = {
    is_edit: !!t.is_edit,
    message_id: t.message_id,
    message_type: t.type
  };
  if (e) {
    console.info(P(e), M(e, "message_rendered", n));
    return;
  }
  console.info("[demo]", M("standalone", "message_rendered", n));
}
function F(e, t = {}) {
  console.debug(P(e.id), M(e.id, "request_completed", t)), ce(e.id);
}
function I(e, t, n = {}) {
  console.error(P(e.id), M(e.id, "ui_error", {
    ...n,
    message: t instanceof Error ? t.message : String(t)
  })), ce(e.id);
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
async function Me(e) {
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
    const { done: l, value: c } = await n.read();
    if (l) break;
    i += s.decode(c, { stream: !0 });
    const r = i.split(`

`);
    i = r.pop() ?? "";
    for (const u of r) {
      const y = u.split(`
`).map((p) => p.trim()).filter(Boolean);
      let h = "message";
      const b = [];
      for (const p of y)
        p.startsWith("event: ") && (h = p.slice(7)), p.startsWith("data: ") && b.push(p.slice(6));
      if (b.length === 0) continue;
      const f = b.join(`
`);
      if (f !== "[DONE]") {
        if (h === "trace") {
          const p = JSON.parse(f);
          if (t.onTrace(p), p.name === "request_failed") {
            const j = p.payload.detail;
            a = typeof j == "string" ? j : "Demo request failed";
          }
          continue;
        }
        t.onMessage(JSON.parse(f));
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
  return await Me("/api/state");
}
async function Re(e, t, n, s) {
  await W(
    "/api/poll/vote",
    { message_id: e, option_ids: t },
    s,
    { "X-Demo-Trace-Id": n }
  );
}
const m = {
  sending: !1,
  stagedFiles: []
};
let K = null;
function E(e) {
  const t = document.getElementById(e);
  if (!t) throw new Error(`Missing element: #${e}`);
  return t;
}
function d() {
  if (K) return K;
  const e = document.querySelector(".chat-container");
  if (!e) throw new Error("Missing element: .chat-container");
  const t = document.querySelector(".chat-input");
  if (!t) throw new Error("Missing element: .chat-input");
  return K = {
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
    chatContainer: e,
    emptyPlaceholder: E("emptyPlaceholder"),
    startContainer: E("startContainer"),
    startBtn: E("startBtn"),
    chatInputEl: t
  }, K;
}
function T(e) {
  const t = d();
  t.sendBtn.disabled = e, t.attachBtn.disabled = e;
}
function Oe() {
  K = null;
}
function me() {
  const e = d();
  e.emptyPlaceholder.style.display = "", e.startContainer.style.display = "", e.chatInputEl.style.display = "none";
}
function qe() {
  const e = d();
  e.emptyPlaceholder.style.display = "none", e.startContainer.style.display = "none", e.chatInputEl.style.display = "flex";
}
const N = {
  botCommands: [],
  menuButtonType: "default"
};
let C = !1, $ = "menu", k = [], _ = -1, ee = null;
function Ae(e) {
  ee = e;
  const t = d();
  t.menuBtn.addEventListener("click", (n) => {
    if (n.preventDefault(), !m.sending && t.menuBtn.classList.contains("visible")) {
      if (C && $ === "menu") {
        L(), te();
        return;
      }
      pe();
    }
  }), t.inputEl.addEventListener("input", () => {
    te();
  }), t.inputEl.addEventListener("keydown", (n) => {
    if (C) {
      if (n.key === "Escape") {
        n.preventDefault(), L();
        return;
      }
      if (k.length > 0) {
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
    if (!C) return;
    const s = n.target;
    s instanceof Node && (t.commandPanelEl.contains(s) || t.menuBtn.contains(s) || t.inputEl.contains(s) || L());
  });
}
function L() {
  const e = d();
  C = !1, $ = "menu", k = [], _ = -1, e.commandPanelEl.classList.remove("visible"), e.commandPanelEl.innerHTML = "";
}
function pe() {
  fe("menu", N.botCommands, "Commands");
}
function te() {
  if (C && $ === "menu") return;
  const e = Ke();
  if (e === null || N.botCommands.length === 0) {
    C && $ === "slash" && L();
    return;
  }
  const t = [];
  for (const n of N.botCommands)
    n.command && n.command.indexOf(e) === 0 && t.push(n);
  if (t.length === 0) {
    C && $ === "slash" && L();
    return;
  }
  fe("slash", t, e ? `Commands matching "/${e}"` : "Commands");
}
function Ke() {
  const { inputEl: e } = d(), t = e.value || "";
  return !t.startsWith("/") || /\s/.test(t) ? null : t.slice(1);
}
function fe(e, t, n) {
  const s = d();
  $ = e, k = Array.isArray(t) ? t : [], _ = k.length > 0 ? 0 : -1, C = !0, s.commandPanelEl.innerHTML = "";
  const i = document.createElement("div");
  i.className = "cp-card";
  const a = document.createElement("div");
  if (a.className = "cp-header", a.textContent = n, i.appendChild(a), k.length === 0) {
    const o = document.createElement("div");
    o.className = "cp-empty", o.textContent = "No commands.", i.appendChild(o);
  } else
    for (const [o, l] of k.entries()) {
      const c = document.createElement("button");
      c.type = "button", c.className = `cp-item${o === _ ? " selected" : ""}`, c.dataset.index = String(o), c.addEventListener("click", () => {
        const u = Number.parseInt(c.dataset.index || "", 10);
        Number.isFinite(u) && (_ = u, ge(), he());
      });
      const r = document.createElement("div");
      if (r.className = "cp-cmd", r.textContent = `/${l.command || "?"}`, c.appendChild(r), l.description) {
        const u = document.createElement("div");
        u.className = "cp-desc", u.textContent = l.description, c.appendChild(u);
      }
      i.appendChild(c);
    }
  s.commandPanelEl.appendChild(i), s.commandPanelEl.classList.add("visible");
}
function ge() {
  const t = d().commandPanelEl.querySelectorAll(".cp-item");
  for (const [n, s] of t.entries())
    n === _ ? s.classList.add("selected") : s.classList.remove("selected");
}
function ae(e) {
  !C || k.length === 0 || (_ = (_ + e) % k.length, _ < 0 && (_ += k.length), ge());
}
function he() {
  if (!C || _ < 0 || _ >= k.length) return !1;
  const t = k[_].command || "";
  if (!t) return !1;
  const { inputEl: n } = d();
  return $ === "slash" ? (n.value = `/${t} `, L(), n.focus(), !0) : (L(), ee && ee(`/${t}`), !0);
}
function ve() {
  const e = d();
  N.menuButtonType === "commands" && N.botCommands.length > 0 ? e.menuBtn.classList.add("visible") : (e.menuBtn.classList.remove("visible"), C && $ === "menu" && L());
}
async function ye() {
  try {
    const e = await Ue();
    N.botCommands = Array.isArray(e.commands) ? e.commands : [], N.menuButtonType = e.menu_button_type || "default", ve(), C && $ === "menu" ? pe() : C || te();
  } catch {
  }
}
function je() {
  N.botCommands = [], N.menuButtonType = "default", ve(), L();
}
function ie(e) {
  const t = e.type || "";
  return t.startsWith("image/") ? "photo" : t.startsWith("audio/") ? "voice" : t.startsWith("video/") ? "video_note" : "document";
}
function oe(e) {
  const t = URL.createObjectURL(e);
  m.stagedFiles.push({ file: e, type: ie(e), localUrl: t }), x("files_staged", { filename: e.name, size_bytes: e.size, kind: ie(e) }), G();
}
function Je(e) {
  const t = m.stagedFiles[e];
  t && (URL.revokeObjectURL(t.localUrl), m.stagedFiles.splice(e, 1), x("files_unstaged", { filename: t.file.name, kind: t.type }), G());
}
function Xe() {
  for (const e of m.stagedFiles) URL.revokeObjectURL(e.localUrl);
  m.stagedFiles.length > 0 && x("files_unstaged", { count: m.stagedFiles.length, mode: "clear_all" }), m.stagedFiles = [], G();
}
function ze() {
  const e = [...m.stagedFiles];
  return m.stagedFiles = [], G(), e;
}
function G() {
  const e = d();
  if (e.stagedFilesEl.innerHTML = "", m.stagedFiles.length === 0) {
    e.stagedFilesEl.classList.remove("visible");
    return;
  }
  e.stagedFilesEl.classList.add("visible");
  for (let t = 0; t < m.stagedFiles.length; t++) {
    const n = m.stagedFiles[t], s = document.createElement("div");
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
      Number.isFinite(o) && Je(o);
    }), s.appendChild(a), e.stagedFilesEl.appendChild(s);
  }
}
function We() {
  const e = d();
  e.attachBtn.addEventListener("click", () => {
    m.sending || e.fileInput.click();
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
      t(n), xe(e, n);
    },
    onTrace(n) {
      Se(n);
    }
  };
}
function v(e) {
  const t = document.createElement("div");
  return t.textContent = e, t.innerHTML;
}
function Q(e) {
  const t = /\/([a-zA-Z0-9_]{1,32})(?=\s|$)/g;
  let n = "", s = 0, i;
  for (; (i = t.exec(e)) !== null; )
    n += v(e.slice(s, i.index)), n += `<span class="tg-command" data-command="${v(i[0])}">${v(i[0])}</span>`, s = i.index + i[0].length;
  return n += v(e.slice(s)), n;
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
      return e.language ? `<pre><code class="language-${v(e.language)}">` : "<pre>";
    case "url":
      return "";
    case "text_url":
      return `<a href="${v(e.url ?? "")}" target="_blank" rel="noopener">`;
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
function D(e, t) {
  if (t.length === 0) return Q(e);
  const n = [...t].sort(
    (a, o) => a.offset !== o.offset ? a.offset - o.offset : o.length - a.length
  );
  let s = "", i = 0;
  for (const a of n) {
    const o = Math.max(0, Math.min(a.offset, e.length)), l = Math.max(o, Math.min(a.offset + a.length, e.length));
    if (o > i && (s += Q(e.slice(i, o))), l > o) {
      const c = e.slice(o, l);
      a.type === "url" ? s += `<a href="${v(c)}" target="_blank" rel="noopener">${v(c)}</a>` : s += Ge(a) + v(c) + Ve(a), i = l;
    }
  }
  return i < e.length && (s += Q(e.slice(i))), s;
}
function U(e) {
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
function q() {
  const e = d();
  e.typingEl.classList.add("visible"), e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function g() {
  d().typingEl.classList.remove("visible");
}
function Y(e, t) {
  return e === "XTR" ? `${t}${t === 1 ? " Star" : " Stars"}` : `${t} ${e}`;
}
function Qe(e, t) {
  const n = d(), s = document.createElement("div");
  s.className = `message ${t}`, s.innerHTML = '<div class="sender">Bot</div>', s.appendChild(e);
  const i = document.createElement("span");
  i.className = "meta", i.textContent = V(), s.appendChild(i), n.messagesEl.appendChild(s), n.messagesEl.scrollTop = n.messagesEl.scrollHeight;
}
function Ze(e, t, n) {
  const s = document.createElement("div");
  s.className = "invoice-card";
  const i = document.createElement("div");
  if (i.className = "invoice-title", i.textContent = e.title || "Invoice", s.appendChild(i), e.description) {
    const r = document.createElement("div");
    r.className = "invoice-desc", r.textContent = e.description, s.appendChild(r);
  }
  const a = e.currency || "", o = e.total_amount ?? 0, l = document.createElement("div");
  l.className = "invoice-amount", l.textContent = Y(a, o), s.appendChild(l);
  const c = document.createElement("button");
  c.className = "invoice-pay", c.textContent = `Pay ${Y(a, o)}`, c.addEventListener("click", async () => {
    if (m.sending) return;
    const r = H("invoice_pay_clicked", { message_id: e.message_id });
    m.sending = !0, T(!0), c.disabled = !0, c.textContent = "Paying...", q();
    try {
      await Ie(
        e.message_id,
        r.id,
        O(r.id, (u) => {
          g(), n.onResponse(u);
        })
      ), g(), c.textContent = "Paid", F(r, { status: "ok" });
    } catch (u) {
      g(), c.disabled = !1, c.textContent = `Pay ${Y(a, o)}`, n.onErrorText(`[Payment error: ${U(u)}]`), I(r, u, { message_id: e.message_id });
    }
    m.sending = !1, T(!1), d().inputEl.focus();
  }), s.appendChild(c), Qe(s, t);
}
function Ee(e, t, n, s, i) {
  const a = document.createElement("div");
  a.className = "inline-keyboard";
  for (const o of t) {
    const l = document.createElement("div");
    l.className = "ik-row";
    for (const c of o) {
      const r = document.createElement("button");
      r.className = "ik-btn", r.textContent = c.text || "?", r.dataset.callbackData = c.callback_data || "", r.dataset.messageId = String(n), r.addEventListener("click", async () => {
        const u = r.dataset.callbackData || "", y = Number.parseInt(r.dataset.messageId || "0", 10);
        if (!u || m.sending) return;
        const h = r.closest(".inline-keyboard"), b = h ? h.querySelectorAll(".ik-btn") : [];
        for (const p of b) p.disabled = !0;
        const f = H("callback_clicked", { callback_data: u, message_id: y });
        m.sending = !0, T(!0), q();
        try {
          await Fe(
            y,
            u,
            f.id,
            O(f.id, (p) => {
              g(), s(p);
            })
          ), g(), F(f, { status: "ok" });
        } catch (p) {
          g(), i(`[Callback error: ${U(p)}]`), I(f, p, { callback_data: u, message_id: y });
        }
        m.sending = !1, T(!1), d().inputEl.focus();
      }), l.appendChild(r);
    }
    a.appendChild(l);
  }
  e.appendChild(a);
}
let ne = null;
function Ye(e) {
  ne = e;
}
function et(e) {
  const t = d();
  t.replyKeyboardEl.innerHTML = "";
  for (const n of e) {
    const s = document.createElement("div");
    s.className = "rk-row";
    for (const i of n) {
      const a = document.createElement("button");
      a.className = "rk-btn", a.textContent = i.text || "?", a.addEventListener("click", () => {
        const o = a.textContent || "";
        o && (m.sending || (be(), ne && ne(o)));
      }), s.appendChild(a);
    }
    t.replyKeyboardEl.appendChild(s);
  }
  t.replyKeyboardEl.classList.add("visible"), t.messagesEl.scrollTop = t.messagesEl.scrollHeight;
}
function be() {
  const e = d();
  e.replyKeyboardEl.classList.remove("visible"), e.replyKeyboardEl.innerHTML = "";
}
function S() {
  const e = d();
  e.messagesEl.scrollTop = e.messagesEl.scrollHeight;
}
function R(e, t) {
  const n = document.createElement("div");
  return n.className = `message ${e}`, e === "received" && (n.innerHTML = '<div class="sender">Bot</div>'), t !== void 0 && (n.dataset.messageId = String(t)), n;
}
function tt(e) {
  return d().messagesEl.querySelector(
    `.message[data-message-id="${e}"]`
  );
}
function A() {
  return `<span class="meta">${V()}</span>`;
}
function Ce(e, t, n, s) {
  const i = d(), a = R(t), o = document.createElement("img");
  if (o.className = "msg-photo", o.src = e, o.alt = "Photo", a.appendChild(o), n) {
    const l = t === "received" && (s != null && s.length) ? D(n, s) : v(n);
    a.innerHTML += `<span class="caption">${l}</span>`;
  }
  a.innerHTML += A(), i.messagesEl.appendChild(a), o.addEventListener("load", () => S()), S();
}
function _e(e, t, n, s) {
  const i = d(), a = R(t), o = document.createElement("div");
  o.className = "voice-player";
  const l = document.createElement("audio");
  l.src = e, l.preload = "metadata";
  const c = document.createElement("button");
  c.className = "vp-play", c.innerHTML = "&#9654;";
  const r = document.createElement("div");
  r.className = "vp-track";
  const u = document.createElement("div");
  u.className = "vp-bar";
  const y = document.createElement("div");
  y.className = "vp-fill", u.appendChild(y);
  const h = document.createElement("span");
  if (h.className = "vp-time", h.textContent = "0:00", r.appendChild(u), r.appendChild(h), o.appendChild(c), o.appendChild(r), a.appendChild(o), n) {
    const f = document.createElement("span");
    f.className = "caption";
    const p = t === "received" && (s != null && s.length) ? D(n, s) : v(n);
    f.innerHTML = p, a.appendChild(f);
  }
  const b = document.createElement("span");
  b.className = "meta", b.textContent = V(), a.appendChild(b), i.messagesEl.appendChild(a), l.addEventListener("loadedmetadata", () => {
    h.textContent = Z(l.duration);
  }), c.addEventListener("click", () => {
    l.paused ? (l.play(), c.innerHTML = "&#9646;&#9646;") : (l.pause(), c.innerHTML = "&#9654;");
  }), l.addEventListener("timeupdate", () => {
    if (l.duration) {
      const f = l.currentTime / l.duration * 100;
      y.style.width = `${f}%`, h.textContent = Z(l.currentTime);
    }
  }), l.addEventListener("ended", () => {
    c.innerHTML = "&#9654;", y.style.width = "0%", h.textContent = Z(l.duration);
  }), u.addEventListener("click", (f) => {
    if (l.duration) {
      const p = u.getBoundingClientRect(), j = (f.clientX - p.left) / p.width;
      l.currentTime = j * l.duration;
    }
  }), S();
}
function we(e, t, n, s) {
  const i = d(), a = R(t), o = document.createElement("video");
  if (o.className = "msg-video-note", o.src = e, o.controls = !0, o.playsInline = !0, a.appendChild(o), n) {
    const l = t === "received" && (s != null && s.length) ? D(n, s) : v(n);
    a.innerHTML += `<span class="caption">${l}</span>`;
  }
  a.innerHTML += A(), i.messagesEl.appendChild(a), S();
}
function ke(e, t, n, s, i) {
  const a = d(), o = R(n), l = document.createElement("a");
  if (l.className = "doc-attachment", l.href = t ? `${t}?download=1` : "#", l.download = e || "", l.innerHTML = `<span class="doc-icon">&#128196;</span><span class="doc-name">${v(e)}</span>`, o.appendChild(l), s) {
    const c = n === "received" && (i != null && i.length) ? D(s, i) : v(s);
    o.innerHTML += `<span class="caption">${c}</span>`;
  }
  o.innerHTML += A(), a.messagesEl.appendChild(o), S();
}
async function nt(e, t) {
  const n = H("poll_vote_submitted", { message_id: e, option_ids: t });
  try {
    T(!0), q(), await Re(
      e,
      t,
      n.id,
      O(n.id, (s) => {
        g(), B(s);
      })
    ), g(), F(n, { status: "ok" });
  } catch (s) {
    g(), w(`[Poll vote failed: ${U(s)}]`, "received"), I(n, s, { message_id: e });
  } finally {
    T(!1);
  }
}
function st(e, t) {
  const n = d(), s = R(t, e.message_id);
  if (e.poll_question) {
    const a = document.createElement("div");
    a.className = "poll-question", a.textContent = e.poll_question, s.appendChild(a);
    const o = document.createElement("div");
    o.className = "poll-type-label", o.textContent = "Poll", s.appendChild(o);
  }
  if (e.poll_options && e.message_id) {
    const a = document.createElement("div");
    a.className = "poll-options", e.poll_options.forEach((o, l) => {
      const c = document.createElement("div");
      c.className = "poll-option-row", c.textContent = o.text, c.onclick = () => {
        at(s, e, l), nt(e.message_id, [l]);
      }, a.appendChild(c);
    }), s.appendChild(a);
  }
  const i = document.createElement("span");
  i.className = "meta", i.textContent = V(), s.appendChild(i), n.messagesEl.appendChild(s), S();
}
function at(e, t, n) {
  const s = e.querySelector(".poll-options");
  !s || !t.poll_options || (s.innerHTML = "", t.poll_options.forEach((i, a) => {
    const o = a === n, l = o ? 100 : 0, c = document.createElement("div");
    c.className = "poll-result-row";
    const r = document.createElement("div");
    r.className = "poll-result-header";
    const u = document.createElement("div");
    u.className = o ? "poll-check" : "poll-dot", o && (u.textContent = "✓"), r.appendChild(u);
    const y = document.createElement("span");
    y.className = "poll-result-pct", y.textContent = `${l}%`, r.appendChild(y);
    const h = document.createElement("span");
    h.className = "poll-result-text", h.textContent = i.text, r.appendChild(h), c.appendChild(r);
    const b = document.createElement("div");
    b.className = "poll-result-bar-track";
    const f = document.createElement("div");
    f.className = "poll-result-bar-fill", f.style.width = "0%", b.appendChild(f), c.appendChild(b), s.appendChild(c), requestAnimationFrame(() => {
      f.style.width = `${l}%`;
    });
  }));
}
function w(e, t, n, s) {
  const i = d(), a = R(t, s), o = t === "received" && (n != null && n.length) ? D(e, n) : v(e);
  a.innerHTML += `<span class="text">${o}</span>${A()}`, i.messagesEl.appendChild(a), S();
}
function it(e, t) {
  const n = D(t.text || "", t.entities ?? []), s = t.reply_markup || null;
  e.innerHTML = '<div class="sender">Bot</div>', e.innerHTML += `<span class="text">${n}</span>${A()}`, s && s.inline_keyboard && Ee(
    e,
    s.inline_keyboard,
    t.message_id,
    B,
    (i) => w(i, "received")
  ), S();
}
function B(e) {
  const t = d(), n = e.reply_markup || null;
  if (e.is_edit && e.type === "text") {
    const s = tt(e.message_id);
    if (s) {
      it(s, e);
      return;
    }
  }
  if (e.type === "text") {
    if (n && n.inline_keyboard) {
      const s = R("received", e.message_id), i = D(e.text || "", e.entities ?? []);
      s.innerHTML += `<span class="text">${i}</span>${A()}`, t.messagesEl.appendChild(s), Ee(
        s,
        n.inline_keyboard,
        e.message_id,
        B,
        (a) => w(a, "received")
      ), S();
    } else
      w(e.text || "", "received", e.entities, e.message_id);
    n && n.keyboard && et(n.keyboard);
    return;
  }
  if (e.type === "invoice") {
    Ze(e, "received", {
      onErrorText: (s) => w(s, "received"),
      onResponse: B
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
    st(e, "received");
    return;
  }
  w(`[Unknown response type: ${e.type}]`, "received");
}
async function ot() {
  const e = d();
  e.startBtn.disabled = !0, qe(), w("/start", "sent"), q();
  const t = H("start_clicked", { command: "/start" });
  try {
    await ue(
      "/start",
      t.id,
      O(t.id, (n) => {
        g(), B(n);
      })
    ), g(), x("state_refresh_started", {}, t.id), await ye(), x("state_refresh_completed", {}, t.id), F(t, { status: "ok" });
  } catch (n) {
    g(), w(`[Error: ${U(n)}]`, "received"), I(t, n, { command: "/start" });
  } finally {
    e.startBtn.disabled = !1;
  }
}
async function lt() {
  const e = d();
  e.resetBtn.disabled = !0;
  const t = H("reset_clicked");
  try {
    await De(), e.messagesEl.innerHTML = '<div class="day-divider"><span>Today</span></div><div class="empty-placeholder" id="emptyPlaceholder">No messages here yet...</div>', be(), je(), Xe(), Oe(), me(), F(t, { status: "ok" });
  } catch (n) {
    w(`[Reset failed: ${U(n)}]`, "received"), I(t, n);
  }
  e.resetBtn.disabled = !1;
}
async function Le(e) {
  x("state_refresh_started", {}, e), await ye(), x("state_refresh_completed", {}, e);
}
async function J(e, t) {
  const n = d(), s = (t == null ? void 0 : t.clearInput) ?? !1;
  if (!e || m.sending) return;
  L(), m.sending = !0, T(!0), s && (n.inputEl.value = ""), w(e, "sent"), q();
  const i = H("send_text", { text: e });
  try {
    await ue(
      e,
      i.id,
      O(i.id, (a) => {
        g(), B(a);
      })
    ), g(), await Le(i.id), F(i, { status: "ok" });
  } catch (a) {
    g(), w(`[${U(a)}]`, "received"), I(i, a, { text: e });
  }
  m.sending = !1, T(!1), n.inputEl.focus();
}
async function ct(e, t, n, s) {
  await He(
    e,
    t,
    n,
    s,
    O(s, (i) => {
      g(), B(i);
    })
  ), g();
}
async function le() {
  const e = d(), t = e.inputEl.value.trim(), n = m.stagedFiles.length > 0;
  if (!t && !n) return;
  if (!n) {
    await J(t, { clearInput: !0 });
    return;
  }
  if (m.sending) return;
  L(), m.sending = !0, T(!0), e.inputEl.value = "";
  const s = ze();
  for (const [i, a] of s.entries()) {
    const o = i === 0 ? t : "", l = H("send_file", {
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
    q();
    try {
      await ct(a.file, a.type, o, l.id), F(l, { status: "ok" });
    } catch (c) {
      g(), w(`[${U(c)}]`, "received"), I(l, c, { filename: a.file.name });
    }
  }
  m.sending = !1, T(!1), e.inputEl.focus(), await Le("send_file-post");
}
function rt() {
  x("app_initialized");
  const e = document.getElementById("buildHint");
  e && (e.style.display = "none");
  const t = d();
  Ye(async (n) => {
    await J(n, { clearInput: !1 });
  }), Ae(async (n) => {
    await J(n, { clearInput: !1 });
  }), We(), t.sendBtn.addEventListener("click", () => {
    le();
  }), t.inputEl.addEventListener("keydown", (n) => {
    n.defaultPrevented || n.key === "Enter" && le();
  }), t.resetBtn.addEventListener("click", () => {
    lt();
  }), t.startBtn.addEventListener("click", () => {
    ot();
  }), t.messagesEl.addEventListener("click", (n) => {
    const s = n.target;
    if (s.classList.contains("tg-command")) {
      const i = s.dataset.command;
      i && J(i, { clearInput: !0 });
    }
    s.classList.contains("tg-spoiler") && !s.classList.contains("revealed") && s.classList.add("revealed");
  }), me();
}
rt();
