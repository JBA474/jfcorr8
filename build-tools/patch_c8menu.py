"""Corridor 8 (2026-11-17): the Keyboard Config page names each key with
keystrings[code & 0x7F] (corr7men.c), a table of 90 names, while the port's
KBD_keyPressed() returns any keystatus[] index 0..255 and an unset action is
255: a code past the table reads a garbage pointer and sprintf() crashes
(Jess: crash while adjusting the controls in the game's menus). The name is
looked up through a bounds-checked helper now.
usage: patch_c8menu.py <jfcorr8 tree>  (idempotent)"""
import os, sys
root = sys.argv[1]

def edit(rel, pairs):
    p = os.path.join(root, rel); s = open(p, encoding='utf-8', errors='replace', newline='').read(); crlf = '\r\n' in s
    for old, new in pairs:
        if crlf: old, new = old.replace('\n', '\r\n'), new.replace('\n', '\r\n')
        if new in s: continue
        assert s.count(old) == 1, f'{rel}: {old[:60]!r} x{s.count(old)}'
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8', newline='').write(s); print('patched', rel)

edit('src/corr7men.c', [
    ('''int
MEN_keyboardConfiguration(void)
{
''', '''// the name of a key code for the Keyboard Config page: keystrings[] has 90
// entries, the codes the port returns (and 255 for an action without a key)
// go further (MiSTer, 2026-11-17)
static const char *
MEN_keyName(int code)
{
     static const int n = sizeof(keystrings) / sizeof(keystrings[0]);
     code &= 0x7F;
     if (code < 0 || code >= n || keystrings[code] == NULL)
          return "";
     return keystrings[code];
}

int
MEN_keyboardConfiguration(void)
{
'''),
    ('''          sprintf(actionName[i],"%s %-6s",
                  controlArray[i].desc,keystrings[keys[i]&0x7F]);
''', '''          sprintf(actionName[i],"%s %-6s",
                  controlArray[i].desc,MEN_keyName(keys[i]));
'''),
    ('''               sprintf(actionName[curKeyboard],"%s %-6s",
                       controlArray[curKeyboard].desc,keystrings[i&0x7F]);
''', '''               sprintf(actionName[curKeyboard],"%s %-6s",
                       controlArray[curKeyboard].desc,MEN_keyName(i));
'''),
])
print('c8 menu OK')
