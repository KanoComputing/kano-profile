#!/usr/bin/env python

# tracking-events.py
#
# Copyright (C) 2015-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A few predefined tracking events

import json

from kano_profile.tracker import get_action_event, track_data
from kano_world.connection import request_wrapper, content_type_json
from kano.utils import get_rpi_model, detect_kano_keyboard, get_partition_info


def _hw_info():
    # TODO: This import is done here to avoid potential
    #       import loops with kano-peripherals.
    from kano_peripherals.wrappers.detection import is_ck2_lite, is_ck2_pro, \
        get_ck2_lite_version, get_ck2_pro_version

    # If CKL/CKCs cannot be detected, defaults to Computer Kits without version.
    kit_type = 'ck'
    kit_version = None

    # Detect CK Lite via the PiHat board.
    if is_ck2_lite():
        kit_type = 'ckl'
        kit_version = get_ck2_lite_version()

    # Detect CK Complete via the PowerHat board and other peripherals.
    elif is_ck2_pro():
        kit_type = 'ckc'
        kit_version = get_ck2_pro_version()

    track_data('hw-info', {
        'keyboard': 'kano' if detect_kano_keyboard() else 'generic',
        'model': get_rpi_model(),
        'partitions': get_partition_info(),
        'kit': {
            'type': kit_type,
            'version': kit_version.vstring if kit_version else kit_version
        }
    })


def _ping():
    """
        The ping event is unauthenticated and is dispatched right away,
        without passing through the caching layer in the `events` file.
    """
    event = json.dumps(get_action_event('ping'))
    status, err, _ = request_wrapper('post', '/tracking/ping', data=event,
                                     headers=content_type_json)

    if not status:
        msg = _("Failed to send the ping event ({})").format(err)
        raise RuntimeError(msg)


def _low_battery():
    track_data('battery', {
        'status': 'low-charge'
    })


def _auto_poweroff():
    track_data('battery', {
        'status': 'automatic-poweroff'
    })


event_templates = {
    'hw-info': _hw_info,
    'ping': _ping,
    'low-battery': _low_battery,
    'auto-poweroff': _auto_poweroff
}


def generate_event(event_name):
    """
        Fires off a predefined tracker event (see the tracking_events module).

        :param name: The identifier of the event.
        :type name: str
    """

    if event_name in event_templates:
        event_templates[event_name]()
    else:
        raise RuntimeError(_("Unknown event template '{}'.").format(event_name))
