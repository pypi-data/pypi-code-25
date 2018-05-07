# Small Python script to convert any video files with subtitle(s) to video supported by Google Chromecast.
#
# Copyright 2017 Arnaud Moura <arnaudmoura@gmail.com>
# This code is released under the terms of the MIT license. See the LICENSE
# file for more details.

# !/usr/bin/env python
# -*- coding: utf-8 -*-


# System
import optparse
import os
import platform
import re
import sys
import threading
import time
if sys.version_info >= (3, 0):
    import queue
else:
    import Queue as queue

# ProgressBar
import progressbar

# Core
from core import convertor
from core import media

__version__ = '2.0.1'

# Get platform name
PLATFORM_NAME = platform.system()

# function to create unknown length progress bar
def createUnknownLengthProgressBar():
    return progressbar.ProgressBar(widgets=['     [', progressbar.Timer(), '] ', progressbar.AnimatedMarker()], max_value=progressbar.UnknownLength)


# function to update progress bar with return in the end
def updateBar(bar, number):
    bar.update(number)
    print('\n')


# function to get all files in folder with extension defined in extension_list
def getFiles(p_folder, p_extension_list, p_options):
    full_file_path_list = []
    for root, dirs, video_file in os.walk(p_folder):
        for name in video_file:
            if re.match(p_options.regex, name) and name.lower().endswith(p_extension_list):
                full_file_path_list.append(os.path.abspath(os.path.join(root, name)))
    return full_file_path_list


# main function
def main():
    # File can be converted
    file_can_be_converted = (".mp4", ".mkv", ".m4v", ".avi", ".mov", ".mpegts", ".3gp", ".webm", ".mpg", ".mpeg", ".wmv", ".ogv")

    # Options
    usage = '''Usage: cm2c.py folder [options]
       cm2c.py --file video [options]
       Video extension supported : ''' + str(file_can_be_converted)[1:-1].replace("'", "")
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--version', "-v", action='store_true', help='show version')
    parser.add_option('--file', "-f", metavar='FILE', help='video file path')
    parser.add_option('--force', action='store_true', help='convert the video(s) even if it already has the right format')
    parser.add_option('--overwrite', "-o", action='store_true', help='overwrite the converted files')
    parser.add_option('--no_sub', "-n", action='store_true', help='no subtitle extracted and burn in video')
    parser.add_option('--burn_sub', "-b", action='store_true', help='burn subtitle in the video')
    parser.add_option('--extract_all_sub', action='store_true', help='extract all subtitles and the option --burn_sub is disable')
    parser.add_option('--ext_sub', "-e", action='store_true', help='use external subtitle in SRT or ASS format to burn it in video'
                                                                   ', it must have the same name of the video')
    parser.add_option('--shutdown', '-s', action='store_true', help='shutdown after all conversions (Windows only)')
    parser.add_option('--preset', '-p', metavar='PRESET_NAME', help='define the preset to convert the video(s) '
                                                                    '[ultrafast, superfast, veryfast, faster, fast, '
                                                                    'medium, slow, slower, veryslow] (default superfast). '
                                                                    'A slower preset will provide better compression'
                                                                    ' (compression is quality per filesize).')
    parser.add_option('--audio_language', '-a', metavar='audio_name', help='define the audio language (default eng)')
    parser.add_option('--sub_language', '-l', metavar='sub_lang', help='define the sub language (default fre, fr, und)')
    parser.add_option('--sub_name_regex', '-d', metavar='sub_name', default='.*', help='define the sub name by regex')
    parser.add_option('--regex', '-r', metavar='reg_ex', default='.*',
                      help='define regular expression apply on file names during file parsing (python regex format)')
    options, remainder = parser.parse_args()

    # Check if ffmpeg is installed
    ffmpeg_exe = "ffmpeg.exe"
    if PLATFORM_NAME == "Linux":
        ffmpeg_exe = "ffmpeg"

    if not convertor.Convertor.runCommand(ffmpeg_exe + " -version"):
        sys.exit(ffmpeg_exe + " not found !")

    # Get options values
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()

    if options.version:
        print(__version__)
        sys.exit()

    preset = "superfast"
    if options.preset:
        preset = options.preset.decode('utf-8')
    video_convert_option = " -c:v libx264 -preset " + preset + " -profile:v high -level 4.1 "

    default_audio_language = "eng"
    if not options.audio_language:
        options.audio_language = default_audio_language

    default_sub_language = ['fre', 'fr', 'und']
    if not options.sub_language:
        options.sub_language = default_sub_language

    # List of command
    convert_information_list = []

    # Media object to analyse video
    media_sniffer = media.MediaSniffer()

    # Result conversion
    result_conversion = dict()

    # Get file name
    full_file_path_list = []
    if options.file is None and len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]):
            full_file_path_list = getFiles(sys.argv[1], file_can_be_converted, options)
        else:
            sys.exit("Error : the argument must be a folder or use --file option to convert only one file")
    else:
        filename = options.file
        if os.path.exists(filename):
            # Resolve path of file
            os.chdir(".")
            full_file_path_list.append(os.path.abspath(filename))
        else:
            sys.exit("Error : file " + filename + " not found")

    # Sort List
    full_file_path_list.sort()
    number_file_done = 0

    # Conversion operations
    print('######################################################################')
    # Create progress bar
    global_bar = progressbar.ProgressBar(max_value=len(full_file_path_list),
                                         widgets=[
                                             progressbar.Percentage(),
                                             ' ',
                                             ' (Video done ',
                                             progressbar.SimpleProgress(),
                                             ')',
                                             progressbar.Bar(),
                                             ' ',
                                             progressbar.Timer(),
                                             ' ',
                                             progressbar.AdaptiveETA()
                                             ]
                                        ).start()
    print('\n')

    print('Analyze videos:')
    for video_file in full_file_path_list:
        print('  - ' + video_file)
        # Change directory dir
        os.chdir(os.path.dirname(video_file))
        # Get file extension
        video_name = os.path.basename(video_file)
        video_extension = os.path.splitext(video_file)[1].lower()
        output_file = video_file.replace(video_extension, ".mp4")
        if video_extension == ".mp4":
            output_file = os.path.splitext(video_file)[0] + " (1).mp4"

        ################################################################################################################
        # Get video information
        ################################################################################################################
        json_metadata = media_sniffer.findVideoMetada(video_name)
        # Check output
        if json_metadata == None:
            print('Error during read file : ' + video_name)
            continue

        metadata_info = media_sniffer.analyseVideo(video_name)

        ################################################################################################################
        # Check if must be converted
        ################################################################################################################
        must_be_converted = media_sniffer.hasGoodFormat(metadata_info)

        # Check if already converted
        if not must_be_converted and os.path.exists(output_file) and not options.overwrite:
            print('Video already converted: ' + video_file)
            result_conversion[os.path.basename(video_file)] = "OK"

            number_file_done += 1
            updateBar(global_bar, number_file_done)
            continue

        if not must_be_converted and not options.force:
            print('Video already in the good format : ' + video_file)
            result_conversion[os.path.basename(video_file)] = "OK"

            number_file_done += 1
            updateBar(global_bar, number_file_done)
        else:
            # Default convert command
            convert_command = ffmpeg_exe + ' -i "' + video_file + '"' + " -y"
            subtitle_command = ""
            list_of_extract_subtitle_command = []
            subtitle_to_remove = ""
            video_command = " -c:v copy "
            audio_command = " -c:a copy "

            ################################################################################################################
            # VIDEO
            ################################################################################################################
            # Convert video codec if needed or if forced
            if metadata_info.video_codec != media.mp4_video_codec_supported or options.force:
                video_command = video_convert_option

            ################################################################################################################
            # SUBTITLE
            ################################################################################################################
            subtitle_command, list_of_extract_subtitle_command = media_sniffer.analyseSubtitle(metadata_info, options)
            if subtitle_command != "":
                video_command = video_convert_option

            ################################################################################################################
            # AUDIO
            ################################################################################################################
            audio_track_pos, audio_command = media_sniffer.analyseAudio(metadata_info, options)

            ################################################################################################################
            # CONVERT
            ################################################################################################################
            if audio_command != "":
                stream_map = ' -map 0:' + str(metadata_info.video_track_position) + ' -map 0:' + str(audio_track_pos) + " "
                convert_command += stream_map + subtitle_command + video_command + audio_command + ' "' + output_file + '"'
            else:
                stream_map = ' -map 0:' + str(metadata_info.video_track_position) + " "
                convert_command += stream_map + subtitle_command + video_command + ' "' + output_file + '"'

            # Add convert movie information in list of convertion
            convert_information_list.append(convertor.ConvertInformation(video_file, list_of_extract_subtitle_command, convert_command, subtitle_to_remove))

    ################################################################################################################
    # CONVERT All MOVIES
    ################################################################################################################
    print('\nConvert videos:')
    for convert_information in convert_information_list:
        print('  - ' + convert_information.video_file)
        result_conversion[os.path.basename(convert_information.video_file)] = "OK"

        # change directory dir
        os.chdir(os.path.dirname(convert_information.video_file))

        for extract_command in convert_information.list_extract_subtitle_command:
            print("    - Extract subtitle")
            progress_bar = createUnknownLengthProgressBar()
            result_queue = queue.Queue()
            extract_thread = threading.Thread(target=lambda q, arg: q.put(convertor.Convertor.runCommand(arg)), args=(result_queue, extract_command), daemon=True)
            extract_thread.start()
            while extract_thread.is_alive():
                time.sleep(1)
                progress_bar.update()

            if not result_queue.get():
                result_conversion[os.path.basename(convert_information.video_file)] = "KO"
                break


        print("    - Run conversion ...")
        return_queue = queue.Queue()
        t = threading.Thread(target=convertor.Convertor.runVideoConversionCommand, args=(convert_information.convert_video_command, return_queue), daemon=True)
        t.start()

        # Create ffmpeg progressbar
        # Wait first value from thread
        while True:
            if not return_queue.empty():
                break
        total_duration = return_queue.get()
        if total_duration != None:
            ffmpeg_bar = progressbar.ProgressBar(max_value=int(total_duration),
                                                widgets=[
                                                    progressbar.Percentage(),
                                                    ' ',
                                                    progressbar.Bar(),
                                                    ' ',
                                                    progressbar.Timer(),
                                                    ' ',
                                                    progressbar.AdaptiveETA()
                                                    ]
                                            )
            while t.is_alive():
                if not return_queue.empty():
                    convertion_return = return_queue.get()
                    if type(convertion_return) is RuntimeError:
                        print(convertion_return)
                        result_conversion[os.path.basename(convert_information.video_file)] = "KO"
                        break
                    else:
                        ffmpeg_bar.update(int(convertion_return))
        else:
            ffmpeg_bar = createUnknownLengthProgressBar()
            while t.is_alive():
                if not return_queue.empty():
                    convertion_return = return_queue.get()
                    if type(convertion_return) is RuntimeError:
                        print(convertion_return)
                        result_conversion[os.path.basename(convert_information.video_file)] = "KO"
                        break
                time.sleep(1)
                ffmpeg_bar.update()

        t.join()
        ffmpeg_bar.finish()
        print('\n')

        if convert_information.subtitle_to_remove != "" and options.burn_sub:
            if os.path.exists(convert_information.subtitle_to_remove):
                os.remove(convert_information.subtitle_to_remove)

        print("  - Conversion done ...")
        number_file_done += 1
        updateBar(global_bar, number_file_done)

    # Show conversion result
    print("Conversion result:")
    for fileName in result_conversion.keys():
        print(fileName + " : " + result_conversion[fileName])

    # Shutdown
    if PLATFORM_NAME != "Linux" and options.shutdown:
        os.system("shutdown /s")



# MAIN entry
if __name__ == "__main__":
    main()
