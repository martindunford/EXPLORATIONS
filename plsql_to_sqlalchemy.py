#! /usr/local/bin/python3

from setup_logger import *
from antlr_plsql import *
from ast import walk
from subprocess import *
import astunparse
import sys

from contextlib import *

plsql1 = '''
        update ct_advanced_option  set enabled = 'Y'where company = p_company and option_name = 'LEAVE REQUEST PROCESSES';
        Insert into ct_advanced_option (COMPANY,OPTION_NAME,ENABLED) values (p_company,'LEAVE REQUEST PROCESSES','Y');
'''

plsql1 = '''
        update ct_advanced_option  set enabled = 'Y',martin = 100 ;
        Insert into ct_advanced_option (COMPANY,OPTION_NAME,ENABLED) values (p_company,'LEAVE REQUEST PROCESSES','Y');
        '''

def main():
    lines = open('/Users/martin/CoreHR_Projects/roster/Roster_Test_Suite/CONFIGS/cost_roster_data_setup.bod').read()

    # t1 = ast.parse(plsql1)

    # Generates huge lines of error output in parsing..just want to see what line is not parsing !!
    #  so use the contextlib to send stderr to help.txt file !!
    os.system ('rm -f stderr.txt')
    with open('stderr.txt', 'w') as f:
        with redirect_stderr(f):
            t1 = ast.parse(lines)



    # See: https://github.com/datacamp/antlr-plsql/blob/master/antlr_plsql/ast.py
    for node in walk(t1):
        t1 = type(node)
        if t1 == ast.UpdateStmt:
            logger.info (f'{sun}{node.table.fields}')
            # print (node.where_clause)
            # print (node.from_clause)
            for upd in node.updates:
                logger.info (f'   {upd.column.fields}')
                if type(upd.expression) == list:
                    # logger.info (f'{tick}{type(upd.expression)}')
                    logger.info (f'   {upd.expression}')
                elif type(upd.expression) == ast.Terminal:
                    logger.info (f'{upd.expression.get_text()}')
                elif type(upd.expression) == ast.Call:
                    logger.info (f'{tick}{upd.expression.name}{upd.expression.args}')
                elif type(upd.expression) == ast.BinaryExpr:
                    expr1 = upd.expression
                    logger.info (f'{tick}{type(expr1.left)}{type(expr1.op)}{type(expr1.right)}')
                else:
                    logger.info (f'{cross_mark} {type(upd.expression)}')



if __name__ == '__main__':
    main()