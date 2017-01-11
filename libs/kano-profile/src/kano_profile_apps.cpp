/**
 *
 * kano_profile_apps.cpp
 *
 * Copyright (C) 2016, 2017 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano Profile functions and C++
 *
 *     kano_profile.apps
 *
 */

#include <Python.h>
#include <string>

#include <kano/python/python_helpers.h>
#include "kano_profile_bindings.h"


kano_profile::apps::apps():
    Binding(KANO_PROFILE_APPS)
{
}


void kano_profile::apps::finalise() {
    Binding::finalise();
}


void kano_profile::apps::save_app_state_decode(std::string app, std::string data) const
{
    PyObject *save_var = this->run_func(
        "save_app_state_decode", new_tuple(app, data)
    );

    if (save_var == NULL)
        return;

    Py_CLEAR(save_var);

    return;
}


void kano_profile::apps::save_app_state_variable(
    std::string app, std::string variable, long val) const
{
    PyObject *save_var = this->run_func(
        "save_app_state_variable", new_tuple(app, variable, val)
    );

    if (save_var == NULL)
        return;

    Py_CLEAR(save_var);

    return;
}


void kano_profile::apps::save_app_state_variable_decode(
    std::string app, std::string variable, std::string val) const
{
    PyObject *save_var = this->run_func(
        "save_app_state_variable_decode", new_tuple(app, variable, val)
    );

    if (save_var == NULL)
        return;

    Py_CLEAR(save_var);

    return;
}

std::string kano_profile::apps::load_app_state_encode(std::string app) const
{
    PyObject *py_var = this->run_func(
        "load_app_state_encode", new_tuple(app)
    );

    std::string var = (py_var == NULL) ? "" : PyString_AsString(py_var);

    Py_CLEAR(py_var);

    return var;
}

long kano_profile::apps::load_app_state_variable(
    std::string app, std::string variable) const
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

std::string kano_profile::apps::load_app_state_variable_encode(
    std::string app, std::string variable) const
{
    PyObject *py_var = this->run_func(
        "load_app_state_variable_encode", new_tuple(app, variable)
    );

    std::string var = (py_var == NULL) ? "" : PyString_AsString(py_var);

    Py_CLEAR(py_var);

    return var;
}
