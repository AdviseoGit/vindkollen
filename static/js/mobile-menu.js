/*
 * Mobilmenyn — en implementation för hela sajten.
 *
 * Flera sidor hade tidigare egna inline-kopior av den här logiken, ibland två
 * på samma sida, vilket gav dubbla lyssnare. Allt ligger nu här, och koden är
 * idempotent: laddas filen två gånger kopplas ingenting på två gånger.
 */
(function () {
    'use strict';

    if (window.__vkMobileMenu) return;   // redan initierad
    window.__vkMobileMenu = true;

    function init() {
        var knapp = document.getElementById('mobile-menu-btn');
        var meny = document.getElementById('mobile-menu');
        var stang = document.getElementById('mobile-menu-close');
        if (!knapp || !meny) return;

        // Vissa overlays är byggda som flex-kolumner och behöver 'flex' för att
        // centreras — 'hidden' bort räcker inte, då blir de vanliga block.
        var behoverFlex = meny.className.indexOf('flex-col') !== -1
            && meny.className.indexOf('flex ') === -1;

        function oppna() {
            meny.classList.remove('hidden');
            if (behoverFlex) meny.classList.add('flex');
            document.body.style.overflow = 'hidden';
            knapp.setAttribute('aria-expanded', 'true');
            // Flytta fokus in i menyn så att tangentbord och skärmläsare följer med.
            var forsta = meny.querySelector('a, button');
            if (forsta) forsta.focus();
        }

        function stangMeny() {
            meny.classList.add('hidden');
            if (behoverFlex) meny.classList.remove('flex');
            document.body.style.overflow = '';
            knapp.setAttribute('aria-expanded', 'false');
        }

        knapp.addEventListener('click', function (e) {
            e.preventDefault();
            if (meny.classList.contains('hidden')) oppna(); else stangMeny();
        });

        if (stang) stang.addEventListener('click', stangMeny);

        // Stäng när man väljer något. Utan detta ligger menyn kvar över sidan
        // vid ankarlänkar, eftersom ingen sidladdning sker.
        meny.addEventListener('click', function (e) {
            if (e.target.closest('a')) stangMeny();
        });

        // Escape stänger, som i vilken dialog som helst.
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && !meny.classList.contains('hidden')) {
                stangMeny();
                knapp.focus();
            }
        });

        // Blir fönstret brett igen ska menyn inte ligga kvar och låsa scrollen.
        window.addEventListener('resize', function () {
            if (window.innerWidth >= 768 && !meny.classList.contains('hidden')) {
                stangMeny();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
