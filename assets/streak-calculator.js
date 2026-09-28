/* Habit streak + consistency calculators for the localized tool pages
   (/xx/tools/habit-streak-calculator/). Strings come from window.STREAK_I18N,
   set inline on each page. The English page keeps its own inline copy.
   Everything runs in the browser; nothing is stored or sent. */
(function () {
    var T = window.STREAK_I18N;
    if (!T) return;
    var DAY = 86400000;
    var MILESTONES = [7, 21, 30, 66, 90, 100, 180, 365];
    var fmt = new Intl.DateTimeFormat(T.locale, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
    var used = {};

    function $(id) { return document.getElementById(id); }
    function fill(template, values) {
        return template.replace(/\{(\w+)\}/g, function (_, key) { return values[key] !== undefined ? values[key] : ''; });
    }
    function plural(forms, n) { return fill(n === 1 && forms.one ? forms.one : forms.other, { n: n.toLocaleString(T.locale) }); }
    function date(t) { return fmt.format(new Date(t)); }
    function track(tool) {
        if (used[tool]) return;
        used[tool] = true;
        if (typeof window.gtag === 'function') window.gtag('event', 'tool_use', { tool_name: tool, page_path: location.pathname });
    }
    function todayUTC() { var n = new Date(); return Date.UTC(n.getFullYear(), n.getMonth(), n.getDate()); }
    function parseDate(value) {
        var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value || '');
        return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) : null;
    }

    var start = $('streakStart');
    var today = todayUTC();
    start.max = new Date(today).toISOString().slice(0, 10);
    start.value = new Date(today - 12 * DAY).toISOString().slice(0, 10);

    function renderStreak() {
        var list = $('milestoneList'), line = $('streakNext');
        var s = parseDate(start.value);
        var doneToday = document.querySelector('input[name="today"]:checked').value === 'yes';
        list.innerHTML = '';
        line.classList.remove('calc-error');
        if (s === null) {
            $('streakDays').textContent = '–'; line.textContent = T.empty; $('streakBar').style.width = '0';
            return;
        }
        var elapsed = Math.round((today - s) / DAY);
        if (elapsed < 0) {
            $('streakDays').textContent = '–'; line.textContent = T.future; line.classList.add('calc-error'); $('streakBar').style.width = '0';
            return;
        }
        var streak = doneToday ? elapsed + 1 : elapsed;
        $('streakDays').textContent = streak.toLocaleString(T.locale);
        var next = null, prev = 0;
        MILESTONES.forEach(function (n) { if (n > streak && next === null) next = n; if (n <= streak) prev = n; });
        var text;
        if (streak === 0) {
            text = T.zero;
        } else if (next && !doneToday && s + (next - 1) * DAY === today) {
            text = fill(T.reach_today, { n: next });
        } else if (next) {
            text = fill(T.next, { left: plural(T.more_days, next - streak), n: next, date: date(s + (next - 1) * DAY) });
            if (!doneToday) text += ' ' + T.keep_going;
        } else {
            text = T.past365;
            if (!doneToday) text += ' ' + T.keep_going;
        }
        line.textContent = text;
        $('streakBar').style.width = next ? Math.max(4, Math.round((streak - prev) / (next - prev) * 100)) + '%' : '100%';

        MILESTONES.forEach(function (n) {
            var li = document.createElement('li');
            var reachedOn = s + (n - 1) * DAY;
            var strong = document.createElement('strong');
            strong.textContent = plural(T.days, n);
            li.appendChild(strong);
            var detail;
            if (streak >= n) {
                li.className = 'is-done';
                detail = fill(T.reached, { date: date(reachedOn) });
            } else if (reachedOn === today) {
                detail = T.today_checkin;
            } else {
                detail = fill(T.to_go, { date: date(reachedOn), left: plural(T.days, n - streak) });
            }
            li.appendChild(document.createTextNode(detail));
            list.appendChild(li);
        });
    }

    function renderConsistency() {
        var planned = parseInt($('plannedDays').value, 10);
        var done = parseInt($('doneDays').value, 10);
        var text = $('consistencyText'), next = $('consistencyNext');
        text.classList.remove('calc-error');
        next.textContent = '';
        if (!(planned >= 1) || !(done >= 0)) {
            $('consistencyPct').textContent = '–'; text.textContent = T.cons_empty;
            return;
        }
        if (done > planned) {
            $('consistencyPct').textContent = '–'; text.textContent = T.cons_error; text.classList.add('calc-error');
            return;
        }
        var pct = Math.round(done / planned * 100);
        $('consistencyPct').textContent = fill(T.percent, { p: pct });
        var verdict = pct >= 80 ? T.verdict_high : pct >= 50 ? T.verdict_mid : T.verdict_low;
        text.textContent = fill(T.cons_text, { done: done, planned: planned, verdict: verdict });
        next.textContent = fill(T.cons_next, {
            up: fill(T.percent, { p: Math.round((done + 1) / (planned + 1) * 100) }),
            down: fill(T.percent, { p: Math.round(done / (planned + 1) * 100) })
        });
    }

    start.addEventListener('input', function () { track('streak_calculator'); renderStreak(); });
    document.querySelectorAll('input[name="today"]').forEach(function (r) {
        r.addEventListener('change', function () { track('streak_calculator'); renderStreak(); });
    });
    ['plannedDays', 'doneDays'].forEach(function (id) {
        $(id).addEventListener('input', function () { track('consistency_calculator'); renderConsistency(); });
    });
    renderStreak();
    renderConsistency();
})();
