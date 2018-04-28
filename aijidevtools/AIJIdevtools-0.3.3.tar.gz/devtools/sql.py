import sqlparse as sp


def update_or_delete_to_select(statement):
    return 'SELECT * FROM ' + \
           str(list(filter(
               lambda x: isinstance(x, sp.sql.Identifier),
               statement))[0])\
           + ' ' + \
           str(list(filter(
               lambda x: isinstance(x, sp.sql.Where),
               statement))[-1])


# Input a sql
# Return a select only SQL list
def selectify(sentence: str):
    for statement in sp.parse(sentence):
        if statement.get_type() in ['UPDATE', 'DELETE']:
            yield update_or_delete_to_select(statement)


a = selectify('update eee where id = 4; update aaa where id =4')
print(list(a))