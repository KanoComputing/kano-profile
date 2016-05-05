/**
 *
 * kano_profile_profile.cpp
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano Profile functions and C++
 *
 *     kano_profile.profile
 *
 */

#include <Python.h>

#include <kano/python/python_helpers.h>
#include "kano_profile_bindings.h"


kano_profile::profile::profile():
    Binding(KANO_PROFILE_PROFILE)
{
}


std::string kano_profile::profile::get_avatar_circ_image_path(bool retry) const
{
    PyObject *py_avatar = this->run_func("get_avatar_circ_image_path");

    std::string avatar;

    if (py_avatar == NULL)
        avatar = "";
    else
        avatar = PyString_AsString(py_avatar);

    Py_CLEAR(py_avatar);

    if (avatar.empty() && retry) {
        // Generate a default content that Dashboard expects to have
        // Remove "~/.character-content" to revert the command below
        system("kano-character-cli -g");
        return kano_profile::profile::get_avatar_circ_image_path(false);
    } else
        return avatar;
}
