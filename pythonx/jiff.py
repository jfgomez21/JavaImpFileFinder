import os
import sys
import subprocess
import pathlib
import vim

def jiff_show_error_message(msg):
    try:
        vim.command("echohl ErrorMsg")

        if isinstance(msg, list):
            for m in msg:
                vim.command("echo \"{0}\"".format(m))
        else:
            vim.command("echo \"{0}\"".format(msg))

        vim.command("echohl None")
    except vim.error:
        pass

def jiff_get_jar_path(path, filename):
    return filename.replace(path, "").replace("_", "/").replace(".jmplst", ".jar")[1:]

def jiff_find_class(path, name):
    args = ["grep", "-rE", "{0}.class$".format(name.replace(".", "/"))]
    args.append(path)

    result = subprocess.run(args, capture_output=True, text=True)
    entries = []

    if result.returncode == 0:
        for line in result.stdout.split("\n"):
            values = line.split(":")

            if len(values) > 1:
                entry = {}
                entry["filename"] = jiff_get_jar_path(path, values[0])
                entry["classname"] = values[1].replace(".class", "")

                entries.append(entry)
    else:
        jiff_show_error_message("Failed to execute grep command")

    return entries

def jiff_select_option(name, options, data=None):
    prompt = "Multiple matches exist for {0}. Select one -".format(name)

    for index, option in enumerate(options):
        prompt = "{0}\n{1} - {2}".format(prompt, index + 1, option)

    skip_option = len(options) + 1

    prompt = "{0}\n{1} - {2}\n".format(prompt, skip_option, "skip")

    vim.command("echohl MoreMsg")
    option = vim.eval("input(\"{0}\")".format(prompt))
    vim.command("echohl None")

    selection = None

    if option.isdigit():
        index = int(float(option)) - 1

        if index >= 0 and index < len(options):
            selection = options[index]

            if data:
                selection = data[index]

    return selection

def jiff_decompile_class(dest, jarfile, name):
    jarfile_no_extension = jarfile.replace(".jar", "")

    filepath = os.path.join(dest, os.path.basename(jarfile_no_extension), os.path.dirname(name))
    javapath = os.path.join(filepath, "{0}.java".format(os.path.basename(name)))

    if os.path.isfile(javapath):
        return javapath

    args = ["java", "-jar", "{0}/java/vineflower-1.11.1-slim.jar".format(vim.eval("s:pluginHome")), "--log-level=error", "--only={0}".format(name), jarfile, os.path.join(dest, os.path.basename(jarfile_no_extension))]

    result = subprocess.run(args)

    if result.returncode != 0:
        jiff_show_error_message("Failed to execute java command")
        javapath = None
    
    return javapath

def jiff_show_more_message(message):
    vim.command("echohl MoreMsg")
    vim.eval("input(\"{0}\")".format(message))
    vim.command("echohl None")

def jiff_find_java_class(name):
    filepath = vim.eval("g:JavaImpDataDir")
    options = jiff_find_class("{0}/cache".format(filepath), name)

    if options:
        selected = options[0]

        if len(options) > 1:
            choices = []

            for option in options:
                choices.append(os.path.basename(option["filename"]))

            selected = jiff_select_option(name, choices, options)

        if selected:
            filename = jiff_decompile_class("{0}/jiff".format(filepath), selected["filename"], selected["classname"])

            if filename:
                vim.command("tabe {0}".format(filename))
    else:
        jiff_show_more_message("No results found for {0}".format(name))

def jiff_read_fd(result):
    dest = []

    for line in result.split("\n"):
        line = line.strip()

        if line:
            dest.append(line)

    return dest

def jiff_fd(pattern, paths):
    args = ["fd"]

    for path in vim.eval("g:JavaImpFileFinderExcludeDirs").split(","):
        if os.path.isdir(path):
            args.append("--exclude")
            args.append(path)

    args.append(pattern)
    args.extend(paths)

    result = subprocess.run(args, capture_output=True, text=True)
    selected = None

    errors = jiff_read_fd(result.stderr)
    files = jiff_read_fd(result.stdout)

    if files:
        for index in range(len(files)):
            files[index] = pathlib.Path(files[index]).as_posix()

        selected = files[0]

        if len(files) > 1:
            selected = jiff_select_option(pattern, files)
    else:
        if not errors:
            jiff_show_more_message("No results found for pattern '{0}'".format(pattern))
        else:
            jiff_show_error_message(errors)

    return selected 

def jiff_parse_tabs():
    vim.command("redir @a")
    vim.command("silent tabs")
    vim.command("redir END")
    lines = vim.eval("@a").splitlines()

    results = []

    for line in lines:
        if line and not line.startswith("Tab"):
            results.append(pathlib.Path(line.replace(">   ", "").replace("  + ", "").strip()).as_posix())

    return results

def jiff_find_tab(tabs, filename):
    for index, value in enumerate(tabs):
        if value == filename:
            return index

    return -1
            
def jiff_go_to_tab(tabs, index):
    vim.command("tabnext {0}".format(index))

def jiff_display_file(filename):
    tabs = jiff_parse_tabs()
    index = jiff_find_tab(tabs, filename)

    if index > 0:
        jiff_go_to_tab(tabs, index + 1)
    else:
        vim.command("tabe {0}".format(filename))

def jiff_find_file(search_file_paths=[]):
    values = vim.eval("a:000")
    paths = []

    if not values:
        jiff_show_error_message("No arguments specified")

        return None

    if len(values) == 1:
        paths.extend(search_file_paths)
    else:		
        paths.extend(values[1:])

    return jiff_fd(values[0], paths)

def jiff_find_java_file():
    paths = []

    for path in vim.eval("g:JavaImpPaths").split(","):
        if os.path.isdir(path):
            paths.append(path)

    filename = jiff_find_file(paths)

    if filename:
        jiff_display_file(filename)

    return filename

def jiff_find_regular_file():
    filename = jiff_find_file()

    if filename:
        jiff_display_file(filename)

    return filename

def jiff_find_regular_file_insert():
    filename = jiff_find_file()

    if filename:
        row, col = vim.current.window.cursor
        line = vim.current.buffer[row - 1]
        new_line = line[:col] + filename + line[col:]

        vim.current.buffer[row - 1] = new_line
        vim.current.window.cursor = (row, col + len(filename))
