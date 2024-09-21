import json

class configparser_multi(object):

    def __init__(self):

        '''
        ------------------------------------------------------------------
        Call class constructor and initialize default values
        ------------------------------------------------------------------
        '''

        self.config_sections = {}

    def add_section(self, sec_name):

        '''
        ------------------------------------------------------------------
        Add config section
        ------------------------------------------------------------------
        '''

        self.config_sections[sec_name] = {}

    def add_subsection(self, ssec_name, parent_section):

        '''
        ------------------------------------------------------------------
        Add config section subsection
        ------------------------------------------------------------------
        '''

        self.config_sections[parent_section].update({ ssec_name : {} })

    def add_items(self, section, key, item):
        for k, it in zip(key, item):
            section[k] = it

    def read(self, file_name):
        
        with open(file_name, 'r') as myfile:
            data = myfile.readlines()
        myfile.close()

        congig_file = {}
        name = ' '
        
        for i, line in enumerate(data):
            if line[0] != '\n':
                if line[0] == "[":
                    config_temp = {}
                    name = line.strip('\n').replace('[', '').replace(']', '')
                else:
                    tmp = line.strip('\n').split(" = ")
                    config_temp[tmp[0]] = json.loads(tmp[1])
                congig_file[name] = config_temp

        self.config_file = congig_file

    def write(self, file_name):
        
        with open(file_name, 'w') as myfile:
            for key, item in self.config_sections.items():
                myfile.write("[{0}]\n".format(key))
                for k, it in item.items():
                    myfile.write("{0} = {1}\n".format(k, json.dumps(it)))
        myfile.close()

