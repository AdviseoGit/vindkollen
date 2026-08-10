document.addEventListener("DOMContentLoaded", function() {
    // 1. CTA Clicks
    const ctas = document.querySelectorAll("a, button");
    ctas.forEach(cta => {
        cta.addEventListener("click", function(e) {
            const isButton = cta.tagName === "BUTTON";
            const isCtaLink = cta.tagName === "A" && (cta.classList.contains("bg-cyan-400") || cta.classList.contains("bg-cyan-500") || cta.classList.contains("bg-cyan-600"));
            
            if ((isButton || isCtaLink) && typeof window.gtag === 'function') {
                let location = 'mid-content';
                if (cta.closest('header') || cta.closest('.hero')) location = 'hero';
                if (cta.closest('footer')) location = 'footer';
                
                window.gtag('event', 'cta_click', {
                    'cta_text': cta.innerText || cta.value || 'unknown',
                    'cta_location': location,
                    'target_page': cta.href || window.location.pathname
                });
            }
            
            // 2. Navigation Clicks
            const isNav = cta.closest('nav') || cta.closest('header');
            const isFooter = cta.closest('footer');
            if (cta.tagName === "A" && (isNav || isFooter) && typeof window.gtag === 'function' && !isCtaLink) {
                let navType = isNav ? 'top' : 'footer';
                // Simple mobile check
                if (window.innerWidth < 768 && isNav) navType = 'mobile';
                
                window.gtag('event', 'navigation_click', {
                    'link_text': cta.innerText || 'unknown',
                    'link_url': cta.href,
                    'navigation_type': navType
                });
            }
        });
    });

    // 3. Scroll Depth
    let scrollMarks = { 25: false, 50: false, 75: false, 90: false };
    window.addEventListener("scroll", function() {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrollPercent = (scrollTop / scrollHeight) * 100;
        
        [25, 50, 75, 90].forEach(mark => {
            if (scrollPercent >= mark && !scrollMarks[mark]) {
                scrollMarks[mark] = true;
                if (typeof window.gtag === 'function') {
                    window.gtag('event', 'scroll_depth', {
                        'percent_scrolled': mark,
                        'page_path': window.location.pathname
                    });
                }
            }
        });
    });
});
