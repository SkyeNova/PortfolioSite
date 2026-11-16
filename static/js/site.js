// Small enhancements only. The site works without this file.
(function () {
    // Mobile menu
    var btn = document.querySelector('.bar .menu');
    var bar = document.querySelector('.bar');
    if (btn && bar) {
        btn.addEventListener('click', function () {
            var open = bar.classList.toggle('open');
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
        var close = function () {
            bar.classList.remove('open');
            btn.setAttribute('aria-expanded', 'false');
        };
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && bar.classList.contains('open')) { close(); btn.focus(); }
        });
        // Tapping a link (same-page anchors included) or anywhere outside closes it.
        document.addEventListener('click', function (e) {
            if (!bar.classList.contains('open')) return;
            if (!bar.contains(e.target) || e.target.closest('nav a')) close();
        });
    }

    // Reveal on scroll. Elements are visible by default; the hidden state only
    // applies once this has run and motion is allowed.
    var items = document.querySelectorAll('[data-reveal]');
    var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!items.length || still || !('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('in');
                io.unobserve(entry.target);
            }
        });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    items.forEach(function (el) {
        if (el.getBoundingClientRect().top < window.innerHeight * 0.9) return; // already on screen
        el.classList.add('pre');
        io.observe(el);
    });
})();

// Sticky header (Rook): frost the pill once the page has scrolled. One passive,
// rAF-throttled listener; only toggles a class, so it costs nothing per frame.
// The look change is colour-only, and its transition is off under
// prefers-reduced-motion in site.css.
(function () {
    var bar = document.querySelector('.bar');
    if (!bar) return;
    var queued = false, last = null;
    function update() {
        queued = false;
        var scrolled = window.scrollY > 24;
        if (scrolled !== last) { bar.classList.toggle('scrolled', scrolled); last = scrolled; }
    }
    window.addEventListener('scroll', function () {
        if (!queued) { queued = true; window.requestAnimationFrame(update); }
    }, { passive: true });
    update();
})();
