class DataError(PycommError):
    pass


def forward_open(self):
    """ CIP implementation of the forward open message

    Refer to ODVA documentation Volume 1 3-5.5.2

    :return: False if any error in the replayed message
    """
    if self._session == 0:
        self._status = (
            4, "A session need to be registered before to call forward_open.")
        raise CommError(
            "A session need to be registered before to call forward open")

    forward_open_msg = [
        FORWARD_OPEN,  # '\x54'
        pack_usint(2),  # struct.pack('B', n)
        CLASS_ID["8-bit"],  # '\x20'
        CLASS_CODE["Connection Manager"],  # '\x06'
        INSTANCE_ID["8-bit"],  # '\x24'
        CONNECTION_MANAGER_INSTANCE['Open Request'],  # '\x01'
        PRIORITY,  # '\x0a'
        TIMEOUT_TICKS,  # '\x05'
        pack_dint(0),  # struct.pack('<i', n)
        self.attribs['cid'],
        self.attribs['csn'],
        self.attribs['vid'],
        self.attribs['vsn'],
        TIMEOUT_MULTIPLIER,
        '\x00\x00\x00',
        pack_dint(self.attribs['rpi'] * 1000),
        pack_uint(CONNECTION_PARAMETER['Default']),
        pack_dint(self.attribs['rpi'] * 1000),
        pack_uint(CONNECTION_PARAMETER['Default']),
        TRANSPORT_CLASS,  # Transport Class
        # CONNECTION_SIZE['Backplane'],
        # pack_usint(self.attribs['backplane']),
        # pack_usint(self.attribs['cpu slot']),
        CLASS_ID["8-bit"],
        CLASS_CODE["Message Router"],
        INSTANCE_ID["8-bit"],
        pack_usint(1)
    ]

    if self.__direct_connections:
        forward_open_msg[20:1] = [
            CONNECTION_SIZE['Direct Network'],
        ]
    else:
        forward_open_msg[20:3] = [
            CONNECTION_SIZE['Backplane'],
            pack_usint(self.attribs['backplane']),
            pack_usint(self.attribs['cpu slot'])
        ]

    if self.send_rr_data(
            build_common_packet_format(DATA_ITEM['Unconnected'], ''.join(forward_open_msg), ADDRESS_ITEM['UCMM'],)):
        self._target_cid = self._reply[44:48]
        self._target_is_connected = True
        return True
    self._status = (4, "forward_open returned False")
    return False


def read_tag(self, tag):
    """ read tag from a connected plc

    Possible combination can be passed to this method:
            - ('Counts') a single tag name
            - (['ControlWord']) a list with one tag or many
            - (['parts', 'ControlWord', 'Counts'])

    At the moment there is not a strong validation for the argument passed. The user should verify
    the correctness of the format passed.

    :return: None is returned in case of error otherwise the tag list is returned
    """
    self.clear()  # In Base Class INIT Tuple of (0,'')
    multi_requests = False  # Tags in a list seperated by comma
    if isinstance(tag, list):  # Checks the tag data type as a list instance.
        multi_requests = True  # if the data type proves then its a multe_req

    # Boolean in base class set by Forward open Method.
    if not self._target_is_connected:
        if not self.forward_open():
            self._status = (
                6, "Target did not connected. read_tag will not be executed.")
            logger.warning(self._status)
            raise DataError(
                "Target did not connected. read_tag will not be executed.")

    if multi_requests:
        rp_list = []
        for t in tag:
            rp = create_tag_rp(t, multi_requests=True)
            if rp is None:
                self._status = (
                    6, "Cannot create tag {0} request packet. read_tag will not be executed.".format(tag))
                raise DataError(
                    "Cannot create tag {0} request packet. read_tag will not be executed.".format(tag))
            else:
                rp_list.append(
                    chr(TAG_SERVICES_REQUEST['Read Tag']) + rp + pack_uint(1))
        message_request = build_multiple_service(rp_list, Base._get_sequence())

    else:
        rp = create_tag_rp(tag)
        if rp is None:
            self._status = (
                6, "Cannot create tag {0} request packet. read_tag will not be executed.".format(tag))
            return None
        else:
            # Creating the Message Request Packet
            message_request = [
                pack_uint(Base._get_sequence()),
                chr(TAG_SERVICES_REQUEST['Read Tag']),  # the Request Service
                # the Request Path Size length in word
                chr(len(rp) / 2),
                rp,                                     # the request path
                pack_uint(1)
            ]

    if self.send_unit_data(
            build_common_packet_format(
                DATA_ITEM['Connected'],
                ''.join(message_request),
                ADDRESS_ITEM['Connection Based'],
                addr_data=self._target_cid,
            )) is None:
        raise DataError("send_unit_data returned not valid data")

    if multi_requests:
        return self._parse_multiple_request_read(tag)
    else:
        # Get the data type
        if self._status[0] == SUCCESS:
            data_type = unpack_uint(self._reply[50:52])
            try:
                return UNPACK_DATA_FUNCTION[I_DATA_TYPE[data_type]](self._reply[52:]), I_DATA_TYPE[data_type]
            except Exception as e:
                raise DataError(e)
        else:
            return None
