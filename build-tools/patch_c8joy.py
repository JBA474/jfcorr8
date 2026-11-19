"""Corridor 8 (2026-11-18): a Joystick Options page. The prototype's Options >
Controller Options > Joysticks entry is an empty stub, and Jess wants to
invert the right stick's look axis. The page has one setting, INVERT LOOK,
kept in corr7.ini under [MISTER] (read and written with the game's other
controller settings, readcfg.c); c8port.c applies it to the right stick's
up/down (the look keys).
usage: patch_c8joy.py <jfcorr8 tree>  (idempotent)"""
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

edit('src/readcfg.c', [
    ('''void
readKeyboardConfig(_INI_INSTANCE *sInstance)
{
''', '''// MiSTer (2026-11-18): the pad's settings, [MISTER] in corr7.ini
int c8_invertlook = 0;

void
readMiSTerConfig(_INI_INSTANCE *sInstance)
{
     if (!hmiINILocateSection(sInstance,"MISTER")) {
          return;
     }
     if (hmiINIGetItemString(sInstance,"INVERT LOOK",tempBuf,16)) {
          if (strlen(tempBuf) > 0) {
               c8_invertlook=atoi(tempBuf) != 0;
          }
     }
}

void
writeMiSTerConfig(_INI_INSTANCE *sInstance)
{
     if (!hmiINILocateSection(sInstance,"MISTER")) {
          hmiINIAddSection(sInstance,"MISTER");
     }
     if (!hmiINILocateItem(sInstance,"INVERT LOOK")) {
          hmiINIAddItemDecimal(sInstance,"INVERT LOOK",(WORD)c8_invertlook,
                               strlen("INVERT LOOK")+4,16);
     }
     else {
          hmiINIWriteDecimal(sInstance,(WORD)c8_invertlook);
     }
}

void
readKeyboardConfig(_INI_INSTANCE *sInstance)
{
'''),
    ('''     readKeyboardConfig(&sInstance);
''', '''     readKeyboardConfig(&sInstance);
     readMiSTerConfig(&sInstance);
'''),
    ('''     writeKeyboardConfig(&sInstance);
''', '''     writeKeyboardConfig(&sInstance);
     writeMiSTerConfig(&sInstance);
'''),
])

edit('src/c8port.c', [
    ('''        int v = joynumaxes > sticks[k].axis ? joyaxis[sticks[k].axis] * sticks[k].sign : 0;
''', '''        int sign = sticks[k].sign;
        if (sticks[k].axis == 3 && c8_invertlook) sign = -sign; // Joystick Options: INVERT LOOK
        int v = joynumaxes > sticks[k].axis ? joyaxis[sticks[k].axis] * sign : 0;
'''),
    ('''static void c8_padkeys(void) {
''', '''extern int c8_invertlook; // readcfg.c, [MISTER] INVERT LOOK
static void c8_padkeys(void) {
'''),
])

edit('src/corr7men.c', [
    ('''},*mouseNames[NUMMOUSEOPTIONS];
''', '''},*mouseNames[NUMMOUSEOPTIONS];

// MiSTer (2026-11-18): the Joystick Options page, which the prototype left
// as a stub; its one setting is kept in corr7.ini (readcfg.c)
enum {
     JMENU_INVERTLOOK,
     JMENU_EXIT,
     NUMJOYSTICKOPTIONS
};

int  curJoystick;
extern int c8_invertlook;

struct menuOption joystickNamesArr[NUMJOYSTICKOPTIONS]={
     {1,MENUOPTION_BOOLEAN,"INVERT LOOK",0,0,0,0,FONT_BIGFONT},
     {1,MENUOPTION_LEFTJUST,"PREVIOUS MENU",0,0,0,0,FONT_BIGFONT}
},*joystickNames[NUMJOYSTICKOPTIONS];
'''),
    ('''          mouseNames[i]=&mouseNamesArr[i];
''', '''          mouseNames[i]=&mouseNamesArr[i];
     }
     for (i=0 ; i < NUMJOYSTICKOPTIONS ; i++) {
          joystickNames[i]=&joystickNamesArr[i];
'''),
    ('''int
MEN_controllerOptions(void)
{
''', '''int
MEN_joystickOptions(void)
{
     int  pic=0,
          r=1;

     joystickNames[JMENU_INVERTLOOK]->misc1=c8_invertlook;
     while (r) {
          pic=menuBackgroundPic;
          r=MEN_doMenu(&curJoystick,NUMJOYSTICKOPTIONS,pic,
                       "JOYSTICK OPTIONS",joystickNames);
          if (r) {
               switch (curJoystick) {
               case JMENU_INVERTLOOK:
                    joystickNames[curJoystick]->misc1^=1;
                    break;
               case JMENU_EXIT:
                    r=0;
                    break;
               }
          }
     }
     c8_invertlook=joystickNames[JMENU_INVERTLOOK]->misc1;
     return(r);
}

int
MEN_controllerOptions(void)
{
'''),
    ('''//                    MEN_joystickControllers();
''', '''                    MEN_joystickOptions();
'''),
])
print('c8 joystick options OK')
