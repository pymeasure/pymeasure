import re, struct
from datetime import datetime as dt
from itertools import chain

class GenericTag(object):
    """ Generic TAG for Rohde & Schwarz IQ waveform file"""

    # Pattern match for parsing
    pattern = "{(?P<name>.*?):(?P<value>.*?)}"

    # Marker for binary fields
    binary_value_marker = '<{} binary value>'
    @classmethod
    def match(cls, content):
        """ Perform pattern matching on content and return dictionary of matches and new content """
        return_value = None
        pattern = cls.pattern
        if isinstance(content, bytes):
            pattern = pattern.encode()
        m = re.match(pattern, content, flags=re.DOTALL)
        if m:
            return_value = m.groupdict()
            content = content[m.span()[1]:]

        return return_value, content
    
    def __init__(self, **kwargs):
        # name must always be there
        assert('name' in kwargs)
        name = kwargs['name']
        del kwargs['name']
        if isinstance(name, bytes):
            name = name.decode()

        self.name = name
        self._field_list = []
        comma = ""
        output_format = ""
        for key, value in kwargs.items():
            v, of = self.guess_content_type(value)
            output_format += "%s{%s:%s}"%(comma, key, of)
            setattr(self, key, v)
            self._field_list.append(key)
            comma = ","
        if not hasattr(self, 'output_format'):
            self.output_format = "{name:s}:" + output_format

    def guess_content_type(self, value):
        """ Try to guess the content type by inspecting the tag value,
        return a tuple with guessed value and format type suitable for conversion to str type """
        if not isinstance(value, (str, bytes)):
            return (value, "")

        return_value = (value, "")
        try:
            return_value = (int(value), "d")
        except ValueError:
            try:
                return_value = (float(value), "f")
            except ValueError:
                if isinstance(value, bytes):
                    if re.match(b"[\w ]+", value):
                        return_value = (value.decode(), "s")

        return return_value

    def to_binary(self, field):
        """ Translate field to binary format """
        hook_name = "to_binary_" + field
        if hasattr(self, hook_name):
            value = getattr(self, hook_name)()
        else:
            value = getattr(self, field).encode()
        return value

    def to_info(self, field, max_size=0):
        """ Translate field to string format suitable for info output """
        hook_name = "to_info_" + field
        if hasattr(self, hook_name):
            value = getattr(self, hook_name)()
        else:
            value = getattr(self, field)
        if max_size:
            try:
                if (len(value) > max_size):
                    value = str(value[:(max_size - 3)]) + "..."
            except:
                pass

        return value

    def to_file_text(self, field):
        """ Translate field to a value suitable for string representation in file format using output_format template"""
        hook_name = "to_file_text_" + field
        if hasattr(self, hook_name):
            value = getattr(self, hook_name)()
        else:
            value = self.to_info(field)

        return value

    def format(self, field, mode, max_size=0):
        """ Format data for output according to mode """

        if mode == 'FILE_BINARY':
            value = self.to_binary(field)
        elif mode == 'FILE_TEXT':
            value = self.to_file_text(field)
        elif mode == 'NATIVE':
            value =  getattr(self, field)
        elif mode == 'INFO':
            value = self.to_info(field, max_size)
        else:
            raise Exception("Invalid mode: \"{}\"".format(mode))
        return value

    def encode_output(self, file_output):
        """ Encode file_output content string in binary format """
        file_output = file_output.encode()

        # Patch binary fields
        pattern = b"<(.*?) binary value>"
        strings = re.findall(pattern, file_output)
        strings = [s.decode() for s in strings]
        for field in strings:
            file_output = file_output.replace("<{} binary value>".format(field).encode(),
                                              self.format(field, mode='FILE_BINARY'))
        return file_output
        
    def file_output (self):
        kwargs = {'name' : self.name}
        for field in self._field_list:
            kwargs[field] = self.format(field, mode = 'FILE_TEXT')

        retval = "{" + self.output_format.format(**kwargs) + "}"
        return self.encode_output(retval)

    def __str__(self):
        return_value = "TAG ({}): {} = (".format(self.__class__.__name__, self.name)
        for index, field in enumerate(self._field_list):
            value = self.format(field, mode='INFO', max_size=64)
            return_value = return_value + "{} = {}".format(field, value)
            if (index < (len(self._field_list) - 1)):
                return_value += ", "
        return_value += ")"
        return return_value

class BinaryTag(GenericTag):
    pattern = "{(?P<name>.*)-(?P<size>\d+):#"
    output_format = "{name:s}-{size:d}:{value:s}"
    @classmethod
    def match(cls, content):
        """ Specific match method for binary tags """
        
        m, content = super(BinaryTag, cls).match(content)
        if m:
            size = int(m['size'].decode())
            m['value'] = content[:size-1]
            content = content[size:]
            del m['size'] # size is not interesting since it is the length of value entry
        return m, content

    def to_file_text_value(self):
        return self.binary_value_marker.format('value')
        
class WaveformTag(BinaryTag):
    """ Tag which carries the actual I/Q samples as 16 bit signed integers

.. warning:: When the tag name is WWAVEFORM (double W) instead of WAVEFORM, this is probably some proprietary
encrypted format from Rohde & Schwarz and so it is not possible to correctly decode the content.

    """
    pattern = "{(?P<name>W?WAVEFORM)-(?P<size>\d+):(?P<extra_chars>0,)?#"
    @classmethod
    def match(cls, content):
        """ Specific match method for waveform tags """

        m, content = super(WaveformTag, cls).match(content)
        if m and (content['extra_chars'] is None):
            content['extra_chars'] = ""
        return m, content

    def __init__(self, value, name="WAVEFORM", extra_chars=""):
        if isinstance(value, bytes):
            length = int(len(value)/2)
            value = struct.unpack("<" + "h"*length, value)
            # Group I/Q samples in sublist
            value = list((value[i], value[i+1]) for i in range(0, len(value), 2))
        # value is a list of (i,q) list, each i and q are signed 16 bit numbers.
        super().__init__(name=name, size=0, value=value, extra_chars=extra_chars)

    @property
    def samples (self):
        return len(self.value)

    @property
    def size (self):
        return len(self.value) * 4 + 1 + len(self.extra_chars)

    @size.setter
    def size (self, value):
        pass

    def to_binary_value(self):
        val = list(chain.from_iterable(self.value))
        val = self.extra_chars.encode() + b'#' + struct.pack("<" + "h"*len(val), *val)
        return val

    def checksum(self):
        result = 0xA50F74FF
        for (i,q) in self.value:
            val = struct.unpack("<I", struct.pack("<hh",i, q))[0]
            result = (result ^ val)

        return(result);

class EmptyTag(BinaryTag):
    """ Empty tag is needed since WAVEFORM tag should start exactly at hex 4000 offset """
    pattern = "{(?P<name>EMPTYTAG)-(?P<size>\d+):#"

    char = ' ' # space
    @property
    def size (self):
        return self._size + 1

    @size.setter
    def size (self, value):
        pass

    @property
    def value (self):
        return_value = "#" + (self.char) * (self._size)
        return return_value

    @value.setter
    def value (self, value):
        self._size = value

    def __init__(self, name="EMPTYTAG", value=0):
        if isinstance(value, bytes):
            size = len(value)
        elif isinstance(value, int):
            size = value
            
        super().__init__(name=name, size = 0, value=size)

class IndexTag(GenericTag):
    pattern = "{(?P<name>(?:[^}]*?) LIST) (?P<index>\d+):(?P<listvalue>.*?)}"
    output_format = "{name:s} {index:d}:" + "{listvalue:s}"
    
    def __init__(self, name, index, listvalue):
        if isinstance(listvalue, (bytes)):
            listvalue = listvalue.decode()

        if isinstance(listvalue, str):
            listvalue = [[int(v1) for v1 in v.split(":")] for v in listvalue.split(";")]

        super().__init__(name=name, index=index, listvalue=listvalue)

    def to_info_listvalue(self):
        args_list = []
        for item in self.listvalue:
            args_list.append("{:d}:{:d}".format(*item))
        return ";".join(args_list)

class StringTag(GenericTag):
    pattern = "{(?P<name>COMMENT|COPYRIGHT):(?P<value>.*?)}"

class TypeTag(GenericTag):
    pattern = "{(?P<name>TYPE):(?P<magic>.*?),(?P<checksum>.*?)}"
    def __init__(self, name="TYPE", **kwargs):
        super().__init__(name=name, **kwargs)

class LevelOffsetTag(GenericTag):
    pattern = "{(?P<name>LEVEL OFFS):(?P<rms>.*?),(?P<peak>.*?)}"

class IntegerTag(GenericTag):
    pattern = "{(?P<name>CLOCK|SAMPLES|MWV_SEGMENT_COUNT):(?P<value>\d+)}"
        
class DateTag(GenericTag):
    pattern = "{(?P<name>DATE):(?P<date>(?:.*?);(?:.*?))}"
    date_format = "%Y-%m-%d;%H:%M:%S"
    def __init__(self, name, date):
        if isinstance(date, bytes):
            date = date.decode()
        if isinstance(date, str):
            date = dt.strptime(date, self.date_format)
        assert(isinstance(date, dt))
        super().__init__(name=name, date=date)

    def to_info_date(self):
        return dt.strftime(self.date, self.date_format)

class SegmentTag(GenericTag):
    pattern = '{(?P<name>MWV_SEGMENT_(?:LENGTH|START|CLOCK|LEVEL_OFFS|FILES)):(?P<listvalue>(?:.*?)(?:(?:,.*?)*))}'
    def __init__(self, name, listvalue):
        if isinstance(listvalue, bytes):
            listvalue = listvalue.decode()
               
        if isinstance(listvalue, str):
            listvalue = listvalue.split(",")
            try:
                listvalue = [int(v) for v in listvalue]
            except ValueError:
                try:
                    listvalue = [float(v) for v in listvalue]
                except ValueError:
                    pass
                
        assert(isinstance(listvalue, list))
        super().__init__(name=name, listvalue=listvalue)

    def to_file_text_listvalue (self):
        return ",".join(str(a) for a in self.listvalue)

class SegmentClockModeTag(GenericTag):
    pattern = "{(?P<name>MWV_SEGMENT_CLOCK_MODE):\s*?(?P<value>UNCHANGED|HIGHEST|USER)}"
        
class SegmentCommentTag(GenericTag):
    pattern = "{(?P<name>MWM_SEGMENT(?P<index>\d+)_COMMENT):(?P<value>.*?)}"

class CLW4Tag(BinaryTag):
    pattern = "{?P<name>CONTROL LIST WIDTH4-(\d+):#"

class RSParser(object):
    TAGS = (
        LevelOffsetTag,
        WaveformTag,
        EmptyTag,
        StringTag,
        TypeTag,
        IntegerTag,
        DateTag,
        SegmentTag,
        SegmentClockModeTag,
        SegmentCommentTag,
        CLW4Tag,
        IndexTag,
        GenericTag,
    )

    def __init__(self, filename):
        self.filename=filename

    def get_tags(self):
        fd = open(self.filename, "rb")
        content = fd.read()
        fd.close()
        tags = []
        done = False
        while (not done):
            for class_tag in self.TAGS:
                done = True
                ret_val, content = class_tag.match(content)
                if ret_val:
                    tags.append(class_tag(**ret_val))
                    done = False
                    break
        return tags

class RSGenerator(object):
    def __init__(self, tag_list):
        self.tag_list = tag_list

    def generate(self, stream):
        # Checks on tags
        assert(isinstance(self.tag_list[-1], WaveformTag))

        if not isinstance(self.tag_list[0], TypeTag):
            self.tag_list.insert(0, TypeTag(name="TYPE", magic = "SMU-WV", checksum = 0))

        if not isinstance(self.tag_list[-2], EmptyTag):
            # Add empty tag
            self.tag_list.insert(-1, EmptyTag())

        empty_tag = self.tag_list[-2]
        waveform_tag = self.tag_list[-1]
        type_tag = self.tag_list[0]

        # Fix checksum
        type_tag.checksum = waveform_tag.checksum()

        # Fix emptytag size
        size = 0
        for tag in self.tag_list[:-2]:
            size += len(tag.file_output())

        size += len("{EMPTYTAG-00000:")
        empty_spaces = 0x4000 - size - 2 # Two is substracted becase of '#' and '}' characters
        # Take into account cases where the digits are less than 5
        empty_spaces += (5 - len("{:d}".format(empty_spaces)))
        empty_tag.value = empty_spaces

        for tag in self.tag_list:
            stream.write(tag.file_output())

if __name__ == "__main__":
    import time, logging, sys, argparse
    # Parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="R&S waveform file", default = None)
    parser.add_argument("--info", help="print infomation details for the input file", action="store_true", default=False)
    parser.add_argument("--output", help="output filename", default=None)
    parser.add_argument("--debug", help="output debug information", action="store_true", default=False)
    args = parser.parse_args()

    # Init logging system
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING

    logging.basicConfig(level=level)
    log = logging.getLogger('')

    rs=RSParser(args.filename)

    if args.info:
        for tag in rs.get_tags():
            print (tag)

    if args.output:
        gen = RSGenerator(rs.get_tags())
        stream = open(args.output, "wb")
        gen.generate(stream)
        stream.close()
