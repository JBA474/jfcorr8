# CMake build of JonoF's Witchaven port for the MiSTer hybrid core (the jfSW
# core), after jfSW_MiSTer's jfsw/CMakeLists.txt: classic software renderer
# only, SDL2 with the MiSTer drivers, the engine and sound library of
# ItsDanik's "mister" branches (jfbuild/, jfaudiolib/).
cmake_minimum_required(VERSION 3.16)
project(jfcorr8 C)

option(MISTER_HYBRID "Build for the MiSTer hybrid core (needs SDL2 with the MiSTer drivers)" ON)
if(NOT CMAKE_BUILD_TYPE)
	set(CMAKE_BUILD_TYPE Release)
endif()
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_EXTENSIONS ON)

find_package(SDL2 REQUIRED CONFIG)
get_target_property(SDL2_INCLUDES SDL2::SDL2-static INTERFACE_INCLUDE_DIRECTORIES)

set(ENGINE jfbuild/src)
set(AUDIO jfaudiolib/src)

add_executable(jfcorr8
	${ENGINE}/a-c.c
	${ENGINE}/asmprot.c
	${ENGINE}/baselayer.c
	${ENGINE}/cache1d.c
	${ENGINE}/compat.c
	${ENGINE}/crc32.c
	${ENGINE}/defs.c
	${ENGINE}/engine.c
	${ENGINE}/kplib.c
	${ENGINE}/mmulti.c
	${ENGINE}/osd.c
	${ENGINE}/pragmas.c
	${ENGINE}/scriptfile.c
	${ENGINE}/textfont.c
	${ENGINE}/talltextfont.c
	${ENGINE}/smalltextfont.c
	${ENGINE}/sdlayer2.c
	${ENGINE}/startwin_stub.c
	${ENGINE}/version.c

	${AUDIO}/drivers.c
	${AUDIO}/fx_man.c
	${AUDIO}/cd.c
	${AUDIO}/multivoc.c
	${AUDIO}/mix.c
	${AUDIO}/mixst.c
	${AUDIO}/pitch.c
	${AUDIO}/music.c
	${AUDIO}/midi.c
	${AUDIO}/driver_nosound.c
	${AUDIO}/driver_sdl.c
	${AUDIO}/driver_misterfm.c
	${AUDIO}/gmtimbre.c
	${AUDIO}/asssys.c

	libsmacker/smacker.c

	src/b5compat.c
	src/c8port.c
	src/corr7.c
	src/corr7act.c
	src/corr7cfg.c
	src/corr7eff.c
	src/corr7eng.c
	src/corr7gam.c
	src/corr7gfx.c
	src/corr7kbd.c
	src/corr7men.c
	src/corr7mul.c
	src/corr7plr.c
	src/corr7smk.c
	src/corr7snd.c
	src/corr7tmr.c
	src/corr7wep.c
	src/mister_port.c
	src/mister_crash.c
	src/profile.c
	src/readcfg.c
	src/sosemu.c
	src/version.c

)

target_include_directories(jfcorr8 PRIVATE
	src jfbuild/include jfbuild/src jfaudiolib/include jfaudiolib/src libsmacker
	${SDL2_INCLUDES})
target_compile_definitions(jfcorr8 PRIVATE
	MISTER_HYBRID=1 RENDERTYPESDL=1 HAVE_SDL=2 _GNU_SOURCE)
target_compile_options(jfcorr8 PRIVATE -fno-strict-aliasing -w)
target_link_libraries(jfcorr8 PRIVATE SDL2::SDL2-static m)
