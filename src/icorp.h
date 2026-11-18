/***************************************************************************
 *   ICORP.H   - main include file for Corridor 7                          *
 *                                                                         *
 *                                                     02/27/96  Les Bird  *
 ***************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <setjmp.h>
#include <fcntl.h>
#include <ctype.h>
#include <sys/types.h>
#include <sys/stat.h>

//** BUILD includes
#include "build.h"
#include "baselayer.h"
#include "cache1d.h"
#include "pragmas.h"
#include "mmulti.h"
#include <unistd.h>
#include "names.h"
#include "pragmas.h"

//** SOS includes
#include "sos.h"
#include "sosm.h"
#include "profile.h"
#if 0
#include "sosez.h"
#endif

//** SCITECH PMODE.LIB includes
// #include "pmpro.h"  /* not in the port */

//** Corridor 7 includes
#include "corr7.h"
#include "c8port.h"
