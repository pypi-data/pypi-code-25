from html import escape
import logging
import markdown
import os
import re
import sys
import yaml

from .base import Step, Connection, Workflow


logger = logging.getLogger(__name__)


class Section(object):
    """Those are the sections of the document, which can be rendered.
    """
    def __init__(self, id):
        self.id = id


class ModuleSection(Section):
    """Module, the output will be obtained by executing it.
    """
    def __init__(self, id, module, lines):
        super(ModuleSection, self).__init__(id)
        self.module = module
        self.lines = lines
        self.inputs = {'env'}
        self.outputs = {'env', 'stream'}

    def render_html(self, workflow_results, **kwargs):
        streams = workflow_results[self.id].get('streams')
        if not streams:
            return None
        return '\n'.join('<pre class="%s">%s</pre>' % (stream, escape(data))
                         for stream, data in streams)


class TextSection(Section):
    """Text, output is just the rendered version of this.
    """
    def __init__(self, id, text):
        super(TextSection, self).__init__(id)
        self.text = text

    def render_html(self, markdown_renderer, **kwargs):
        return markdown_renderer.convert(''.join(self.text))


class Noteflow(object):
    """A notebook, ie a markdown document with embedded cacheflow steps.
    """
    def __init__(self, sections, meta):
        self.sections = sections

        steps = {}
        outputs = {}
        connections = {}
        for section in sections:
            if isinstance(section, ModuleSection):
                # Create step
                step = Step(section.id, section.module,
                            section.inputs, section.outputs,
                            {'code': [''.join(section.lines)]})
                steps[step.id] = step

                # Create connections
                for ref in section.inputs:
                    try:
                        from_step_id = outputs[ref]
                    except KeyError:
                        continue
                    else:
                        connections[len(connections)] = Connection(
                            len(connections),
                            from_step_id,
                            ref,
                            step.id,
                            ref,
                        )
                for ref in section.outputs:
                    outputs[ref] = step.id

        self.workflow = Workflow(steps, connections, meta)


_re_step_start = re.compile(r'^``` *(\{.*\}) *$')
_re_step_end = re.compile(r'^``` *$')


def load_noteflow(fileobj):
    sections = []
    lines = []
    for line in fileobj:
        m = _re_step_start.match(line)
        if m is not None:
            sections.append(TextSection(len(sections), lines))
            lines = []

            module = yaml.load(m.group(1))
            code = []
            for line in fileobj:
                if _re_step_end.match(line) is not None:
                    break
                code.append(line)
            sections.append(ModuleSection(len(sections), module, code))
        else:
            lines.append(line)

    if lines:
        sections.append(TextSection(len(sections), lines))

    return Noteflow(sections, {})


def render(noteflow, executor, out):
    logger.info("Executing...")
    results = executor.execute(noteflow.workflow)

    md = markdown.Markdown()

    logger.info("Writing output...")
    for section in noteflow.sections:
        rendered = section.render_html(markdown_renderer=md,
                                       workflow_results=results)
        if rendered:
            out.write(rendered)


def main():
    """Entrypoint for the ``noteflow`` command.
    """
    from .base import NullCache
    from .builtin_modules import BuiltinModulesLoader
    from .executor import Executor
    from .python import BuiltinPythonLoader


    logging.basicConfig(level=logging.INFO)

    logger.info("Loading noteflow file...")
    with open(sys.argv[1]) as fp:
        noteflow = load_noteflow(fp)

    executor = Executor(NullCache(),
                        [BuiltinPythonLoader(), BuiltinModulesLoader()])
    with open(os.path.splitext(sys.argv[1])[0] + '.html', 'w') as out:
        render(noteflow, executor, out)
