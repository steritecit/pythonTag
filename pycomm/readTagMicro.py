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
        self.clear() #In Base Class INIT Tuple of (0,'')
        multi_requests = False #Tags in a list seperated by comma
        if isinstance(tag, list): #Checks the tag data type as a list instance.
            multi_requests = True # if the data type proves then its a multe_req

        if not self._target_is_connected: #Boolean in base class set by Forward open Method. 
            if not self.forward_open(): 
                self._status = (6, "Target did not connected. read_tag will not be executed.")
                logger.warning(self._status)
                raise DataError("Target did not connected. read_tag will not be executed.")

        if multi_requests:
            rp_list = []
            for t in tag:
                rp = create_tag_rp(t, multi_requests=True)
                if rp is None:
                    self._status = (6, "Cannot create tag {0} request packet. read_tag will not be executed.".format(tag))
                    raise DataError("Cannot create tag {0} request packet. read_tag will not be executed.".format(tag))
                else:
                    rp_list.append(chr(TAG_SERVICES_REQUEST['Read Tag']) + rp + pack_uint(1))
            message_request = build_multiple_service(rp_list, Base._get_sequence())

        else:
            rp = create_tag_rp(tag)
            if rp is None:
                self._status = (6, "Cannot create tag {0} request packet. read_tag will not be executed.".format(tag))
                return None
            else:
                # Creating the Message Request Packet
                message_request = [
                    pack_uint(Base._get_sequence()),
                    chr(TAG_SERVICES_REQUEST['Read Tag']),  # the Request Service
                    chr(len(rp) / 2),                       # the Request Path Size length in word
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
