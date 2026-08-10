function trackCalculatorComplete(elarea, distance, height, count, compensation, promille) {
    if (typeof window.gtag === 'function') {
        window.gtag('event', 'calculator_complete', {
            'elarea': elarea,
            'distance_m': distance,
            'turbine_height_m': height,
            'turbine_count': count,
            'estimated_compensation_sek': compensation,
            'promille': promille,
            'currency': 'SEK',
            'value': compensation
        });
    }
}
