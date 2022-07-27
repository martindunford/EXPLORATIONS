#! /usr/local/bin/python3

from setup_logger import *
from antlr_plsql import *
from ast import walk
from subprocess import *
import astunparse
import sys

from contextlib import *
# Insert into table1 (TEMPLATE_ID,POS,COLUMN_VALUE,COLUMN_HEADER) values ('2020040717017321',1,'PAY_CODE','Pay Code');
#  FAILS to parse because - I suspect - of the "column_value" Identifier i.e  rename
#   identifier to "column_valu" below and all well !!
#
# NOTE: Very likely related to tokens in the parser i.e
#   antlr_plsql/antlr_py/plsqlLexer.tokens
#         74:COLUMN_VALUE=74
# NOTE1: "position" is also a reserved token so column name matching same
#          will also not parse

will_not_parse = '''
        insert into table3 (column_value) values ('1');
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
            # t1 = ast.parse(will_not_parse)

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