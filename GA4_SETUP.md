# GA4 Key Events Setup & Configuration

## Implementation Summary (2026-08-03)

Vindkollen now tracks comprehensive conversion and engagement events via GA4.

### Events Implemented

#### 1. Calculator Events
**`calculator_complete`**
- Fired when: User completes compensation calculator
- Parameters:
  - `elarea`: SE1-SE4 (electricity area)
  - `distance_m`: Distance to turbine
  - `turbine_height_m`: Turbine height
  - `turbine_count`: Number of turbines
  - `estimated_compensation_sek`: Calculated annual compensation
  - `promille`: Share of park revenue (‰)
  - `within_limit`: Boolean - if within 9x height limit
  - `currency`: SEK
  - `value`: Compensation amount (for revenue attribution)
- Location: `/kalkylator`
- Business value: Core conversion signal - shows serious intent

**`lease_calculator_complete`**
- Fired when: User completes lease calculator
- Parameters:
  - `turbine_count`: Number of turbines
  - `capacity_mw`: Turbine capacity in MW
  - `full_load_hours`: Operating hours
  - `price_sek_kwh`: Electricity price
  - `royalty_percent`: Royalty percentage
  - `annual_royalty_sek`: Calculated annual royalty
  - `minimum_lease_sek`: Minimum lease amount
  - `upfront_sek`: Upfront payment
  - `currency`: SEK
  - `value`: Annual royalty (for revenue attribution)
- Location: `/arrendekalkylator`
- Business value: High-value markägare segment qualification

#### 2. Lead Generation (Enhanced)
**`generate_lead`** (already existed, now enhanced)
- Parameters include `value` for revenue tracking
- Markägare leads: SEK 800 value
- Närboende leads: SEK 60 value
- Kommun leads: SEK 300 value

#### 3. Engagement Events
**`scroll_depth`**
- Fired when: User scrolls to 25%, 50%, 75%, 90%
- Parameters:
  - `percent_scrolled`: 25|50|75|90
  - `page_path`: Current page
- Business value: Content quality indicator, engagement depth

**`cta_click`**
- Fired when: Main CTA buttons clicked
- Parameters:
  - `cta_text`: Button text
  - `cta_location`: hero|navigation|footer|content
  - `target_page`: Destination URL
- Business value: Conversion funnel tracking

**`navigation_click`**
- Fired when: Navigation links clicked
- Parameters:
  - `link_text`: Link text
  - `link_url`: Destination
  - `navigation_type`: top|footer|mobile
- Business value: User journey mapping

**`outbound_click`**
- Fired when: External links clicked
- Parameters:
  - `link_url`: External URL
  - `link_text`: Link text
- Business value: Partnership tracking

#### 4. Tool Interactions
**`tool_interaction`**
- Fired when: Interactive tools used
- Parameters:
  - `tool_name`: Name of tool
  - `interaction_type`: view|filter|compare
- Business value: Engagement depth

**`view_lead_form`** (existing)
- Fired when: Lead form shown
- Parameters:
  - `segment`: markagare|narboende|kommun

**`select_segment`** (existing)
- Fired when: User picks their segment
- Parameters:
  - `segment`: Selected segment

## GA4 Admin Configuration

### Step 1: Mark as Key Events
In GA4 Admin > Events, mark these as "Key Events":

1. ✅ **generate_lead** (highest priority)
2. ✅ **calculator_complete** (high priority)
3. ✅ **lease_calculator_complete** (high priority)
4. **scroll_depth** (engagement)
5. **cta_click** (engagement)

### Step 2: Create Custom Dimensions
Configure these custom dimensions for better reporting:

**Event-scoped dimensions:**
- `segment` - User segment (markagare/närboende/kommun)
- `elarea` - Electricity area (SE1-SE4)
- `county` - Swedish county
- `percent_scrolled` - Scroll depth percentage
- `cta_location` - CTA position on page
- `navigation_type` - Navigation type
- `tool_name` - Interactive tool name

**User-scoped dimensions:**
- `remembered_segment` - Stored segment preference (via localStorage)

### Step 3: Create Audiences
Segment users for remarketing and analysis:

**High-Intent Markägare:**
- Trigger: `calculator_complete` OR `lease_calculator_complete`
- Parameter: `segment = markagare`
- Membership: 90 days

**Närboende Qualified:**
- Trigger: `calculator_complete`
- Parameter: `segment = narboende` AND `within_limit = true`
- Membership: 60 days

**Deep Engagers:**
- Trigger: `scroll_depth` with `percent_scrolled = 90`
- Sessions > 2
- Membership: 30 days

**Tool Users:**
- Trigger: `calculator_complete` OR `lease_calculator_complete`
- No lead form submission yet
- Membership: 30 days

### Step 4: Create Explorations
Build these custom reports:

**Conversion Funnel:**
1. Page view
2. `scroll_depth` (50%)
3. `calculator_complete` OR `lease_calculator_complete`
4. `view_lead_form`
5. `generate_lead`

**Segment Performance:**
- Compare revenue by segment (using `value` parameter)
- Group by `elarea`, `county` for regional analysis

**Content Engagement:**
- `scroll_depth` by page
- Average scroll depth
- Correlation with lead generation

## Revenue Tracking
All conversion events include a `value` parameter:
- Calculator completions: Estimated compensation/royalty amount
- Lead generation: Expected lead value (800/300/60 SEK)
- Currency: Always SEK

This enables:
- Channel ROI analysis
- Attribution modeling
- Campaign optimization
- Regional value comparison

## Files Modified
- `static/kalkylator.html` - Added calculator_complete event
- `static/arrendekalkylator.html` - Added lease_calculator_complete event
- `static/js/vk-analytics.js` - NEW: Global engagement tracking
- `static/js/vk-silo.js` - Enhanced with revenue values
- 5 main pages - Added vk-analytics.js script

## Testing
Verify events in GA4 Realtime view:
1. Visit `/kalkylator`
2. Fill calculator and click "Beräkna"
3. Scroll down to 50%, 75%, 90%
4. Click navigation links
5. Fill and submit lead form

All events should appear in Realtime within seconds.

## Next Steps
1. **Mark Key Events in GA4 Admin** (manual step - requires GA4 access)
2. Monitor event volume for 1 week
3. Create custom explorations
4. Set up automated Looker Studio reports
5. Use audiences for remarketing (if running ads)

## Support
If events aren't firing:
- Check browser console for errors
- Verify GA4 tag ID: `G-2ZDTQZXPRC`
- Test with GA4 DebugView (Chrome extension)
- All tracking code is defensive (try/catch) - won't break if GA4 fails
