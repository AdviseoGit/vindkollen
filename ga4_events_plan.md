# GA4 Key Events Implementation Plan

## Current State
- GA4 installed: `G-2ZDTQZXPRC`
- Existing events (via vk-silo.js):
  - `generate_lead` - fired when lead form submitted
  - `select_segment` - when user picks markägare/närboende/kommun
  - `view_lead_form` - when lead form is shown

## Key Events to Add

### 1. Calculator Usage (High Priority)
**Event:** `calculator_complete`
- **Trigger:** When user clicks "Beräkna min ersättning" and results are shown
- **Parameters:**
  - `elarea`: SE1-SE4
  - `distance_m`: distance to turbine
  - `turbine_height_m`: turbine height
  - `turbine_count`: number of turbines
  - `estimated_compensation_sek`: calculated result
  - `promille`: promille of park revenue
  - `currency`: 'SEK'
  - `value`: estimated_compensation_sek (for revenue tracking)
- **Location:** static/kalkylator.html - calculate() function
- **Business Value:** Core conversion funnel step - shows serious intent

### 2. Arrendekalkylator Usage
**Event:** `lease_calculator_complete`
- **Trigger:** When lease calculator results shown
- **Parameters:**
  - `land_hectares`: land size
  - `lease_type`: type selected
  - `estimated_revenue_sek`: calculated amount
  - `currency`: 'SEK'
  - `value`: estimated_revenue_sek
- **Location:** static/arrendeavtal-vindkraft.html (need to verify calculator location)
- **Business Value:** Markägare segment qualification

### 3. Content Engagement
**Event:** `scroll_depth`
- **Trigger:** When user scrolls 25%, 50%, 75%, 90%
- **Parameters:**
  - `percent_scrolled`: 25|50|75|90
  - `page_path`: window.location.pathname
- **Location:** Add to all main HTML templates
- **Business Value:** Content quality indicator, SEO engagement signal

### 4. CTA Clicks
**Event:** `cta_click`
- **Trigger:** Main CTA button clicks (not form submits)
- **Parameters:**
  - `cta_text`: button text
  - `cta_location`: 'hero'|'mid-content'|'footer'
  - `target_page`: destination URL
- **Location:** All main CTAs across site
- **Business Value:** Conversion funnel tracking

### 5. Navigation Events
**Event:** `navigation_click`
- **Trigger:** Top nav or footer navigation clicks
- **Parameters:**
  - `link_text`: text of link
  - `link_url`: destination
  - `navigation_type`: 'top'|'footer'|'mobile'
- **Location:** Navigation components
- **Business Value:** User journey mapping

### 6. Tool Interaction
**Event:** `tool_interaction`
- **Trigger:** Interactive tool usage (compare tool, dashboards)
- **Parameters:**
  - `tool_name`: 'compare'|'kommun-dashboard'
  - `interaction_type`: 'view'|'filter'|'compare'
- **Location:** Interactive tool pages
- **Business Value:** Engagement depth

### 7. Report Download/Email
**Event:** `report_request`
- **Trigger:** When user requests detailed report (already tracked via generate_lead, but add explicit event)
- **Parameters:**
  - `report_type`: 'compensation'|'lease'
  - `segment`: user segment
- **Location:** Report request forms
- **Business Value:** Lead quality indicator

## Implementation Priority

### Phase 1 (This Sprint) - Core Conversions
1. ✅ `calculator_complete` - kalkylator.html
2. ✅ `lease_calculator_complete` - arrendeavtal page
3. ✅ Enhanced `generate_lead` with revenue value

### Phase 2 (Next Week) - Engagement
4. `scroll_depth` - global script
5. `cta_click` - main CTAs
6. `navigation_click` - nav components

### Phase 3 (Ongoing) - Advanced
7. `tool_interaction` - interactive tools
8. Enhanced parameters on existing events

## Technical Implementation

### Pattern for all events:
```javascript
if (typeof window.gtag === 'function') {
    window.gtag('event', 'event_name', {
        param1: value1,
        param2: value2,
        // Always include these for e-commerce tracking:
        currency: 'SEK',
        value: numeric_value  // for revenue attribution
    });
}
```

### GA4 Configuration
After deploying events, mark these as "Key Events" in GA4 admin:
1. `generate_lead` ← Already tracked
2. `calculator_complete` ← New
3. `lease_calculator_complete` ← New

These will be used for:
- Conversion tracking
- Attribution reporting
- Channel ROI analysis
- Bidding optimization (if we run ads)
