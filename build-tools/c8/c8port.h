// Corridor 8 on the MiSTer: the port's part (c8port.c)
#ifndef C8PORT_H
#define C8PORT_H
void c8_misterinit(void);   // nothing: app_main did the port's init before ExtInit
int c8_setgamemode(void);   // the screen mode the OSD says (the DOS setgamemode())
void keytimerstuff(void);   // the editor's (nothing in the game)
void c8_nextpage(void);     // every frame flip pumps the engine's events (the DOS game had interrupts)
#define nextpage() c8_nextpage()
extern int qsetmode;        // 200 once the 3D mode is set (the DOS engine's)
extern char tempbuf[8192];  // the DOS engine's scratch buffer the game uses
int c8_loadboard(const char *name, int *x, int *y, int *z, short *ang, short *sect);
int c8_getpacket(short *node, char *buf);
void c8_getmousevalues(short *x, short *y, short *b);
// the BUILD editor's functions the game's editor mode calls: nothing on the MiSTer
short getnumber16(char *namestart, short num, int maxnumber);
void printmessage16(char *name);
void clearmidstatbar16(void);
int gettile(int tilenum);
void draw2dscreen(int posxe, int posye, short ange, int zoome, short gride);
void clear2dscreen(int col);
void printext16(int x, int y, short col, short backcol, char *name, char fontsize);
void editinput(void);
void drawline16(int x1, int y1, int x2, int y2, char col);
void _splitpath(const char *path, char *drive, char *dir, char *fname, char *ext);
#define initcrc() ((void)0)
#define showengineinfo() ((void)0)
#define getch() 0
#define SND_uninitSOS SND_unInitSOS
#define initmultiplayers(a, b, c) ((void)0)
#endif
