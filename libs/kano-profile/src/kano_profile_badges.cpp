/**
 *
 * kano_profile_badges.cpp
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano Profile functions and C++
 *
 *     kano_profile.badges
 *
 */

#include <Python.h>
#include <stdint.h>

#include <kano/python/python_helpers.h>
#include "kano_profile_bindings.h"


kano_profile::badges::badges():
    Binding(KANO_PROFILE_BADGES)
{
}


long kano_profile::badges::calculate_xp() const
{
    PyObject *py_xp = this->run_func("calculate_xp");

    if (py_xp == NULL)
        return 0;

    long xp = PyInt_AsLong(py_xp);

    Py_CLEAR(py_xp);

    return xp;
}


long kano_profile::badges::calculate_kano_level() const
{
    PyObject *py_progress = this->run_func("calculate_kano_level");

    if (py_progress == NULL)
        return 0;

    if (py_progress == Py_None
            || !PyTuple_Check(py_progress)
            || PyTuple_Size(py_progress) < 1) {
        Py_CLEAR(py_progress);
        return 0;
    }

    PyObject *py_level = PyTuple_GetItem(py_progress, 0);

    long level = PyInt_AsLong(py_level);

    Py_CLEAR(py_progress);

    return level;
}

long kano_profile::badges::get_xp_to_next_level() const
{
    PyObject *py_xp_boundaries = this->run_func("calculate_min_current_max_xp");

    if (py_xp_boundaries == NULL)
        return 0;

    if (py_xp_boundaries == Py_None
            || !PyTuple_Check(py_xp_boundaries)
            || PyTuple_Size(py_xp_boundaries) < 3) {
        Py_CLEAR(py_xp_boundaries);
        return 0;
    }

    PyObject *py_success = PyTuple_GetItem(py_xp_boundaries, 0);
    PyObject *py_current_xp = NULL;
    PyObject *py_next_level_xp = NULL;

    if (PyInt_AsLong(py_success) != -1) {
        py_current_xp = PyTuple_GetItem(py_xp_boundaries, 1);
        py_next_level_xp = PyTuple_GetItem(py_xp_boundaries, 2);
    }

    long next_level_xp;
    long current_xp;

    if ((next_level_xp = PyInt_AsLong(py_next_level_xp)) == -1
            && PyErr_Occurred() != NULL)
        next_level_xp = INTMAX_MAX;

    if ((current_xp = PyInt_AsLong(py_current_xp)) == -1
            && PyErr_Occurred() != NULL)
        current_xp = 0;

    Py_CLEAR(py_xp_boundaries);

    return next_level_xp - current_xp;
}


double kano_profile::badges::get_progress_to_next_level() const
{
    PyObject *py_progress = this->run_func("calculate_kano_level");

    if (py_progress == NULL)
        return 0;

    if (py_progress == Py_None
            || !PyTuple_Check(py_progress)
            || PyTuple_Size(py_progress) < 1) {
        Py_CLEAR(py_progress);
        return 0;
    }


    PyObject *py_percent = PyTuple_GetItem(py_progress, 1);
    double progress = PyFloat_AsDouble(py_percent);

    Py_CLEAR(py_progress);

    return progress;
}
