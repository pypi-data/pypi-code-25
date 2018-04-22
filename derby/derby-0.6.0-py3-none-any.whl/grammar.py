grammar = """
?start: roll

roll: group
    | "(" group ")" mod*

group: dice+
dice: number "d"i number mod*

mod: op number
op: "+" -> add
   | "-" -> sub
   | "l" -> low
   | "h" -> high

number: INT

%import common.INT
%import common.WS
%ignore WS
"""
