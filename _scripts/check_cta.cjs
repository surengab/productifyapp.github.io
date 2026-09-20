// Run against a local build: node _scripts/check_cta.cjs http://127.0.0.1:8768
// Requires Playwright. CHROME_PATH can select an existing Chrome executable.
const assert = require('node:assert/strict');
const { chromium, devices } = require('playwright');
const base = process.argv[2] || 'http://127.0.0.1:8768';
const output = process.env.CTA_SCREENSHOTS;
(async () => {
    const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH });
    try {
        for (const mode of ['desktop', 'iphone', 'android', 'storage-denied', 'no-js']) {
            const mobile = ['iphone', 'storage-denied'].includes(mode);
            const context = await browser.newContext({
                ...(mobile ? devices['iPhone 13'] : mode === 'android' ? devices['Pixel 7'] : { viewport: { width: 1440, height: 1000 } }),
                javaScriptEnabled: mode !== 'no-js', reducedMotion: 'reduce'
            });
            // Never send test events to production analytics or third-party stores.
            await context.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
            if (mode === 'storage-denied') await context.addInitScript(() => {
                Object.defineProperty(window, 'sessionStorage', { get() { throw new DOMException('Blocked', 'SecurityError'); } });
            });
            const page = await context.newPage();
            const errors = [];
            page.on('pageerror', error => errors.push(error.message));
            await page.goto(base, { waitUntil: 'networkidle' });
            assert.equal(await page.locator('script[src*="googletagmanager.com/gtag/js"]').count(), 1, 'Exactly one GA library load is expected');
            const hero = page.locator('.hero [data-cta="hero"]');
            assert.match(await hero.getAttribute('href'), mobile || mode === 'no-js' ? /apps\.apple\.com/ : /\/download\/$/);
            assert.equal((await hero.innerText()).replace(/\s+/g, ' ').trim(), 'Get Productify free →');
            if (output && ['desktop', 'iphone'].includes(mode)) await page.screenshot({ path: `${output}/home-${mode}.png` });
            if (mode !== 'no-js') {
                await page.evaluate(() => {
                    window.ctaEvents = [];
                    window.gtag = (...args) => window.ctaEvents.push(args);
                    document.addEventListener('click', e => { if (e.target.closest('a')) e.preventDefault(); });
                });
                await hero.click();
                const [event] = await page.evaluate(() => window.ctaEvents);
                assert.equal(event[1], mobile ? 'download_click' : 'download_page_click');
                assert.equal(event[2].cta_location, 'hero');
                assert.match(event[2].link_url, mobile ? /apps\.apple\.com/ : /\/download\/$/);
                await page.locator('.testimonials-aggregate__label').click();
                assert.equal(await page.evaluate(() => window.ctaEvents.length), 1, 'Review links must not inflate CTA clicks');
            }
            await page.goto(`${base}/download/`, { waitUntil: 'networkidle' });
            assert.equal(await page.locator('.dl-handoff').isVisible(), !mobile);
            assert.match(await page.locator('[data-cta="hero"]').getAttribute('href'), /apps\.apple\.com/);
            if (mode !== 'no-js') {
                await page.evaluate(() => {
                    window.ctaEvents = [];
                    window.gtag = (...args) => window.ctaEvents.push(args);
                    document.addEventListener('click', e => { if (e.target.closest('a')) e.preventDefault(); });
                });
                await page.locator('[data-cta="hero"] img').click();
                const [event] = await page.evaluate(() => window.ctaEvents);
                assert.equal(event[1], 'download_click', 'Nested badge clicks must count as outbound downloads');
                assert.equal(event[2].cta_location, 'hero');
                assert.match(event[2].link_url, /apps\.apple\.com\/us\/app\/habit-tracker-productify\/id1389900237/);
            }
            if (output && ['desktop', 'iphone'].includes(mode)) await page.screenshot({ path: `${output}/download-${mode}.png` });
            if (mode !== 'no-js') {
                await page.goto(`${base}/blog/habit-tracker-vs-to-do-list/`, { waitUntil: 'networkidle' });
                await page.locator('.inline-cta').scrollIntoViewIfNeeded();
                await page.waitForFunction(() => !document.querySelector('#stickyCta').classList.contains('is-visible'));
                const inline = page.locator('.inline-cta .download-button');
                assert.equal(await inline.evaluate(el => getComputedStyle(el).color), 'rgb(255, 255, 255)');
                assert.ok(await inline.isVisible());
                if (output && ['desktop', 'iphone'].includes(mode)) await page.screenshot({ path: `${output}/article-${mode}.png` });
                if (mobile) {
                    await page.locator('#quick-answer').evaluate(el => window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 140));
                    await page.waitForFunction(() => document.querySelector('#stickyCta').classList.contains('is-visible'));
                    assert.equal(await page.locator('#stickyCta').evaluate(el => el.inert), false);
                    if (output && mode === 'iphone') await page.screenshot({ path: `${output}/sticky-iphone.png` });
                    await page.locator('#stickyCtaClose').click();
                    await page.waitForFunction(() => document.querySelector('#stickyCta').hidden);
                    await page.reload({ waitUntil: 'networkidle' });
                    if (mode === 'iphone') assert.equal(await page.locator('#stickyCta').isVisible(), false);
                } else assert.equal(await page.locator('#stickyCta').isVisible(), false);
            }
            // Check narrow phone widths as well as normal desktop/mobile sizes.
            if (mode !== 'no-js') {
                await page.setViewportSize({ width: 320, height: 740 });
                await page.goto(base, { waitUntil: 'networkidle' });
                assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${mode}: homepage overflow`);
            }
            assert.deepEqual(errors, [], `${mode}: JavaScript errors`);
            await context.close();
            console.log(`CTA checks passed: ${mode}`);
        }
    } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
