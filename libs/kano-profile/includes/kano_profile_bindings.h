/**
 *
 * kano_profile_bindings.h
 *
 * Copyright (C) 2016, 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano Profile functions and C++
 *
 *     kano_profile.*
 *
 */


#ifndef __KANO_PROFILE_BINDINGS_H__
#define __KANO_PROFILE_BINDINGS_H__

#include <string>
#include <kano/python/python_helpers.h>

#define KANO_PROFILE_APPS "kano_profile.apps"
#define KANO_PROFILE_BADGES "kano_profile.badges"
#define KANO_PROFILE_PROFILE "kano_profile.profile"
#define KANO_PROFILE_TRACKER "kano_profile.tracker"

namespace kano_profile {

    class apps : private Binding
    {
        public:
            apps();
            void finalise();

            void save_app_state_decode(std::string app, std::string data) const;

            void save_app_state_variable(
                std::string app, std::string variable, long val
            ) const;
            void save_app_state_variable_decode(
                std::string app, std::string variable, std::string val
            ) const;

            std::string load_app_state_encode(std::string app) const;

            long load_app_state_variable(
                std::string app, std::string variable
            ) const;
            std::string load_app_state_variable_encode(
                std::string app, std::string variable
            ) const;
    };

    class badges : private Binding
    {
        public:
            badges();
            long calculate_xp() const;
            long calculate_kano_level() const;
            long get_xp_to_next_level() const;
            double get_progress_to_next_level() const;
    };

    class profile : private Binding
    {
        public:
            profile();
            std::string get_avatar_circ_image_path(bool retry = true) const;
    };

    class tracker : private Binding
    {
        public:
            tracker();
            std::string session_start(std::string app_name) const;
            void session_end(std::string session_file) const;
            void track_action(std::string name) const;
            bool track_data(std::string name, std::string data) const;
    };

}


#endif
