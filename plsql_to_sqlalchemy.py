#! /usr/local/bin/python3

from setup_logger import *
from antlr_plsql import *
from ast import walk,dump
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
procedure setGlobals(p_company in test_data_pay_group.orgz_ref%type) is 

begin
    
    select company_prefix1,company_prefix2
    into g_prefix_1, g_prefix_2
    from test_data_pay_group
    where orgz_ref  = p_company;

end setGlobals;
procedure set_employee_menu_options is

begin

    insert into core_menu_group(group_name, system_id, menu_id)
    values('COREPORTAL_EMPLOYEE', 'COCP', 'MAIN_MENU.COREPORTAL_REMOTE_TIMESHEET');

    insert into core_menu_group(group_name, system_id, menu_id)
    values('COREPORTAL_EMPLOYEE', 'COCP', 'MAIN_MENU.EMPTIMESHEETSWEEKCLKS');

    insert into core_menu_group(group_name, system_id, menu_id)
    values('COREPORTAL_EMPLOYEE', 'COCP', 'MAIN_MENU.TIMESHEET_EMP_SUMMARY');

    insert into core_menu_group(group_name, system_id, menu_id)
    values('COREPORTAL_EMPLOYEE', 'COCP', 'MAIN_MENU.TIMESHEET_INPUT_V2_EMPLOYEE');

    insert into core_menu_group(group_name, system_id, menu_id)
    values('COREPORTAL_EMPLOYEE', 'COCP', 'MAIN_MENU.TIMESHEET_INPUT_V2');

    insert into core_menu_group(group_name, system_id, menu_id)
    values('COREPORTAL_EMPLOYEE', 'COCP', 'MAIN_MENU.EMPTIMESHEETS');

end set_employee_menu_options;
'''
def main():
    # lines = open('/Users/martin/CoreHR_Projects/roster/Roster_Test_Suite/CONFIGS/cost_roster_data_setup.bod').read()
    lines = open('/Users/martin/CoreHR_Projects/roster/Roster_Test_Suite/CONFIGS/timesheet_config.bod').read()

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
            # logger.info (node.where_clause)
            # logger.info (node.from_clause)
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
                    logger.info (f'{globe} {type(upd.expression)}')
        elif t1 == ast.InsertStmt:
            try:
                table_name = node.table.get_text()
                cols = []
                vals = []
                item = None
                for item in node.columns:
                    cols.append (item.get_text())
                for item in node.values:
                    if type(item) == list:
                        vals += [x.value for x in item]
                    else:
                        vals.append(item.value)

                iclause = ''
                for cname,val in zip(cols,vals):
                    iclause += f'{cname}={val},'
                iclause = iclause.strip(',')

                insert_stmt = f'ins1 = insert({table_name}).values({iclause})'
                logger.info (f'   {sun} {insert_stmt}')
                logger.info (f'   {sun} self.session.execute(ins1)')
                logger.info (f'   {sun} self.session.commit()')
            except Exception as inst:
                logger.info(f'{cross_mark}{inst}')
                logger.info (dump(node))


        elif t1 == ast.SelectStmt:
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
            try:
                for x,y in zip(node.target_list,node.into_clause):
                    cname = x.get_text()
                    varname = y.get_text()
                    assigns.append(f'{varname} = res.{cname}')
            except Exception as inst:
                logger.info (f'{cross_mark} {inst}')
                logger.info (f'{cross_mark} {dump(node)}')

            for astmt in assigns:
                logger.info (f'{sun} {astmt}')

        # doesn't recognize ast.Create_procedure_body as a class type to be compared to
        # (Dynamic class?) , so match the string instead
        elif 'Create_procedure_body' in str(t1):
            logger.info(dump(node))
            pname = node.procedure_name.get_text()
            plist = []
            for item in node.parameter:
                plist.append (item.parameter_name.get_text())
                # logger.info (item.type_spec.get_text())
            # Generate Python method definition
            logger.info (f'{sun} def {pname}({",".join(plist)}):')
        else:
            pass
            # if t1 == ast.Create_procedure_body:
            #     logger.info (f'{sun}{sun}{sun}{sun}{sun}{sun}')
if __name__ == '__main__':
    main()