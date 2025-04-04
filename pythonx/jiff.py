import os
import sys
import subprocess
import vim

def jiff_show_error_message(msg):
    try:
        vim.command("echohl ErrorMsg")
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
            #TODO - handle lines starting with [fd error]:
            values = line.split(":")

            if len(values) > 1:
                entry = {}
                entry["filename"] = jiff_get_jar_path(path, values[0])
                entry["classname"] = values[1].replace(".class", "")

                entries.append(entry)
    else:
        jiff_show_error_message("Failed to execute grep command")

    return entries

def jiff_select_option(name, options):
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

    return selection

def jiff_decompile_class(dest, jarfile, name):
    jarfile_no_extension = jarfile.replace(".jar", "")

    filepath = os.path.join(dest, os.path.basename(jarfile_no_extension), os.path.dirname(name))
    javapath = os.path.join(filepath, "{0}.java".format(os.path.basename(name)))

    if os.path.isfile(javapath):
        return javapath

    args = ["java", "-jar", "{0}/vineflower-1.11.1-slim.jar".format(vim.eval("s:pluginHome")), "--log-level=error , ""--only={0}".format(name), jarfile, os.path.join(dest, os.path.basename(jarfile_no_extension))]

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
    options = jiff_find_class(".javaImp/cache", name)

    if options:
        selected = options[0]

        if len(options) > 1:
            selected = jiff_select_option(name, options)

        if selected:
            filename = jiff_decompile_class(".javaImp/jif", selected["filename"], selected["classname"])

            if filename:
                vim.command("tabe {0}".format(filename))
    else:
        jiff_show_more_message("No results found for {0}".format(name))

def jiff_fd(pattern, paths):
    args = ["fd", pattern]
    args.extend(paths)

    result = subprocess.run(args, capture_output=True, text=True)
    selected = None

    if result.returncode == 0:
        files = []

        for line in result.stdout.split("\n"):
            if line.strip():
                files.append(line)

        if files:
            selected = files[0]

            if len(files) > 1:
                selected = jiff_select_option(pattern, files)
        else:
            jiff_show_more_message("No results found for pattern '{0}'".format(pattern))
    else:
        jiff_show_error_message("Failed to execute fd command")

    return selected 

def jiff_find_file():
    values = vim.eval("a:000")
    paths = []

    if values:
        if len(values) == 1:
            paths.append(".")

            for path in vim.eval("g:JavaImpPaths").split(","):
                if os.path.isdir(path):
                    paths.append(path)
        else:		
            paths.extend(values[1:])
    else:
        jiff_show_error_message("No arguments specified")

    filename = jiff_fd(values[0], paths)

    if filename:
        vim.command("tabe {0}".format(filename))
