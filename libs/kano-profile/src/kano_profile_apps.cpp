/**
 *
 * kano_profile_apps.cpp
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano Profile functions and C++
 *
 *     kano_profile.apps
 *
 */

#include <Python.h>

#include <kano/python/python_helpers.h>
#include "kano_profile_bindings.h"


kano_profile::apps::apps():
    Binding(KANO_PROFILE_APPS)
{
}


void kano_profile::apps::save_app_state_variable(std::string app, std::string variable, long val) const
{
    PyObject *save_var = this->run_func(
        "save_app_state_variable", new_tuple(app, variable, val)
    );

    if (save_var == NULL)
        return;

    Py_CLEAR(save_var);

    return;
}


long kano_profile::apps::load_app_state_variable(std::string app, std::string variable) const
{
    PyObject *py_var = this->run_func(
        "load_app_state_variable", new_tuple(app, variable)
    );

    if (py_var == NULL)
        return 0;

    long var = PyInt_AsLong(py_var);

    Py_CLEAR(py_var);

    return var;
}
