/* Real-browser regressions; uses an existing Playwright installation (see docs). */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const os = require('node:os');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const site = path.resolve(__dirname, '../site');
const output = process.env.QA_DIR || fs.mkdtempSync(path.join(os.tmpdir(), 'orbital-qa-'));
fs.mkdirSync(output, { recursive: true });
const results = [];
const server = http.createServer((req, res) => {
  const file = path.resolve(site, '.' + new URL(req.url, 'http://localhost').pathname.replace(/\/$/, '/index.html'));
  if (!file.startsWith(site + path.sep) || !fs.existsSync(file)) { res.writeHead(404).end(); return; }
  const types = {'.html':'text/html', '.css':'text/css', '.js':'text/javascript', '.svg':'image/svg+xml'};
  res.setHeader('Content-Type', types[path.extname(file)] || 'text/plain');
  res.end(fs.readFileSync(file));
});
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch({channel: process.env.BROWSER_CHANNEL || 'chrome', headless: true});
  try {
    async function run(name, options, action, init) {
      const context = await browser.newContext(options);
      const page = await context.newPage();
      const errors = [], requests = [];
      page.on('pageerror', e => errors.push(e.message));
      page.on('console', m => { if (['error', 'warning'].includes(m.type())) errors.push(m.text()); });
      page.on('requestfailed', r => errors.push(r.failure().errorText));
      page.on('request', r => requests.push(r.url()));
      await page.addInitScript(() => {
        window.qaFrames = 0; window.qaLongTasks = [];
        const raf = window.requestAnimationFrame;
        window.requestAnimationFrame = cb => raf.call(window, t => { window.qaFrames++; cb(t); });
        new PerformanceObserver(list => window.qaLongTasks.push(...list.getEntries().map(e => e.duration))).observe({type:'longtask', buffered:true});
      });
      if (init) await page.addInitScript(init);
      try {
        await page.goto(url);
        assert.equal(await page.title(), 'Software. Infrastructure. Connected. — Jenya');
        assert.equal(new URL(page.url()).pathname, '/');
        assert.equal(await page.locator('h1').innerText(), 'Software.\nInfrastructure.\nConnected.');
        assert.equal(await page.locator('.project').count(), 3);
        assert.equal(await page.locator('.orbital-art svg > rect').count(), 0, 'inline hero has no opaque canvas');
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
        await action(page, context);
        await page.screenshot({path:path.join(output, `${name}.png`), fullPage:true});
        assert.deepEqual(errors, [], name + ' console/network');
        assert(requests.every(r => r.startsWith(url)), name + ' no external resources');
        results.push({name, result:'PASS', viewport:options.viewport, errors, requests:requests.length,
          metrics:await page.evaluate(() => ({rafCallbacks:window.qaFrames, longTasksMs:window.qaLongTasks,
            domNodes:document.querySelectorAll('*').length, domContentLoadedMs:performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd}))});
        console.log(name + ': PASS');
      } finally { await context.close(); }
    }
    const geometry = p => p.locator('#orbital-moving-helix').innerHTML();
    const pausedSpin = async p => {
      assert.equal(await p.locator('#orbital-play').innerText(), 'Play');
      assert.equal(await p.locator('#orbital-play').getAttribute('aria-label'), 'Play helix rotation');
      const stopped = await geometry(p);
      await sleep(700); // allow any independent parallax easing to settle
      assert.equal(await geometry(p), stopped, 'paused angle is exact');
      const frames = await p.evaluate(() => window.qaFrames);
      await sleep(150);
      assert.equal(await p.evaluate(() => window.qaFrames), frames, 'paused mode schedules no idle frames');
    };
    const staticVisible = async p => {
      assert.equal(await p.locator('.helix-control').isVisible(), false);
      assert.notEqual(await p.locator('#orbital-static-helix').getAttribute('visibility'), 'hidden');
      assert.equal(await p.locator('#orbital-field').getAttribute('transform'), null);
      assert.equal(await p.locator('.orbital-art svg').getAttribute('role'), 'img');
    };
    for (const [width, height] of [[1440,1024], [1280,720]]) {
      await run(`desktop-${width}`, {viewport:{width,height}, ...(width === 1280 ? {recordVideo:{dir:path.join(output,'video'),size:{width:1280,height:720}}} : {})}, async p => {
        const slider = p.getByRole('slider', {name:'Helix rotation'});
        await slider.waitFor({state:'visible'});
        const titleBox = await p.locator('h1').boundingBox();
        const box = await p.locator('.orbital-art').boundingBox();
        await p.mouse.move(box.x+box.width*.85, box.y+box.height*.2);
        await p.waitForFunction(() => document.querySelector('#orbital-field').getAttribute('transform') !== null);
        await sleep(650);
        const transform = await p.locator('#orbital-field').getAttribute('transform');
        const values = transform.match(/-?\d+(?:\.\d+)?/g).map(Number);
        assert(Math.abs(values[0]) <= 6 && Math.abs(values[1]) <= 4);
        assert.notEqual(transform, 'translate(0.00 0.00)');
        assert.deepEqual(await p.locator('h1').boundingBox(), titleBox);
        await slider.hover();
        assert.equal(await slider.evaluate(e => getComputedStyle(e).cursor), 'grab');
        assert.notEqual(await p.locator('#orbital-moving-helix').evaluate(e => getComputedStyle(e).filter), 'none');
        await p.screenshot({path:path.join(output, `hover-${width}.png`)});
        const before = await geometry(p);
        const hb = await slider.boundingBox(), cx = hb.x+hb.width/2, cy=hb.y+hb.height/2;
        await p.mouse.move(cx,cy); await p.mouse.down(); await p.mouse.move(cx+80,cy, {steps:12});
        await p.waitForFunction(() => Number(document.querySelector('.helix-control').getAttribute('aria-valuenow')) > 0);
        await sleep(50);
        assert.notEqual(await geometry(p), before);
        await p.screenshot({path:path.join(output, `drag-${width}.png`)});
        await p.mouse.move(cx,cy,{steps:12}); await p.mouse.up(); await sleep(60);
        assert.equal(await geometry(p), before, 'drag reversal returns exact geometry');
        await p.mouse.down(); await p.mouse.move(cx+100,cy,{steps:10}); await p.mouse.up();
        await sleep(60); const released = await geometry(p);
        await p.mouse.move(5,5); await sleep(700);
        assert.equal(await geometry(p), released, 'release freezes phase');
        assert.equal(await p.locator('#orbital-field').getAttribute('transform'), 'translate(0.00 0.00)');
        const frames = await p.evaluate(() => window.qaFrames); await sleep(180);
        assert.equal(await p.evaluate(() => window.qaFrames), frames, 'no idle animation');
        // Reach the control using Tab alone; it is not trapped in the artwork.
        await p.reload();
        for (let i=0;i<12 && !await slider.evaluate(e => e === document.activeElement);i++) await p.keyboard.press('Tab');
        assert.equal(await slider.evaluate(e => e === document.activeElement), true);
        assert.equal(await slider.evaluate(e => getComputedStyle(e).outlineStyle), 'solid');
        await p.keyboard.press('ArrowRight'); await sleep(40);
        assert.equal(await slider.getAttribute('aria-valuenow'), '15');
        await p.keyboard.press('ArrowLeft'); await sleep(40);
        assert.equal(await slider.getAttribute('aria-valuenow'), '0');
        await p.keyboard.press('End'); await sleep(40);
        assert.equal(await slider.getAttribute('aria-valuenow'), '359');
        await p.keyboard.press('Home'); await sleep(40);
        assert.equal(await slider.getAttribute('aria-valuenow'), '0');
        fs.writeFileSync(path.join(output, `accessibility-${width}.txt`), await p.locator('#orbital').ariaSnapshot());
        await p.screenshot({path:path.join(output, `focus-${width}.png`)});
        await p.keyboard.press('Tab'); assert.equal(await p.getByRole('button',{name:'Rotate helix left'}).evaluate(e=>e===document.activeElement),true);
        await p.getByRole('button',{name:'Static artwork'}).click(); await staticVisible(p);
        assert.equal(await p.getByRole('button',{name:'Rotate helix left'}).isDisabled(),true);
        await p.getByRole('button',{name:'Static artwork'}).click(); assert.equal(await slider.isVisible(),true);
        // Capture continues beyond the artwork; cancellation releases it cleanly.
        await slider.hover(); await p.mouse.down(); await p.mouse.move(4,4,{steps:8}); await p.mouse.up();
        assert.equal(await p.locator('#orbital').evaluate(e=>e.classList.contains('is-dragging')),false);
        await slider.hover(); await p.mouse.down(); await p.mouse.move(cx+50,cy,{steps:4});
        await slider.dispatchEvent('pointercancel');
        const cancelled=await geometry(p); await p.mouse.move(cx+90,cy); await p.mouse.up(); await sleep(50);
        assert.equal(await geometry(p),cancelled,'cancel freezes phase');
        assert.equal(await p.locator('#orbital').evaluate(e=>e.classList.contains('is-dragging')),false);
        await p.getByRole('link',{name:/Explore the work/}).click();
        assert.equal(new URL(p.url()).hash, '#work');
        for (const summary of await p.locator('summary').all()) { await summary.click(); assert.equal(await summary.evaluate(e=>e.parentElement.open),true); }
        await p.goto(url);
      });
    }
    for (const width of [1440,1280,390,320]) {
      const mobile = width < 720;
      await run(`spin-${width}`, {viewport:{width,height:mobile?844:1024},isMobile:mobile,hasTouch:mobile,
        ...(width===1440?{recordVideo:{dir:path.join(output,'spin-video'),size:{width:1440,height:1024}}}:{})}, async p => {
        const slider=p.getByRole('slider'), play=p.locator('#orbital-play');
        const activate = async locator => mobile ? locator.tap() : locator.click();
        await pausedSpin(p); // no autoplay at load
        await slider.scrollIntoViewIfNeeded();
        const initial=await geometry(p);
        await activate(slider);
        assert.equal(await slider.evaluate(e=>e===document.activeElement),true,'pointer focuses helix');
        assert.equal(await play.innerText(),'Pause');
        assert.equal(await play.getAttribute('aria-label'),'Pause helix rotation');
        await sleep(350);
        assert.notEqual(await geometry(p),initial,'user opt-in rotates strand geometry');
        await p.screenshot({path:path.join(output,`playing-${width}.png`)});
        await activate(slider); await pausedSpin(p);
        await activate(play); await sleep(100);
        assert.equal(await play.innerText(),'Pause','one button click starts');
        await activate(play); await pausedSpin(p);
        // Manual steps work with one activation, and stop a running rotation.
        await activate(slider);
        await p.keyboard.press('Home'); await sleep(50);
        await pausedSpin(p);
        assert.equal(await slider.getAttribute('aria-valuenow'),'0');
        await p.keyboard.press('ArrowRight'); await sleep(50);
        assert.equal(await slider.getAttribute('aria-valuenow'),'15','no Enter after pointer focus');
        await activate(play); await sleep(100);
        const angle=Number(await slider.getAttribute('aria-valuenow'));
        await activate(p.getByRole('button',{name:'Rotate helix right'})); await sleep(50);
        assert(Math.abs(Number(await slider.getAttribute('aria-valuenow'))-angle-15)<5);
        await pausedSpin(p);
        // Native button keyboard activation, visible focus, and no global arrows.
        await play.focus();
        await p.keyboard.press('Enter'); assert.equal(await play.innerText(),'Pause');
        await p.keyboard.press('Space'); await pausedSpin(p);
        assert.equal(await play.evaluate(e=>getComputedStyle(e).outlineStyle),'solid');
        const fixed=await geometry(p);
        await p.keyboard.press('ArrowRight'); await sleep(50);
        assert.equal(await geometry(p),fixed,'arrows only affect focused slider');
        await p.keyboard.press('Space'); assert.equal(await play.innerText(),'Pause');
        await p.keyboard.press('Enter'); await pausedSpin(p);
        await activate(play);
        await p.getByRole('link',{name:/Explore the work/}).focus();
        await pausedSpin(p); // leaving controls never leaves rotation running
        await activate(play);
        await p.getByRole('button',{name:'Static artwork'}).click(); await staticVisible(p);
        assert.equal(await play.isDisabled(),true);
        const frames=await p.evaluate(()=>window.qaFrames); await sleep(150);
        assert.equal(await p.evaluate(()=>window.qaFrames),frames);
        await p.getByRole('button',{name:'Static artwork'}).click();
        await pausedSpin(p); // returning from static mode never resumes
        await p.locator('#orbital').scrollIntoViewIfNeeded();
        await p.screenshot({path:path.join(output,`controls-${width}.png`)});
      });
    }
    await run('spin-drag-threshold', {viewport:{width:1440,height:1024}}, async p => {
      const slider=p.getByRole('slider'), play=p.locator('#orbital-play');
      const b=await slider.boundingBox(), x=b.x+b.width/2,y=b.y+b.height/2;
      await p.mouse.move(x,y); await p.mouse.down(); await p.mouse.move(x+3,y+2); await p.mouse.up();
      assert.equal(await play.innerText(),'Pause','small pointer jitter is a click');
      await sleep(100);
      await p.mouse.move(x,y); await p.mouse.down();
      const start=await geometry(p);
      await sleep(120); assert.equal(await geometry(p),start,'pointerdown freezes current angle');
      await p.mouse.move(x+40,y,{steps:5}); await sleep(50);
      assert.notEqual(await geometry(p),start,'drag remains manual');
      await p.mouse.move(x,y,{steps:5}); await p.mouse.up();
      await pausedSpin(p);
      assert.equal(await geometry(p),start,'drag reversal preserves exact starting angle');
      await slider.click(); await p.mouse.down();
      await slider.dispatchEvent('pointercancel'); await p.mouse.up();
      await pausedSpin(p); // release/cancel must not count as another Play
      await slider.click(); await p.mouse.down();
      await slider.dispatchEvent('lostpointercapture'); await p.mouse.up();
      await pausedSpin(p);
      await slider.click(); await p.mouse.down(); await p.mouse.move(x,y+25); await p.mouse.up();
      await pausedSpin(p); // vertical movement is not a Play shortcut
    });
    await run('spin-clock-and-visibility', {viewport:{width:1440,height:1024}}, async p => {
      // Controlled rAF timestamps exercise rate independence and hidden-state
      // scheduling deterministically; this case injects the visibility event.
      const play=p.locator('#orbital-play'), slider=p.getByRole('slider');
      await play.click();
      await p.evaluate(()=>{qaAdvance(0);for(let i=0;i<60;i++)qaAdvance(1000/60);});
      assert.equal(await slider.getAttribute('aria-valuenow'),'18','18 degrees in one second at 60Hz');
      await slider.focus(); await p.keyboard.press('Home');
      await play.click();
      await p.evaluate(()=>{qaAdvance(0);for(let i=0;i<20;i++)qaAdvance(50);});
      assert.equal(await slider.getAttribute('aria-valuenow'),'18','same speed at 20Hz');
      await p.evaluate(()=>qaAdvance(10000));
      assert(Number(await slider.getAttribute('aria-valuenow'))<21,'stall cannot jump a turn');
      const frozen=await geometry(p);
      await p.evaluate(()=>qaVisibility(true));
      assert.equal(await play.innerText(),'Play');
      assert.equal(await p.evaluate(()=>qaPending()),0,'hidden state cancels frames');
      await play.evaluate(e=>e.click());
      assert.equal(await play.innerText(),'Play','hidden document cannot start');
      await p.evaluate(()=>{qaAdvance(10000);qaVisibility(false);qaAdvance(0);});
      assert.equal(await geometry(p),frozen,'restore preserves angle without elapsed-time jump');
      assert.equal(await p.evaluate(()=>qaPending()),0,'restore stays idle');
    }, () => {
      let id=0,time=0,hidden=false;
      const frames=new Map();
      window.requestAnimationFrame=cb=>{frames.set(++id,cb);return id;};
      window.cancelAnimationFrame=id=>frames.delete(id);
      window.qaAdvance=ms=>{time+=ms;const pending=[...frames.values()];frames.clear();for(const cb of pending)cb(time);};
      window.qaPending=()=>frames.size;
      Object.defineProperty(document,'hidden',{get:()=>hidden});
      window.qaVisibility=value=>{hidden=value;document.dispatchEvent(new Event('visibilitychange'));};
    });
    for (const width of [390,320]) {
      await run(`touch-${width}`, {viewport:{width,height:844},isMobile:true,hasTouch:true}, async (p,ctx) => {
        const slider = p.getByRole('slider');
        await slider.scrollIntoViewIfNeeded();
        await p.getByRole('button',{name:'Rotate helix right'}).tap(); await sleep(50);
        assert.equal(await slider.getAttribute('aria-valuenow'),'15');
        await p.getByRole('button',{name:'Rotate helix left'}).tap(); await sleep(50);
        assert.equal(await slider.getAttribute('aria-valuenow'),'0');
        // Native Chromium touch input, including browser pan-y/pointercancel.
        const cdp = await ctx.newCDPSession(p);
        const b=await slider.boundingBox(), x=b.x+b.width/2, y=b.y+b.height*.7;
        const touch = async (type,x,y) => cdp.send('Input.dispatchTouchEvent',{type,touchPoints:type==='touchEnd'?[]:[{x,y}]});
        await touch('touchStart',x,y);
        for(let i=1;i<=8;i++){await touch('touchMove',x+i*7,y);await sleep(16);}
        await touch('touchEnd'); await sleep(60);
        assert(Number(await slider.getAttribute('aria-valuenow'))>0,'touch drag rotates');
        const fixed=await geometry(p); await sleep(100); assert.equal(await geometry(p),fixed);
        await slider.tap(); assert.equal(await p.locator('#orbital-play').innerText(),'Pause');
        await sleep(80);
        await slider.scrollIntoViewIfNeeded();
        const s=await slider.boundingBox(), sx=s.x+s.width/2, sy=s.y+s.height*.75;
        const scroll=await p.evaluate(()=>scrollY);
        await touch('touchStart',sx,sy);
        const beforeScroll=await geometry(p);
        for(let i=1;i<=8;i++){await touch('touchMove',sx,sy-i*15);await sleep(20);}
        await touch('touchEnd'); await sleep(350);
        assert(await p.evaluate(()=>scrollY)>scroll+30,'vertical gesture scrolls the page');
        assert.equal(await geometry(p),beforeScroll,'scroll pauses automatic rotation without twisting');
        await pausedSpin(p);
        await cdp.detach();
        await p.locator('#orbital').scrollIntoViewIfNeeded();
        await p.screenshot({path:path.join(output, `mobile-art-${width}.png`)});
      });
      await run(`no-js-${width}`, {viewport:{width,height:844},javaScriptEnabled:false}, staticVisible);
    }
    await run('no-js-desktop', {viewport:{width:1440,height:1024},javaScriptEnabled:false}, staticVisible);
    await run('reduced-motion', {viewport:{width:1440,height:1024},reducedMotion:'reduce'}, async (p) => {
      await staticVisible(p); assert.equal(await p.locator('.orbital-controls').isVisible(),false);
      await p.emulateMedia({reducedMotion:'no-preference'}); await p.getByRole('slider').waitFor({state:'visible'});
      await p.getByRole('slider').press('ArrowRight'); await sleep(50);
      await p.locator('#orbital-play').click();
      await p.emulateMedia({reducedMotion:'reduce'});
      await p.waitForFunction(()=>document.querySelector('#orbital-static-helix').getAttribute('visibility') !== 'hidden');
      await staticVisible(p);
      const frames=await p.evaluate(()=>window.qaFrames); await sleep(150);
      assert.equal(await p.evaluate(()=>window.qaFrames),frames);
      await p.emulateMedia({reducedMotion:'no-preference'});
      await p.getByRole('slider').waitFor({state:'visible'}); await pausedSpin(p);
    });
    await run('unsupported-input', {viewport:{width:1440,height:1024}}, staticVisible, () => { window.PointerEvent=undefined; });
    await run('initialization-error', {viewport:{width:1440,height:1024}}, async p => {
      await staticVisible(p); assert.equal(await p.locator('.orbital-controls').isVisible(),false);
    }, () => { document.createElementNS=()=>{throw new Error('QA initialization fault');}; });
    await run('interaction-error', {viewport:{width:1440,height:1024}}, async p => {
      await p.evaluate(()=> { document.querySelector('#orbital-moving-helix path').setAttribute=()=>{throw new Error('QA drawing fault');}; });
      await p.getByRole('button',{name:'Rotate helix right'}).click(); await sleep(60);
      await staticVisible(p); assert.equal(await p.locator('.orbital-controls').isVisible(),false);
    });
    fs.writeFileSync(path.join(output,'results.json'),JSON.stringify({browser:browser.version(),url,results},null,2));
    console.log(JSON.stringify({browser:browser.version(),cases:results.length,result:'PASS',artifacts:output},null,2));
  } finally { await browser.close(); server.close(); }
})().catch(e => { console.error(e); server.close(); process.exitCode=1; });
