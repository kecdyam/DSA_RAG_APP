/* Calm cursor FX: a soft colour light + a grid that glows near the cursor. Nothing moves except the light. */
(() => {
  window.__fxInit = true;
  const d = document;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const lvl = () => (reduce ? 0 : (window.__fxLevel ?? 0.5));
  const grid = d.createElement("div"); grid.id = "fx-grid";
  const light = d.createElement("div"); light.id = "fx-light";
  d.body.append(grid, light);

  let mx = innerWidth / 2, my = innerHeight / 2, gx = mx, gy = my, raf = 0;
  const loop = () => {
    gx += (mx - gx) * 0.14; gy += (my - gy) * 0.14;
    const o = lvl() ? Math.min(lvl() * 1.4, 1) : 0;
    for (const el of [grid, light]) {
      el.style.setProperty("--mx", gx + "px"); el.style.setProperty("--my", gy + "px"); el.style.opacity = o;
    }
    raf = Math.abs(mx - gx) > 0.5 || Math.abs(my - gy) > 0.5 ? requestAnimationFrame(loop) : 0;
  };

  /* panels, buttons and the header get a soft light that follows the cursor while hovered */
  const SEL = ".stButton>button,[data-testid='stChatMessage'],[data-testid='stChatInput']>div,.hdr,.src";
  let last = null;
  const clear = () => { if (last) { last.style.removeProperty("--lx"); last.style.removeProperty("--ly"); last = null; } };
  addEventListener("pointermove", e => {
    mx = e.clientX; my = e.clientY; if (!raf) raf = requestAnimationFrame(loop);
    const t = e.target.closest ? e.target.closest(SEL) : null;
    if (t !== last) clear();
    if (t) {
      last = t; const r = t.getBoundingClientRect();
      t.style.setProperty("--lx", e.clientX - r.left + "px"); t.style.setProperty("--ly", e.clientY - r.top + "px");
    }
  }, { passive: true });
  d.documentElement.addEventListener("mouseleave", clear);
  loop();
})();