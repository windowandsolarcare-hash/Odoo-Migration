---
name: project_foldable_mobile_modal_fixes
description: "DJ uses a Samsung foldable — the recipe that makes owner/field pages + bottom-sheet modals fit the cover screen, scroll, and not get cut off."
metadata: 
  node_type: memory
  type: project
  originSessionId: f3bc8d84-66ee-4ee9-b6c2-8cd69a165d04
---

**DJ's phone is a Samsung foldable (Galaxy Z Fold-style).** Pages laid out for the wide *unfolded* screen don't reflow to the narrow *cover* screen, so content overflows / pans sideways and bottom-sheet popups render too wide or below the fold. Fixed the My Day page (`static/owner/myday.html`) 2026-06-24/25 through several rounds — this is the working recipe for ANY owner/field screen with the same symptoms.

**KEYBOARD pushes modal header off-screen — ROOT CAUSE + FIX (2026-06-25, My Day editor):** a bottom-sheet `.fu-sheet{max-height:92dvh}` breaks when the keyboard opens because **dvh ignores the keyboard** — the sheet stays ~92% of the FULL screen, taller than the visible area, and (being `align-items:flex-end` bottom-anchored) its TOP/header overflows above the viewport while the bottom buttons sit on the keyboard. DJ: "keyboard kicks the whole screen up, you see Done right above the keyboard, title gone." FIX: in `fitModal()` (which already pins each modal to `window.visualViewport`), ALSO pin the inner sheet: `var sh=m.querySelector('.fu-sheet'); if(sh) sh.style.maxHeight=vv.height+'px';` → sheet ≤ visible viewport → flex header pinned top, body scrolls, actions at bottom. Apply anywhere a `dvh`-capped sheet shows a keyboard. (The earlier "show task name in sticky #tkTitle" fix helped see WHICH task but did NOT fix the off-screen scroll — this does.)

**THE RECIPE (apply all that fit the symptom):**

1. **Stop sideways pan / horizontal overflow:** `html,body{overflow-x:clip;max-width:100%;overscroll-behavior:none}`.
   - ⚠️ Use `overflow-x:clip`, **NOT `overflow-x:hidden`** — `hidden` on the root makes html a scroll container and **kills vertical scrolling** (DJ: "it will not scroll, just one screen"). `clip` blocks the horizontal pan while leaving vertical scroll alone.
   - `overscroll-behavior:none` is also the no-pull-to-refresh rule ([[feedback_disable_pull_to_refresh]]) — was missing from myday.html; re-add wherever absent.

2. **Bottom-sheet modal must use the VISIBLE viewport, not the layout viewport:**
   - Container: `position:fixed;inset:0;height:100dvh` (dvh = dynamic viewport, follows the visible area; plain `vh`/`inset:0` uses the layout viewport which on a foldable is wider/taller than the screen → sheet renders below the fold or off to the side).
   - Sheet: `max-height:92vh;max-height:92dvh` (vh fallback then dvh).
   - **`fitModal()` JS — the real fix for the foldable width problem:** on open AND on `visualViewport` resize/scroll, pin each modal to the actually-visible rect:
     ```
     function fitModal(){ var vv=window.visualViewport; if(!vv) return;
       ['add-modal','task-modal',...].forEach(function(id){ var m=document.getElementById(id); if(!m) return;
         m.style.inset='auto'; m.style.left=vv.offsetLeft+'px'; m.style.top=vv.offsetTop+'px';
         m.style.width=vv.width+'px'; m.style.height=vv.height+'px'; }); }
     if(window.visualViewport){ window.visualViewport.addEventListener('resize',fitModal);
       window.visualViewport.addEventListener('scroll',fitModal); }
     ```
     Call `fitModal()` right after `.classList.add('open')`. No-op on normal phones (vv = full screen); on the fold it snaps the popup to fit so **Save/right-edge buttons aren't cut off**.

3. **Open the editor at the top + don't let fields explode the height:**
   - After opening, snap the scroll container to top across two `requestAnimationFrame`s + a 150ms backup: `var b=$('task-modal').querySelector('.fu-body'); b.scrollTop=0;` so the first field is visible (not buried below the fold).
   - Auto-grow textareas must be **capped** then scroll internally, or a long note makes the editor taller than the screen: `autoGrow(el){ el.style.height='auto'; var max=el.classList.contains('fu-grow')?130:240; var h=el.scrollHeight; if(h>max){el.style.height=max+'px';el.style.overflowY='auto';} else {el.style.height=h+'px';el.style.overflowY='hidden';} }` (title field made a `<textarea>` so it wraps instead of scrolling sideways — DJ hates reading across).

**Last-resort caveat to tell DJ:** if a page is *still* wide after all this, the webview is genuinely stuck at the unfolded width — he must **fully close the app and reopen it while folded** so it lays out for the cover screen.

**Why:** DJ works in the field on this foldable; an editor with the Save button off-screen or a frozen page is a hard blocker. **How to apply:** when DJ reports "so far down / cut off / pans sideways / won't fit / won't scroll" on a phone screen, walk this list. TODO (DJ wants, not yet done): apply #1 + #2 to the other owner/field screens (field.html etc.) so they're foldable-safe too. Related: [[feedback_field_readability_sunlight]], [[project_clockin_bar_customer_overlay]].
