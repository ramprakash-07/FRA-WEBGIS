# FRA Sentinel - Internationalization (i18n) Guide

## Overview
The FRA Sentinel application now supports full internationalization with Flask-Babel, supporting English (en), Hindi (hi), Tamil (ta), and Telugu (te).

## Features
- ✅ Language detection via URL parameter (`?lang=hi`)
- ✅ Language persistence via cookies
- ✅ Browser language fallback
- ✅ Language dropdown in all templates
- ✅ Translated UI elements

## Supported Languages
- 🇺🇸 **English (en)** - Default
- 🇮🇳 **Hindi (hi)** - हिंदी
- 🇮🇳 **Tamil (ta)** - தமிழ்  
- 🇮🇳 **Telugu (te)** - తెలుగు

## Translation Management Commands

### Extract New Strings
```bash
pybabel extract -F babel.cfg -o messages.pot .
```

### Initialize New Language
```bash
pybabel init -i messages.pot -d translations -l <language_code>
```

### Update Existing Translations
```bash
pybabel update -i messages.pot -d translations
```

### Compile Translations
```bash
pybabel compile -d translations
```

## Adding New Translations

1. **Add translation tags to templates:**
   ```html
   {% trans %}Your text here{% endtrans %}
   ```

2. **Add translations to Python code:**
   ```python
   from flask_babel import gettext as _
   flash(_('Your message here'))
   ```

3. **Extract strings:**
   ```bash
   pybabel extract -F babel.cfg -o messages.pot .
   ```

4. **Update translation files:**
   ```bash
   pybabel update -i messages.pot -d translations
   ```

5. **Edit translation files:**
   - Edit `translations/<lang>/LC_MESSAGES/messages.po`
   - Add translations for `msgstr ""` entries

6. **Compile translations:**
   ```bash
   pybabel compile -d translations
   ```

## Language Switching

### URL Parameter
```
http://localhost:5000/schemes?lang=hi
```

### Cookie-based (persistent)
```
http://localhost:5000/lang/hi
```

### Language Dropdown
- Available in top-right corner of all pages
- Sets cookie and redirects to maintain language preference

## File Structure
```
webgis/
├── babel.cfg                 # Babel configuration
├── messages.pot             # Translation template
├── translations/            # Translation files
│   ├── hi/LC_MESSAGES/
│   │   ├── messages.po      # Hindi translations (source)
│   │   └── messages.mo      # Hindi translations (compiled)
│   ├── ta/LC_MESSAGES/
│   │   ├── messages.po      # Tamil translations (source)
│   │   └── messages.mo      # Tamil translations (compiled)
│   └── te/LC_MESSAGES/
│       ├── messages.po      # Telugu translations (source)
│       └── messages.mo      # Telugu translations (compiled)
└── templates/
    ├── base.html            # Base template with language dropdown
    ├── dashboard.html       # Dashboard with translations
    ├── schemes.html         # Schemes page with translations
    └── fra_data_collection.html # Data collection with translations
```

## Testing Translations

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Test language switching:**
   - Visit `http://localhost:5000`
   - Use language dropdown or URL parameters
   - Verify translations appear correctly

3. **Test cookie persistence:**
   - Switch language using dropdown
   - Refresh page - language should persist
   - Close browser and reopen - language should persist

## Adding New Languages

1. **Initialize new language:**
   ```bash
   pybabel init -i messages.pot -d translations -l <new_lang>
   ```

2. **Add translations to the new .po file**

3. **Compile translations:**
   ```bash
   pybabel compile -d translations
   ```

4. **Update language dropdown in base.html**

## Troubleshooting

### Translations not appearing
- Ensure translations are compiled: `pybabel compile -d translations`
- Check browser cache
- Verify language code is supported in `select_locale()` function

### Missing strings
- Extract strings: `pybabel extract -F babel.cfg -o messages.pot .`
- Update translations: `pybabel update -i messages.pot -d translations`
- Add missing translations to .po files
- Compile: `pybabel compile -d translations`

### Language not persisting
- Check cookie settings in browser
- Verify `change_language()` function is working
- Test with different browsers

