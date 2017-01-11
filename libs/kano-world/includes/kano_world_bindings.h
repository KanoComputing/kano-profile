/**
 *
 * kano_world_bindings.h
 *
 * Copyright (C) 2016, 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano World functions and C++
 *
 *     kano_world.*
 *
 */


#ifndef __KANO_WORLD_BINDINGS_H__
#define __KANO_WORLD_BINDINGS_H__

#include <string>

#include <kano/python/python_helpers.h>

#define KANO_WORLD_FUNCTIONS "kano_world.functions"

namespace kano_world {
    class functions : Binding {
        public:
            functions();
            void finalise();

            bool is_registered() const;
            std::string get_mixed_username() const;
            std::string get_token() const;
    };
}

#endif
