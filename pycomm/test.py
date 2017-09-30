from ab_comm.clx import Driver as ClxDriver
import logging
import time

if __name__ == '__main__':
    logging.basicConfig(
        filename="ClxDriver.log",
        format="%(levelname)-10s %(asctime)s %(message)s",
        level=logging.DEBUG
    )
    c = ClxDriver()

    if c.open('192.168.6.70'):
        print('Something here')
        # print(c.read_tag('Raymond_DINT'))
        val = c.read_tag('Raymond_INT')
        c.write_tag(bytes(val))
        # print(c.read_tag('Raymond_Real'))
        # print(c.read_tag('Raymond_SINT'))
        # print(c.read_tag('Scan_Counter'))
        # print(c.read_string('Raymond_String'))
        # print(c.read_tag(['parts', 'ControlWord', 'Counts']))

        # print(c.write_tag('Raymond_INT', 1, 'INT'))
        # print(c.read_tag('Raymond_INT'))
        # print(c.write_tag(('Counts', 26, 'INT')))
        # print(c.write_tag([('Counts', 26, 'INT')]))
        # print(c.write_tag([('Counts', -26, 'INT'), ('ControlWord', -30, 'DINT'), ('parts', 31, 'DINT')]))

        # To read an array
        # r_array = c.read_array("TotalCount", 1750)
        # for tag in r_array:
        #     print (tag)

        # To read string
        # c.write_string('Raymond_String', 'is there anyone out there')
        # c.read_string('Raymond_String')

        # reset tha array to all 0
        # w_array = []
        # for i in xrange(1750):
        #     w_array.append(0)
        # c.write_array("TotalCount", w_array, "SINT")
        # while True:
        #     print(c.read_tag('Scan_Counter'))

        #     time.sleep(.5)

        # c.close()
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Done!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
