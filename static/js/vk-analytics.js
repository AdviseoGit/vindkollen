/*
 * vk-analytics.js — Enhanced GA4 event tracking for Vindkollen
 *
 * Tracks scroll depth, CTA clicks, and navigation interactions.
 * Include this script on all pages after vk-silo.js
 */
(function () {
    'use strict';

    var scrollDepthTracked = {};
    var scrollThresholds = [25, 50, 75, 90];

    function track(name, params) {
        if (typeof window.gtag === 'function') {
            try { 
                window.gtag('event', name, params || {}); 
            } catch (e) { 
                console.error('GA4 tracking error:', e);
            }
        }
    }

    /* --- Scroll Depth Tracking -------------------------------------------- */
    function getScrollPercent() {
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        var scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        return scrollHeight > 0 ? Math.round((scrollTop / scrollHeight) * 100) : 0;
    }

    function checkScrollDepth() {
        var percent = getScrollPercent();
        scrollThresholds.forEach(function (threshold) {
            if (percent >= threshold && !scrollDepthTracked[threshold]) {
                scrollDepthTracked[threshold] = true;
                track('scroll_depth', {
                    percent_scrolled: threshold,
                    page_path: window.location.pathname
                });
            }
        });
    }

    /* --- CTA Click Tracking ----------------------------------------------- */
    function trackCTAClick(el) {
        var text = el.textContent.trim();
        var href = el.href || el.dataset.href || '';
        var location = 'unknown';
        
        // Determine CTA location based on parent classes or position
        if (el.closest('header') || el.closest('nav')) {
            location = 'navigation';
        } else if (el.closest('footer')) {
            location = 'footer';
        } else if (el.closest('.hero-gradient') || el.closest('[class*="hero"]')) {
            location = 'hero';
        } else {
            location = 'content';
        }

        track('cta_click', {
            cta_text: text.substring(0, 100),  // Limit length
            cta_location: location,
            target_page: href.replace(window.location.origin, '')  // Relative URL
        });
    }

    /* --- Navigation Click Tracking ---------------------------------------- */
    function trackNavClick(el) {
        var text = el.textContent.trim();
        var href = el.href || '';
        var navType = 'unknown';

        if (el.closest('#mobile-menu')) {
            navType = 'mobile';
        } else if (el.closest('footer')) {
            navType = 'footer';
        } else if (el.closest('nav')) {
            navType = 'top';
        }

        track('navigation_click', {
            link_text: text.substring(0, 100),
            link_url: href.replace(window.location.origin, ''),
            navigation_type: navType
        });
    }

    /* --- Outbound Link Tracking ------------------------------------------- */
    function trackOutboundClick(el) {
        var href = el.href || '';
        track('outbound_click', {
            link_url: href,
            link_text: el.textContent.trim().substring(0, 100)
        });
    }

    /* --- Click Handlers --------------------------------------------------- */
    function handleClick(ev) {
        var el = ev.target.closest('a, button');
        if (!el) return;

        var href = el.href || '';
        var isCTA = el.classList.contains('cta') 
            || el.classList.contains('btn-primary')
            || el.dataset.trackCta === 'true'
            || (el.tagName === 'BUTTON' && el.type === 'button');
        
        var isNav = el.closest('nav') || el.closest('footer nav');
        var isOutbound = href && (href.indexOf('http') === 0) && (href.indexOf(window.location.host) === -1);

        if (isCTA) {
            trackCTAClick(el);
        } else if (isOutbound) {
            trackOutboundClick(el);
        } else if (isNav) {
            trackNavClick(el);
        }
    }

    /* --- Tool Interaction Tracking ---------------------------------------- */
    window.VKAnalytics = {
        track: track,
        trackToolInteraction: function(toolName, interactionType, params) {
            track('tool_interaction', Object.assign({
                tool_name: toolName,
                interaction_type: interactionType
            }, params || {}));
        }
    };

    /* --- Initialization --------------------------------------------------- */
    function init() {
        // Scroll depth
        var scrollDebounce;
        window.addEventListener('scroll', function() {
            clearTimeout(scrollDebounce);
            scrollDebounce = setTimeout(checkScrollDepth, 100);
        }, { passive: true });

        // Check scroll on load (for short pages)
        setTimeout(checkScrollDepth, 1000);

        // Click tracking
        document.addEventListener('click', handleClick, true);

        // Track page view with path
        track('page_view', {
            page_path: window.location.pathname,
            page_title: document.title
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
