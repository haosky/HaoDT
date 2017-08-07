# -*- coding: utf-8 -*-

from haomongodb.mongodbmaster import gxmongo

__author__ = 'hao'

gxmongo_initance = gxmongo()

class odbs_generator:

    _db = None

    def __init__(self):
        self._db = gxmongo_initance.get_odbs()

    def generate(self):
        table_list = self._db.collection_names(include_system_collections=False)
        strs = []
        for table in table_list:
            if 'A'<= table[0] <= 'Z':
               one = self._db[table].find_one()
               if one is not None:
                   keys = one.keys()
                   if len(keys) < 1:
                       continue
                   strs.append('\n\nclass %s():\n' % table)
                   for key in keys :
                       strs.append('    %s = %s ' % (key, 'None'))
        return '\n'.join(strs)


def main_generate():
    file = open('./mongodb_modles.py','wb')
    pycomment = '# -*- coding: utf-8 -*-\n__author__ = \'hao\'\n '
    odbs_generator_str = odbs_generator().generate()
    generate_str = odbs_generator_str
    file.write(pycomment+generate_str)
    file.close()
    return 'success'


if __name__ == '__main__':
   print  main_generate()
