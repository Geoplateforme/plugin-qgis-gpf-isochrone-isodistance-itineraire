# Manage translations

## Requirements

Qt Linguist tools are used to manage translations. Typically on Ubuntu:

```bash
sudo apt install qttools5-dev-tools
```

## Workflow

1. Generate the `plugin_translation.pro` file:

    ```bash
    python scripts/generate_translation_profile.py
    ```

1. Update `.ts` files:

    ```bash
    pylupdate5 -noobsolete -verbose gpf_isochrone_isodistance_itineraire/resources/i18n/plugin_translation.pro
    ```

1. Translate your text using QLinguist or directly into `.ts` files. Launching it through command-line is possible:

    ```bash
    linguist gpf_isochrone_isodistance_itineraire/resources/i18n/*.ts
    ```

1. Compile it:

    ```bash
    lrelease gpf_isochrone_isodistance_itineraire/resources/i18n/*.ts
    ```
