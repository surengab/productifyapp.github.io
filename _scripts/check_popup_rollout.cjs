// Run after a Jekyll build: node _scripts/check_popup_rollout.cjs <build-directory>
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');

const root = process.argv[2] || '_site';
const hasPopup = page => readFileSync(join(root, page), 'utf8').includes('id="downloadPopup"');

for (const page of [
    'index.html', 'pricing/index.html', 'features/habit-duo/index.html',
    'compare/productify-vs-loop/index.html', 'solutions/morning-routine/index.html',
    'blog/habit-duo/index.html', 'guides/index.html'
]) assert.equal(hasPopup(page), true, `${page} should show the desktop offer`);

for (const page of ['download/index.html', '404.html', 'editorial/index.html', 'privacy.html']) {
    assert.equal(hasPopup(page), false, `${page} should not show the offer`);
}

console.log('Popup rollout targets verified');
