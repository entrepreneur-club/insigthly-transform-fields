#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Insightly "Web To Contact" does not allow to
directly store custom fields. But it allows
adding custom fields to the web form which then will
be added to the "Background" field in ``key: value\n``
form. Example::

    <form name="insightly_web_to_contact"
        action="https://...insight.ly/WebToContact/Create"
        method="post">

        <input type="hidden" name="formId" value="..." />

        <label for="insightly_firstName">First Name: </label>
        <input id="insightly_firstName" name="FirstName" type="text" />
        <br/>
        ...

        <label for="CONTACT_FIELD_1">Gender</label>
        <input id="CONTACT_FIELD_1" name="CONTACT_FIELD_1" type="text" />
        <br/>

        <label for="CONTACT_FIELD_2">University</label>
        <input id="CONTACT_FIELD_2" name="CONTACT_FIELD_2" type="text" />
        <br/>
        ...

        <label for="insightly_background">Additional information: </label>
        <br>
        <textarea id="insightly_background" name="background"></textarea>
        <br/>
        <input type="submit" value="Submit" />
    </form>

Will produce a Background field like this::

    CONTACT_FIELD_1: Male
    CONTACT_FIELD_2: ETHZ

This script fetches the contacts via Insigntly HTTPS JSON API,
finds all contacts with such custom values in the background field
and then updates the contact. To record which contacts already have been
processed, another custom field is introduced (you may name it was you want,
I use ``custom_field_copied`` and the help text ``DO NOT DO ANYTHING WITH
THIS FIELD. It is for automatic use only.``). The only important thing is the
custom field id of this field which must be set below in
``ISPROCESSED_FIELD_ID``.

Then, also set your API key, and let the script run periodically via CRON.
"""

from __future__ import unicode_literals, division
import base64
import json
import re
# sadly, we have to use urllib instead of requests
# because hostpoint python does not have more packages
import urllib2

API_KEY = 'ENTER API KEY HERE'
API_BASE = 'https://api.insight.ly/v2/%s'
# id of the field which specifies
# if the conversion for a record has been done or not
ISPROCESSED_FIELD_ID = 'CONTACT_FIELD_5'
# if the meta field is set to this value, the contact
# has been processed already
ISPROCESSED_FIELD_YES = 'yes'


def add_opener():
    opener = urllib2.build_opener()
    opener.addheaders = [
        ('Authorization', 'Basic %s' % base64.b64encode(API_KEY))
    ]
    urllib2.install_opener(opener)
    return opener


def get_custom_field_ids():
    """
    Get a list of all custom field ids for which we are going
    to search in the "Background" (i.a. comments/diverse things) field.
    """
    cust_fields = json.loads(
        urllib2.urlopen(API_BASE % 'CustomFields').read())
    return [f['CUSTOM_FIELD_ID'] for f in cust_fields]


def get_contacts():
    customers = json.loads(
        urllib2.urlopen(API_BASE % 'Contacts').read())
    return customers


def filter_contacts_unprocessed(contacts):
    """
    Filter a list of contacts so that only the ones which
    have not yet been processed come through (meta field not set
    to yes)
    """
    return [c for c in contacts if c[ISPROCESSED_FIELD_ID] != ISPROCESSED_FIELD_YES]


def extract_fields(contact, custom_field_ids):
    background = contact['BACKGROUND']
    fields = {}

    if background is None:
        return None

    for f in custom_field_ids:
        r = re.compile('^%s:\s(.+)$' % f, re.MULTILINE)

        def repl(matchobj):
            fields[f] = matchobj.group(1)
            return ''

        background = r.sub(repl, background)

    fields['BACKGROUND'] = background.strip()
    return fields


def put_contact(contact, fields_to_update):
    contact.update(fields_to_update)
    contact[ISPROCESSED_FIELD_ID] = ISPROCESSED_FIELD_YES

    request = urllib2.Request(API_BASE % 'Contacts', data=json.dumps(contact))
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'PUT'
    req = urllib2._opener.open(request)
    if not req.getcode() == 200:
        print 'Update failed, status code is not 200. Body:'
        print req.read()


def main():
    add_opener()
    custom_field_ids = get_custom_field_ids()
    unprocessed_contacts = filter_contacts_unprocessed(get_contacts())
    for c in unprocessed_contacts:
        fields = extract_fields(c, custom_field_ids)
        if fields is not None:
            # always overwrite the 'ETH EC Membership' custom field with
            # the least-dangerous default value.
            fields['CONTACT_FIELD_4'] = 'Newsletter (Non-Member)'
            put_contact(c, fields)

if __name__ == '__main__':
    main()
