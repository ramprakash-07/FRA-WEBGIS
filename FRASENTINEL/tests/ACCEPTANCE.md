# FRA Sentinel - Acceptance Checks (Manual Testing Guide)

## Overview
This document provides step-by-step manual testing procedures for the FRA Sentinel system to ensure it meets the Policy Statement requirements. Each test should be completed in approximately 10 minutes.

## Prerequisites
- FRA Sentinel application running on localhost:5000
- Demo user accounts available (ccf.admin@fra.gov.in / fra2025ccf)
- Sample patta documents in uploads/ directory
- Browser with developer tools enabled

## Test Environment Setup
```bash
# Start the application
cd 001/FRA-SENTINEL/webgis
python app.py

# Verify application is running
curl http://localhost:5000/api/system_status
```

## 1. Atlas Module Testing

### 1.1 IFR/CR/CFR Toggles
**Objective**: Verify layer toggles work correctly
**Steps**:
1. Navigate to `/dashboard`
2. Login with `ccf.admin@fra.gov.in` / `fra2025ccf`
3. Look for layer control panel on the right side
4. **Expected**: Toggle buttons for IFR, CR, CFR layers
5. **Actual**: [ ] IFR toggle present [ ] CR toggle present [ ] CFR toggle present
6. Click each toggle and verify map markers appear/disappear
7. **Expected**: Markers filter based on claim type
8. **Actual**: [ ] IFR markers filter correctly [ ] CR markers filter correctly [ ] CFR markers filter correctly

### 1.2 District Filter
**Objective**: Verify district-level filtering
**Steps**:
1. In the Atlas interface, locate district filter dropdown
2. **Expected**: Dropdown with available districts (Khargone, Jhabua, Koraput)
3. **Actual**: [ ] District dropdown present [ ] Contains expected districts
4. Select "Khargone" district
5. **Expected**: Map zooms to Khargone, only Khargone villages visible
6. **Actual**: [ ] Map zooms correctly [ ] Only Khargone villages visible
7. Select "All Districts"
8. **Expected**: All villages visible, map resets to full view
9. **Actual**: [ ] All villages visible [ ] Map resets correctly

### 1.3 Village Detail Panel
**Objective**: Verify village information display
**Steps**:
1. Click on any village marker on the map
2. **Expected**: Popup appears with village details
3. **Actual**: [ ] Popup appears [ ] Contains village name [ ] Contains patta holder info [ ] Contains area/status
4. Click "View Details" button in popup
5. **Expected**: Right panel opens with detailed village information
6. **Actual**: [ ] Right panel opens [ ] Shows patta holder details [ ] Shows land use statistics [ ] Shows recommendations

### 1.4 Export Functionality
**Objective**: Verify data export capabilities
**Steps**:
1. In the Atlas interface, locate export buttons
2. **Expected**: "Export CSV" and "Export GeoJSON" buttons
3. **Actual**: [ ] CSV export button present [ ] GeoJSON export button present
4. Click "Export CSV"
5. **Expected**: CSV file downloads with village data
6. **Actual**: [ ] CSV file downloads [ ] Contains expected columns [ ] Contains current filter data
7. Click "Export GeoJSON"
8. **Expected**: GeoJSON file downloads with spatial data
9. **Actual**: [ ] GeoJSON file downloads [ ] Contains geometry data [ ] Contains properties

## 2. Assets Module Testing

### 2.1 Overlay Layers
**Objective**: Verify asset mapping overlays
**Steps**:
1. Navigate to Assets tab in the dashboard
2. **Expected**: Map with overlay controls
3. **Actual**: [ ] Assets tab present [ ] Map displays correctly
4. Look for overlay toggle buttons
5. **Expected**: Toggles for Agriculture, Forest, Water Bodies, Homesteads
6. **Actual**: [ ] Agriculture toggle [ ] Forest toggle [ ] Water toggle [ ] Homestead toggle
7. Enable "Agriculture" overlay
8. **Expected**: Agricultural areas highlighted on map
9. **Actual**: [ ] Agriculture overlay displays [ ] Areas highlighted correctly
10. Enable "Forest" overlay
11. **Expected**: Forest areas highlighted, legend shows confidence levels
12. **Actual**: [ ] Forest overlay displays [ ] Legend shows confidence [ ] Per-class confidence visible

### 2.2 Groundwater and PM Gati Shakti Toggles
**Objective**: Verify additional overlay options
**Steps**:
1. In Assets interface, look for additional toggles
2. **Expected**: "Groundwater" and "PM Gati Shakti" toggles
3. **Actual**: [ ] Groundwater toggle present [ ] PM Gati Shakti toggle present
4. Enable "Groundwater" toggle
5. **Expected**: Groundwater data overlay appears
6. **Actual**: [ ] Groundwater overlay displays [ ] Data appears correctly
7. Enable "PM Gati Shakti" toggle
8. **Expected**: PM Gati Shakti infrastructure overlay appears
9. **Actual**: [ ] PM Gati Shakti overlay displays [ ] Infrastructure data visible

## 3. Digitization Module Testing

### 3.1 Upload Sample Patta
**Objective**: Verify patta document processing
**Steps**:
1. Navigate to `/patta-extractor`
2. **Expected**: Upload interface with file input
3. **Actual**: [ ] Upload interface present [ ] File input functional
4. Upload a sample patta document (use sample_fra_claim.pdf)
5. **Expected**: Processing begins, progress indicator shows
6. **Actual**: [ ] Processing starts [ ] Progress indicator visible
7. Wait for processing to complete
8. **Expected**: Results display with extracted entities
9. **Actual**: [ ] Processing completes [ ] Results display [ ] Holder name extracted [ ] Village name extracted [ ] Survey number extracted [ ] Coordinates extracted [ ] Claim status identified

### 3.2 Timing and Accuracy Badges
**Objective**: Verify processing metrics display
**Steps**:
1. After patta processing, look for timing and accuracy information
2. **Expected**: Processing time badge (e.g., "3.2s")
3. **Actual**: [ ] Processing time badge present [ ] Shows actual processing time
4. **Expected**: Accuracy badge (e.g., "91.5%")
5. **Actual**: [ ] Accuracy badge present [ ] Shows extraction accuracy
6. **Expected**: Confidence indicators for each extracted field
7. **Actual**: [ ] Confidence indicators present [ ] Show per-field confidence

### 3.3 Pin on Map Action
**Objective**: Verify map integration
**Steps**:
1. After patta processing, look for "Pin on Map" button
2. **Expected**: "Pin on Map" button present
3. **Actual**: [ ] Pin on Map button present
4. Click "Pin on Map" button
5. **Expected**: Map opens with village location marked
6. **Actual**: [ ] Map opens [ ] Village location marked [ ] Popup shows patta details

## 4. DSS Module Testing

### 4.1 DAJGUA Mode Toggle
**Objective**: Verify DAJGUA convergence mode
**Steps**:
1. Navigate to `/schemes` or DSS section
2. **Expected**: DSS interface with scheme recommendations
3. **Actual**: [ ] DSS interface present [ ] Scheme recommendations visible
4. Look for "DAJGUA Mode" toggle
5. **Expected**: DAJGUA mode toggle present
6. **Actual**: [ ] DAJGUA mode toggle present
7. Enable DAJGUA mode
8. **Expected**: Recommendations update to show DAJGUA-aligned schemes
9. **Actual**: [ ] Recommendations update [ ] DAJGUA schemes visible [ ] Convergence scoring shown

### 4.2 Scheme Eligibility and Ministry Tags
**Objective**: Verify scheme information display
**Steps**:
1. In DSS interface, examine scheme recommendations
2. **Expected**: 6-8 marquee schemes displayed
3. **Actual**: [ ] 6-8 schemes visible [ ] PM-KISAN present [ ] Jal Jeevan Mission present [ ] MGNREGA present [ ] PMAY-G present [ ] RKVY present [ ] PMMSY present [ ] NLM present [ ] RGSA present
3. For each scheme, verify ministry tags
4. **Expected**: Each scheme shows ministry (Agri, Jal Shakti, MoRD, etc.)
5. **Actual**: [ ] Ministry tags present [ ] Tags accurate [ ] Color coding consistent
6. Verify eligibility information
7. **Expected**: Eligibility reasons and scores displayed
8. **Actual**: [ ] Eligibility reasons shown [ ] Scores displayed [ ] Reasoning clear

### 4.3 Village Convergence Score
**Objective**: Verify convergence scoring
**Steps**:
1. Select a village in the DSS interface
2. **Expected**: Village convergence score displayed
3. **Actual**: [ ] Convergence score present [ ] Score calculated correctly [ ] Score updates with village selection
4. Click on a scheme recommendation
5. **Expected**: Map zooms to village with highlighted evidence
6. **Actual**: [ ] Map zooms correctly [ ] Village highlighted [ ] Evidence layers visible [ ] Scheme-specific overlays shown

## 5. Progress Tracking Testing

### 5.1 Rollup Navigation
**Objective**: Verify hierarchical progress display
**Steps**:
1. Navigate to Progress tab in Atlas interface
2. **Expected**: Progress tracking interface
3. **Actual**: [ ] Progress tab present [ ] Interface loads correctly
4. Verify breadcrumb navigation
5. **Expected**: State → District → Block → Village breadcrumbs
6. **Actual**: [ ] Breadcrumbs present [ ] Navigation functional [ ] Hierarchy correct
7. Click on different levels
8. **Expected**: Data updates to show appropriate level
9. **Actual**: [ ] State level data [ ] District level data [ ] Block level data [ ] Village level data

### 5.2 Stacked Bars
**Objective**: Verify progress visualization
**Steps**:
1. In Progress interface, look for stacked bar charts
2. **Expected**: Stacked bars for IFR/CR/CFR granted vs total
3. **Actual**: [ ] Stacked bars present [ ] IFR data [ ] CR data [ ] CFR data [ ] Granted vs total comparison
4. Verify data accuracy
5. **Expected**: Bars reflect actual data from FRA_ATLAS_DATA
6. **Actual**: [ ] Data accurate [ ] Totals correct [ ] Granted percentages correct

### 5.3 Top Pending Villages
**Objective**: Verify pending claims display
**Steps**:
1. In Progress interface, look for "Top Pending Villages" table
2. **Expected**: Table with pending villages
3. **Actual**: [ ] Table present [ ] Pending villages listed [ ] Sortable columns
4. Verify table functionality
5. **Expected**: Clickable rows, sorting, filtering
6. **Actual**: [ ] Rows clickable [ ] Sorting works [ ] Filtering functional

## 6. Governance Module Testing

### 6.1 Resources Drawer
**Objective**: Verify governance resources access
**Steps**:
1. Look for "Resources" button in header
2. **Expected**: Resources button present
3. **Actual**: [ ] Resources button present
4. Click Resources button
5. **Expected**: Right-side drawer opens
6. **Actual**: [ ] Drawer opens [ ] Slides in smoothly [ ] Contains expected content
6. Verify drawer contents
7. **Expected**: MoTA FRA portal link, FRA guidelines PDF, DAJGUA guidelines PDF
8. **Actual**: [ ] MoTA FRA portal link [ ] FRA guidelines PDF [ ] DAJGUA guidelines PDF
9. Click on MoTA FRA portal link
10. **Expected**: Opens in new tab, correct URL
11. **Actual**: [ ] Opens in new tab [ ] Correct URL [ ] Portal accessible

### 6.2 State Contacts
**Objective**: Verify state contact information
**Steps**:
1. In Resources drawer, look for state contacts section
2. **Expected**: State Tribal Welfare contacts
3. **Actual**: [ ] State contacts present [ ] Contact information complete
4. Verify contact details
5. **Expected**: Names, emails, phone numbers
6. **Actual**: [ ] Names present [ ] Emails present [ ] Phone numbers present
7. Look for central desk information
8. **Expected**: Central desk contact lines
9. **Actual**: [ ] Central desk contacts [ ] Multiple contact methods

### 6.3 Compliance Notes
**Objective**: Verify policy alignment indicators
**Steps**:
1. In Atlas interface, look for compliance note
2. **Expected**: "Aligned with MoTA FRA guidelines and DAJGUA convergence model"
3. **Actual**: [ ] Compliance note present [ ] Text accurate [ ] Visible on page
4. In DSS interface, look for compliance note
5. **Expected**: Same compliance note
6. **Actual**: [ ] Compliance note present [ ] Consistent with Atlas

## 7. Metrics Ribbon Testing

### 7.1 Persistent Display
**Objective**: Verify metrics ribbon visibility
**Steps**:
1. Navigate to any page in the application
2. **Expected**: Bottom-center translucent ribbon visible
3. **Actual**: [ ] Ribbon present [ ] Bottom-center position [ ] Translucent styling
4. Verify ribbon contents
5. **Expected**: "3.2s", "91.5%", "47", "127.8 ha"
6. **Actual**: [ ] Processing time (3.2s) [ ] Accuracy (91.5%) [ ] Documents (47) [ ] Area (127.8 ha)
7. Navigate between pages
8. **Expected**: Ribbon remains visible
9. **Actual**: [ ] Ribbon persistent [ ] Updates correctly [ ] No flickering

### 7.2 Accessibility
**Objective**: Verify accessibility compliance
**Steps**:
1. Test with reduced motion preference
2. **Expected**: Ribbon respects prefers-reduced-motion
3. **Actual**: [ ] Reduced motion respected [ ] Animations disabled
4. Test print functionality
5. **Expected**: Ribbon hidden on print
6. **Actual**: [ ] Ribbon hidden on print [ ] Print layout clean

## 8. Demo Hub Testing

### 8.1 Four-Click Flow
**Objective**: Verify demo flow functionality
**Steps**:
1. Navigate to `/demo`
2. **Expected**: Demo hub page with four large buttons
3. **Actual**: [ ] Demo hub present [ ] Four buttons visible [ ] Buttons labeled correctly
4. Click "Atlas" button
5. **Expected**: Opens Atlas with pre-filtered district
6. **Actual**: [ ] Atlas opens [ ] Pre-filtered correctly [ ] Demo data visible
7. Click "Assets" button
8. **Expected**: Opens Assets with same AOI
9. **Actual**: [ ] Assets open [ ] Same AOI [ ] Overlays ready
10. Click "Digitization" button
11. **Expected**: Opens with sample ready
12. **Actual**: [ ] Digitization opens [ ] Sample loaded [ ] Ready for demo
13. Click "DSS" button
14. **Expected**: Opens DSS with DAJGUA mode on for same village
15. **Actual**: [ ] DSS opens [ ] DAJGUA mode on [ ] Same village selected

### 8.2 Presenter Guide
**Objective**: Verify demo guidance
**Steps**:
1. In demo hub, look for left panel
2. **Expected**: Four-click steps and expected results
3. **Actual**: [ ] Left panel present [ ] Steps listed [ ] Expected results described
4. Verify guide completeness
5. **Expected**: Clear instructions for each step
6. **Actual**: [ ] Instructions clear [ ] Results described [ ] Timing guidance

## 9. Integration Testing

### 9.1 End-to-End Flow
**Objective**: Verify complete system integration
**Steps**:
1. Start from login page
2. Login with demo credentials
3. Navigate through Atlas → Assets → Digitization → DSS
4. **Expected**: Smooth transitions, data consistency
5. **Actual**: [ ] Transitions smooth [ ] Data consistent [ ] No errors
6. Test export functionality
7. **Expected**: Exports work from all modules
8. **Actual**: [ ] Atlas export [ ] Assets export [ ] Digitization export [ ] DSS export

### 9.2 Performance Testing
**Objective**: Verify system performance
**Steps**:
1. Measure page load times
2. **Expected**: Pages load within 3 seconds
3. **Actual**: [ ] Atlas loads < 3s [ ] Assets loads < 3s [ ] Digitization loads < 3s [ ] DSS loads < 3s
4. Test with multiple users
5. **Expected**: System handles concurrent users
6. **Actual**: [ ] Multiple users supported [ ] No performance degradation

## 10. Error Handling Testing

### 10.1 Graceful Error Handling
**Objective**: Verify error handling
**Steps**:
1. Test with invalid data
2. **Expected**: Graceful error messages
3. **Actual**: [ ] Error messages clear [ ] No system crashes [ ] Recovery possible
4. Test with network issues
5. **Expected**: Offline handling
6. **Actual**: [ ] Offline mode [ ] Data cached [ ] Sync on reconnect

## Test Results Summary

### Pass/Fail Checklist
- [ ] Atlas IFR/CR/CFR toggles
- [ ] District filter functionality
- [ ] Village detail panel
- [ ] Export CSV/GeoJSON
- [ ] Asset overlay layers
- [ ] Groundwater/PM Gati Shakti toggles
- [ ] Patta upload and processing
- [ ] Timing/accuracy badges
- [ ] Pin on map action
- [ ] DAJGUA mode toggle
- [ ] Scheme eligibility display
- [ ] Village convergence score
- [ ] Progress rollup navigation
- [ ] Stacked bar charts
- [ ] Top pending villages table
- [ ] Resources drawer
- [ ] State contacts
- [ ] Compliance notes
- [ ] Metrics ribbon
- [ ] Demo hub four-click flow
- [ ] Presenter guide
- [ ] End-to-end integration
- [ ] Performance requirements
- [ ] Error handling

### Overall Assessment
- **Total Tests**: 25
- **Passed**: ___/25
- **Failed**: ___/25
- **Blocking Issues**: ___
- **Recommendations**: ___

## Notes
- Each test should take approximately 2-3 minutes
- Total testing time: ~10 minutes
- Document any deviations from expected behavior
- Report any performance issues or errors encountered
- Verify all demo requirements are met for presentation readiness

