import xml.etree.ElementTree as ET
import sys


class PythonNode:
    def __init__(self, text, indent_level):
        self.text = text
        self.indent_level = indent_level


def print_python_node_list(python_node_list):
    for pn in python_node_list:
        print("    " * pn.indent_level + pn.text)


def write_python_node_list(python_node_list, output_path):
    f = open(output_path, 'w')
    for pn in python_node_list:
        print("    " * pn.indent_level + pn.text, file=f)
    f.close()


def surround_quote(text):
    return "\"" + text + "\""


def get_variant(statement):
    return statement.attrib['variant']


def print_error_message(variant, location):
    # We should have this stop the compiling process
    print("ERROR: variant number:", variant, " is invalid at the location", location)


# ==== program generation ====

# returns list of statement_nodes
def codegen_program(program_xml):
    indent_level = 0
    python_nodes_list = [PythonNode("from PMap import *", indent_level)]
    # contains basic import for PMap class. Necessary for generated python script to compile

    variant = get_variant(program_xml)
    if variant != '0':
        print_error_message(variant, "program")
        return

    actor_decleration_block_nodes = \
        codegen_actor_declaration_block(program_xml.find("actor_declaration_block"), indent_level)
    map_option_block_nodes = \
        codegen_map_option_declaration_opt(program_xml.find("map_option_declaration_opt"), indent_level)
    mapgen_definition_block_nodes = \
        codegen_mapgen_definition(program_xml.find("mapgen_definition"), indent_level)
    function_definitions_block_nodes = \
        codegen_function_definitions_opt(program_xml.find("function_definitions_opt"), indent_level)

    python_nodes_list.extend(actor_decleration_block_nodes)
    python_nodes_list.extend(map_option_block_nodes)
    python_nodes_list.extend(mapgen_definition_block_nodes)
    python_nodes_list.extend(function_definitions_block_nodes)

    return python_nodes_list


# ==== actor declaration generation ====
def codegen_actor_declaration_block(actor_declaration_block_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(actor_declaration_block_xml)
    if variant != '0':
        print_error_message(variant, "actor_declaration_block")
        return python_nodes_list

    actor_declarations_xml = actor_declaration_block_xml.find("actor_declarations")
    python_nodes_list.extend(codegen_actor_declarations(actor_declarations_xml, indent_level))

    return python_nodes_list


def codegen_actor_declarations(actor_declarations_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(actor_declarations_xml)
    if variant == '0':  # actor_declaration:ad
        child_actor_declaration = actor_declarations_xml.find("actor_declaration")
        python_nodes_list.extend(codegen_actor_declaration(child_actor_declaration, indent_level))

    elif variant == '1':  # actor_declarations:ad1 actor_declaration:ad2
        child_actor_declarations = actor_declarations_xml.find("actor_declarations")
        child_actor_declaration = actor_declarations_xml.find("actor_declaration")

        python_nodes_list.extend(codegen_actor_declarations(child_actor_declarations, indent_level))
        python_nodes_list.extend(codegen_actor_declaration(child_actor_declaration, indent_level))
    else:
        print_error_message(variant, "actor_declarations")

    return python_nodes_list


def codegen_actor_declaration(actor_declaration_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(actor_declaration_xml)
    if variant != '0':
        print_error_message(variant, "actor_declaration")
        return python_nodes_list

    # IDENTIFIER:ident EQ CHARACTER_LITERAL:charl SEMICOLON
    ident = actor_declaration_xml.find("ident")
    charl = actor_declaration_xml.find("charl")

    code_text = ident.text + " = " + surround_quote(charl.text)
    python_nodes_list.append(PythonNode(code_text, indent_level))
    return python_nodes_list


# ==== map options optional ====
def codegen_map_option_declaration_opt(map_option_declaration_opt_xml, indent_level):
    # map_options = {id: id, id: id}
    map_option_dict = "map_options = {"
    variant = get_variant(map_option_declaration_opt_xml)
    if variant == '0':  # MAPOPTIONSDECL LBRACE map_option_declarations:ads RBRACE
        child_map_option_declarations = map_option_declaration_opt_xml.find("map_option_declarations")
        map_option_dict += codegen_map_option_declarations(child_map_option_declarations)
    elif variant == '1':  # | ;
        pass  # declaration doesn't exist; do nothing
    else:
        print_error_message(variant, "map_option_declaration_opt")

    map_option_dict += "}"
    return [PythonNode(map_option_dict, indent_level)]


def codegen_map_option_declarations(map_option_declarations_xml):
    map_option_dict_inside = ""

    variant = get_variant(map_option_declarations_xml)
    if variant == '0':  # map_option_declaration:mod
        map_option_dict_inside += \
            codegen_map_option_declaration(map_option_declarations_xml.find("map_option_declaration"))
    elif variant == '1':  # map_option_declarations:mods map_option_declaration:mod
        child_map_option_declarations_xml = map_option_declarations_xml.find("map_option_declarations")
        child_map_option_declaration_xml = map_option_declarations_xml.find("map_option_declaration")

        map_option_dict_inside += codegen_map_option_declarations(child_map_option_declarations_xml) + ", "
        map_option_dict_inside += codegen_map_option_declaration(child_map_option_declaration_xml)
    else:
        print_error_message(variant, "map_option_declaration_opt")

    return map_option_dict_inside


def codegen_map_option_declaration(map_option_declaration_xml):
    variant = get_variant(map_option_declaration_xml)

    map_option_declaration = ""
    if variant == '0':  # IDENTIFIER:lident EQ IDENTIFIER:rident SEMICOLON
        map_option_declaration += surround_quote(map_option_declaration_xml.find("lident").text) + " : " + \
                                  map_option_declaration_xml.find("rident").text
    elif variant == '1':  # IDENTIFIER:lident EQ LBRACK comma_identifiers:ridents RBRACK SEMICOLON
        map_option_declaration += surround_quote(map_option_declaration_xml.find("lident").text) + " : " + \
                                  "[" + \
                                  codegen_comma_identifiers(map_option_declaration_xml.find("comma_identifiers")) + \
                                  "]"
    else:
        print_error_message(variant, "map_option_declaration")

    return map_option_declaration


def codegen_comma_identifiers(comma_identifiers_xml):
    variant = get_variant(comma_identifiers_xml)
    comma_id = ""
    if variant == '0':  # IDENTIFIER:ident
        comma_id += comma_identifiers_xml.find("ident").text
    elif variant == '1':  # comma_identifiers:idents COMMA IDENTIFIER:ident ;
        comma_id += codegen_comma_identifiers(comma_identifiers_xml.find("comma_identifiers")) + ", " + \
                    comma_identifiers_xml.find("ident").text
    else:
        print_error_message(variant, "comma_identifiers")

    return comma_id


# === mapgen def====
def codegen_mapgen_definition(mapgen_definition_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(mapgen_definition_xml)
    if variant != '0':
        print_error_message(variant, "mapgen_definition")
        return python_nodes_list
    # MAP GENERATOR LPAREN RPAREN statements_block:sb

    python_nodes_list.append(PythonNode("def generator():", 0))

    statements_block_xml = mapgen_definition_xml.find("statements_block")
    python_nodes_list.extend(codegen_statements_block(statements_block_xml, indent_level))

    return python_nodes_list


# === function def ====
def codegen_function_definitions_opt(function_definitions_opt_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(function_definitions_opt_xml)
    if variant == '0':  # function_definitions:fundefs
        function_definitions_xml = function_definitions_opt_xml.find("function_definitions")
        python_nodes_list.extend(codegen_function_definitions(function_definitions_xml, indent_level))
    elif variant == '1':  # | ;
        return python_nodes_list
    else:
        print_error_message(variant, "function_definitions_opt")

    return python_nodes_list


def codegen_function_definitions(function_definitions_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(function_definitions_xml)
    if variant == '0':  # function_definition:fundef
        function_definition = function_definitions_xml.find("function_definition")
        python_nodes_list.extend(codegen_function_definition(function_definition, indent_level))
    elif variant == '1':  # function_definitions:fundefs function_definition:fundef
        function_definitions = function_definitions_xml.find("function_definitions")
        function_definition = function_definitions_xml.find("function_definition")
        python_nodes_list.extend(codegen_function_definitions(function_definitions, indent_level))
        python_nodes_list.extend(codegen_function_definition(function_definition, indent_level))
    else:
        print_error_message(variant, "function_definitions")

    return python_nodes_list


def codegen_function_definition(function_definition_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(function_definition_xml)
    if variant == '0':  # type:t IDENTIFIER:ident LPAREN function_parameters_opt:funparamsopt RPAREN statements_block:sb
        ident = function_definition_xml.find("ident")
        function_parameters_opt = function_definition_xml.find("function_parameters_opt")
        statements_block = function_definition_xml.find("statements_block")
        function_decl_text = "def " + ident.text + \
                             "(" + codegen_function_parameters_opt(function_parameters_opt) + "):"

        python_nodes_list.append(PythonNode(function_decl_text, indent_level))
        python_nodes_list.extend(codegen_statements_block(statements_block, indent_level))

    elif variant == '1':  # VOID:t IDENTIFIER:ident LPAREN function_parameters_opt:funparamsopt RPAREN statements_block:sb
        ident = function_definition_xml.find("ident")
        function_parameters_opt = function_definition_xml.find("function_parameters_opt")
        statements_block = function_definition_xml.find("statements_block")
        function_decl_text = "def " + ident.text + \
                             "(" + codegen_function_parameters_opt(function_parameters_opt) + "):"

        python_nodes_list.append(PythonNode(function_decl_text, indent_level))
        python_nodes_list.extend(codegen_statements_block(statements_block, indent_level))
    else:
        print_error_message(variant, "function_definition")

    return python_nodes_list


def codegen_function_parameters_opt(function_parameters_opt_xml):
    variant = get_variant(function_parameters_opt_xml)
    if variant == '0':  # function_parameters:funparams
        function_parameters_xml = function_parameters_opt_xml.find("function_parameters")
        return codegen_function_parameters(function_parameters_xml)
    elif variant == '1':  # | ;
        return ""
    else:
        print_error_message(variant, "function_parameters_opt")

    return "function_parameters_opt_NotYetImplemented"


def codegen_function_parameters(function_parameters_xml):
    variant = get_variant(function_parameters_xml)
    if variant == '0':  # function_parameter:funparam
        child_function_parameter_xml = function_parameters_xml.find("function_parameter")
        return codegen_function_parameter(child_function_parameter_xml)
    elif variant == '1':  # function_parameters:funparams COMMA function_parameter:funparam
        child_function_parameters_xml = function_parameters_xml.find("function_parameters")
        child_function_parameter_xml = function_parameters_xml.find("function_parameter")

        return codegen_function_parameters(child_function_parameters_xml) + ", " + \
               codegen_function_parameter(child_function_parameter_xml)
    else:
        print_error_message(variant, "function_parameters_opt")
    return "codegen_function_parameters_error"


def codegen_function_parameter(function_parameter_xml):
    variant = get_variant(function_parameter_xml)
    if variant == '0':  # type:t IDENTIFIER:ident
        ident = function_parameter_xml.find("ident")
        return ident.text
    else:
        print_error_message(variant, "function_parameter")
    return "codegen_function_parameter_error"


# === statements ====
def codegen_statements_block(statements_block_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(statements_block_xml)
    if variant != '0':
        print_error_message(variant, "statements_block")
        return python_nodes_list

    # LBRACE statements:s RBRACE;
    statements_xml = statements_block_xml.find("statements")
    python_nodes_list.extend(codegen_statements(statements_xml, indent_level + 1))
    # since this is tatement block, child nodes needs to be indented

    return python_nodes_list


def codegen_statements(statements_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(statements_xml)
    if variant == '0':  # statement:stmt
        child_statement_xml = statements_xml.find("statement")
        python_nodes_list.extend(codegen_statement(child_statement_xml, indent_level))
    elif variant == '1':  # statements:stmts statement:stmt
        child_statements_xml = statements_xml.find("statements")
        child_statement_xml = statements_xml.find("statement")
        python_nodes_list.extend(codegen_statements(child_statements_xml, indent_level))
        python_nodes_list.extend(codegen_statement(child_statement_xml, indent_level))
    else:
        print_error_message(variant, "statements")
    return python_nodes_list


def codegen_return_statement(return_statement_xml, indent_level):
    variant = get_variant(return_statement_xml)
    return_text = "return"
    if variant == '0':  # RETURN expression:expr SEMICOLON
        child_expression_xml = return_statement_xml.find("expression")
        return_text += " " + codegen_expression(child_expression_xml)
    elif variant == '1':  # RETURN SEMICOLON
        pass  # no need to do anything
    else:
        print_error_message(variant, "return_statement")
        return []

    return [PythonNode(return_text, indent_level)]


def codegen_function_call_statement(function_call_statement_xml, indent_level):
    variant = get_variant(function_call_statement_xml)
    if variant != '0':
        print_error_message(variant, "codegen_function_call_statement")
        return []
    else:
        return [PythonNode(codegen_function_call(function_call_statement_xml.find('function_call')), indent_level)]


def codegen_argument_list(argument_list_xml):
    text = ""
    variant = get_variant(argument_list_xml)
    if (variant == '0'):
        return codegen_expression(argument_list_xml.find('expression'))
    elif (variant == '1'):
        text = codegen_argument_list(argument_list_xml.find('argument_list')) + ',' + codegen_expression(
            argument_list_xml.find('expression'))
    else:
        print_error_message(variant, "argument_list")

    return text


def codegen_argument_list_opt(argument_list_opt_xml):
    text = ""
    variant = get_variant(argument_list_opt_xml)
    if variant == '0':
        # argument_list:al
        argument_list_xml = argument_list_opt_xml.find('argument_list')
        text = codegen_argument_list(argument_list_xml)
        pass
    elif variant == '1':
        # empty string
        pass
    else:
        print_error_message(variant, "argument_list_opt")
    return text


# implement variant one
def codegen_function_call(function_call_xml):
    variant = get_variant(function_call_xml)
    python_function_call_text = ""
    if variant == '0':
        # IDENTIFIER:ident LPAREN argument_list_opt:alo RPAREN
        text_ident = function_call_xml.find("ident").text
        text_arg_opt = codegen_argument_list_opt(function_call_xml.find('argument_list_opt'))
        return text_ident + "(" + text_arg_opt + ")"
    elif variant == '1':
        # MAP LPAREN expression COMMA expression RPAREN
        child_expression_xmls = function_call_xml.findall("expression")
        return "PMap(" + codegen_expression(child_expression_xmls[0]) + ", " + \
               codegen_expression(child_expression_xmls[1]) + ")"
    else:
        print_error_message(variant, "function_call")
    return python_function_call_text


# Finished
def codegen_break_statement(break_statement_xml, indent_level):
    variant = get_variant(break_statement_xml)
    if variant != '0':
        print_error_message(variant, "break_statement")
        return []
    return [PythonNode("break", indent_level)]


def codegen_map_assignment_statement(map_assignment_statement_xml, indent_level):
    variant = get_variant(map_assignment_statement_xml)
    if variant != '0':
        print_error_message(variant, "map_assignment_statement")
        return []

    # map_assignment_access:maa EQ expression:expr SEMICOLON
    map_assignment_access_xml = map_assignment_statement_xml.find("map_assignment_access")
    map_ident_text, assignment_argument_text = codegen_parse_map_assignment_access(map_assignment_access_xml)

    child_right_expression_xml = map_assignment_statement_xml.find("expression")
    child_right_expression_text = codegen_expression(child_right_expression_xml)

    map_assignment_line = \
        map_ident_text + ".assign(" + assignment_argument_text + ", " + child_right_expression_text + ")"

    return [PythonNode(map_assignment_line, indent_level)]


def codegen_parse_map_assignment_access(map_assignment_access_xml):
    """
        return  (map_id, "[y], [x]") if map_assignment_expression's variant == '0';
                (map_id, "[y1, y2], [x1, x2]") if map_assignment_expression's variant == '1'
    """
    variant = get_variant(map_assignment_access_xml)
    if variant != '0':
        print_error_message(variant, "map_assignment_access")
        return []
    # IDENTIFIER:ident LBRACK map_assignment_expression:maexpr1 RBRACK LBRACK map_assignment_expression:maexpr2 RBRACK
    ident_text = map_assignment_access_xml.find("ident").text
    map_expression_xmls = map_assignment_access_xml.findall("map_assignment_expression")
    return ident_text, codegen_map_assignment_expression(map_expression_xmls[0]) + ", " + \
           codegen_map_assignment_expression(map_expression_xmls[1])


def codegen_map_assignment_expression(map_assignment_expression_xml):
    """
        return  "[expr]" if map_assignment_expression's variant == '0';
                "[expr1, expr2]" if map_assignment_expression's variant == '1'
    """
    variant = get_variant(map_assignment_expression_xml)
    if variant == '0':  # expression:expr
        child_expression_xml = map_assignment_expression_xml.find("expression")
        return "[" + codegen_expression(child_expression_xml) + "]"
    elif variant == '1':  # expression:expr1 COLON expression:expr2
        child_expression_xmls = map_assignment_expression_xml.findall("expression")
        return "[" + codegen_expression(child_expression_xmls[0]) + ", " + \
               codegen_expression(child_expression_xmls[1]) + "]"
    else:
        print_error_message(variant, "map_expression")


def codegen_statement(statement_xml, indent_level):
    variant = get_variant(statement_xml)
    if variant == '0':  # variable_declaration:vd
        sub_statement_xml = statement_xml.find("variable_declaration")
        return codegen_variable_declaration(sub_statement_xml, indent_level)
    elif variant == '1':  # assignment_statement:as
        sub_statement_xml = statement_xml.find("assignment_statement")
        return codegen_assignment_statement(sub_statement_xml, indent_level)
    elif variant == '2':  # if_statement:ifs
        sub_statement_xml = statement_xml.find("if_statement")
        return codegen_if_statement(sub_statement_xml, indent_level)
    elif variant == '3':  # while_statement:whiles
        sub_statement_xml = statement_xml.find("while_statement")
        return codegen_while_statement(sub_statement_xml, indent_level)
    elif variant == '4':  # return_statement:rets
        sub_statement_xml = statement_xml.find("return_statement")
        return codegen_return_statement(sub_statement_xml, indent_level)
    elif variant == '5':  # function_call_statement:fcs
        sub_statement_xml = statement_xml.find("function_call_statement")
        return codegen_function_call_statement(sub_statement_xml, indent_level)
    elif variant == '6':  # break_statement:brks
        sub_statement_xml = statement_xml.find("break_statement")
        return codegen_break_statement(sub_statement_xml, indent_level)
    elif variant == '7':  # map_assignment_statement:mas
        sub_statement_xml = statement_xml.find("map_assignment_statement")
        return codegen_map_assignment_statement(sub_statement_xml, indent_level)
    else:
        print_error_message(variant, "statement")

    return []


def codegen_assignment_statement(assignment_statement_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(assignment_statement_xml)
    assignment_statement_line = ""
    if variant == '0':  # IDENTIFIER:ident assignment_operator:assignop expression:expr SEMICOLON
        ident = assignment_statement_xml.find('ident')
        assignment_op_xml = assignment_statement_xml.find('assignment_operator')
        expr_xml = assignment_statement_xml.find('expression')
        assignment_node = PythonNode(ident.text + codegen_assignment_operator(assignment_op_xml) +
                                     codegen_expression(expr_xml), indent_level)
        python_nodes_list.append(assignment_node)
    else:
        print_error_message(variant, "assignment_statement")

    return python_nodes_list


def codegen_variable_declaration(variable_declaration_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(variable_declaration_xml)
    variable_declaration_line = ""
    if variant == '0':  # type:t IDENTIFIER:ident SEMICOLON
        pass  # in python, there is no need to declare variable without assignment
    elif variant == '1':  # type:t IDENTIFIER:ident EQ expression:expr SEMICOLON
        ident = variable_declaration_xml.find("ident")
        child_expression_xml = variable_declaration_xml.find("expression")
        variable_declaration_line += ident.text + " = " + codegen_expression(child_expression_xml)
        python_nodes_list.append(PythonNode(variable_declaration_line, indent_level))
    else:
        print_error_message(variant, "variable_declaration")

    return python_nodes_list


def codegen_while_statement(while_statement_xml, indent_level):
    python_nodes_list = []
    variant = get_variant(while_statement_xml)
    if variant != '0':
        print_error_message(variant, "while_statement")
        return []

    # WHILE LPAREN expression:expr RPAREN statements_block:sb
    expression_xml = while_statement_xml.find("expression")
    statements_block = while_statement_xml.find("statements_block")
    while_text = "while (" + codegen_expression(expression_xml) + "):"
    python_nodes_list.append(PythonNode(while_text, indent_level))
    python_nodes_list.extend(codegen_statements_block(statements_block, indent_level))

    return python_nodes_list


def codegen_if_statement(if_statement_xml, indent_level):
    python_nodes_list = []

    variant = get_variant(if_statement_xml)
    if variant == '0':
        # IF LPAREN expression:expr RPAREN statements_block:sb
        expression_xml = if_statement_xml.find("expression")
        statements_block = if_statement_xml.find("statements_block")
        if_text = "if (" + codegen_expression(expression_xml) + "):"
        python_nodes_list.append(PythonNode(if_text, indent_level))
        python_nodes_list.extend(codegen_statements_block(statements_block, indent_level))
    elif variant == '1':
        # IF LPAREN expression:expr RPAREN statements_block:sb1 ELSE statements_block:sb2
        expression_xml = if_statement_xml.find("expression")
        statements_blocks = if_statement_xml.findall("statements_block")
        if_text = "if (" + codegen_expression(expression_xml) + "):"
        else_text = "else:"
        if_node = PythonNode(if_text, indent_level)
        else_node = PythonNode(else_text, indent_level)
        if_block_node = codegen_statements_block(statements_blocks[0], indent_level)
        else_block_node = codegen_statements_block(statements_blocks[1], indent_level)
        python_nodes_list.append(if_node)
        python_nodes_list.extend(if_block_node)
        python_nodes_list.append(else_node)
        python_nodes_list.extend(else_block_node)
    else:
        # somethin' screwed up
        print_error_message(variant, "if_statement")

    return python_nodes_list


def codegen_expression(expression_xml):
    variant = get_variant(expression_xml)
    if variant == '0':  # IDENTIFIER:ident1 DOT IDENTIFIER:ident2
        ident1 = expression_xml.find("ident1")
        ident2 = expression_xml.find("ident2")
        return ident1.text + "." + ident2.text
    elif variant == '1':  # expression:expr1 binary_operator:binop expression:expr2
        expressions_xmls = expression_xml.findall("expression")
        binary_ops_xml = expression_xml.find("binary_operator")

        return codegen_expression(expressions_xmls[0]) + codegen_binary_operator(binary_ops_xml) + \
               codegen_expression(expressions_xmls[1])

    elif variant == '2':  # unary_operator:unaryop expression:expr
        unary_op_xml = expression_xml.find("unary_operator")
        child_expression_xml = expression_xml.find("expression")
        # maybe wrap this in brackets to make sure order of operations is preserved?
        return codegen_unary_operator(unary_op_xml) + codegen_expression(child_expression_xml)

    elif variant == '3':  # INTEGER_LITERAL:intl
        integer_literal_xml = expression_xml.find("intl")
        return integer_literal_xml.text
    elif variant == '4':  # BOOLEAN_LITERAL:booll
        boolean_literal_xml = expression_xml.find("booll")
        if (boolean_literal_xml == "true"):
            return "True"
        elif (boolean_literal_xml == "false"):
            return "False"
    elif variant == '5':  # IDENTIFIER:ident
        child_ident_xml = expression_xml.find("ident")
        return child_ident_xml.text
    elif variant == '6':  # map_simple_access:mapsa
        map_simple_access_xml = expression_xml.find("map_simple_access")
        return codegen_map_simple_access(map_simple_access_xml)
    elif variant == '7':  # function_call:funcall
        child_function_call_xml = expression_xml.find("function_call")
        return codegen_function_call(child_function_call_xml)
    elif variant == '8':  # LPAREN expression:expr RPAREN
        child_expression_xml = expression_xml.find("expression")
        return "(" + codegen_expression(child_expression_xml) + ")"
    else:
        print_error_message(variant, "expression")

    return " expression_error "


def codegen_map_simple_access(map_simple_access_xml):
    variant = get_variant(map_simple_access_xml)
    if variant != '0':
        print_error_message(variant, "map_simple_access")
        return []

    # IDENTIFIER:ident LBRACK expression:expr1 RBRACK LBRACK expression:expr2 RBRACK
    ident_text = map_simple_access_xml.find("ident").text
    expression_xmls = map_simple_access_xml.findall("expression")

    return ident_text + ".get(" + codegen_expression(expression_xmls[0]) + ", " + \
           codegen_expression(expression_xmls[1]) + ")"


def codegen_unary_operator(unary_operator_xml):
    variant = get_variant(unary_operator_xml)
    if variant == '0':  # NOT
        return " not "
    elif variant == '1':  # MINUS (integer negative)
        return "-"
    else:
        print_error_message(variant, "unary_operator")


def codegen_assignment_operator(assignment_operator_xml):
    variant = get_variant(assignment_operator_xml)
    if variant == '0':  # EQ
        return " = "
    elif variant == '1':  # MULTEQ
        return " *= "
    elif variant == '2':  # DIVEQ
        return " /= "
    elif variant == '3':  # MODEQ
        return " %= "
    elif variant == '4':  # PLUSEQ
        return " += "
    elif variant == '5':  # MINUSEQ
        return " -= "
    else:
        print_error_message(variant, "assignment_operator")

    return " assignment_operator_error "


def codegen_binary_operator(binary_operator_xml):
    variant = get_variant(binary_operator_xml)
    if variant == '0':  # GT
        return " > "
    elif variant == '1':  # LT
        return " < "
    elif variant == '2':  # EQEQ
        return " == "
    elif variant == '3':  # LTEQ
        return " <= "
    elif variant == '4':  # GTEQ
        return " >= "
    elif variant == '5':  # NOTEQ
        return " != "
    elif variant == '6':  # ANDAND
        return " and "
    elif variant == '7':  # OROR
        return " or "
    elif variant == '8':  # PLUS
        return " + "
    elif variant == '9':  # MINUS
        return " - "
    elif variant == '10':  # MULT
        return " * "
    elif variant == '11':  # DIV
        return " / "
    elif variant == '12':  # MOD
        return " % "
    else:
        print_error_message(variant, "binary_operator")

    return " binary_operator_error "


def generate_python_code_from_xml_file(xml_path, layout_output_path, int_out_name):
    """
    :param xml_path: path to xml intermediate syntax tree repr.
    :param layout_output_path: path where final map.lay should be
    :return path to intermediate python code that can just be launched to generate layout in layout_output_path:
    :param int_out_name: some string to identify the intermediate output (for testing)
    """
    intermediate_output = int_out_name + ".py"

    tree = ET.parse(xml_path)
    root = tree.getroot()
    # program is always at index 0, but search anyway
    program_et = root.find('program')

    # map def is non optional and always at index 1
    python_node_list = codegen_program(program_et)

    python_node_list.append(PythonNode("generator().write_lay_file(" + surround_quote(layout_output_path) + ")", 0))

    write_python_node_list(python_node_list, intermediate_output)
    return intermediate_output


if __name__ == "__main__":
    # path to xml, path to output file, intermediate name
    generate_python_code_from_xml_file(sys.argv[1], sys.argv[2], sys.argv[3])
