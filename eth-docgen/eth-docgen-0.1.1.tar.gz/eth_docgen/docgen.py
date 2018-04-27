from yattag import Doc
import os, pathlib, shutil, subprocess, sys
import json, re
import pkg_resources
from cgi import escape

def deconstruct_pragma(pragma):
    if pragma[0] == 'solidity':
        version = ''.join(pragma[2:])
        if pragma[1] == '^':
            return [pragma[0], 'Solidity version must be greater than {}'.format(version)]

def make_js(line, abi, source, bytecode):
    line('script', """
        function copyToClipboard(text) {{
            var textArea = document.getElementById('__doc_copy');
            if(!textArea) {{
                textArea = document.createElement("textarea");
                textArea.setAttribute('id', '__doc_copy');
            document.body.appendChild(textArea);
            }}
            textArea.value = text;
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
        }}
        function copyOnClick(text) {{ return function() {{ copyToClipboard(text); }}}}
        window.onload = function() {{
            document.getElementById("copy_abi").onclick = copyOnClick('{abi}');
            document.getElementById("copy_source").onclick = copyOnClick({source});
            document.getElementById("copy_bytecode").onclick = copyOnClick('{bytecode}');
        }}
    """.format(abi=abi, source=json.dumps(source), bytecode=escape(bytecode)))

def make_overview(tag, line, contract_doc, base_contracts, pragmas):
    with tag('div', id="contract_info"):
        section_title(line, 'Contract Overview')

        contract_doc = [line.strip() for line in contract_doc.split('\n')]
        authors = []
        for doc_line in contract_doc:
            if doc_line.startswith('@author'):
                authors.append(doc_line[7:])
        if len(authors) > 0:
            if len(authors) == 1:
                authors_text = authors[0]
            else:
                authors_text = ', '.join(authors[:-1]) + ' and ' + authors[-1]
            line('div', 'Authored by {}'.format(authors_text))
        if len(base_contracts) > 0:
            line('div', 'Inherits from {}'.format(', '.join(base_contracts)), klass='inherit')
        line('h4', 'Click to copy data')
        line('textarea', '', id='__doc_copy')
        with tag('div', klass='copy_data'):
            line('div', 'ABI', id='copy_abi')
            line('div', 'Source', id='copy_source')
            line('div', 'Bytecode', id='copy_bytecode')

        if len(pragmas) > 0:
            def display_fn(tag, line, item):
                line('td', item[0], klass='pragma_name center')
                line('td', item[1], klass='info')
            pragma_data = [deconstruct_pragma(pragma) for pragma in pragmas]
            section(tag, line, 'pragmas', 'Pragmas', pragma_data, display_fn)

def section_title(line, name):
    line('h2', name)
    line('hr', '')

def section(tag, line, id, title, data, display_fn):

    with tag('table', id=id, klass="section"):
        if title:
            with tag('tr'):
                line('th', title, colspan='2')
        for item in data:
            with tag('tr'):
                display_fn(tag, line, item)

def full_type(type_node):
    return type_node['attributes']['type']

# variable is an AST node that represents a state variable
def type_name(type_node, full=False):
    
    if type_node['name'] == 'ArrayTypeName':
        if full:
            return full_type(type_node)
        return type_node['children'][0]['attributes']['name']+'[]'

    if type_node['name'] == 'Mapping':
        key_name = type_name(type_node['children'][0])
        value_name = type_name(type_node['children'][1])
        return "mapping({} => {})".format(key_name, value_name)
    else:
        if full:
            return full_type(type_node)
        return type_node['attributes']['name']

def base_var_type(var_type):
    if var_type.startswith('mapping'):
        return 'mapping'
    bracket = var_type.find('[')
    if bracket != -1:
        return var_type[:bracket]
    return var_type
def glean_comments(source_lines, index):
    comments = {'notice': []}
    while True:
        if index <= 0:
            return comments
            print('Something weird happened, comment was first source line?')
        c = source_lines[index].strip()
        if c.startswith('///'):
            c = c[3:].strip()
            if c.startswith('@param'):
                words = c.split()
                if len(words) > 1:
                    comments[words[1]] = ' '.join(words[2:])
            elif c.startswith('@notice'):
                comments['notice'].append(c[7:].strip())
            elif not c.startswith('@'):
                comments['notice'].append(c)
        else:
            return comments
        index -= 1

def generic_comments(source_lines, regex):
    matcher = re.compile(regex)
    for i, line in enumerate(source_lines):
        if matcher.search(line):
            return glean_comments(source_lines, i-1)
    return {'notice': []}

def event_comments(source_lines, name):
    return generic_comments(source_lines, r'event\s+?{}\(.*?\);'.format(name))

def struct_comments(source_lines, name):
    return generic_comments(source_lines, r'struct\s+?{}\s*?{{'.format(name))

def function_comments(source_lines, name):
    return generic_comments(source_lines, r'function\s*?{}\(.*?{{'.format(name))

def var_comments(source_lines, name, var_type):
    var_type = base_var_type(var_type)
    regex = r'.*?{}[ \[\]()=>a-zA-Z0-9]*?\s*?{}\s*?(=.*?)?;.*?'.format(var_type, name)
    return generic_comments(source_lines, regex)

def custom_display_fn(source_lines, showVisibility=False, comment_fn=var_comments):
    cols = '1' if showVisibility else '2'
    def display_fn(tag, line, item):
        tname = type_name(item['children'][0])
        name = item['attributes']['name']
        desc = '<br />'.join(comment_fn(source_lines, name, tname)['notice'])

        if showVisibility:
            line('td', item['attributes']['visibility'], klass="visibility center")
        with tag('td', klass="info", colspan=cols):
            line('span', name, klass='name')
            line('span', tname, klass='type')
            if desc:
                line('div', desc, klass='description')
    return display_fn

def make_variables(tag, line, contract, source_lines):
    state = filter(lambda x: x['name']=='VariableDeclaration', contract)
    section_title(line, 'State Variables')
    display_fn = custom_display_fn(source_lines, showVisibility=True)
    section(tag, line, 'state_vars', None, state, display_fn)

def make_structs(tag, line, contract, source_lines):
    state = filter(lambda x: x['name']=='StructDefinition', contract)

    section_title(line, 'Structs')
    for struct in state:
        display_fn = custom_display_fn(source_lines)
        name = struct['attributes']['name']
        line('h3', name)
        comments = struct_comments(source_lines, name)
        if comments['notice']:
            line('div', '<br />'.join(comments['notice']), klass='function_desc')
        section(tag, line, 'structs', 'Fields', struct['children'], display_fn)

def make_events(tag, line, contract, source_lines):
    state = filter(lambda x: x['name']=='EventDefinition', contract)

    section_title(line, 'Events')
    for event in state:
        display_fn = custom_display_fn(source_lines)
        name = event['attributes']['name']
        line('h3', name)
        comments = event_comments(source_lines, name)
        if comments['notice']:
            line('div', '<br />'.join(comments['notice']), klass='function_desc')
        section(tag, line, 'events', 'Parameters', event['children'][0]['children'], display_fn)

def userdoc_notice(meta_doc, fn_sig):
    methods = meta_doc['userdoc']['methods']
    if fn_sig in methods:
        fn_doc = methods[fn_sig]
        if 'notice' in fn_doc:
            return fn_doc['notice']
    return ''

def devdoc_param(meta_doc, fn_sig, param):
    methods = meta_doc['devdoc']['methods']
    return methods[fn_sig]['params'][param]

def devdoc_return(meta_doc, fn_sig):
    methods = meta_doc['devdoc']['methods']
    return methods[fn_sig]['return']

def abi_signature(function):
    params = ','.join(type_name(n['children'][0], full=True) for n in function['children'][0]['children'])
    return "{}({})".format(function['attributes']['name'], params)

def var_list(param_node):
    return [(type_name(n['children'][0]), n['attributes']['name']) for n in param_node]

def fn_signature(tag, line, text, function):
    text(function['attributes']['name']+'(')
    var_decls = var_list(function['children'][0]['children'])
    for i, var_decl in enumerate(var_decls):
        line('span', var_decl[0], klass='type')
        text(' ')
        line('span', var_decl[1], klass='name')
        if i != len(var_decls) - 1:
            text(', ')
    text(') ')
            
    line('span', function['attributes']['visibility'], klass='visibility')
    if function['attributes']['stateMutability'] != 'nonpayable':
        line('span', ' '+function['attributes']['stateMutability'], klass='mutability')
    
    returns = var_list(function['children'][1]['children'])
    if len(returns) != 0:
        text(' ')
    for i, ret in enumerate(returns):
        line('span', ret[0], klass='type')
        line('span', ' '+ret[1], klass='name')
        if i != len(returns) - 1:
            text(', ')

def make_functions(tag, line, text, contract, meta_doc, source_lines):
    state = filter(lambda x: x['name']=='FunctionDefinition', contract)

    section_title(line, 'Functions')
    for function in state:
        fn_name = function['attributes']['name']

        if fn_name == '':
            line('h3', 'Fallback function')
        else:
            line('h3', function['attributes']['name'])

        with tag('div', klass="function_sig"):
            fn_signature(tag, line, text, function)

        signature = abi_signature(function)
        
        comments = function_comments(source_lines, fn_name)
        if comments['notice']:
            line('div', ' '.join(comments['notice'][::-1]), klass='function_desc')

        def param_display(param=True):
            def display_fn(tag, line, item):
                tname = type_name(item['children'][0])
                name = item['attributes']['name']
                if param:
                    desc = devdoc_param(meta_doc, signature, name)
                else:
                    desc = devdoc_return(meta_doc, signature)

                with tag('td', klass="info", colspan='2'):
                    line('span', name, klass='name')
                    line('span', tname, klass='type')
                    if desc:
                        line('div', desc, klass='description')
            return display_fn

        params = function['children'][0]['children']
        if len(params) > 0:
            section(tag, line, 'parameters', 'Parameters', params, param_display())
        returns = function['children'][1]['children']
        if len(returns) > 0:
            section(tag, line, 'returns', 'Returns', returns, param_display(param=False))

def contract_info(filename, compile_result):
    contract_name = filename.split('/')[-1].split('.')[0]
    for source_name in compile_result:
        if contract_name in source_name:
            filename = source_name
    
    info_key = '{}:{}'.format(filename, contract_name)
    info = compile_result['contracts'][info_key]
    for k, v in info.items():
        if k != "bin":
            info[k] = json.loads(v)

    ast = compile_result['sources'][filename]['AST']

    return [info, ast]

def compile_contract(contract):
    solc = get_solc()
    if not solc:
        print("Error - solc not found in path")
        return False

    command = [solc, '--combined-json', 'abi,ast,bin,devdoc,interface,metadata,userdoc', contract]

    proc = subprocess.Popen(command,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode != 0:
        print("Compile failed!\n")
        print(stdoutdata)
        print(stderrdata)
        sys.exit(1)
    
    output = json.loads(stdoutdata)
    with open(contract, 'r') as f:
        source = f.read()

    [info, ast] = contract_info(contract, output)
    return [source, info, ast]

# Generate solidity html docs from metadata file
#   produced using: solc --metadata ... 
def generate_docs(source, info, ast, out_dir, inline=False):

    pragmas = []
    base_contracts = []
    for node in ast['children']:
        if node['name'] == 'PragmaDirective':
            pragmas.append(node['attributes']['literals'])
        elif node['name'] == 'ContractDefinition':
            contract = node['children']
            #base_contracts = [n['baseName']['name'] for n in node['baseContracts']]
            name = node['attributes']['name']
            contract_doc = node['attributes']['documentation']
    
    metadata = info['metadata']
    meta_doc = metadata['output']
    
    print('Compiler version: {}'.format(metadata['compiler']['version']))
    source_lines = source.split('\n')

    css_file = pkg_resources.resource_filename('eth_docgen', 'data/doc.css')
    with open(css_file, 'r') as f:
        css = f.read()

    if out_dir:
        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
        html_file = open(os.path.join(out_dir, '{}.html'.format(name)), 'w')
    else:
        html_file = sys.stdout

    doc, tag, text, line = Doc().ttl()
    make_js(line, json.dumps(info['abi']), source, info['bin'])
    if inline:
        line('style', css)
    else:
        doc.asis('<link rel="stylesheet" type="text/css" href="./doc.css" />')
    line('h1', '{} Contract Documentation'.format(name))
    devdoc = info['devdoc']
    if 'title' in devdoc:
        line('div', devdoc['title'], klass='title_desc')

    make_overview(tag, line, contract_doc, base_contracts, pragmas)

    make_variables(tag, line, contract, source_lines)
    make_structs(tag, line, contract, source_lines)
    make_events(tag, line, contract, source_lines)
    make_functions(tag, line, text, contract, meta_doc, source_lines)

    with tag('div', id='footer'):
        line('hr', '')
        line('div', 'Contract documentation generated with eth-docgen')

    html_file.write(doc.getvalue())

    if html_file is not sys.stdout:
        html_file.close()
    
    if not inline:
        with open(os.path.join(out_dir, 'doc.css'), 'w') as f:
            f.write(css)

def get_solc():
    """Check whether solc is available."""
    from shutil import which

    return which(os.environ.get('SOLC_BINARY', 'solc'))