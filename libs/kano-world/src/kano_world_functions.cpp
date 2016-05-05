/**
 *
 * kano_world_functions.cpp
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano World functions and C++
 *
 *     kano_world.functions
 *
 */


#include <Python.h>
#include <string>

#include <kano/python/python_helpers.h>
#include "kano_world_bindings.h"


kano_world::functions::functions():
    Binding(KANO_WORLD_FUNCTIONS)
{
}


bool kano_world::functions::is_registered() const
{
    PyObject *py_registered = this->run_func("is_registered");

    if (py_registered == NULL)
        return false;

    bool registered = py_registered == Py_True;

    Py_CLEAR(py_registered);

    return registered;
}


std::string kano_world::functions::get_mixed_username() const
{
    PyObject *py_username = this->run_func("get_mixed_username");

    if (py_username == NULL)
        return "";

    std::string username = PyString_AsString(py_username);

    Py_CLEAR(py_username);

    return username;
}
