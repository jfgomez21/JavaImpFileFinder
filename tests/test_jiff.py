import subprocess
import unittest

from pyfakefs.fake_filesystem_unittest import TestCase
from unittest.mock import patch

import vim
import jiff

class TestJiff(TestCase):
    def setUp(self):
        self.setUpPyfakefs() 
        vim.reset()

    @patch('subprocess.run')
    def test_jiff_find_file(self, mock_run):
        self.fs.create_file("src/main/java/com/example/MyClass.java")

        vim.set_eval("g:JavaImpPaths", "src/main/java") 
        vim.set_eval("a:000", ["MyClass"])

        mock_run.return_value.stdout = "src/main/java/com/example/MyClass.java"
        mock_run.return_value.returncode = 0

        jiff.jiff_find_file()

        self.assertEqual("src/main/java/com/example/MyClass.java", vim.properties["file_name"]) 

    @patch('subprocess.run')
    def test_jiff_find_file_with_path_argument(self, mock_run):
        self.fs.create_file("src/main/java/com/example/MyClass.java")

        vim.set_eval("g:JavaImpPaths", "src/test/java") 
        vim.set_eval("a:000", ["MyClass", "src/main/java"])

        mock_run.return_value.stdout = "src/main/java/com/example/MyClass.java"
        mock_run.return_value.returncode = 0

        jiff.jiff_find_file()

        self.assertEqual("src/main/java/com/example/MyClass.java", vim.properties["file_name"]) 

    @patch('subprocess.run')
    def test_jiff_find_file_with_no_arguments(self, mock_run):
        self.fs.create_file("src/main/java/com/example/MyClass.java")

        vim.set_eval("g:JavaImpPaths", "src/main/java") 
        vim.set_eval("a:000", [])

        mock_run.return_value.stdout = "src/main/java/com/example/MyClass.java"
        mock_run.return_value.returncode = 0

        jiff.jiff_find_file()

        self.assertEqual("", vim.properties["file_name"]) 
        self.assertEqual(1, len(vim.properties["error_messages"]))
        self.assertEqual("No arguments specified", vim.properties["error_messages"][0])

    @patch('subprocess.run')
    def test_jiff_find_file_with_no_results(self, mock_run):
        self.fs.create_file("src/main/java/com/example/MyClass.java")

        vim.set_eval("g:JavaImpPaths", "src/main/java") 
        vim.set_eval("a:000", ["MyService"])

        mock_run.return_value.stdout = ""
        mock_run.return_value.returncode = 0

        jiff.jiff_find_file()

        self.assertEqual("", vim.properties["file_name"])
        self.assertEqual("No results found for pattern 'MyService'", vim.properties["input_messages"][0])
        self.assertEqual(1, len(vim.properties["input_messages"]))

    @patch('subprocess.run')
    def test_jiff_find_file_with_error_messages(self, mock_run):
        self.fs.create_file("src/main/java/com/example/MyClass.java")

        vim.set_eval("g:JavaImpPaths", "src/main/java,src/test/java,abc") 
        vim.set_eval("a:000", ["MyService"])

        invalid_paths = ["src/test/java", "abc"]
        error_messages = []

        for path in invalid_paths:
            error_messages.append("[fd error]: Search path '{0}' is not a directory".format(path)) 

        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "\n".join(error_messages)
        mock_run.return_value.returncode = 0

        jiff.jiff_find_file()

        self.assertEqual("", vim.properties["file_name"])

        for index in range(min(len(error_messages), len(vim.properties["error_messages"]))):
            self.assertEqual(error_messages[index], vim.properties["error_messages"][index])

    @patch('subprocess.run')
    def test_jiff_find_file_with_multiple_options(self, mock_run):
        self.fs.create_file("src/main/java/com/example/MyClass.java")
        self.fs.create_file("src/main/java/com/example/service/MyService.java")
        self.fs.create_file("src/test/java/com/example/service/TestMyService.java")

        vim.set_eval("g:JavaImpPaths", "src/main/java,src/test/java") 
        vim.set_eval("a:000", ["My"])
        vim.set_input_return_value("2")

        stdout_results = [
            "src/main/java/com/example/MyClass.java",
            "src/main/java/com/example/service/MyService.java",
            "src/test/java/com/example/service/TestMyService.java"
        ]

        mock_run.return_value.stdout = "\n".join(stdout_results)
        mock_run.return_value.returncode = 0

        jiff.jiff_find_file()

        expected_input_messages = ["Multiple matches exist for My. Select one -"]

        for index, value in enumerate(stdout_results):
            expected_input_messages.append("{0} - {1}".format(index + 1, value))

        expected_input_messages.append("4 - skip")

        self.assertEqual("src/main/java/com/example/service/MyService.java", vim.properties["file_name"]) 
        
        for index in range(min(len(expected_input_messages), len(vim.properties["input_messages"]))):
            self.assertEqual(expected_input_messages[index], vim.properties["input_messages"][index])

        self.assertEqual(len(expected_input_messages), len(vim.properties["input_messages"]))

    @patch('subprocess.run')
    def test_jiff_find_java_class(self, mock_run):
        self.fs.create_file(".JavaImp/cache/lib_module.jmplst")
        self.fs.create_file("lib/module.jar")

        vim.set_eval("g:JavaImpDataDir", ".JavaImp")

        mock_run.side_effect = [
            subprocess.CompletedProcess(args=["grep"], returncode=0, stdout=".JavaImp/cache/lib_module.jmplst:com/example/service/MyService.class"),
            subprocess.CompletedProcess(args=["java"], returncode=0)
        ]

        jiff.jiff_find_java_class("com.example.service.MyService")

        self.assertEqual(".JavaImp/jiff/module/com/example/service/MyService.java", vim.properties["file_name"])

    @patch('subprocess.run')
    def test_jiff_find_java_class_with_multiple_choices(self, mock_run):
        self.fs.create_file(".JavaImp/cache/lib_module.jmplst")
        self.fs.create_file(".JavaImp/cache/lib_module-services.jmplst")
        self.fs.create_file("lib/module.jar")
        self.fs.create_file("lib/module-services.jar")

        vim.set_eval("g:JavaImpDataDir", ".JavaImp")
        vim.set_input_return_value("2")

        mock_run.side_effect = [
            subprocess.CompletedProcess(args=["grep"], returncode=0, stdout=".JavaImp/cache/lib_module.jmplst:com/example/service/MyService.class\n.JavaImp/cache/lib_module-services.jmplst:com/example/service/MyService.class\n"),
            subprocess.CompletedProcess(args=["java"], returncode=0)
        ]

        expected_input_messages = [
            "Multiple matches exist for com.example.service.MyService. Select one -",
            "1 - module.jar",
            "2 - module-services.jar",
            "3 - skip",
        ]

        jiff.jiff_find_java_class("com.example.service.MyService")

        self.assertEqual(".JavaImp/jiff/module-services/com/example/service/MyService.java", vim.properties["file_name"])
        for index in range(min(len(expected_input_messages), len(vim.properties["input_messages"]))):
            self.assertEqual(expected_input_messages[index], vim.properties["input_messages"][index])

        self.assertEqual(len(expected_input_messages), len(vim.properties["input_messages"]))

    @patch('subprocess.run')
    def test_jiff_find_java_class_with_class_already_decompile(self, mock_run):
        self.fs.create_file(".JavaImp/cache/lib_module.jmplst")
        self.fs.create_file("lib/module.jar")
        self.fs.create_file(".JavaImp/jiff/module/com/example/service/MyService.java")

        vim.set_eval("g:JavaImpDataDir", ".JavaImp")

        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ".JavaImp/cache/lib_module.jmplst:com/example/service/MyService.class"

        jiff.jiff_find_java_class("com.example.service.MyService")

        self.assertEqual(".JavaImp/jiff/module/com/example/service/MyService.java", vim.properties["file_name"])

    @patch('subprocess.run')
    def test_jiff_find_java_class_with_grep_error(self, mock_run):
        self.fs.create_file(".JavaImp/cache/lib_module.jmplst")
        self.fs.create_file("lib/module.jar")

        vim.set_eval("g:JavaImpDataDir", ".JavaImp")

        mock_run.return_value.returncode = 1

        expected_error_messages = ["Failed to execute grep command"]

        jiff.jiff_find_java_class("com.example.service.MyService")

        self.assertEqual("", vim.properties["file_name"])

        for index in range(min(len(expected_error_messages), len(vim.properties["error_messages"]))):
            self.assertEqual(expected_error_messages[index], vim.properties["error_messages"][index])

        self.assertEqual(len(expected_error_messages), len(vim.properties["error_messages"]))

    @patch('subprocess.run')
    def test_jiff_find_java_class_with_java_error(self, mock_run):
        self.fs.create_file(".JavaImp/cache/lib_module.jmplst")
        self.fs.create_file("lib/module.jar")

        vim.set_eval("g:JavaImpDataDir", ".JavaImp")

        mock_run.side_effect = [
            subprocess.CompletedProcess(args=["grep"], returncode=0, stdout=".JavaImp/cache/lib_module.jmplst:com/example/service/MyService.class\n"),
            subprocess.CompletedProcess(args=["java"], returncode=1)
        ]

        expected_error_messages = ["Failed to execute java command"]

        jiff.jiff_find_java_class("com.example.service.MyService")

        self.assertEqual("", vim.properties["file_name"])

        for index in range(min(len(expected_error_messages), len(vim.properties["error_messages"]))):
            self.assertEqual(expected_error_messages[index], vim.properties["error_messages"][index])

        self.assertEqual(len(expected_error_messages), len(vim.properties["error_messages"]))

