/* @ds-bundle: {"format":4,"namespace":"NeroesDesignSystem_23f8b7","components":[{"name":"Button","sourcePath":"components/actions/Button.jsx"},{"name":"IconButton","sourcePath":"components/actions/IconButton.jsx"},{"name":"Metric","sourcePath":"components/data/Metric.jsx"},{"name":"StatusDot","sourcePath":"components/data/StatusDot.jsx"},{"name":"TraceChart","sourcePath":"components/data/TraceChart.jsx"},{"name":"Badge","sourcePath":"components/display/Badge.jsx"},{"name":"Card","sourcePath":"components/display/Card.jsx"},{"name":"Divider","sourcePath":"components/display/Divider.jsx"},{"name":"Tabs","sourcePath":"components/display/Tabs.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Radio","sourcePath":"components/forms/Radio.jsx"},{"name":"Select","sourcePath":"components/forms/Select.jsx"},{"name":"Switch","sourcePath":"components/forms/Switch.jsx"},{"name":"Icon","sourcePath":"components/icons/Icon.jsx"},{"name":"Dialog","sourcePath":"components/overlay/Dialog.jsx"},{"name":"Toast","sourcePath":"components/overlay/Toast.jsx"},{"name":"Tooltip","sourcePath":"components/overlay/Tooltip.jsx"},{"name":"VoiceQuote","sourcePath":"components/voice/VoiceQuote.jsx"}],"sourceHashes":{"components/actions/Button.jsx":"969b67173f99","components/actions/IconButton.jsx":"eeaddf69c6ca","components/data/Metric.jsx":"537a417c874e","components/data/StatusDot.jsx":"10794d8cfff8","components/data/TraceChart.jsx":"edb01b9247a8","components/display/Badge.jsx":"d32c718a0dce","components/display/Card.jsx":"afd6f234d1ac","components/display/Divider.jsx":"5ebceb96b88d","components/display/Tabs.jsx":"3c66a849e627","components/forms/Checkbox.jsx":"82de4df10558","components/forms/Input.jsx":"27c0bf053710","components/forms/Radio.jsx":"a71d7e2b9d35","components/forms/Select.jsx":"d5cd3b4895fe","components/forms/Switch.jsx":"770dd41f85c8","components/icons/Icon.jsx":"6fc43339b014","components/overlay/Dialog.jsx":"8633542d7953","components/overlay/Toast.jsx":"917ed8b65acb","components/overlay/Tooltip.jsx":"ee159d0ba63e","components/voice/VoiceQuote.jsx":"bac78529bb04","ui_kits/platform/DashboardScreen.jsx":"b2aa4abcde4a","ui_kits/platform/PlatformShell.jsx":"f2205ead7661","ui_kits/platform/ProgressScreen.jsx":"13e14361b5d7","ui_kits/platform/ProtocolsScreen.jsx":"e118b8a54a08","ui_kits/platform/SessionScreen.jsx":"7dd14dd3c2c2","ui_kits/website/LandingSections.jsx":"0bc998a45088","ui_kits/website/SiteChrome.jsx":"fa1c6b62bcb3"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.NeroesDesignSystem_23f8b7 = window.NeroesDesignSystem_23f8b7 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/actions/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const neroesButtonCSS = `
.ds-btn {
  display: inline-flex; align-items: center; justify-content: center;
  gap: var(--gap-inline);
  border-radius: var(--radius-pill);
  font-family: var(--font-sans);
  font-weight: var(--weight-medium);
  letter-spacing: 0.01em;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background var(--duration-fast) var(--ease-out),
              border-color var(--duration-fast) var(--ease-out),
              color var(--duration-fast) var(--ease-out);
  white-space: nowrap;
  user-select: none;
}
.ds-btn:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.ds-btn:disabled { opacity: 0.42; cursor: not-allowed; }

.ds-btn--sm { height: 30px; padding: 0 14px; font-size: 12px; }
.ds-btn--md { height: 38px; padding: 0 var(--pad-control-x); font-size: 13px; }
.ds-btn--lg { height: 46px; padding: 0 24px; font-size: 14px; }

.ds-btn--primary { background: var(--teal); color: var(--on-accent); }
.ds-btn--primary:hover:not(:disabled) { background: var(--teal-bright); }
.ds-btn--primary:active:not(:disabled) { background: var(--petrol); color: var(--text-1); }

.ds-btn--secondary { background: transparent; border-color: var(--border-2); color: var(--text-1); }
.ds-btn--secondary:hover:not(:disabled) { border-color: var(--teal); background: var(--teal-dim); }
.ds-btn--secondary:active:not(:disabled) { background: rgba(46,146,150,0.26); }

.ds-btn--ghost { background: transparent; color: var(--text-2); }
.ds-btn--ghost:hover:not(:disabled) { color: var(--text-1); background: var(--surface-raised); }
.ds-btn--ghost:active:not(:disabled) { background: var(--ink-500); }

.ds-btn--warm { background: var(--brass); color: var(--on-accent); }
.ds-btn--warm:hover:not(:disabled) { background: var(--brass-bright); }
.ds-btn--warm:active:not(:disabled) { background: #9A7132; }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-btn-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-btn-css';
  s.textContent = neroesButtonCSS;
  document.head.appendChild(s);
}
function Button({
  variant = 'primary',
  size = 'md',
  icon,
  disabled,
  fullWidth,
  children,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("button", _extends({
    className: `ds-btn ds-btn--${variant} ds-btn--${size}`,
    style: fullWidth ? {
      width: '100%'
    } : undefined,
    disabled: disabled
  }, rest), icon, children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/actions/Button.jsx", error: String((e && e.message) || e) }); }

// components/actions/IconButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const neroesIconBtnCSS = `
.ds-iconbtn {
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: var(--radius-pill);
  background: transparent; color: var(--text-2);
  border: 1px solid transparent;
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out),
              color var(--duration-fast) var(--ease-out),
              border-color var(--duration-fast) var(--ease-out);
}
.ds-iconbtn:hover:not(:disabled) { color: var(--text-1); background: var(--surface-raised); }
.ds-iconbtn:active:not(:disabled) { background: var(--ink-500); }
.ds-iconbtn:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.ds-iconbtn:disabled { opacity: 0.42; cursor: not-allowed; }
.ds-iconbtn--outline { border-color: var(--border-2); color: var(--text-1); }
.ds-iconbtn--outline:hover:not(:disabled) { border-color: var(--teal); background: var(--teal-dim); }
.ds-iconbtn--sm { width: 28px; height: 28px; }
.ds-iconbtn--md { width: 36px; height: 36px; }
.ds-iconbtn--lg { width: 44px; height: 44px; }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-iconbtn-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-iconbtn-css';
  s.textContent = neroesIconBtnCSS;
  document.head.appendChild(s);
}
function IconButton({
  variant = 'ghost',
  size = 'md',
  label,
  children,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("button", _extends({
    className: `ds-iconbtn ds-iconbtn--${variant} ds-iconbtn--${size}`,
    "aria-label": label,
    title: label
  }, rest), children);
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/actions/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/data/Metric.jsx
try { (() => {
const neroesMetricCSS = `
.ds-metric { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.ds-metric__label {
  font-family: var(--font-mono); font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-label); text-transform: uppercase;
  color: var(--text-label);
  display: flex; align-items: center; gap: 8px;
}
.ds-metric__row { display: flex; align-items: baseline; gap: 8px; }
.ds-metric__value {
  font-family: var(--font-sans); font-weight: var(--weight-light);
  color: var(--text-1); line-height: 1;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}
.ds-metric--md .ds-metric__value { font-size: 32px; }
.ds-metric--lg .ds-metric__value { font-size: 48px; }
.ds-metric--xl .ds-metric__value { font-size: 68px; }
.ds-metric__unit { font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: 0.08em; color: var(--text-3); white-space: nowrap; }
.ds-metric__delta { font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: 0.04em; white-space: nowrap; }
.ds-metric__delta--up { color: var(--green-bright); }
.ds-metric__delta--down { color: var(--signal-poor); }
.ds-metric__delta--flat { color: var(--text-3); }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-metric-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-metric-css';
  s.textContent = neroesMetricCSS;
  document.head.appendChild(s);
}
function Metric({
  label,
  value,
  unit,
  delta,
  deltaDirection,
  size = 'md',
  style
}) {
  const dir = deltaDirection || (typeof delta === 'string' && delta.trim().startsWith('-') ? 'down' : delta ? 'up' : 'flat');
  return /*#__PURE__*/React.createElement("div", {
    className: `ds-metric ds-metric--${size}`,
    style: style
  }, label ? /*#__PURE__*/React.createElement("span", {
    className: "ds-metric__label"
  }, label) : null, /*#__PURE__*/React.createElement("span", {
    className: "ds-metric__row"
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-metric__value"
  }, value), unit ? /*#__PURE__*/React.createElement("span", {
    className: "ds-metric__unit"
  }, unit) : null, delta ? /*#__PURE__*/React.createElement("span", {
    className: `ds-metric__delta ds-metric__delta--${dir}`
  }, delta) : null));
}
Object.assign(__ds_scope, { Metric });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/Metric.jsx", error: String((e && e.message) || e) }); }

// components/data/StatusDot.jsx
try { (() => {
const neroesStatusCSS = `
.ds-status { display: inline-flex; align-items: center; gap: 8px; }
.ds-status__dot { width: 7px; height: 7px; border-radius: 50%; flex: none; position: relative; }
.ds-status__dot--pulse::after {
  content: ''; position: absolute; inset: -4px; border-radius: 50%;
  border: 1px solid currentColor; opacity: 0;
  animation: ds-status-pulse 2.4s var(--ease-out) infinite;
}
@keyframes ds-status-pulse {
  0% { transform: scale(0.5); opacity: 0.7; }
  70% { transform: scale(1.15); opacity: 0; }
  100% { transform: scale(1.15); opacity: 0; }
}
@media (prefers-reduced-motion: reduce) { .ds-status__dot--pulse::after { animation: none; } }
.ds-status__text {
  font-family: var(--font-mono); font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-label); text-transform: uppercase;
  color: var(--text-2);
}
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-status-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-status-css';
  s.textContent = neroesStatusCSS;
  document.head.appendChild(s);
}
const neroesStatusColors = {
  live: {
    color: 'var(--teal-bright)',
    pulse: true
  },
  good: {
    color: 'var(--green-bright)',
    pulse: false
  },
  caution: {
    color: 'var(--brass-bright)',
    pulse: false
  },
  poor: {
    color: 'var(--signal-poor)',
    pulse: false
  },
  idle: {
    color: 'var(--text-3)',
    pulse: false
  }
};
function StatusDot({
  state = 'idle',
  label,
  style
}) {
  const cfg = neroesStatusColors[state] || neroesStatusColors.idle;
  return /*#__PURE__*/React.createElement("span", {
    className: "ds-status",
    style: style
  }, /*#__PURE__*/React.createElement("span", {
    className: `ds-status__dot${cfg.pulse ? ' ds-status__dot--pulse' : ''}`,
    style: {
      background: cfg.color,
      color: cfg.color
    }
  }), label ? /*#__PURE__*/React.createElement("span", {
    className: "ds-status__text"
  }, label) : null);
}
Object.assign(__ds_scope, { StatusDot });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/StatusDot.jsx", error: String((e && e.message) || e) }); }

// components/data/TraceChart.jsx
try { (() => {
const neroesTraceCSS = `
.ds-trace { display: block; width: 100%; }
.ds-trace text {
  font-family: var(--font-mono); font-size: 9px;
  letter-spacing: 0.08em; fill: var(--text-3);
}
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-trace-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-trace-css';
  s.textContent = neroesTraceCSS;
  document.head.appendChild(s);
}
let neroesTraceUid = 0;

/** Luminous line chart on a dark grid — the core Neroes data element. */
function TraceChart({
  series = [],
  height = 160,
  min,
  max,
  grid = true,
  area = true,
  glow = true,
  yLabels,
  xLabels
}) {
  const id = React.useMemo(() => `trace${++neroesTraceUid}`, []);
  const W = 600;
  const H = height;
  const padL = yLabels ? 34 : 8;
  const padR = 8;
  const padY = 12;
  const all = series.flatMap(s => s.data);
  const lo = min !== undefined ? min : Math.min(...all);
  const hi = max !== undefined ? max : Math.max(...all);
  const span = hi - lo || 1;
  const colors = {
    teal: 'var(--teal-bright)',
    green: 'var(--green-bright)',
    blue: 'var(--blue-bright)',
    brass: 'var(--brass-bright)',
    ember: 'var(--signal-poor)'
  };
  const rawColors = {
    teal: '#43BEC3',
    green: '#5BBC99',
    blue: '#5B8AD4',
    brass: '#D4A455',
    ember: '#C4685A'
  };
  const toPts = data => data.map((v, i) => {
    const x = padL + i / (data.length - 1 || 1) * (W - padL - padR);
    const y = H - padY - (v - lo) / span * (H - 2 * padY);
    return [x, y];
  });
  const gridRows = 4;
  const gridCols = 12;
  return /*#__PURE__*/React.createElement("svg", {
    className: "ds-trace",
    viewBox: `0 0 ${W} ${H}`,
    preserveAspectRatio: "none",
    style: {
      height
    }
  }, /*#__PURE__*/React.createElement("defs", null, series.map((s, si) => /*#__PURE__*/React.createElement("linearGradient", {
    key: si,
    id: `${id}-a${si}`,
    x1: "0",
    y1: "0",
    x2: "0",
    y2: "1"
  }, /*#__PURE__*/React.createElement("stop", {
    offset: "0%",
    stopColor: rawColors[s.color || 'teal'],
    stopOpacity: "0.22"
  }), /*#__PURE__*/React.createElement("stop", {
    offset: "100%",
    stopColor: rawColors[s.color || 'teal'],
    stopOpacity: "0"
  })))), grid ? /*#__PURE__*/React.createElement("g", null, Array.from({
    length: gridRows + 1
  }, (_, r) => {
    const y = padY + r / gridRows * (H - 2 * padY);
    return /*#__PURE__*/React.createElement("line", {
      key: `r${r}`,
      x1: padL,
      x2: W - padR,
      y1: y,
      y2: y,
      stroke: "var(--border-1)",
      strokeWidth: "1",
      vectorEffect: "non-scaling-stroke",
      strokeDasharray: r === gridRows ? '' : '1 5'
    });
  }), Array.from({
    length: gridCols + 1
  }, (_, c) => {
    const x = padL + c / gridCols * (W - padL - padR);
    return /*#__PURE__*/React.createElement("line", {
      key: `c${c}`,
      x1: x,
      x2: x,
      y1: padY,
      y2: H - padY,
      stroke: "var(--divider)",
      strokeWidth: "1",
      vectorEffect: "non-scaling-stroke"
    });
  })) : null, yLabels ? yLabels.map((t, i) => {
    const y = padY + (1 - i / (yLabels.length - 1 || 1)) * (H - 2 * padY);
    return /*#__PURE__*/React.createElement("text", {
      key: i,
      x: padL - 8,
      y: y + 3,
      textAnchor: "end"
    }, t);
  }) : null, series.map((s, si) => {
    const pts = toPts(s.data);
    const line = pts.map(p => p.join(',')).join(' ');
    const areaPath = `${line} ${W - padR},${H - padY} ${padL},${H - padY}`;
    const c = colors[s.color || 'teal'];
    return /*#__PURE__*/React.createElement("g", {
      key: si
    }, area ? /*#__PURE__*/React.createElement("polygon", {
      points: areaPath,
      fill: `url(#${id}-a${si})`
    }) : null, glow ? /*#__PURE__*/React.createElement("polyline", {
      points: line,
      fill: "none",
      stroke: c,
      strokeWidth: "5",
      strokeLinejoin: "round",
      strokeLinecap: "round",
      opacity: "0.18",
      vectorEffect: "non-scaling-stroke"
    }) : null, /*#__PURE__*/React.createElement("polyline", {
      points: line,
      fill: "none",
      stroke: c,
      strokeWidth: "1.5",
      strokeLinejoin: "round",
      strokeLinecap: "round",
      vectorEffect: "non-scaling-stroke"
    }));
  }), xLabels ? xLabels.map((t, i) => {
    const x = padL + i / (xLabels.length - 1 || 1) * (W - padL - padR);
    return /*#__PURE__*/React.createElement("text", {
      key: i,
      x: x,
      y: H - 1,
      textAnchor: i === 0 ? 'start' : i === xLabels.length - 1 ? 'end' : 'middle'
    }, t);
  }) : null);
}
Object.assign(__ds_scope, { TraceChart });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/TraceChart.jsx", error: String((e && e.message) || e) }); }

// components/display/Badge.jsx
try { (() => {
const neroesBadgeCSS = `
.ds-badge {
  display: inline-flex; align-items: center; gap: 6px;
  height: 22px; padding: 0 10px;
  border-radius: var(--radius-pill);
  border: 1px solid transparent;
  font-family: var(--font-mono); font-size: var(--text-2xs);
  font-weight: var(--weight-medium);
  letter-spacing: 0.1em; text-transform: uppercase;
  white-space: nowrap;
}
.ds-badge__dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; flex: none; }
.ds-badge--neutral { background: var(--surface-raised); color: var(--text-2); }
.ds-badge--outline { border-color: var(--border-2); color: var(--text-2); }
.ds-badge--teal  { background: var(--teal-dim);  color: var(--teal-bright); }
.ds-badge--green { background: var(--green-dim); color: var(--green-bright); }
.ds-badge--blue  { background: var(--blue-dim);  color: var(--blue-bright); }
.ds-badge--brass { background: var(--brass-dim); color: var(--brass-bright); }
.ds-badge--ember { background: var(--signal-poor-dim); color: var(--signal-poor); }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-badge-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-badge-css';
  s.textContent = neroesBadgeCSS;
  document.head.appendChild(s);
}
function Badge({
  variant = 'neutral',
  dot,
  style,
  children
}) {
  return /*#__PURE__*/React.createElement("span", {
    className: `ds-badge ds-badge--${variant}`,
    style: style
  }, dot ? /*#__PURE__*/React.createElement("span", {
    className: "ds-badge__dot"
  }) : null, children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Badge.jsx", error: String((e && e.message) || e) }); }

// components/display/Card.jsx
try { (() => {
const neroesCardCSS = `
.ds-card {
  background: var(--surface-card);
  border: 1px solid var(--border-1);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-1);
}
.ds-card--inset { background: var(--surface-inset); }
.ds-card__head {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 14px var(--pad-card);
  border-bottom: 1px solid var(--divider);
}
.ds-card__label {
  font-family: var(--font-mono); font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-label); text-transform: uppercase;
  color: var(--text-label);
}
.ds-card__title { font-size: var(--text-md); font-weight: var(--weight-semibold); color: var(--text-1); }
.ds-card__body { padding: var(--pad-card); }
.ds-card--flush .ds-card__body { padding: 0; }
.ds-card__foot {
  display: flex; align-items: center; justify-content: flex-end; gap: 8px;
  padding: 12px var(--pad-card);
  border-top: 1px solid var(--divider);
}
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-card-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-card-css';
  s.textContent = neroesCardCSS;
  document.head.appendChild(s);
}
function Card({
  label,
  title,
  actions,
  footer,
  inset,
  flush,
  style,
  children
}) {
  const hasHead = label || title || actions;
  return /*#__PURE__*/React.createElement("div", {
    className: `ds-card${inset ? ' ds-card--inset' : ''}${flush ? ' ds-card--flush' : ''}`,
    style: style
  }, hasHead ? /*#__PURE__*/React.createElement("div", {
    className: "ds-card__head"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '2px'
    }
  }, label ? /*#__PURE__*/React.createElement("span", {
    className: "ds-card__label"
  }, label) : null, title ? /*#__PURE__*/React.createElement("span", {
    className: "ds-card__title"
  }, title) : null), actions ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '8px'
    }
  }, actions) : null) : null, /*#__PURE__*/React.createElement("div", {
    className: "ds-card__body"
  }, children), footer ? /*#__PURE__*/React.createElement("div", {
    className: "ds-card__foot"
  }, footer) : null);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Card.jsx", error: String((e && e.message) || e) }); }

// components/display/Divider.jsx
try { (() => {
const neroesDividerCSS = `
.ds-divider { display: flex; align-items: center; gap: 12px; border: none; margin: 0; }
.ds-divider__line { flex: 1; height: 1px; background: var(--divider); }
.ds-divider__label {
  font-family: var(--font-mono); font-size: var(--text-2xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-label); text-transform: uppercase;
  color: var(--text-3); flex: none;
}
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-divider-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-divider-css';
  s.textContent = neroesDividerCSS;
  document.head.appendChild(s);
}
function Divider({
  label,
  style
}) {
  if (!label) return /*#__PURE__*/React.createElement("div", {
    className: "ds-divider",
    style: style
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-divider__line"
  }));
  return /*#__PURE__*/React.createElement("div", {
    className: "ds-divider",
    style: style
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-divider__line"
  }), /*#__PURE__*/React.createElement("span", {
    className: "ds-divider__label"
  }, label), /*#__PURE__*/React.createElement("span", {
    className: "ds-divider__line"
  }));
}
Object.assign(__ds_scope, { Divider });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Divider.jsx", error: String((e && e.message) || e) }); }

// components/display/Tabs.jsx
try { (() => {
const neroesTabsCSS = `
.ds-tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--divider); }
.ds-tabs__tab {
  appearance: none; background: none; border: none; cursor: pointer;
  padding: 10px 14px 12px;
  font-family: var(--font-mono); font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-label); text-transform: uppercase;
  color: var(--text-3);
  position: relative;
  transition: color var(--duration-fast) var(--ease-out);
}
.ds-tabs__tab:hover { color: var(--text-2); }
.ds-tabs__tab:focus-visible { outline: none; box-shadow: var(--focus-ring); border-radius: var(--radius-xs); }
.ds-tabs__tab--active { color: var(--text-1); }
.ds-tabs__tab--active::after {
  content: ''; position: absolute; left: 14px; right: 14px; bottom: -1px;
  height: 2px; background: var(--teal); border-radius: 1px;
}
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-tabs-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-tabs-css';
  s.textContent = neroesTabsCSS;
  document.head.appendChild(s);
}
function Tabs({
  items = [],
  value,
  onChange,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "ds-tabs",
    role: "tablist",
    style: style
  }, items.map(it => {
    const item = typeof it === 'string' ? {
      value: it,
      label: it
    } : it;
    const active = item.value === value;
    return /*#__PURE__*/React.createElement("button", {
      key: item.value,
      role: "tab",
      "aria-selected": active,
      className: `ds-tabs__tab${active ? ' ds-tabs__tab--active' : ''}`,
      onClick: () => onChange && onChange(item.value)
    }, item.label);
  }));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Tabs.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const neroesCheckboxCSS = `
.ds-check { display: inline-flex; align-items: center; gap: 10px; cursor: pointer; user-select: none; }
.ds-check input { position: absolute; opacity: 0; width: 0; height: 0; }
.ds-check__pad {
  width: 16px; height: 16px; flex: none;
  border: 1px solid var(--border-2);
  border-radius: 3px; /* square pad — PCB motif */
  background: var(--surface-inset);
  display: inline-flex; align-items: center; justify-content: center;
  transition: background var(--duration-fast) var(--ease-out),
              border-color var(--duration-fast) var(--ease-out);
}
.ds-check:hover .ds-check__pad { border-color: var(--teal); }
.ds-check input:focus-visible + .ds-check__pad { box-shadow: var(--focus-ring); }
.ds-check input:checked + .ds-check__pad { background: var(--teal); border-color: var(--teal); }
.ds-check__mark {
  width: 9px; height: 5px;
  border-left: 1.6px solid var(--on-accent);
  border-bottom: 1.6px solid var(--on-accent);
  transform: rotate(-45deg) translate(0.5px, -1px);
  opacity: 0; transition: opacity var(--duration-fast) var(--ease-out);
}
.ds-check input:checked + .ds-check__pad .ds-check__mark { opacity: 1; }
.ds-check__text { font-size: var(--text-sm); color: var(--text-2); }
.ds-check input:checked ~ .ds-check__text { color: var(--text-1); }
.ds-check--disabled { opacity: 0.42; cursor: not-allowed; }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-check-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-check-css';
  s.textContent = neroesCheckboxCSS;
  document.head.appendChild(s);
}
function Checkbox({
  label,
  disabled,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: `ds-check${disabled ? ' ds-check--disabled' : ''}`,
    style: style
  }, /*#__PURE__*/React.createElement("input", _extends({
    type: "checkbox",
    disabled: disabled
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "ds-check__pad"
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-check__mark"
  })), label ? /*#__PURE__*/React.createElement("span", {
    className: "ds-check__text"
  }, label) : null);
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
const neroesFieldCSS = `
.ds-field { display: flex; flex-direction: column; gap: 6px; }
.ds-field__label {
  font-family: var(--font-mono); font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-label); text-transform: uppercase;
  color: var(--text-label);
}
.ds-field__input {
  display: flex; align-items: center; gap: 8px;
  background: var(--surface-inset);
  border: 1px solid var(--border-1);
  border-radius: var(--radius-sm);
  padding: 0 12px; height: 38px;
  transition: border-color var(--duration-fast) var(--ease-out);
}
.ds-field__input:hover { border-color: var(--border-2); }
.ds-field__input:focus-within { border-color: var(--teal); }
.ds-field__input input {
  flex: 1; min-width: 0; background: none; border: none; outline: none;
  color: var(--text-1); font-family: var(--font-sans); font-size: var(--text-sm);
}
.ds-field__input input::placeholder { color: var(--text-3); }
.ds-field__affix { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--text-3); }
.ds-field__hint { font-size: 12px; color: var(--text-3); }
.ds-field--invalid .ds-field__input { border-color: var(--signal-poor); }
.ds-field--invalid .ds-field__hint { color: var(--signal-poor); }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-field-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-field-css';
  s.textContent = neroesFieldCSS;
  document.head.appendChild(s);
}
function Input({
  label,
  hint,
  prefix,
  suffix,
  invalid,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: `ds-field${invalid ? ' ds-field--invalid' : ''}`,
    style: style
  }, label ? /*#__PURE__*/React.createElement("span", {
    className: "ds-field__label"
  }, label) : null, /*#__PURE__*/React.createElement("span", {
    className: "ds-field__input"
  }, prefix ? /*#__PURE__*/React.createElement("span", {
    className: "ds-field__affix"
  }, prefix) : null, /*#__PURE__*/React.createElement("input", rest), suffix ? /*#__PURE__*/React.createElement("span", {
    className: "ds-field__affix"
  }, suffix) : null), hint ? /*#__PURE__*/React.createElement("span", {
    className: "ds-field__hint"
  }, hint) : null);
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Radio.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const neroesRadioCSS = `
.ds-radio { display: inline-flex; align-items: center; gap: 10px; cursor: pointer; user-select: none; }
.ds-radio input { position: absolute; opacity: 0; width: 0; height: 0; }
.ds-radio__via {
  width: 16px; height: 16px; flex: none;
  border: 1px solid var(--border-2);
  border-radius: 50%; /* round via — PCB motif */
  background: var(--surface-inset);
  display: inline-flex; align-items: center; justify-content: center;
  transition: border-color var(--duration-fast) var(--ease-out);
}
.ds-radio:hover .ds-radio__via { border-color: var(--teal); }
.ds-radio input:focus-visible + .ds-radio__via { box-shadow: var(--focus-ring); }
.ds-radio input:checked + .ds-radio__via { border-color: var(--teal); }
.ds-radio__dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--teal);
  transform: scale(0); transition: transform var(--duration-fast) var(--ease-out);
}
.ds-radio input:checked + .ds-radio__via .ds-radio__dot { transform: scale(1); }
.ds-radio__text { font-size: var(--text-sm); color: var(--text-2); }
.ds-radio input:checked ~ .ds-radio__text { color: var(--text-1); }
.ds-radio--disabled { opacity: 0.42; cursor: not-allowed; }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-radio-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-radio-css';
  s.textContent = neroesRadioCSS;
  document.head.appendChild(s);
}
function Radio({
  label,
  disabled,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: `ds-radio${disabled ? ' ds-radio--disabled' : ''}`,
    style: style
  }, /*#__PURE__*/React.createElement("input", _extends({
    type: "radio",
    disabled: disabled
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "ds-radio__via"
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-radio__dot"
  })), label ? /*#__PURE__*/React.createElement("span", {
    className: "ds-radio__text"
  }, label) : null);
}
Object.assign(__ds_scope, { Radio });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Radio.jsx", error: String((e && e.message) || e) }); }

// components/forms/Select.jsx
try { (() => {
const neroesSelectCSS = `
.ds-select { display: flex; flex-direction: column; gap: 6px; }
.ds-select__label {
  font-family: var(--font-mono); font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-label); text-transform: uppercase;
  color: var(--text-label);
}
.ds-select__wrap { position: relative; }
.ds-select__wrap select {
  appearance: none; -webkit-appearance: none;
  width: 100%; height: 38px;
  background: var(--surface-inset);
  border: 1px solid var(--border-1);
  border-radius: var(--radius-sm);
  color: var(--text-1);
  font-family: var(--font-sans); font-size: var(--text-sm);
  padding: 0 32px 0 12px;
  cursor: pointer; outline: none;
  transition: border-color var(--duration-fast) var(--ease-out);
}
.ds-select__wrap select:hover { border-color: var(--border-2); }
.ds-select__wrap select:focus { border-color: var(--teal); }
.ds-select__chev {
  position: absolute; right: 12px; top: 50%;
  width: 8px; height: 8px;
  border-right: 1.5px solid var(--text-3);
  border-bottom: 1.5px solid var(--text-3);
  transform: translateY(-70%) rotate(45deg);
  pointer-events: none;
}
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-select-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-select-css';
  s.textContent = neroesSelectCSS;
  document.head.appendChild(s);
}
function Select({
  label,
  options = [],
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: "ds-select",
    style: style
  }, label ? /*#__PURE__*/React.createElement("span", {
    className: "ds-select__label"
  }, label) : null, /*#__PURE__*/React.createElement("span", {
    className: "ds-select__wrap"
  }, /*#__PURE__*/React.createElement("select", rest, options.map(o => {
    const opt = typeof o === 'string' ? {
      value: o,
      label: o
    } : o;
    return /*#__PURE__*/React.createElement("option", {
      key: opt.value,
      value: opt.value
    }, opt.label);
  })), /*#__PURE__*/React.createElement("span", {
    className: "ds-select__chev"
  })));
}
Object.assign(__ds_scope, { Select });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Select.jsx", error: String((e && e.message) || e) }); }

// components/forms/Switch.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const neroesSwitchCSS = `
.ds-switch { display: inline-flex; align-items: center; gap: 10px; cursor: pointer; user-select: none; }
.ds-switch input { position: absolute; opacity: 0; width: 0; height: 0; }
.ds-switch__track {
  width: 36px; height: 20px; flex: none;
  border-radius: var(--radius-pill);
  background: var(--surface-inset);
  border: 1px solid var(--border-2);
  position: relative;
  transition: background var(--duration-base) var(--ease-out),
              border-color var(--duration-base) var(--ease-out);
}
.ds-switch__thumb {
  position: absolute; top: 2px; left: 2px;
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--text-3);
  transition: transform var(--duration-base) var(--ease-out),
              background var(--duration-base) var(--ease-out);
}
.ds-switch input:checked + .ds-switch__track { background: var(--teal); border-color: var(--teal); }
.ds-switch input:checked + .ds-switch__track .ds-switch__thumb {
  transform: translateX(16px); background: var(--on-accent);
}
.ds-switch input:focus-visible + .ds-switch__track { box-shadow: var(--focus-ring); }
.ds-switch__text { font-size: var(--text-sm); color: var(--text-2); }
.ds-switch input:checked ~ .ds-switch__text { color: var(--text-1); }
.ds-switch--disabled { opacity: 0.42; cursor: not-allowed; }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-switch-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-switch-css';
  s.textContent = neroesSwitchCSS;
  document.head.appendChild(s);
}
function Switch({
  label,
  disabled,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: `ds-switch${disabled ? ' ds-switch--disabled' : ''}`,
    style: style
  }, /*#__PURE__*/React.createElement("input", _extends({
    type: "checkbox",
    role: "switch",
    disabled: disabled
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "ds-switch__track"
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-switch__thumb"
  })), label ? /*#__PURE__*/React.createElement("span", {
    className: "ds-switch__text"
  }, label) : null);
}
Object.assign(__ds_scope, { Switch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Switch.jsx", error: String((e && e.message) || e) }); }

// components/icons/Icon.jsx
try { (() => {
/* Icon — thin-stroke glyphs at instrument weight (1.5px).
   Uses Lucide (ISC license) from CDN — closest match to the brand's
   thin PCB-line iconography. Self-loads the library if absent. */

if (typeof document !== 'undefined' && !window.lucide && !document.getElementById('neroes-lucide')) {
  const neroesLucideScript = document.createElement('script');
  neroesLucideScript.id = 'neroes-lucide';
  neroesLucideScript.src = 'https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js';
  document.head.appendChild(neroesLucideScript);
}
function Icon({
  name,
  size = 16,
  strokeWidth = 1.5,
  color,
  style
}) {
  const [html, setHtml] = React.useState('');
  React.useEffect(() => {
    let cancelled = false;
    const tryRender = () => {
      const lucide = window.lucide;
      if (!lucide) return false;
      const pascal = String(name).split('-').map(w => w ? w[0].toUpperCase() + w.slice(1) : w).join('');
      const map = lucide.icons || lucide;
      const node = map[pascal] || map[name];
      if (!node) {
        console.warn(`[neroes/Icon] unknown icon "${name}"`);
        if (!cancelled) setHtml('');
        return true;
      }
      try {
        if (typeof node.toSvg === 'function') {
          if (!cancelled) setHtml(node.toSvg({
            width: size,
            height: size,
            'stroke-width': strokeWidth
          }));
          return true;
        }
        if (typeof lucide.createElement === 'function') {
          const el = lucide.createElement(node);
          el.setAttribute('width', size);
          el.setAttribute('height', size);
          el.setAttribute('stroke-width', strokeWidth);
          if (!cancelled) setHtml(el.outerHTML);
          return true;
        }
      } catch (e) {
        console.warn('[neroes/Icon] render failed', e);
      }
      return true;
    };
    if (!tryRender()) {
      const t = setInterval(() => {
        if (tryRender()) clearInterval(t);
      }, 120);
      return () => {
        cancelled = true;
        clearInterval(t);
      };
    }
    return () => {
      cancelled = true;
    };
  }, [name, size, strokeWidth]);
  return /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      display: 'inline-flex',
      width: size,
      height: size,
      flex: 'none',
      color: color,
      verticalAlign: 'middle',
      ...style
    },
    dangerouslySetInnerHTML: {
      __html: html
    }
  });
}
Object.assign(__ds_scope, { Icon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/icons/Icon.jsx", error: String((e && e.message) || e) }); }

// components/overlay/Dialog.jsx
try { (() => {
const neroesDialogCSS = `
.ds-dialog__overlay {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(8, 20, 26, 0.62);
  backdrop-filter: blur(3px); -webkit-backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
  animation: ds-dialog-fade var(--duration-base) var(--ease-out);
}
.ds-dialog {
  background: var(--surface-overlay);
  border: 1px solid var(--border-1);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-overlay);
  width: 100%; max-width: 440px;
  animation: ds-dialog-rise var(--duration-base) var(--ease-out);
}
@keyframes ds-dialog-fade { from { opacity: 0; } }
@keyframes ds-dialog-rise { from { opacity: 0; transform: translateY(8px); } }
@media (prefers-reduced-motion: reduce) { .ds-dialog__overlay, .ds-dialog { animation: none; } }
.ds-dialog__head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding: 20px 20px 0; }
.ds-dialog__label {
  font-family: var(--font-mono); font-size: var(--text-2xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-label); text-transform: uppercase;
  color: var(--text-3); display: block; margin-bottom: 6px;
}
.ds-dialog__title { font-size: var(--text-lg); font-weight: var(--weight-semibold); color: var(--text-1); letter-spacing: var(--tracking-heading); }
.ds-dialog__close {
  appearance: none; background: none; border: none; cursor: pointer;
  width: 28px; height: 28px; border-radius: 50%; flex: none;
  color: var(--text-3); font-size: 16px; line-height: 1;
  display: inline-flex; align-items: center; justify-content: center;
  transition: color var(--duration-fast) var(--ease-out), background var(--duration-fast) var(--ease-out);
}
.ds-dialog__close:hover { color: var(--text-1); background: var(--surface-raised); }
.ds-dialog__body { padding: 14px 20px 20px; font-size: var(--text-sm); color: var(--text-2); line-height: var(--leading-body); }
.ds-dialog__foot { display: flex; justify-content: flex-end; gap: 8px; padding: 14px 20px; border-top: 1px solid var(--divider); }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-dialog-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-dialog-css';
  s.textContent = neroesDialogCSS;
  document.head.appendChild(s);
}
function Dialog({
  open,
  onClose,
  label,
  title,
  footer,
  children
}) {
  if (!open) return null;
  return /*#__PURE__*/React.createElement("div", {
    className: "ds-dialog__overlay",
    onClick: e => {
      if (e.target === e.currentTarget && onClose) onClose();
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "ds-dialog",
    role: "dialog",
    "aria-modal": "true"
  }, /*#__PURE__*/React.createElement("div", {
    className: "ds-dialog__head"
  }, /*#__PURE__*/React.createElement("div", null, label ? /*#__PURE__*/React.createElement("span", {
    className: "ds-dialog__label"
  }, label) : null, title ? /*#__PURE__*/React.createElement("span", {
    className: "ds-dialog__title"
  }, title) : null), /*#__PURE__*/React.createElement("button", {
    className: "ds-dialog__close",
    "aria-label": "Close",
    onClick: onClose
  }, "\xD7")), /*#__PURE__*/React.createElement("div", {
    className: "ds-dialog__body"
  }, children), footer ? /*#__PURE__*/React.createElement("div", {
    className: "ds-dialog__foot"
  }, footer) : null));
}
Object.assign(__ds_scope, { Dialog });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/overlay/Dialog.jsx", error: String((e && e.message) || e) }); }

// components/overlay/Toast.jsx
try { (() => {
const neroesToastCSS = `
.ds-toast {
  display: flex; align-items: flex-start; gap: 10px;
  background: var(--ink-900);
  border: 1px solid var(--border-1);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-2);
  padding: 12px 14px;
  max-width: 360px;
}
.ds-toast__dot { width: 7px; height: 7px; border-radius: 50%; flex: none; margin-top: 5px; }
.ds-toast--info .ds-toast__dot { background: var(--teal-bright); }
.ds-toast--success .ds-toast__dot { background: var(--green-bright); }
.ds-toast--caution .ds-toast__dot { background: var(--brass-bright); }
.ds-toast--error .ds-toast__dot { background: var(--signal-poor); }
.ds-toast__title { font-size: var(--text-sm); font-weight: var(--weight-medium); color: var(--text-1); }
.ds-toast__desc { font-family: var(--font-mono); font-size: var(--text-2xs); letter-spacing: 0.04em; color: var(--text-3); margin-top: 3px; }
.ds-toast__close {
  appearance: none; background: none; border: none; cursor: pointer;
  color: var(--text-3); font-size: 14px; line-height: 1; padding: 2px;
  margin-left: auto; flex: none;
}
.ds-toast__close:hover { color: var(--text-1); }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-toast-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-toast-css';
  s.textContent = neroesToastCSS;
  document.head.appendChild(s);
}
function Toast({
  state = 'info',
  title,
  description,
  onClose,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: `ds-toast ds-toast--${state}`,
    role: "status",
    style: style
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-toast__dot"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, title ? /*#__PURE__*/React.createElement("div", {
    className: "ds-toast__title"
  }, title) : null, description ? /*#__PURE__*/React.createElement("div", {
    className: "ds-toast__desc"
  }, description) : null), onClose ? /*#__PURE__*/React.createElement("button", {
    className: "ds-toast__close",
    "aria-label": "Dismiss",
    onClick: onClose
  }, "\xD7") : null);
}
Object.assign(__ds_scope, { Toast });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/overlay/Toast.jsx", error: String((e && e.message) || e) }); }

// components/overlay/Tooltip.jsx
try { (() => {
const neroesTooltipCSS = `
.ds-tooltip { position: relative; display: inline-flex; }
.ds-tooltip__tip {
  position: absolute; bottom: calc(100% + 8px); left: 50%;
  transform: translateX(-50%) translateY(2px);
  background: var(--ink-900);
  border: 1px solid var(--border-1);
  border-radius: var(--radius-sm);
  padding: 5px 10px;
  font-family: var(--font-mono); font-size: var(--text-2xs);
  letter-spacing: 0.06em; color: var(--text-2);
  white-space: nowrap; pointer-events: none;
  opacity: 0;
  transition: opacity var(--duration-fast) var(--ease-out), transform var(--duration-fast) var(--ease-out);
  z-index: 50;
}
.ds-tooltip:hover .ds-tooltip__tip,
.ds-tooltip:focus-within .ds-tooltip__tip {
  opacity: 1; transform: translateX(-50%) translateY(0);
}
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-tooltip-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-tooltip-css';
  s.textContent = neroesTooltipCSS;
  document.head.appendChild(s);
}
function Tooltip({
  content,
  style,
  children
}) {
  return /*#__PURE__*/React.createElement("span", {
    className: "ds-tooltip",
    style: style
  }, children, /*#__PURE__*/React.createElement("span", {
    className: "ds-tooltip__tip",
    role: "tooltip"
  }, content));
}
Object.assign(__ds_scope, { Tooltip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/overlay/Tooltip.jsx", error: String((e && e.message) || e) }); }

// components/voice/VoiceQuote.jsx
try { (() => {
const neroesVoiceCSS = `
.ds-voice { display: flex; flex-direction: column; gap: 14px; max-width: 62ch; }
.ds-voice__tag {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--font-mono); font-size: var(--text-2xs);
  font-weight: var(--weight-medium);
  letter-spacing: var(--tracking-label-wide); text-transform: uppercase;
}
.ds-voice__dot { width: 7px; height: 7px; border-radius: 50%; flex: none; }
.ds-voice--measured .ds-voice__tag { color: var(--text-3); }
.ds-voice--measured .ds-voice__dot { background: var(--teal); }
.ds-voice--vision .ds-voice__tag { color: var(--text-3); }
.ds-voice--vision .ds-voice__dot { background: var(--brass); }
.ds-voice--measured .ds-voice__text {
  font-family: var(--font-mono); font-size: var(--text-sm);
  line-height: var(--leading-mono); color: var(--text-2);
}
.ds-voice--vision .ds-voice__text {
  font-family: var(--font-serif); font-style: italic; font-weight: 400;
  font-size: var(--text-xl); line-height: 1.42; color: var(--text-1);
  letter-spacing: 0.002em;
}
.ds-voice--vision.ds-voice--lg .ds-voice__text { font-size: var(--text-2xl); line-height: 1.32; }
.ds-voice__source { font-family: var(--font-mono); font-size: var(--text-2xs); letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-3); }
`;
if (typeof document !== 'undefined' && !document.getElementById('neroes-voice-css')) {
  const s = document.createElement('style');
  s.id = 'neroes-voice-css';
  s.textContent = neroesVoiceCSS;
  document.head.appendChild(s);
}
function VoiceQuote({
  voice = 'measured',
  tag,
  size,
  source,
  style,
  children
}) {
  const defaultTag = voice === 'vision' ? 'Vision' : 'Measured';
  return /*#__PURE__*/React.createElement("figure", {
    className: `ds-voice ds-voice--${voice}${size === 'lg' ? ' ds-voice--lg' : ''}`,
    style: {
      margin: 0,
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-voice__tag"
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-voice__dot"
  }), tag || defaultTag), /*#__PURE__*/React.createElement("blockquote", {
    className: "ds-voice__text",
    style: {
      margin: 0
    }
  }, children), source ? /*#__PURE__*/React.createElement("figcaption", {
    className: "ds-voice__source"
  }, source) : null);
}
Object.assign(__ds_scope, { VoiceQuote });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/voice/VoiceQuote.jsx", error: String((e && e.message) || e) }); }

// ui_kits/platform/DashboardScreen.jsx
try { (() => {
/* Today — readiness, weekly trace, recent sessions. */
const {
  Card,
  Button,
  Badge,
  Metric,
  TraceChart,
  StatusDot,
  Divider,
  Icon
} = window.NeroesDesignSystem_23f8b7;
const npSessions = [{
  id: 14,
  name: 'Focus hold',
  when: 'Yesterday · 16:02',
  len: '24 MIN',
  score: 74,
  delta: '+6',
  state: 'green'
}, {
  id: 13,
  name: 'Calm baseline',
  when: 'Tue · 08:15',
  len: '18 MIN',
  score: 68,
  delta: '+2',
  state: 'green'
}, {
  id: 12,
  name: 'Stress recovery',
  when: 'Mon · 19:40',
  len: '22 MIN',
  score: 61,
  delta: '-3',
  state: 'ember'
}];
function DashboardScreen({
  onStart
}) {
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Today",
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      maxWidth: '1060px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-end',
      justifyContent: 'space-between',
      gap: '16px'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "ds-label",
    style: {
      marginBottom: '6px'
    }
  }, "Good afternoon, Rui"), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontSize: '26px'
    }
  }, "Ready for session 15.")), /*#__PURE__*/React.createElement(Button, {
    icon: /*#__PURE__*/React.createElement(Icon, {
      name: "play",
      size: 14
    }),
    onClick: onStart
  }, "Start session")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr 1fr',
      gap: '16px'
    }
  }, /*#__PURE__*/React.createElement(Card, {
    label: "Readiness",
    title: "High"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "82",
    unit: "/100",
    delta: "+4",
    size: "lg"
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '10.5px',
      letterSpacing: '0.06em',
      color: 'var(--text-3)'
    }
  }, "SLEEP 7.4H \xB7 HRV 64MS \xB7 REST DAY PRIOR"))), /*#__PURE__*/React.createElement(Card, {
    label: "This week",
    title: "3 of 4 sessions"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "64",
    unit: "MIN TRAINED",
    size: "lg"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '6px'
    }
  }, ['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      flex: 1,
      height: '26px',
      borderRadius: '4px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'var(--font-mono)',
      fontSize: '9px',
      color: i < 3 ? 'var(--on-accent)' : 'var(--text-3)',
      background: i < 3 ? 'var(--teal)' : 'var(--surface-inset)',
      border: i < 3 ? '1px solid var(--teal)' : '1px solid var(--border-1)'
    }
  }, d))))), /*#__PURE__*/React.createElement(Card, {
    label: "Current block",
    title: "Focus \xB7 Week 3 of 6"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "12.4",
    unit: "HZ ALPHA",
    delta: "+0.8",
    size: "lg"
  }), /*#__PURE__*/React.createElement(StatusDot, {
    state: "good",
    label: "On track"
  })))), /*#__PURE__*/React.createElement(Card, {
    label: "Focus index",
    title: "Last 12 sessions",
    flush: true,
    actions: /*#__PURE__*/React.createElement(Badge, {
      variant: "green"
    }, "Trending up")
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '16px 20px 12px'
    }
  }, /*#__PURE__*/React.createElement(TraceChart, {
    height: 170,
    series: [{
      data: [52, 55, 51, 58, 56, 62, 60, 66, 63, 68, 70, 74],
      color: 'teal'
    }, {
      data: [48, 49, 50, 50, 51, 52, 53, 54, 54, 55, 56, 57],
      color: 'blue'
    }],
    min: 40,
    max: 80,
    yLabels: ['40', '60', '80'],
    xLabels: ['S3', 'S6', 'S9', 'S12']
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '18px',
      padding: '10px 4px 4px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '10px',
      letterSpacing: '0.1em',
      color: 'var(--teal-bright)'
    }
  }, "\u2014 YOU"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '10px',
      letterSpacing: '0.1em',
      color: 'var(--blue-bright)'
    }
  }, "\u2014 COHORT MEDIAN")))), /*#__PURE__*/React.createElement(Card, {
    label: "Recent sessions",
    flush: true
  }, /*#__PURE__*/React.createElement("div", null, npSessions.map((s, i) => /*#__PURE__*/React.createElement("div", {
    key: s.id,
    style: {
      display: 'grid',
      gridTemplateColumns: '44px 1.4fr 1fr 90px 110px 32px',
      alignItems: 'center',
      gap: '12px',
      padding: '13px 20px',
      borderTop: i === 0 ? 'none' : '1px solid var(--divider)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '11px',
      color: 'var(--text-3)'
    }
  }, "#", s.id), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: '13.5px',
      color: 'var(--text-1)',
      fontWeight: 500
    }
  }, s.name), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '10.5px',
      letterSpacing: '0.06em',
      color: 'var(--text-3)'
    }
  }, s.when), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '10.5px',
      letterSpacing: '0.06em',
      color: 'var(--text-3)'
    }
  }, s.len), /*#__PURE__*/React.createElement(Badge, {
    variant: s.state === 'ember' ? 'ember' : 'green'
  }, s.score, " \xB7 ", s.delta), /*#__PURE__*/React.createElement(Icon, {
    name: "chevron-right",
    size: 14,
    color: "var(--text-3)"
  }))))));
}
Object.assign(window, {
  DashboardScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/platform/DashboardScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/platform/PlatformShell.jsx
try { (() => {
/* Neroes Mental Training Platform — app shell (sidebar + topbar). */
const {
  Icon,
  StatusDot,
  Badge
} = window.NeroesDesignSystem_23f8b7;
const platformShellCSS = `
  .np-shell { display: flex; height: 100vh; overflow: hidden; background: var(--surface-page); }
  .np-side {
    width: 224px; flex: none; display: flex; flex-direction: column;
    background: var(--ink-800); border-right: 1px solid var(--divider);
    padding: 20px 14px;
  }
  .np-brand { display: flex; align-items: center; gap: 10px; padding: 0 8px 22px; }
  .np-brand img { width: 30px; height: 30px; border-radius: 8px; }
  .np-brand span { font-family: var(--font-sans); font-weight: 600; font-size: 17px; color: var(--text-1); letter-spacing: -0.01em; }
  .np-nav { display: flex; flex-direction: column; gap: 2px; }
  .np-nav__item {
    display: flex; align-items: center; gap: 10px;
    appearance: none; background: none; border: none; cursor: pointer; text-align: left;
    padding: 9px 10px; border-radius: var(--radius-sm);
    font-family: var(--font-mono); font-size: 11px; font-weight: 500;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-3);
    transition: color var(--duration-fast) var(--ease-out), background var(--duration-fast) var(--ease-out);
    position: relative;
  }
  .np-nav__item:hover { color: var(--text-2); background: rgba(169,191,197,0.05); }
  .np-nav__item--active { color: var(--text-1); background: var(--surface-raised); }
  .np-nav__item--active::before {
    content: ''; position: absolute; left: -14px; top: 50%; transform: translateY(-50%);
    width: 5px; height: 5px; background: var(--teal); border-radius: 1px; /* square pad */
  }
  .np-side__foot { margin-top: auto; display: flex; flex-direction: column; gap: 14px; padding: 14px 8px 0; border-top: 1px solid var(--divider); }
  .np-user { display: flex; align-items: center; gap: 10px; }
  .np-user__avatar {
    width: 28px; height: 28px; border-radius: 50%; flex: none;
    background: var(--petrol); color: var(--text-1);
    display: flex; align-items: center; justify-content: center;
    font-family: var(--font-mono); font-size: 10px; letter-spacing: 0.05em;
  }
  .np-user__name { font-size: 12.5px; color: var(--text-2); }
  .np-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
  .np-top {
    height: 58px; flex: none; display: flex; align-items: center; gap: 16px;
    padding: 0 28px; border-bottom: 1px solid var(--divider);
  }
  .np-top__crumb { font-family: var(--font-mono); font-size: 11px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-2); }
  .np-top__date { font-family: var(--font-mono); font-size: 10.5px; letter-spacing: 0.08em; color: var(--text-3); }
  .np-top__right { margin-left: auto; display: flex; align-items: center; gap: 16px; }
  .np-screen { flex: 1; overflow-y: auto; padding: 28px; }
`;
if (!document.getElementById('np-shell-css')) {
  const s = document.createElement('style');
  s.id = 'np-shell-css';
  s.textContent = platformShellCSS;
  document.head.appendChild(s);
}
const NP_NAV = [{
  id: 'today',
  label: 'Today',
  icon: 'gauge'
}, {
  id: 'session',
  label: 'Live session',
  icon: 'activity'
}, {
  id: 'progress',
  label: 'Progress',
  icon: 'trending-up'
}, {
  id: 'protocols',
  label: 'Protocols',
  icon: 'list'
}];
function PlatformShell({
  screen,
  onNavigate,
  crumb,
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "np-shell"
  }, /*#__PURE__*/React.createElement("aside", {
    className: "np-side"
  }, /*#__PURE__*/React.createElement("div", {
    className: "np-brand"
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logo/neroes-appicon-dark.png",
    alt: "neroes"
  }), /*#__PURE__*/React.createElement("span", null, "neroes")), /*#__PURE__*/React.createElement("nav", {
    className: "np-nav"
  }, NP_NAV.map(item => /*#__PURE__*/React.createElement("button", {
    key: item.id,
    className: `np-nav__item${screen === item.id ? ' np-nav__item--active' : ''}`,
    onClick: () => onNavigate(item.id)
  }, /*#__PURE__*/React.createElement(Icon, {
    name: item.icon,
    size: 15
  }), item.label))), /*#__PURE__*/React.createElement("div", {
    className: "np-side__foot"
  }, /*#__PURE__*/React.createElement(StatusDot, {
    state: "good",
    label: "Headset \xB7 92%"
  }), /*#__PURE__*/React.createElement("div", {
    className: "np-user"
  }, /*#__PURE__*/React.createElement("span", {
    className: "np-user__avatar"
  }, "RM"), /*#__PURE__*/React.createElement("span", {
    className: "np-user__name"
  }, "Rui Martins")))), /*#__PURE__*/React.createElement("div", {
    className: "np-main"
  }, /*#__PURE__*/React.createElement("header", {
    className: "np-top"
  }, /*#__PURE__*/React.createElement("span", {
    className: "np-top__crumb"
  }, crumb), /*#__PURE__*/React.createElement("span", {
    className: "np-top__date"
  }, "THU 09 JUL 2026"), /*#__PURE__*/React.createElement("div", {
    className: "np-top__right"
  }, /*#__PURE__*/React.createElement(Badge, {
    variant: "teal",
    dot: true
  }, "Headset linked"), /*#__PURE__*/React.createElement(Icon, {
    name: "bell",
    size: 16,
    color: "var(--text-3)"
  }))), /*#__PURE__*/React.createElement("main", {
    className: "np-screen"
  }, children)));
}
Object.assign(window, {
  PlatformShell
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/platform/PlatformShell.jsx", error: String((e && e.message) || e) }); }

// ui_kits/platform/ProgressScreen.jsx
try { (() => {
/* Progress — longitudinal trends and session history. */
const {
  Card,
  Badge,
  Metric,
  TraceChart,
  Tabs,
  VoiceQuote,
  Divider
} = window.NeroesDesignSystem_23f8b7;
function ProgressScreen() {
  const [range, setRange] = React.useState('12w');
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Progress",
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      maxWidth: '1060px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-end',
      justifyContent: 'space-between'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "ds-label",
    style: {
      marginBottom: '6px'
    }
  }, "Focus block \xB7 Week 3 of 6"), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontSize: '26px'
    }
  }, "Progress")), /*#__PURE__*/React.createElement(Tabs, {
    items: [{
      value: '4w',
      label: '4 wk'
    }, {
      value: '12w',
      label: '12 wk'
    }, {
      value: 'all',
      label: 'All'
    }],
    value: range,
    onChange: setRange
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: '16px'
    }
  }, /*#__PURE__*/React.createElement(Card, {
    label: "Focus index"
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "74",
    unit: "/100",
    delta: "+22 SINCE W1"
  })), /*#__PURE__*/React.createElement(Card, {
    label: "Time to calm"
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "94",
    unit: "SEC",
    delta: "-38",
    deltaDirection: "up"
  })), /*#__PURE__*/React.createElement(Card, {
    label: "Sessions"
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "14",
    unit: "OF 24"
  })), /*#__PURE__*/React.createElement(Card, {
    label: "Artifact rate"
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "3.1",
    unit: "%",
    delta: "-1.2",
    deltaDirection: "up"
  }))), /*#__PURE__*/React.createElement(Card, {
    label: "Alpha power \xB7 weekly mean",
    flush: true,
    actions: /*#__PURE__*/React.createElement(Badge, {
      variant: "green"
    }, "+0.8 HZ this block")
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '16px 20px 12px'
    }
  }, /*#__PURE__*/React.createElement(TraceChart, {
    height: 190,
    series: [{
      data: [10.9, 11.1, 11.0, 11.4, 11.3, 11.8, 11.7, 12.0, 12.2, 12.1, 12.3, 12.4],
      color: 'teal'
    }, {
      data: [11.0, 11.0, 11.1, 11.1, 11.2, 11.2, 11.3, 11.3, 11.4, 11.4, 11.5, 11.5],
      color: 'blue'
    }],
    min: 10.5,
    max: 13,
    yLabels: ['10.5', '11.75', '13.0'],
    xLabels: ['W1', 'W4', 'W8', 'W12']
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1.4fr 1fr',
      gap: '16px'
    }
  }, /*#__PURE__*/React.createElement(Card, {
    label: "Band distribution \xB7 session 14",
    flush: true
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '18px 20px',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }
  }, [{
    band: 'DELTA · 0.5–4 HZ',
    pct: 18,
    color: 'var(--blue)'
  }, {
    band: 'THETA · 4–8 HZ',
    pct: 24,
    color: 'var(--blue-bright)'
  }, {
    band: 'ALPHA · 8–12 HZ',
    pct: 38,
    color: 'var(--teal-bright)'
  }, {
    band: 'BETA · 12–30 HZ',
    pct: 20,
    color: 'var(--green-bright)'
  }].map(b => /*#__PURE__*/React.createElement("div", {
    key: b.band,
    style: {
      display: 'grid',
      gridTemplateColumns: '150px 1fr 40px',
      alignItems: 'center',
      gap: '12px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '9.5px',
      letterSpacing: '0.08em',
      color: 'var(--text-3)'
    }
  }, b.band), /*#__PURE__*/React.createElement("div", {
    style: {
      height: '8px',
      background: 'var(--surface-inset)',
      border: '1px solid var(--border-1)',
      borderRadius: '4px',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: `${b.pct * 2}%`,
      height: '100%',
      background: b.color,
      opacity: 0.85
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '10.5px',
      color: 'var(--text-2)',
      textAlign: 'right'
    }
  }, b.pct, "%"))))), /*#__PURE__*/React.createElement(Card, {
    label: "Coach note"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '14px'
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: '13.5px',
      lineHeight: 1.6,
      color: 'var(--text-2)'
    }
  }, "Alpha gains are holding outside sessions. Next block adds distraction load during the hold phase."), /*#__PURE__*/React.createElement(Divider, null), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '9.5px',
      letterSpacing: '0.1em',
      textTransform: 'uppercase',
      color: 'var(--text-3)'
    }
  }, "Dr. A. Ferreira \xB7 07 Jul")))));
}
Object.assign(window, {
  ProgressScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/platform/ProgressScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/platform/ProtocolsScreen.jsx
try { (() => {
/* Protocols — training program library. */
const {
  Card,
  Button,
  Badge,
  Icon,
  Divider
} = window.NeroesDesignSystem_23f8b7;
const NP_PROTOCOLS = [{
  name: 'Focus hold',
  target: 'ALPHA 8–12 HZ',
  len: '24 MIN',
  level: 'Block 2',
  state: 'Active',
  desc: 'Sustain alpha above threshold under increasing load.'
}, {
  name: 'Calm baseline',
  target: 'HRV + ALPHA',
  len: '18 MIN',
  level: 'Block 1',
  state: 'Done',
  desc: 'Down-regulate arousal; establish a resting reference.'
}, {
  name: 'Stress recovery',
  target: 'TIME TO CALM',
  len: '22 MIN',
  level: 'Block 2',
  state: 'Available',
  desc: 'Recover to baseline after a controlled stressor.'
}, {
  name: 'Deep focus intervals',
  target: 'BETA / THETA RATIO',
  len: '30 MIN',
  level: 'Block 3',
  state: 'Locked',
  desc: 'Alternating hold and release intervals at threshold.'
}];
function npStateBadge(state) {
  if (state === 'Active') return /*#__PURE__*/React.createElement(Badge, {
    variant: "teal",
    dot: true
  }, "Active");
  if (state === 'Done') return /*#__PURE__*/React.createElement(Badge, {
    variant: "green"
  }, "Done");
  if (state === 'Locked') return /*#__PURE__*/React.createElement(Badge, {
    variant: "neutral"
  }, "Locked");
  return /*#__PURE__*/React.createElement(Badge, {
    variant: "outline"
  }, "Available");
}
function ProtocolsScreen({
  onStart
}) {
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Protocols",
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      maxWidth: '1060px'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "ds-label",
    style: {
      marginBottom: '6px'
    }
  }, "Training library"), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontSize: '26px'
    }
  }, "Protocols")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '16px'
    }
  }, NP_PROTOCOLS.map(p => /*#__PURE__*/React.createElement(Card, {
    key: p.name,
    label: p.target,
    title: p.name,
    actions: npStateBadge(p.state),
    footer: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", {
      style: {
        marginRight: 'auto',
        fontFamily: 'var(--font-mono)',
        fontSize: '10px',
        letterSpacing: '0.08em',
        color: 'var(--text-3)'
      }
    }, p.len, " \xB7 ", p.level.toUpperCase()), /*#__PURE__*/React.createElement(Button, {
      size: "sm",
      variant: p.state === 'Active' ? 'primary' : 'secondary',
      disabled: p.state === 'Locked',
      icon: p.state !== 'Locked' ? /*#__PURE__*/React.createElement(Icon, {
        name: "play",
        size: 13
      }) : null,
      onClick: onStart
    }, p.state === 'Active' ? 'Continue' : 'Start'))
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: '13px',
      lineHeight: 1.55,
      color: 'var(--text-2)'
    }
  }, p.desc)))));
}
Object.assign(window, {
  ProtocolsScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/platform/ProtocolsScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/platform/SessionScreen.jsx
try { (() => {
/* Live session — real-time trace, focus readout, protocol phases. */
const {
  Card,
  Button,
  IconButton,
  Badge,
  Metric,
  TraceChart,
  StatusDot,
  Icon
} = window.NeroesDesignSystem_23f8b7;
function npMakeLive(seed, n) {
  const out = [];
  let v = 60;
  for (let i = 0; i < n; i++) {
    v += Math.sin((seed + i) * 1.7) * 6 + Math.sin((seed + i) * 0.31) * 3;
    v = Math.max(20, Math.min(95, v));
    out.push(v);
  }
  return out;
}
const NP_PHASES = [{
  name: 'Baseline',
  min: 3,
  done: true
}, {
  name: 'Hold',
  min: 12,
  done: false,
  active: true
}, {
  name: 'Recover',
  min: 5,
  done: false
}, {
  name: 'Re-test',
  min: 4,
  done: false
}];
function SessionScreen({
  onEnd
}) {
  const [tick, setTick] = React.useState(0);
  const [paused, setPaused] = React.useState(false);
  React.useEffect(() => {
    if (paused) return;
    const t = setInterval(() => setTick(v => v + 1), 700);
    return () => clearInterval(t);
  }, [paused]);
  const eeg = React.useMemo(() => npMakeLive(tick, 60), [tick]);
  const focus = Math.round(64 + Math.sin(tick * 0.4) * 6);
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Live session",
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      maxWidth: '1060px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: '14px'
    }
  }, /*#__PURE__*/React.createElement(StatusDot, {
    state: paused ? 'idle' : 'live',
    label: paused ? 'Paused' : 'Recording'
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '11px',
      letterSpacing: '0.1em',
      color: 'var(--text-3)'
    }
  }, "SESSION 15 \xB7 FOCUS HOLD \xB7 08:41 ELAPSED"), /*#__PURE__*/React.createElement("div", {
    style: {
      marginLeft: 'auto',
      display: 'flex',
      gap: '8px'
    }
  }, /*#__PURE__*/React.createElement(IconButton, {
    variant: "outline",
    label: paused ? 'Resume' : 'Pause',
    onClick: () => setPaused(!paused)
  }, /*#__PURE__*/React.createElement(Icon, {
    name: paused ? 'play' : 'pause',
    size: 15
  })), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    onClick: onEnd
  }, "End session"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '2.2fr 1fr',
      gap: '16px'
    }
  }, /*#__PURE__*/React.createElement(Card, {
    label: "EEG \xB7 CH 1\u20134 composite",
    flush: true,
    actions: /*#__PURE__*/React.createElement(Badge, {
      variant: "teal",
      dot: true
    }, paused ? 'Held' : 'Live')
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '14px 16px 10px',
      background: 'var(--surface-inset)',
      borderRadius: '0 0 var(--radius-md) var(--radius-md)'
    }
  }, /*#__PURE__*/React.createElement(TraceChart, {
    height: 210,
    min: 0,
    max: 100,
    series: [{
      data: eeg,
      color: 'teal'
    }],
    yLabels: ['0', '50', '100']
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '16px'
    }
  }, /*#__PURE__*/React.createElement(Card, {
    label: "Focus index"
  }, /*#__PURE__*/React.createElement(Metric, {
    value: String(focus),
    unit: "/100",
    size: "xl"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: '14px',
      height: '6px',
      borderRadius: '3px',
      background: 'var(--surface-inset)',
      border: '1px solid var(--border-1)',
      position: 'relative',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      inset: '0 auto 0 0',
      width: `${focus}%`,
      background: 'var(--teal)',
      borderRadius: '3px',
      transition: 'width 600ms var(--ease-out)'
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      marginTop: '6px',
      fontFamily: 'var(--font-mono)',
      fontSize: '9px',
      color: 'var(--text-3)',
      letterSpacing: '0.08em'
    }
  }, /*#__PURE__*/React.createElement("span", null, "TARGET 60"), /*#__PURE__*/React.createElement("span", null, "PEAK 78"))), /*#__PURE__*/React.createElement(Card, {
    label: "Signal"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '10px'
    }
  }, /*#__PURE__*/React.createElement(StatusDot, {
    state: "good",
    label: "CH-1 \xB7 Strong"
  }), /*#__PURE__*/React.createElement(StatusDot, {
    state: "good",
    label: "CH-2 \xB7 Strong"
  }), /*#__PURE__*/React.createElement(StatusDot, {
    state: "caution",
    label: "CH-3 \xB7 Drift"
  }), /*#__PURE__*/React.createElement(StatusDot, {
    state: "good",
    label: "CH-4 \xB7 Strong"
  }))))), /*#__PURE__*/React.createElement(Card, {
    label: "Protocol",
    title: "Focus hold \xB7 24 min",
    flush: true
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)'
    }
  }, NP_PHASES.map((p, i) => /*#__PURE__*/React.createElement("div", {
    key: p.name,
    style: {
      padding: '14px 20px',
      borderLeft: i === 0 ? 'none' : '1px solid var(--divider)',
      display: 'flex',
      flexDirection: 'column',
      gap: '6px',
      background: p.active ? 'var(--teal-dim)' : 'transparent'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '9.5px',
      letterSpacing: '0.12em',
      textTransform: 'uppercase',
      color: p.active ? 'var(--teal-bright)' : 'var(--text-3)'
    }
  }, p.done ? '✓ ' : '', "Phase ", i + 1), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: '13.5px',
      fontWeight: 500,
      color: p.active || p.done ? 'var(--text-1)' : 'var(--text-3)'
    }
  }, p.name), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '10px',
      color: 'var(--text-3)'
    }
  }, p.min, " MIN"))))));
}
Object.assign(window, {
  SessionScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/platform/SessionScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/LandingSections.jsx
try { (() => {
/* Landing page sections — hero, evidence, method, vision, CTA. */
const {
  Button,
  Badge,
  Card,
  Metric,
  TraceChart,
  StatusDot,
  VoiceQuote,
  Divider,
  Icon
} = window.NeroesDesignSystem_23f8b7;
const landingCSS = `
  .nw-wrap { max-width: 1120px; margin: 0 auto; padding: 0 40px; }
  .nw-eyebrow {
    font-family: var(--font-mono); font-size: 10.5px; font-weight: 500;
    letter-spacing: 0.22em; text-transform: uppercase; color: var(--teal-bright);
    display: inline-flex; align-items: center; gap: 10px;
  }
  .nw-eyebrow::before { content: ''; width: 20px; height: 1px; background: var(--teal); }
  .nw-h1 { font-size: 56px; font-weight: 600; line-height: 1.1; letter-spacing: var(--tracking-display); color: var(--text-1); margin: 18px 0 0; text-wrap: balance; }
  .nw-h2 { font-size: 32px; font-weight: 600; line-height: 1.18; letter-spacing: var(--tracking-heading); color: var(--text-1); margin: 14px 0 0; text-wrap: balance; }
  .nw-sub { font-size: 16px; line-height: 1.65; color: var(--text-2); max-width: 54ch; margin: 18px 0 0; text-wrap: pretty; }
  .nw-hero { padding-top: 88px; padding-bottom: 72px; display: grid; grid-template-columns: 1.05fr 1fr; gap: 56px; align-items: center; }
  .nw-panel { background: var(--surface-card); border: 1px solid var(--border-1); border-radius: var(--radius-lg); box-shadow: var(--shadow-2); overflow: hidden; }
  .nw-panel__bar { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-bottom: 1px solid var(--divider); }
  .nw-section { padding: 72px 0; border-top: 1px solid var(--divider); }
  .nw-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 40px; }
  .nw-step { border: 1px solid var(--border-1); border-radius: var(--radius-md); background: var(--surface-card); padding: 22px; display: flex; flex-direction: column; gap: 12px; }
  .nw-step__n { font-family: var(--font-mono); font-size: 10px; letter-spacing: 0.16em; color: var(--teal-bright); }
  .nw-step__t { font-size: 17px; font-weight: 600; color: var(--text-1); }
  .nw-step__d { font-size: 13.5px; line-height: 1.6; color: var(--text-2); margin: 0; }
  .nw-evidence { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 40px; }
`;
if (!document.getElementById('nw-landing-css')) {
  const s = document.createElement('style');
  s.id = 'nw-landing-css';
  s.textContent = landingCSS;
  document.head.appendChild(s);
}
function HeroSection() {
  return /*#__PURE__*/React.createElement("section", {
    className: "nw-wrap nw-hero",
    "data-screen-label": "Hero"
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("span", {
    className: "nw-eyebrow"
  }, "Closed-loop neurotechnology \xB7 Lisbon"), /*#__PURE__*/React.createElement("h1", {
    className: "nw-h1"
  }, "Train the mind the way you train the body."), /*#__PURE__*/React.createElement("p", {
    className: "nw-sub"
  }, "Neroes reads the brain in real time and trains the circuits behind anxiety, focus, and performance \u2014 with objective feedback instead of guesswork."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '12px',
      marginTop: '32px'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    size: "lg"
  }, "Request access"), /*#__PURE__*/React.createElement(Button, {
    size: "lg",
    variant: "secondary"
  }, "See the science")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '24px',
      marginTop: '36px'
    }
  }, /*#__PURE__*/React.createElement(StatusDot, {
    state: "good",
    label: "CE-marked hardware"
  }), /*#__PURE__*/React.createElement(StatusDot, {
    state: "good",
    label: "Data stays yours"
  }))), /*#__PURE__*/React.createElement("div", {
    className: "nw-panel"
  }, /*#__PURE__*/React.createElement("div", {
    className: "nw-panel__bar"
  }, /*#__PURE__*/React.createElement(StatusDot, {
    state: "live",
    label: "Session 15 \xB7 Live"
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      marginLeft: 'auto',
      fontFamily: 'var(--font-mono)',
      fontSize: '10px',
      letterSpacing: '0.08em',
      color: 'var(--text-3)'
    }
  }, "ALPHA 12.4 HZ")), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '18px 16px 10px',
      background: 'var(--surface-inset)'
    }
  }, /*#__PURE__*/React.createElement(TraceChart, {
    height: 180,
    min: 0,
    max: 100,
    series: [{
      data: [48, 52, 46, 58, 50, 62, 55, 68, 60, 72, 66, 74, 70, 78, 72],
      color: 'teal'
    }, {
      data: [40, 42, 41, 44, 43, 46, 45, 48, 47, 50, 49, 52, 51, 54, 53],
      color: 'blue'
    }],
    yLabels: ['0', '50', '100'],
    xLabels: ['0:00', '12:00', '24:00']
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '28px',
      padding: '14px 16px'
    }
  }, /*#__PURE__*/React.createElement(Metric, {
    label: "Focus index",
    value: "74",
    delta: "+6"
  }), /*#__PURE__*/React.createElement(Metric, {
    label: "Time to calm",
    value: "94",
    unit: "SEC",
    delta: "-38",
    deltaDirection: "up"
  }))));
}
function EvidenceSection() {
  return /*#__PURE__*/React.createElement("section", {
    className: "nw-section",
    id: "evidence",
    "data-screen-label": "Evidence"
  }, /*#__PURE__*/React.createElement("div", {
    className: "nw-wrap"
  }, /*#__PURE__*/React.createElement("span", {
    className: "nw-eyebrow"
  }, "Measured"), /*#__PURE__*/React.createElement("h2", {
    className: "nw-h2"
  }, "The evidence earns the right to the vision."), /*#__PURE__*/React.createElement("div", {
    className: "nw-evidence"
  }, /*#__PURE__*/React.createElement(Card, {
    label: "Pilot \xB7 N=41 \xB7 2025"
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "31",
    unit: "%",
    size: "lg"
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: '10px 0 0',
      fontFamily: 'var(--font-mono)',
      fontSize: '11px',
      lineHeight: 1.7,
      letterSpacing: '0.04em',
      color: 'var(--text-2)'
    }
  }, "MEAN ANXIETY SCORE REDUCTION OVER EIGHT SESSIONS")), /*#__PURE__*/React.createElement(Card, {
    label: "Follow-up \xB7 12 weeks"
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "87",
    unit: "%",
    size: "lg"
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: '10px 0 0',
      fontFamily: 'var(--font-mono)',
      fontSize: '11px',
      lineHeight: 1.7,
      letterSpacing: '0.04em',
      color: 'var(--text-2)'
    }
  }, "OF PARTICIPANTS HELD OR EXTENDED THEIR GAINS")), /*#__PURE__*/React.createElement(Card, {
    label: "Loop latency"
  }, /*#__PURE__*/React.createElement(Metric, {
    value: "<40",
    unit: "MS",
    size: "lg"
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: '10px 0 0',
      fontFamily: 'var(--font-mono)',
      fontSize: '11px',
      lineHeight: 1.7,
      letterSpacing: '0.04em',
      color: 'var(--text-2)'
    }
  }, "FROM SIGNAL TO FEEDBACK, EVERY CYCLE")))));
}
function MethodSection() {
  return /*#__PURE__*/React.createElement("section", {
    className: "nw-section",
    id: "platform",
    "data-screen-label": "Method"
  }, /*#__PURE__*/React.createElement("div", {
    className: "nw-wrap"
  }, /*#__PURE__*/React.createElement("span", {
    className: "nw-eyebrow"
  }, "The loop"), /*#__PURE__*/React.createElement("h2", {
    className: "nw-h2"
  }, "Read. Train. Measure. Repeat."), /*#__PURE__*/React.createElement("div", {
    className: "nw-steps"
  }, /*#__PURE__*/React.createElement("div", {
    className: "nw-step"
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "waves",
    size: 20,
    color: "var(--teal-bright)"
  }), /*#__PURE__*/React.createElement("span", {
    className: "nw-step__n"
  }, "01 \xB7 READ"), /*#__PURE__*/React.createElement("span", {
    className: "nw-step__t"
  }, "Signal, not guesswork"), /*#__PURE__*/React.createElement("p", {
    className: "nw-step__d"
  }, "Research-grade EEG reads the circuits behind anxiety, focus, and performance \u2014 live, at the millisecond scale.")), /*#__PURE__*/React.createElement("div", {
    className: "nw-step"
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "activity",
    size: 20,
    color: "var(--teal-bright)"
  }), /*#__PURE__*/React.createElement("span", {
    className: "nw-step__n"
  }, "02 \xB7 TRAIN"), /*#__PURE__*/React.createElement("span", {
    className: "nw-step__t"
  }, "Closed-loop protocols"), /*#__PURE__*/React.createElement("p", {
    className: "nw-step__d"
  }, "When the target circuit engages, you know instantly. The loop closes in under 40 milliseconds, session after session.")), /*#__PURE__*/React.createElement("div", {
    className: "nw-step"
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "trending-up",
    size: 20,
    color: "var(--teal-bright)"
  }), /*#__PURE__*/React.createElement("span", {
    className: "nw-step__n"
  }, "03 \xB7 MEASURE"), /*#__PURE__*/React.createElement("span", {
    className: "nw-step__t"
  }, "Progress you can see"), /*#__PURE__*/React.createElement("p", {
    className: "nw-step__d"
  }, "Every session ends in numbers \u2014 focus index, time to calm, alpha power \u2014 tracked against your own baseline.")))));
}
function VisionSection() {
  return /*#__PURE__*/React.createElement("section", {
    className: "nw-section",
    id: "science",
    "data-screen-label": "Vision",
    style: {
      background: 'var(--ink-800)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "nw-wrap",
    style: {
      display: 'flex',
      justifyContent: 'center',
      padding: '24px 40px'
    }
  }, /*#__PURE__*/React.createElement(VoiceQuote, {
    voice: "vision",
    size: "lg",
    source: "Neroes \xB7 Founding note"
  }, "A gym for the mind \u2014 where mental fitness is trained, measured, and earned like physical fitness.")));
}
function CtaSection() {
  return /*#__PURE__*/React.createElement("section", {
    className: "nw-section",
    id: "company",
    "data-screen-label": "CTA"
  }, /*#__PURE__*/React.createElement("div", {
    className: "nw-wrap",
    style: {
      textAlign: 'center',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '8px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "nw-eyebrow",
    style: {
      justifyContent: 'center'
    }
  }, "Early access"), /*#__PURE__*/React.createElement("h2", {
    className: "nw-h2"
  }, "Start training with your own signal."), /*#__PURE__*/React.createElement("p", {
    className: "nw-sub",
    style: {
      margin: '14px auto 0'
    }
  }, "Now onboarding performance teams and research partners in Lisbon and remote."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '12px',
      marginTop: '28px'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    size: "lg"
  }, "Request access"), /*#__PURE__*/React.createElement(Button, {
    size: "lg",
    variant: "ghost"
  }, "Talk to research"))));
}
Object.assign(window, {
  HeroSection,
  EvidenceSection,
  MethodSection,
  VisionSection,
  CtaSection
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/LandingSections.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/SiteChrome.jsx
try { (() => {
/* Site chrome — marketing nav + footer. */
const {
  Button,
  Badge
} = window.NeroesDesignSystem_23f8b7;
const siteChromeCSS = `
  .nw-nav {
    position: sticky; top: 0; z-index: 40;
    display: flex; align-items: center; gap: 28px;
    padding: 0 40px; height: 64px;
    background: rgba(21, 46, 56, 0.82);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--divider);
  }
  .nw-nav__brand { display: flex; align-items: center; gap: 10px; }
  .nw-nav__brand img { width: 28px; height: 28px; border-radius: 7px; }
  .nw-nav__brand span { font-weight: 600; font-size: 17px; color: var(--text-1); letter-spacing: -0.01em; }
  .nw-nav__links { display: flex; gap: 4px; margin-left: 12px; }
  .nw-nav__link {
    font-family: var(--font-mono); font-size: 10.5px; font-weight: 500;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--text-3); padding: 8px 12px; border-radius: var(--radius-pill);
    transition: color var(--duration-fast) var(--ease-out);
  }
  .nw-nav__link:hover { color: var(--text-1); }
  .nw-nav__right { margin-left: auto; display: flex; align-items: center; gap: 10px; }
  .nw-foot {
    border-top: 1px solid var(--divider);
    padding: 48px 40px 40px;
    display: flex; flex-wrap: wrap; gap: 48px; justify-content: space-between;
  }
  .nw-foot__col { display: flex; flex-direction: column; gap: 10px; }
  .nw-foot__head { font-family: var(--font-mono); font-size: 10px; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--text-3); margin-bottom: 4px; }
  .nw-foot__link { font-size: 13px; color: var(--text-2); }
  .nw-foot__link:hover { color: var(--text-1); }
  .nw-foot__legal { font-family: var(--font-mono); font-size: 10px; letter-spacing: 0.06em; color: var(--text-3); line-height: 1.8; max-width: 380px; }
`;
if (!document.getElementById('nw-chrome-css')) {
  const s = document.createElement('style');
  s.id = 'nw-chrome-css';
  s.textContent = siteChromeCSS;
  document.head.appendChild(s);
}
function SiteNav() {
  return /*#__PURE__*/React.createElement("nav", {
    className: "nw-nav"
  }, /*#__PURE__*/React.createElement("a", {
    href: "#",
    className: "nw-nav__brand"
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logo/neroes-appicon-dark.png",
    alt: ""
  }), /*#__PURE__*/React.createElement("span", null, "neroes")), /*#__PURE__*/React.createElement("div", {
    className: "nw-nav__links"
  }, /*#__PURE__*/React.createElement("a", {
    className: "nw-nav__link",
    href: "#platform"
  }, "Platform"), /*#__PURE__*/React.createElement("a", {
    className: "nw-nav__link",
    href: "#science"
  }, "Science"), /*#__PURE__*/React.createElement("a", {
    className: "nw-nav__link",
    href: "#evidence"
  }, "Evidence"), /*#__PURE__*/React.createElement("a", {
    className: "nw-nav__link",
    href: "#company"
  }, "Company")), /*#__PURE__*/React.createElement("div", {
    className: "nw-nav__right"
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    size: "sm"
  }, "Sign in"), /*#__PURE__*/React.createElement(Button, {
    size: "sm"
  }, "Request access")));
}
function SiteFooter() {
  return /*#__PURE__*/React.createElement("footer", {
    className: "nw-foot"
  }, /*#__PURE__*/React.createElement("div", {
    className: "nw-foot__col"
  }, /*#__PURE__*/React.createElement("div", {
    className: "nw-nav__brand",
    style: {
      marginBottom: '10px'
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logo/neroes-appicon-dark.png",
    alt: "",
    style: {
      width: '26px',
      height: '26px',
      borderRadius: '6px'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 600,
      fontSize: '15px',
      color: 'var(--text-1)'
    }
  }, "neroes")), /*#__PURE__*/React.createElement("p", {
    className: "nw-foot__legal",
    style: {
      margin: 0
    }
  }, "NEROES \xB7 LISBOA, PORTUGAL", /*#__PURE__*/React.createElement("br", null), "A TRAINING AND RESEARCH PLATFORM. NOT A MEDICAL DEVICE; DOES NOT DIAGNOSE, CURE, OR TREAT ANY CONDITION.")), /*#__PURE__*/React.createElement("div", {
    className: "nw-foot__col"
  }, /*#__PURE__*/React.createElement("span", {
    className: "nw-foot__head"
  }, "Platform"), /*#__PURE__*/React.createElement("a", {
    className: "nw-foot__link",
    href: "#"
  }, "Mental Training"), /*#__PURE__*/React.createElement("a", {
    className: "nw-foot__link",
    href: "#"
  }, "For teams"), /*#__PURE__*/React.createElement("a", {
    className: "nw-foot__link",
    href: "#"
  }, "For researchers")), /*#__PURE__*/React.createElement("div", {
    className: "nw-foot__col"
  }, /*#__PURE__*/React.createElement("span", {
    className: "nw-foot__head"
  }, "Science"), /*#__PURE__*/React.createElement("a", {
    className: "nw-foot__link",
    href: "#"
  }, "Method"), /*#__PURE__*/React.createElement("a", {
    className: "nw-foot__link",
    href: "#"
  }, "Publications"), /*#__PURE__*/React.createElement("a", {
    className: "nw-foot__link",
    href: "#"
  }, "Data practices")), /*#__PURE__*/React.createElement("div", {
    className: "nw-foot__col"
  }, /*#__PURE__*/React.createElement("span", {
    className: "nw-foot__head"
  }, "Company"), /*#__PURE__*/React.createElement("a", {
    className: "nw-foot__link",
    href: "#"
  }, "About"), /*#__PURE__*/React.createElement("a", {
    className: "nw-foot__link",
    href: "#"
  }, "Careers"), /*#__PURE__*/React.createElement("a", {
    className: "nw-foot__link",
    href: "#"
  }, "Contact")));
}
Object.assign(window, {
  SiteNav,
  SiteFooter
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/SiteChrome.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.Metric = __ds_scope.Metric;

__ds_ns.StatusDot = __ds_scope.StatusDot;

__ds_ns.TraceChart = __ds_scope.TraceChart;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Divider = __ds_scope.Divider;

__ds_ns.Tabs = __ds_scope.Tabs;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Radio = __ds_scope.Radio;

__ds_ns.Select = __ds_scope.Select;

__ds_ns.Switch = __ds_scope.Switch;

__ds_ns.Icon = __ds_scope.Icon;

__ds_ns.Dialog = __ds_scope.Dialog;

__ds_ns.Toast = __ds_scope.Toast;

__ds_ns.Tooltip = __ds_scope.Tooltip;

__ds_ns.VoiceQuote = __ds_scope.VoiceQuote;

})();
