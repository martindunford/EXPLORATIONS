#! /usr/local/bin/python3

from setup_logger import *
from antlr_plsql import *
from ast import walk,dump,iter_child_nodes
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
procedure update_calendar_period (p_company in test_data_pay_group.orgz_ref%type ) is 

    cursor get_current_period is
    select period
    from ct_calendar
    where company = p_company
    and sysdate between start_date and start_date + 6;

    l_current_period number;

    begin

    open get_current_period;
    fetch get_current_period into l_current_period;
    close get_current_period;

    update ct_param set current_period = l_current_period where company = p_company;
    update ct_calendar set completed_ind = 'Y' where company = p_company and period < l_current_period;

end update_calendar_period;

'''

def process_binary_expr(node):
    pylines  = []
    if type(node.left) == ast.Identifier:
        left = node.left.get_text()
    elif type(node.left) == ast.BinaryExpr:
        left = process_binary_expr(node.left)
    if type(node.op) == ast.Terminal:
        op = node.op.get_text()
        if op == '=': op = '=='
    if type(node.right) == ast.Identifier:
        right = node.right.get_text()
    elif type(node.right) == ast.BinaryExpr:
        right = process_binary_expr(node.right)

    return f'{left} {op} {right}'

def process_update (node):
    '''
    :param node:
    :return:
    '''
    pylines = []
    print  (f'{sun}{node.table.fields}')
    for upd in node.updates:
        if type(upd.column) == ast.Identifier:
            print (upd.column.get_text())
        if type(upd.expression) == ast.Identifier:
            print (upd.expression.get_text())

    wclause = node.where_clause
    if type(wclause) == ast.BinaryExpr:
        res = process_binary_expr(wclause)
        print (res)


def process_select(node):
    table_name  = f'{node.from_clause[0].get_text()}'
    select_stmt = f'res = self.find({table_name}).filter(F1).one()'
    pylines = []

    c1 = node.where_clause
    left = c1.left.get_text()
    right = c1.right.get_text()
    op = c1.op.get_text()
    if op == '=':
        op = '=='
    filter = f'F1 = {table_name}.{left} {op} {right}'
    pylines.append(f'   {filter}')
    pylines.append(f'   {select_stmt}')
    try:
        for x,y in zip(node.target_list,node.into_clause):
            cname = x.get_text()
            varname = y.get_text()
            pylines.append(f'   {varname} = res.{cname}')
    except Exception as inst:
        logger.info (f'{cross_mark} {inst}')
        logger.info (f'{cross_mark} {dump(node)}')

    return (pylines)

# TODO: Detect multiple inserts to same table and use for loop
def process_insert(node):
    '''
    :param node:
    :return:
    '''
    pylines = []
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
        pylines.append (f'   {insert_stmt}')
        pylines.append (f'   self.session.execute(ins1)')
        pylines.append (f'   self.session.commit()')

    except Exception as inst:
        logger.info(f'{cross_mark}{inst}')
        logger.info (dump(node))

    return pylines


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
        # doesn't recognize ast.Create_procedure_body as a class type to be compared to
        # (Dynamic class?) , so match the string instead
        if 'Create_procedure_body' in str(t1):
            pname = node.procedure_name.get_text()
            plist = []
            for item in node.parameter:
                plist.append (item.parameter_name.get_text())
            # Generate Python method definition
            print  (f'def {pname}({",".join(plist)}): {sun}')
            for cnode in node.children:
                if 'ast.Body' in str(type(cnode)):
                    for snode in iter_child_nodes(cnode):
                        if type(snode) == ast.SelectStmt:
                            python_code = process_select(snode)
                            for item in python_code:
                                print (item)
                        elif type(snode) == ast.InsertStmt:
                            python_code = process_insert(snode)
                            for item in python_code:
                                print (item)
                        elif type(snode) == ast.UpdateStmt:
                            python_code = process_update(snode)
        else:
            pass

if __name__ == '__main__':
    main()