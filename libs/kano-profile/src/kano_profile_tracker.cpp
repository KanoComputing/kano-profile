/**
 *
 * kano_profile_tracker.cpp
 *
 * Copyright (C) 2016 Kano Computing Ltd.
 * License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
 *
 * Adds the interface between useful Kano Profile functions and C++
 *
 *     kano_profile.tracker
 *
 */

#include <Python.h>

#include <kano/python/python_helpers.h>
#include <parson/parson.h>
#include "kano_profile_bindings.h"


kano_profile::tracker::tracker():
    Binding(KANO_PROFILE_TRACKER)
{
}


std::string kano_profile::tracker::session_start(std::string app_name) const
{
    PyObject *py_session_path = this->run_func("session_start", new_tuple(app_name));

    if (py_session_path == NULL)
        return "";

    std::string session_path = PyString_AsString(py_session_path);

    Py_CLEAR(py_session_path);

    return session_path;
}


void kano_profile::tracker::session_end(std::string session_file) const
{
    this->run_func("session_end", new_tuple(session_file));

    return;
}


void kano_profile::tracker::track_action(std::string name) const
{
    this->run_func("track_action", new_tuple(name));

    return;
}


/**
 * Takes a string formatted as a JSON
 *
 * TODO: Add another function accepting a JSON_Object
 */
bool kano_profile::tracker::track_data(std::string name, std::string data) const
{
    JSON_Object *root;
    JSON_Value *root_value;

    root_value = json_parse_string(data.c_str());

    if (json_value_get_type(root_value) != JSONObject) {
        json_value_free(root_value);
        return false;
    }

    root = json_value_get_object(root_value);

    size_t param_count = json_object_get_count(root);
    char *param;
    char *val;
    PyObject *py_data = PyDict_New();
    PyObject *py_val;

    for (size_t i = 0; i < param_count; i++) {
        param = const_cast<char *>(json_object_get_name (root, i));
        val = const_cast<char *>(json_object_get_string(root , param));

        py_val = PyString_FromString(val);
        PyDict_SetItemString(py_data, param, py_val);

        Py_CLEAR(py_val);
    }

    this->run_func("track_data", new_tuple(name, py_data));

    Py_CLEAR(py_data);
    json_value_free(root_value);

    return true;
}
