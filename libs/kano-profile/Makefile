#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Build file for libkano_profile
#

PLATFORM := $(shell uname)

ifeq ($(PLATFORM), Linux)
	SONAME_FLAG=-soname
	SONAME=libkano_profile.so.1
	LD_TYPE=-shared
else ifeq ($(PLATFORM), Darwin)
	SONAME_FLAG=-install_name
	SONAME=libkano_profile.dylib
	LD_TYPE=-dynamiclib
endif

CXXFLAGS+=-Wall -Wextra -O3 -fPIC -c -std=c++11 `python-config --cflags`
LDFLAGS+=$(LD_TYPE) -Wl,$(SONAME_FLAG),$(SONAME) `python-config --ldflags` -lparson -lkano_python
INCLUDES+=-I./includes
OBJS=\
	 kano_profile_apps.so \
	 kano_profile_badges.so \
	 kano_profile_profile.so \
	 kano_profile_tracker.so

OUTDIR=release
DEBUG_OUTDIR=debug

all: ensure-dir $(SONAME)

debug: CXXFLAGS += -DDEBUG -g
debug: OUTDIR=$(DEBUG_OUTDIR)
debug: $(SONAME)

ensure-dir:
	mkdir -p $(OUTDIR)
	mkdir -p $(DEBUG_OUTDIR)

$(SONAME): $(OBJS)
	$(CXX) $(LDFLAGS) $(addprefix $(OUTDIR)/, $?) -o $(OUTDIR)/$@

%.so: src/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) $< -o $(OUTDIR)/$@

clean-release:
	@rm -f $(OUTDIR)/$(OBJS)
	@rm -f $(OUTDIR)/$(SONAME)

clean-debug:
	@rm -f $(DEBUG_OUTDIR)/$(OBJS)
	@rm -f $(DEBUG_OUTDIR)/$(SONAME)

clean: clean-release clean-debug
