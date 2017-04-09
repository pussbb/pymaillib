# -*- coding: utf-8 -*-
"""
    Imap4 Entity
    ~~~~~~~~~~~~~~~~
    Imap4 Entity is abstract thing to represent values from IMAP in human
    readable form

    :copyright: (c) 2017 WTFPL.
    :license: WTFPL, see LICENSE for more details.
"""


class ImapEntity(object):
    """Imap4 Entity is abstract thing to represent values from IMAP in human
    readable form

    """
    __slots__ = ()

    @staticmethod
    def build(data):
        """Abstract

        :param data:
        :return:
        """
        raise NotImplementedError()

    def dump(self):
        """Serializable form

        :return:
        """
        raise NotImplementedError()

    def __repr__(self):
        return '{}'.format(self.dump())


class SlotBasedImapEntity(ImapEntity):
    """NamedTuple analog maybe remove it in the future

    """

    @staticmethod
    def build(data):
        super().build(data)

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        if not args and not kwargs:
            raise TypeError('No Arguments provided')

        args, kwargs = self._bulk_append(self.__slots__, list(args), kwargs)

        if args or kwargs:
            raise TypeError('Too many values provided {} {}'.format(args,
                                                                    kwargs))

    def _bulk_append(self, keys, args, kwargs):
        if args:
            for item in keys:
                if item in kwargs:
                    break
                try:
                    setattr(self, item, args.pop(0))
                    # super().__setattr__(item, args.pop(0))
                except IndexError as exp:
                    raise TypeError('Missing positional argument for'
                                    ' {}'.format(item), exp)
        for name in list(kwargs):
            setattr(self, name, kwargs.pop(name))
            # super().__setattr__(name, kwargs.pop(name))

        # left items
        return args, kwargs

    def dump(self) -> dict:
        """Convert class attributes into dictionary

        :return: dict
        """
        res = {}
        for item in self.__slots__:
            if item.startswith('_'):
                continue

            def recursive_dict_bytes_to_str(value):
                if not isinstance(value, dict):
                    if isinstance(value, (bytearray, bytes)):
                        return value.decode()
                    return value

                res = {}
                for key, item_value in value.items():
                    if isinstance(key, (bytearray, bytes)):
                        key = key.decode()
                    res[key] = recursive_dict_bytes_to_str(item_value)
                return res

            res[item] = recursive_dict_bytes_to_str(getattr(self, item))
        return res
