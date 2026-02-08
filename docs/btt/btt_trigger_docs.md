---
noteId: "6f0b9e80046011f1b0d475b0778c2e69"
tags: []

---

# BTT Trigger JSON Reference

## Required Structure
```json
{"BTTTriggerType": <id>, "BTTTriggerClass": "<class>", "BTTActionsToExecute": [{"BTTPredefinedActionType": <id>}]}
```

## Common Optional Fields
`BTTUUID` (auto-generated), `BTTTriggerTypeDescription` (display name), `BTTEnabled` (0/1), `BTTOrder`, `BTTActionsToExecute` (array).

## Modifier Key Flags
Cmd=1048576, Opt=524288, Ctrl=262144, Shift=131072, Fn=8388608. Combine by addition (Cmd+Shift=1179648).

## Colors
RGBA comma-separated: `"255, 0, 0, 128"` = red 50% transparent.

## Icons
Base64 in `BTTIconData`, SF Symbol in `BTTTouchBarItemSFSymbolDefaultIcon`, or file path for Stream Deck.

---

## 1. Trackpad Gestures
Classes: `BTTTriggerTypeTouchpadAll`, `BTTTriggerTypeTouchpadBuiltIn`, `BTTTriggerTypeTouchpadMagicTrackpad`, `BTTTriggerTypeTouchpadMagicTrackpad2`, `BTTTriggerTypeTouchBarTrackpad`

### 0-finger (release)
214=Release Last Finger (any), 209-213=Release After 1-5 Finger Touch

### 1-finger
215=Touch Start, 157/158=Corner Click BL/BR, 182/183=Corner Click TL/TR, 184-187=Corner Force Click TL/TR/BL/BR, 207=Tap, 208=Double Tap, 203=Force Click, 100-109=Tap regions (Left/Right/Bottom/Top/LeftMid/RightMid/UL/UR/BL/BR)

### 2-finger
216=Touch Start, 173=Tap, 179=Double Tap, 174=Click, 175=Force Click, 176/177/178=Click (Left/Right/Both harder), 180/181=Force Click (Left/Right harder), 159-162=Swipe L/R/U/D, 165-168=Swipe from Edge L/R/T/B, 121/122=Pinch In/Out, 138=TipTap Middle, 132/133=TipTap L/R, 142/143/145/146=TipSwipe LF Down/Up/Right/Left

### 3-finger
217=Touch Start, 110=Tap, 163=Double Tap, 111=Click, 170=Force Click, 181=Click&Hold, 188-190=Click (L/M/R harder), 191-193=Force Click (L/M/R harder), 112-115=Swipe U/D/L/R, 197/198=Pinch In/Out, 139/140=Tap Bottom/Top, 152=Dragging, 153-156=Clickswipe L/R/U/D, 136/137=TipTap L/R, 147-150=Triangle Swipe TL/TR/BL/BR, 204=Drawing

### 4-finger
218=Touch Start, 116=Tap, 169=Double Tap, 117=Click, 171=Force Click, 182=Click&Hold, 123-126=Swipe U/D/L/R, 194/195=Pinch In/Out, 205=Drawing

### 5+ finger
219=Touch Start, 119=Tap, 141=Click, 172=Force Click, 130/131=Swipe D/U, 128/129=Swipe L/R, 200/201=Pinch In/Out, 206=Drawing, 151=Touch/Move, 199=11-Finger/Whole Hand

### Custom
164=Custom Tap Sequence (4F), 220=First Touch X Then Release Y

---

## 2. Magic Mouse (`BTTTriggerTypeMagicMouse`)

### 0-finger: 51=Release Any, 52-56=Release After 1-5F
### 1-finger: 50=Touch Start, 1=Tap, 2/3=Tap L/R, 23=Middle Click, 24=Tap Middle, 32=Tap Above Apple, 18/19=Scroll U/D (modifier needed), 33-36=Swipe D/U/L/R
### 2-finger: 57=Touch Start, 4=Tap, 62=Double Tap, 20=Click, 7/8=Swipe U/D, 5/6=Swipe L/R, 14/15=Pinch In/Out, 16/17=TipTap L/R
### 3-finger: 58=Touch Start, 9=Tap, 63=Double Tap, 21=Click, 13/12=Swipe U/D, 10/11=Swipe L/R, 30=TipTap L, 37=TipTap M, 31=TipTap R, 60/61=TipSwipe LF Up/Down
### 4-finger: 59=Touch Start, 25=Click, 27/26=Swipe U/D, 28/29=Swipe L/R
### Moving/Resize: 40=1F Top, 38=2F Top, 39=3F Top

---

## 3. Other Triggers / Automations (`BTTTriggerTypeOtherTriggers`)

### Named Trigger: 643
```json
{"BTTTriggerType":643,"BTTTriggerClass":"BTTTriggerTypeOtherTriggers","BTTTriggerName":"my_trigger","BTTNamedTriggerAIDescription":"desc","BTTNamedTriggerAIAllow":1,"BTTActionsToExecute":[]}
```

### App Events: 687=App Focus Changed, 131=Launch, 132=Terminate, 133=Activate, 134=Deactivate
### Window: 693=Focused Window Changed, 713=Window/Title Changed, 600=Dblclick Titlebar, 613=Dblclick Menubar
### Window Buttons (Left/Right/Other click): Red=622/601/626, Orange=621/602/625, Green=615/603/628, Fullscreen=623/614/627
### System: 605=Before Sleep, 606=After Wake, 707/708=Lid Open/Close, 709/710=Screensaver Start/Stop, 711/712=Lock/Unlock Screen
### Network: 681/682=WiFi Connect/Disconnect, 683/684=Screen Connect/Disconnect
### Bluetooth/USB: 672/673=USB Connect/Disconnect, 679/680=BT Connect/Disconnect, 616-619=BT LE Close/Away/OutOfRange/InRange
### Battery: 703/704=Below/Above X%, 705/706=AC Connected/On Battery
### Input/Variables: 694=Variable Changed, 692=Input Source Changed, 698=Text Selection Changed, 699=Script Output Changed, 700=Adv Condition Changed, 701/702=Conditional Group Activated/Deactivated, 714=Dynamic JS Variable, 715=Clipboard Transformer, 719=Clipboard Changed
### File/URL: 697=File Changed, 695=Did Open URL
### Notch: 649=Click, 650=Dblclick, 651=Rightclick, 652/653/654=Mouse To/Away/Away+Menubar
### Screen Corners: 609-612=TL/TR/BL/BR, 655-658=Away TL/TR/BL/BR
### Screen Edges: 659-662=Mouse To L/R/B/T, 663-666=Away L/R/B/T
### Misc: 685/686=Mobile Connect/Disconnect, 688=Notification Showed, 689=Key Remap, 691=Dock Icon, 696=Finder Context Menu, 607=Distributed Notification, 641=Serial Number Match, 690=Workspace Notification, 716/717/718=Ambient Light Below/Above/Change
### Time: 678=Date/Time Repeating (cron in `BTTAdditionalConfiguration`: `{"BTTTimedRepeatEveryXSeconds":"0 0 * * * *"}`)
### Menu Bar: 667=Icon, 668=Icon (AppleScript), 669=Icon (Shell), 670=Always Hidden Status Item

---

## 4. Keyboard Shortcuts (`BTTTriggerTypeKeyboardShortcut`)
Type: 0. Props: `BTTShortcutKeyCode`, `BTTShortcutModifierKeys`, `BTTLayoutIndependentChar`, `BTTAutoAdaptToKeyboardLayout`, `BTTShortcutScope`, `BTTKeyboardShortcutMinTime`/`MaxTime`

## 5. Key Sequences (`BTTTriggerTypeKeySequence`): Type 624
## 6. Drawings (`BTTTriggerTypeDrawings`): Type 620, config in `BTTTriggerConfig.BTTDrawingName`
## 7. Mouse (`BTTTriggerTypeMouse`): Regular buttons configured differently

## 8. Siri Remote (`BTTTriggerTypeSiriRemote`)
Buttons: 320-325=VolUp/VolDown/Siri/PlayPause/TV/Menu, 332-337=same Hold
Touchpad: 326=Click, 338=Click Hold, 327-330=Swipe L/R/U/D, 331=Tap, 339-342=Click L/R/T/B, 343-346=Tap L/R/T/B, 347-350=Click Hold L/R/T/B
Remote 2: 351-354=Button L/R/U/D, 355=Power, 356-360=Hold versions, 361/362=Mute/Mute Hold

## 9. Touch Bar (`BTTTriggerTypeTouchBar`): Type 630
Config in `BTTTriggerConfig`: `BTTTouchBarButtonColor` (RGBA), `BTTTouchBarFontColor`, `BTTTouchBarFontSize`, `BTTTouchBarButtonWidth`/`Height`, `BTTTouchBarItemIconWidth`/`Height`, `BTTTouchBarItemPadding`, `BTTTouchBarOnlyShowIcon`

## 10. Stream Deck (`BTTTriggerTypeStreamDeck`): Similar to Touch Bar config
## 11. Notch Bar (`BTTTriggerTypeNotchBar`): Similar to Touch Bar config

## 12. Floating Menu (`BTTTriggerTypeFloatingMenu`)
800=Menu, 827=MenuItem, 840=Slider, 852=TextField, 853=TextArea, 871=Submenu, 872=BackButton, 873=Webview, 870=StatusWidget, 874=iOSTrackpad, 875=RowBreaker, 876=ColumnBreaker

## 13. MIDI (`BTTTriggerTypeMIDI`): Type 650, config `BTTMidiTriggerDeviceName` ("*" for any)
## 14. Generic Device (`BTTTriggerTypeGenericDevice`): 880=Analyzer, 881=Trigger
## 15. BTT Remote Legacy (`BTTTriggerTypeBTTRemote`): Types 300-362
