import asyncio
import logging
import os
import xml
import xmltodict
from collections import OrderedDict
from dateutil.parser import parse
from .abs_enhancer import AbsEnhancer


async def _do_subprocess(filename, date, path, results):
    command = 'java -jar de.unihd.dbs.heideltime.standalone.jar -it -t NEWS ' + filename + ' -dct ' + date
    print(command)
    proc = await asyncio.create_subprocess_shell(command,
                                                 shell=True, cwd=path,
                                                 stdout=asyncio.subprocess.PIPE)
    results.append(await proc.stdout.read())


class Heideltime(AbsEnhancer):
    """
    Heideltime
     - is a commandline tool (jar)
     - can only read and write files
     therefore it has to be called over the command line
    """
    def __init__(self, questions):
        self.log = logging.getLogger('GiveMe5W-Enhancer')
        super().__init__(questions)

    def get_enhancer_id(self):
        return 'heideltime'

    def process(self, document):
        filename = self.get_path_to_runtime() + '/tmp.txt'
        path_abs = os.path.abspath(filename)
        # raw document date
        date = document.get_date()

        if date:
            try:
                # parsed document date
                date = parse(date)
                date = date.strftime('%Y-%m-%d')

                # write the question as file to disc
                outfile = open(path_abs, 'w')
                full_text = document.get_full_text()
                outfile.write(full_text)
                outfile.close()

                results = []
                event_loop = asyncio.get_event_loop()
                tasks = [
                    asyncio.ensure_future(_do_subprocess(path_abs, date, self.get_path_to_runtime() + '/heideltime-standalone', results))]

                # wait for the event-loop to be done
                event_loop.run_until_complete(asyncio.wait(tasks))

                # WARNING direct conversion to JSON, some information can`t be transferred
                try:
                    o = xmltodict.parse(results[0])
                    last_index = 0
                    timeML_wrapper = o.get('TimeML', [])

                    # if there was no finding timeML_wrapper is a simple string
                    if isinstance(timeML_wrapper, str):
                        return

                    timex3s = timeML_wrapper.get('TIMEX3')
                    if timex3s:

                        result = []
                        # Heideltime isn`t including offsets, therefore they have to be added afterwards

                        # If there was one candidate the return has a different format..
                        if isinstance(timex3s, OrderedDict):
                            candidate_text = timex3s.get('#text')
                            tmp_last_index = full_text.find(candidate_text, last_index)
                            if tmp_last_index != -1:
                                last_index = tmp_last_index
                                timex3s['characterOffset'] = (last_index, last_index + len(candidate_text))
                                result.append(timex3s)
                        else:
                            for timex3 in timex3s:
                                # more than one finding
                                candidate_text = timex3.get('#text')
                                tmp_last_index = full_text.find(candidate_text, last_index)
                                if tmp_last_index != -1:
                                    last_index = tmp_last_index
                                    timex3['characterOffset'] = (last_index, last_index + len(candidate_text))
                                    result.append(timex3)
                        if len(result) > 0:
                            # just take candidates with offset, there is no way to map without
                            document.set_enhancement(self.get_enhancer_id(), result)
                except xml.parsers.expat.ExpatError:
                    self.log.error('')
                    self.log.error(document.get_document_id() + ': ' + document.get_title())
                    self.log.error(
                        "         Heideltime result was not parseable, this usually happens with strange special characters")

            except ValueError:
                self.log.error('')
                self.log.error(document.get_document_id() + ': ' + document.get_title())
                self.log.error(
                    "         Heideltime found a date entry, but it was not parseable:"+ date)
        else:
            self.log.error('')
            self.log.error(document.get_document_id() + ': ' + document.get_title())
            self.log.error(
                "         Heideltime needs a publish date to parse news. Input:" + document.get_rawData().get('date_publish'))


    def process_data(self, process_data, character_offset):
        # there could be more than one mention per character_offset
        result = []
        for timex3 in process_data:
            process_data_offset = timex3.get('characterOffset')
            if self.is_overlapping(character_offset, process_data_offset):
                result.append(timex3)
        return result
