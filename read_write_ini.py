import re
import future_collections
from copy import deepcopy
from collections import defaultdict

# This regex and part of the read_ini_file are straight from
# python ConfigParser.
# Regular expressions for parsing section headers and options.
#
SECTCRE = re.compile(
    r'\['                                 # [
    r'(?P<header>[^]]+)'                  # very permissive!
    r'\]'                                 # ]
    )
OPTCRE = re.compile(
    r'(?P<option>[^;=\s][^;=]*)'          # very permissive!
    r'\s*(?P<vi>[;=])\s*'                 # any number of space/tab,
                                          # followed by separator
                                          # (either ; or =), followed
                                          # by any # space/tab
    r'(?P<value>.*)$'                     # everything up to eol
    )



def w_ini_file(file_name, data, new_data):
    temp_data = data
    for section, opt_val in new_data.items():
        if section in temp_data.keys():
            if len(new_data[section]) == 0:
                del temp_data[section]
            else:    
                for option, value in opt_val.items():
                    if not value:
                        del temp_data[section][option]
                    else:    
                        no_match=True
                        for k in temp_data[section].keys():
                            if option == k:
                                temp_data[section][k] = value
                                no_match=False
                                break
                        if no_match:
                            temp_data[section][option] = value
        else:
            temp = future_collections.OrderedDict()
            for option, value in opt_val.items():
                temp[option] = value
                temp_data[section] = temp

    with open(file_name, 'w') as out:
        for k,v in temp_data.items():
            out.write('[{0}]\n'.format(k))
            for x,y in v.items():
                out.write('{0}{1}{2}\n'.format(x[0], x[1], y))
            out.write('\n')

class HostInfoChanges(object):
    def __init__(self, file_name=None):
        self.file_name = file_name
        
        def _nested_dict_factory():
            return defaultdict(str)
        
        self.data_dict = defaultdict(_nested_dict_factory)
    
    def setData(self, section, option=None, value=None, delim='='):
        if option:
            self.data_dict[section][(option, delim)] = value
        else:
            self.data_dict[section]

    def read_ini_file(self, file_name):
        with open(file_name, 'r') as fd:
            section = future_collections.OrderedDict()
            while True:
                line = fd.readline()
                if not line:
                    break
                if line.strip() == '' or line[0] in "#":
                    continue
                mo = SECTCRE.match(line)
                if mo:
                    sect_name = mo.group('header')
                    values = future_collections.OrderedDict()
                else:
                    mo = OPTCRE.match(line)
                    if mo:
                        opt, delim, val = mo.group('option', 'vi', 'value')
                        if delim in ('=', ';'):
                            values[(opt, delim)] = val
                    section[sect_name] = values 
                    
            return section

    def write_ini_file(self, file_name, data, new_data):
        for section, opt_val in new_data.items():
            if section in data.keys():
                if len(new_data[section]) == 0:
                    del data[section]
                else:    
                    for option, value in opt_val.items():
                        if not value:
                            del data[section][option]
                        else:    
                            no_match=True
                            for k in data[section].keys():
                                if option == k:
                                    data[section][k] = value
                                    no_match=False
                                    break
                            if no_match:
                                data[section][option] = value
            else:
                temp = future_collections.OrderedDict()
                for option, value in opt_val.items():
                    temp[option] = value
                    data[section] = temp

        with open(file_name, 'w') as out:
            for k,v in data.items():
                out.write('[{0}]\n'.format(k))
                for x,y in v.items():
                    out.write('{0}{1}{2}\n'.format(x[0], x[1], y))
                out.write('\n')

    def execute(self):
        data = self.read_ini_file(self.file_name)
        self.write_ini_file('ini_to_write_to.cfg', data, self.data_dict)


from pprint import pprint
if __name__ == '__main__':
####new_data={'OrderServer1':{('OrderServerIP', '='):'172.31.1.83', 
####                          ('OrderServerPort', '='):'9000'}, 
####          'OrderServer12':{('OrderServerIP', '='):'172.31.2.73'},
####          'NotIniSection':{('FirstOne', ';'):'ValueTwo', 
####                           ('SecondOne', ';'):'z;l;k;j', 
####                           ('ThirdOne',';'):'A;S;D;F'},
####          'NewSection':{('Option1', '='):'value1', 
####                        ('Option2', '='):'value2', 
####                        ('Option3', ';'):'vale3;value4;value5',
####                        ('Option4', '='):'1,2,3,4'},
####          'SpreadRatios':{},
####          'PriceServer':{('PSUser', '='): None}}


   #data = read_ini_file(file_name='ini_to_read_from.cfg')
   #write_ini_file('ini_to_write_to.cfg', data, new_data)


    h1=HostInfoChanges('ini_to_read_from.cfg')
    h1.setData(section='OrderServer1',
               option='OrderServerIP',
               value='172.31.1.83')
    h1.setData(section='OrderServer1',
               option='OrderServerPort',
               value='9000')
    h1.setData(section='OrderServer12', 
               option='OrderServerIP', 
               value='172.31.2.73'),

    h1.setData(section='NotIniSection', option='FirstOne', value='ValueTwo', delim=';')
    h1.setData(section='NotIniSection', option='SecondOne', value='z;l;k;j', delim=';')
    h1.setData(section='NotIniSection', option='ThirdOne', value='A;S;D;F', delim=';')
    h1.setData(section='NewSection', option='Option1', value='value1')
    h1.setData(section='NewSection', option='Option2', value='value2')
    h1.setData(section='NewSection', option='Option3', value='value1;value4', delim=';')
    h1.setData(section='NewSection', option='Option4', value='1,2,3,4,5')
    h1.setData(section='SpreadRatios')
    h1.setData(section='PriceServer', option='PSUser')


    h1.execute()
