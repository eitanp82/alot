# Copyright (C) 2015  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU GPL, version 3 or a later revision.
# For further details see the COPYING file
from twisted.internet.defer import inlineCallbacks, returnValue

from alot.errors import GPGProblem, GPGCode
from alot import crypto


@inlineCallbacks
def get_keys(ui, encrypt_keyids, block_error=False):
    keys = {}
    for keyid in encrypt_keyids:
        try:
            key = crypto.get_key(keyid, validate=True, encrypt=True)
        except GPGProblem as e:
            if e.code == GPGCode.AMBIGUOUS_NAME:
                possible_keys = crypto.list_keys(hint=keyid)
                tmp_choices = [k.uids[0].uid for k in possible_keys]
                choices = {str(len(tmp_choices) - x): tmp_choices[x]
                           for x in range(0, len(tmp_choices))}
                keyid = yield ui.choice("ambiguous keyid! Which " +
                                        "key do you want to use?",
                                        choices, cancel=None)
                if keyid:
                    encrypt_keyids.append(keyid)
                continue
            else:
                ui.notify(e.message, priority='error', block=block_error)
                continue
        keys[crypto.hash_key(key)] = key
    returnValue(keys)
