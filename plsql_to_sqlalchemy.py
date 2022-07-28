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

pl1 = '''
procedure setGlobals(p_company in test_data_pay_group.orgz_ref%type,
                     p_manager in varchar2) is 

begin
	select company_prefix1,company_prefix2
	into g_prefix_1, g_prefix_2
	from test_data_pay_group
	where orgz_ref  = p_company;

	select p_manager,
		   forename,
		   surname
	into
	g_manager,
	g_manager_forname,
	g_manager_surname
	from hr_person
	where personnel_no = p_manager;

end setGlobals;

'''
def main():
    # lines = open('/Users/martin/CoreHR_Projects/roster/Roster_Test_Suite/CONFIGS/cost_roster_data_setup.bod').read()
    lines = open('/Users/martin/CoreHR_Projects/roster/Roster_Test_Suite/CONFIGS/timesheet_config.bod').read()

    # t1 = ast.parse(plsql1)

    # Generates huge lines of error output in parsing..just want to see what line is not parsing !!
    #  so use the contextlib to send stderr to help.txt file !!

    os.system ('rm -f stderr.txt')
    with open('stderr.txt', 'w') as f:
        with redirect_stderr(f):
            # t1 = ast.parse(lines)
            t1 = ast.parse(pl1)
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

        elif t1 == ast.SelectStmt:
            for clause in [node.target_list, node.from_clause, node.into_clause]:
                logger.info (f'{tick}{type(clause)}')
                for item in clause:
                    logger.info (item.get_text())
            table_name  = f'{node.from_clause[0].get_text()}'
            select_stmt = f'res = self.find({table_name}).filter(F1).one()'

            c1 = node.where_clause
            left = c1.left.get_text()
            right = c1.right.get_text()
            op = c1.op.get_text()
            if op == '=':
                op = '=='
            filter = f'F1 = {table_name}.{left} {op} {right}'
            logger.info (f'{sun} {filter}')
            logger.info (f'{sun} {select_stmt}')

            assigns = []
            for x,y in zip(node.target_list,node.into_clause):
                cname = x.get_text()
                varname = y.get_text()
                assigns.append(f'{varname} = res.{cname}')
            for astmt in assigns:
                logger.info (f'{sun} {astmt}')



        # doesn't recognize ast.Create_procedure_body as a class type to be compared to
        # (Dynamic class?) , so match the string instead
        elif 'Create_procedure_body' in str(t1):
            pname = node.procedure_name.get_text()
            plist = []
            for item in node.parameter:
                plist.append (item.parameter_name.get_text())
                # logger.info (item.type_spec.get_text())
            # Generate Python method definition
            logger.info (f'{sun} def {pname}({",".join(plist)}):')
        else:
            logger.info (t1)
            # if t1 == ast.Create_procedure_body:
            #     logger.info (f'{sun}{sun}{sun}{sun}{sun}{sun}')
if __name__ == '__main__':
    main()