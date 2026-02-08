---
noteId: "44437880046011f1b0d475b0778c2e69"
tags: []

---

# BTT CLI / Socket Server Reference

Socket: `/tmp/com.hegenberg.BetterTouchTool.sock` (must enable in BTT Scripting Settings).
Command format: `/<command>/?param1=value1&param2=value2`
CLI tool: `bttcli <command> [params]`

## Clipboard & Selection

| Command | Key Params | Notes |
|---|---|---|
| `get_selection` | `type` (pasteboard type, default `NSPasteboardTypeString`), `asBase64` | Gets selected text/content |
| `get_clipboard_content` | `type`, `asBase64`, `excludeConcealed` | Gets clipboard |
| `set_clipboard_content` | `content`/`text`, `format` | Sets single clipboard type |
| `set_clipboard_contents` | `contents` (array), `formats` (array) | Sets multiple clipboard types |

Pasteboard types: `NSPasteboardTypeString`, `NSPasteboardTypeTIFF`, `NSPasteboardTypePNG`, `NSPasteboardTypeRTF`, `NSPasteboardTypeHTML`, `NSPasteboardTypeURL`, `NSPasteboardTypeFileURL`, plus `RTFD`, `TabularText`, `Font`, `Ruler`, `Color`, `Sound`, `MultipleTextSelection`, `TextFinderOptions`.

## Variables

| Command | Key Params |
|---|---|
| `set_string_variable` | `variableName`, `to` |
| `set_persistent_string_variable` | `variableName`, `to` (survives restart) |
| `set_number_variable` | `variableName`, `to` |
| `set_persistent_number_variable` | `variableName`, `to` (survives restart) |
| `get_string_variable` | `variableName`, `default` |
| `get_number_variable` | `variableName`, `default` |

### Special writable number variables
`BTTDisabled`, `BTTSiriRemoteMouseModeActive`, `SystemDoNotDisturbState`, `BluetoothConnectionState-<addr>`, `CurrentDisplayBrightness`, `BuiltInDisplayBrightness`, `OutputVolume`

### Special readable number variables
`BTTIdleTime`, `BTTDisabled`, `SystemDoNotDisturbState`, `BluetoothConnectionState-<addr>`, `CurrentDisplayBrightness`, `BuiltInDisplayBrightness`, `ActiveSpace`, `OutputVolume`

### Special readable string variables
`BTTActiveWindowTitle`, `BTTActiveWindowNumber`, `BTTCurrentlyPlaying`, `BTTNowPlaying*`, `clipboard_content`, `hovered_link`, `selected_text`

## Triggers & Actions

| Command | Key Params |
|---|---|
| `trigger_named` | `trigger_name`, `cancel_delayed` — sync, waits for result |
| `trigger_named_async_without_response` | `trigger_name`, `delay`, `cancel_delayed` — async |
| `cancel_delayed_named_trigger_execution` | `trigger_name` |
| `trigger_action` | `json` (action JSON definition) |
| `execute_assigned_actions_for_trigger` | `uuid` |
| `get_trigger` | `uuid` |
| `get_triggers` | `trigger_uuid`, `trigger_type`, `trigger_id`, `trigger_parent_uuid`, `trigger_app_bundle_identifier`, `preset`, `return_only_if_modifiers_match` |
| `add_new_trigger` | `json` (trigger JSON) |
| `update_trigger` | `uuid`, `json`, `trigger_parent_uuid` |
| `delete_trigger` | `uuid` |
| `delete_triggers` | Same filters as `get_triggers` |

## UI & Widgets

| Command | Key Params |
|---|---|
| `display_notification` | `""` (body), `title`, `subTitle`, `soundName`, `imagePath` |
| `paste_text` | `text`, `format`, `insert_by_pasting`, `move_cursor_left_by_x_after_pasting` |
| `reveal_element_in_ui` | `uuid` |
| `refresh_widget` | `uuid` |
| `update_touch_bar_widget` | `""` (uuid), plus widget-specific params |
| `update_stream_deck_widget` | `""` (uuid), `text`, `json` |
| `update_menubar_item` | `""` (uuid), plus item-specific params |

## Floating Menus

| Command | Key Params |
|---|---|
| `get_menu_item_value` / `get_floating_menu_item_value` | `uuid` or (`menu_name` + `item_name`) |
| `set_menu_item_value` | `uuid`/`menu_name`+`item_name`, `value` |
| `update_menu_item` / `update_floating_menu_item` | `uuid`/`menu_name`+`item_name`, `json`, `persist` |
| `get_menu_item_details` | `itemPath` |
| `webview_menu_item_load_html_url_js` | `uuid`/`menu_name`+`item_name`, `html_or_url`, `javascript_to_execute`, `useragent` |

## Presets

| Command | Key Params |
|---|---|
| `get_preset_details` | `name` |
| `import_preset` | `path`, `replaceExisting` (default true) |
| `export_preset` | `name`, `compress`, `includeSettings`, `outputPath`, `comment`, `link`, `minimumVersion` |

## Other

| Command | Key Params |
|---|---|
| `is_app_running` | `app` (name or bundle ID) |
| `get_dock_badge_for` | `app`, `update_interval` (min 0.5s) |
| `get_active_touch_bar_group` | (none) |
| `is_true_tone_enabled` | (none) |
| `get_location` | `format` (default `{LAT},{LON}`) |
| `get_weather` | `location` ("auto" or coords), `unit` ("fahrenheit" or celsius) |
| `run_shortcut` | `shortcut_name`, `input` (Apple Shortcuts) |
| `chat_gpt` | `identifier`, `user`, `system`, `input`, `maxHistory`, `model` (default gpt-4o-mini), `apiKey`, `customURL` |

## Security
- Socket server must be explicitly enabled in BTT preferences
- Optional shared secret for auth
- `import_preset` shows security warning unless user opted to always allow
- External scripting must be enabled for non-webserver requests
