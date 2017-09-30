
class Base(object):
    def __init__(self):
        Self._target_is_connected = False
        self._status = (0, "")
        self._reply = None
        self._session = 0
        self._message = 0

    def _send(self):
        """
        socket send
        :return: true if no error otherwise false
        """
        try:
            logger.debug(print_bytes_msg(
                self._message, '-------------- SEND --------------'))
            self.__sock.send(self._message)
        except Exception as e:
            # self.clean_up()
            raise CommError

    def build_header(self, command, length):
            """ Build the encapsulate message header

        The header is 24 bytes fixed length, and includes the command and the length of the optional data portion.

         :return: the headre
        """
        try:
            h = command                                 # Command UINT
            h += pack_uint(length) #struct.pack('<H', n)                   # Length UINT
            h += pack_dint(self._session)                 # Session Handle UDINT
            h += pack_dint(0)                           # Status UDINT
            h += self.attribs['context'] # '_pycomm_'               # Sender Context 8 bytes
            h += pack_dint(self.attribs['option']) # 0     # Option UDINT
            return h
        except Exception as e:
            raise CommError(e)
    
    
    def _send(self):
        """
        socket send
        :return: true if no error otherwise false
        """
        try:
            logger.debug(print_bytes_msg(self._message, '-------------- SEND --------------'))
            self.__sock.send(self._message)
        except Exception as e:
            # self.clean_up()
            raise CommError(e)




    def send_rr_data(self, msg):
            """ SendRRData transfer an encapsulated request/reply packet between the originator and target

        :param msg: The message to be send to the target
        :return: the replay received from the target
        """
        self._message = self.build_header(
                                        ENCAPSULATION_COMMAND["send_rr_data"], # '\x6F\x00'
                                        len(msg)) 
        self._message += msg 
        self._send()
        self._receive()
        return self._check_reply()
    
    def build_common_packet_format(message_type, message, addr_type, addr_data=None, timeout=10):
        """ build_common_packet_format

        It creates the common part for a CIP message. Check Volume 2 (page 2.22) of CIP specification  for reference
        """
        msg = pack_dint(0)   # Interface Handle: shall be 0 for CIP
        msg += pack_uint(timeout)   # timeout
        msg += pack_uint(2)  # Item count: should be at list 2 (Address and Data)
        msg += addr_type  # Address Item Type ID

        if addr_data is not None:
            msg += pack_uint(len(addr_data))  # Address Item Length
            msg += addr_data
        else:
            msg += pack_uint(0)  # Address Item Length
        msg += message_type  # Data Type ID
        msg += pack_uint(len(message))   # Data Item Length
        msg += message
        return ms

    def forward_open(self):
        """ CIP implementation of the forward open message

        Refer to ODVA documentation Volume 1 3-5.5.2

        :return: False if any error in the replayed message
        """
        if self._session == 0:
            self._status = (4, "A session need to be registered before to call forward_open.")
            raise CommError("A session need to be registered before to call forward open")

        forward_open_msg = [
            FORWARD_OPEN, #'\x54'
            pack_usint(2), #struct.pack('B', n)
            CLASS_ID["8-bit"], #'\x20'
            CLASS_CODE["Connection Manager"],  # Volume 1: 5-1 ----->#'\x06'
            INSTANCE_ID["8-bit"], #'\x24'
            CONNECTION_MANAGER_INSTANCE['Open Request'], # '\x01'
            PRIORITY, #'\x0a'
            TIMEOUT_TICKS, # '\x05'
            pack_dint(0), # struct.pack('<i', n)
            self.attribs['cid'],  #'\x27\x04\x19\x71'
            self.attribs['csn'], # '\x27\x04'
            self.attribs['vid'], #'\x09\x10'
            self.attribs['vsn'], #'\x09\x10\x19\x71'
            TIMEOUT_MULTIPLIER, #'\x01'
            '\x00\x00\x00',
            pack_dint(self.attribs['rpi'] * 1000), # rpi=5000 * 1000
            pack_uint(CONNECTION_PARAMETER['Default']), #0x43f8
            pack_dint(self.attribs['rpi'] * 1000), # rpi=5000 * 1000
            pack_uint(CONNECTION_PARAMETER['Default']), # #0x43f8
            TRANSPORT_CLASS,  # Transport Class
            # CONNECTION_SIZE['Backplane'],
            # pack_usint(self.attribs['backplane']),
            # pack_usint(self.attribs['cpu slot']),
            CLASS_ID["8-bit"],#'\x20'
            CLASS_CODE["Message Router"], #'\x02'
            INSTANCE_ID["8-bit"], #'\x24'
            pack_usint(1)# struct.pack('B', n)
        ]

        if self.__direct_connections:
            forward_open_msg[20:1] = [
                CONNECTION_SIZE['Direct Network'],#'\x02'
            ]
        else:
            forward_open_msg[20:3] = [
                CONNECTION_SIZE['Backplane'], # '\x03',
                pack_usint(self.attribs['backplane']), # 1
                pack_usint(self.attribs['cpu slot']) #0
            ]

        if self.send_rr_data( # Lets Send a built packet!!! 
                build_common_packet_format( 
                                            DATA_ITEM['Unconnected'], #'\xb2\x00' <----- Message Type?
                                            ''.join(forward_open_msg),  # This is the message 
                                            ADDRESS_ITEM['UCMM'], # '\x00\x00'
                                            )):
            
            
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
        self.clear() #In Base Class INIT Tuple of (0,'')
        multi_requests = False #Tags in a list seperated by comma
        if isinstance(tag, list): #Checks the tag data type as a list instance.
            multi_requests = True # if the data type proves then its a multe_req

        if not self._target_is_connected: #Boolean in base class set by Forward open Method. 
            if not self.forward_open(): # Open Socket invoked in Base Class.
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
