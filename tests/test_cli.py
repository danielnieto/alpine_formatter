from unittest import TestCase
from pathlib import Path
from alpine_formatter.cli import should_process, collect_files, load_gitignore
from alpine_formatter.exceptions import InvalidPathError
from pathspec import GitIgnoreSpec
from unittest.mock import patch, mock_open


class TestShouldProcess(TestCase):
    def test_should_process_supported_extension_no_gitignore(self):
        file = Path("/tmp/test.html")
        result = should_process(file)
        self.assertTrue(result)

    def test_should_not_process_supported_extension_and_gitignored(self):
        file = Path("/tmp/test.html")
        gitignore = GitIgnoreSpec.from_lines(["*.html"])
        result = should_process(file, gitignore)
        self.assertFalse(result)

    def test_should_process_supported_extension_and_not_gitignored(self):
        file = Path("/tmp/test.html")
        gitignore = GitIgnoreSpec.from_lines(["*.jpg"])
        result = should_process(file, gitignore)
        self.assertTrue(result)

    def test_should_not_process_unsupported_extension_no_gitignore(self):
        file = Path("/tmp/test.jsx")
        result = should_process(file)
        self.assertFalse(result)

    def test_should_not_process_unsupported_extension_and_gitignored(self):
        file = Path("/tmp/test.jsx")
        gitignore = GitIgnoreSpec.from_lines(["*.jsx"])
        result = should_process(file, gitignore)
        self.assertFalse(result)

    def test_should_not_process_unsupported_extension_and_not_gitignored(self):
        file = Path("/tmp/test.jsx")
        gitignore = GitIgnoreSpec.from_lines(["*.jpg"])
        result = should_process(file, gitignore)
        self.assertFalse(result)


class TestCollectFiles(TestCase):
    @patch("alpine_formatter.cli.Path.exists", return_value=False)
    def test_collect_files_nonexistent_path(self, *args):
        path = Path("/nonexistent/path")
        with self.assertRaises(InvalidPathError):
            collect_files(path)

    @patch("alpine_formatter.cli.Path.exists", return_value=True)
    @patch("alpine_formatter.cli.Path.is_file", return_value=True)
    @patch("alpine_formatter.cli.load_gitignore", return_value=None)
    @patch("alpine_formatter.cli.should_process", return_value=True)
    def test_collect_files_single_file(self, *args):
        path = Path("/some/file.html")
        result = collect_files(path)
        self.assertEqual(result, [path])

    @patch("alpine_formatter.cli.Path.exists", return_value=True)
    @patch("alpine_formatter.cli.Path.is_file", return_value=False)
    @patch("alpine_formatter.cli.Path.is_dir", return_value=True)
    @patch("alpine_formatter.cli.load_gitignore", return_value=None)
    @patch("alpine_formatter.cli.should_process", return_value=True)
    @patch("alpine_formatter.cli.Path.rglob")
    def test_collect_files_directory(self, mock_rglob, *args):
        path = Path("/some/directory")
        files = [
            Path("/some/directory/file1.html"),
            Path("/some/directory/file2.jinja"),
        ]
        mock_rglob.return_value = files
        result = collect_files(path)
        self.assertEqual(result, files)

    @patch("alpine_formatter.cli.Path.exists", return_value=True)
    @patch("alpine_formatter.cli.Path.is_file", return_value=False)
    @patch("alpine_formatter.cli.Path.is_dir", return_value=True)
    @patch("alpine_formatter.cli.load_gitignore", return_value=None)
    @patch("alpine_formatter.cli.should_process", side_effect=[True, True, False])
    @patch("alpine_formatter.cli.Path.rglob")
    def test_collect_files_doesnt_collect_files_that_should_not_be_processed(
        self, mock_rglob, *args
    ):
        path = Path("/some/directory")
        file1 = Path("/some/directory/file1.html")
        file2 = Path("/some/directory/file2.jinja")
        file_should_not_process = Path("/some/directory/file3.jsx")
        all_files = [file1, file2, file_should_not_process]
        mock_rglob.return_value = all_files
        result = collect_files(path)
        self.assertEqual(result, [file1, file2])


class TestLoadGitignore(TestCase):
    @patch("alpine_formatter.cli.Path.is_dir", return_value=True)
    @patch("alpine_formatter.cli.Path.exists", return_value=True)
    @patch("alpine_formatter.cli.open", new_callable=mock_open, read_data="*.jsx")
    @patch("alpine_formatter.cli.Path.resolve")
    def test_load_gitignore_in_current_directory_when_path_is_directory(
        self, mock_resolve, mock_open, mock_exists, *args
    ):
        path = Path("/some/directory")
        mock_resolve.return_value = path
        gitignore = load_gitignore(path)
        self.assertIsNotNone(gitignore)
        mock_open.assert_called_once_with(Path("/some/directory/.gitignore"))
        self.assertEqual(mock_exists.call_count, 1)
        self.assertTrue(gitignore.match_file("file.jsx"))
        self.assertFalse(gitignore.match_file("file.html"))

    @patch("alpine_formatter.cli.Path.is_dir", return_value=True)
    @patch("alpine_formatter.cli.Path.exists", side_effect=[False, False, True])
    @patch("alpine_formatter.cli.open", new_callable=mock_open, read_data="*.jsx")
    @patch("alpine_formatter.cli.Path.resolve")
    def test_load_gitignore_in_parent_directory_when_path_is_directory(
        self, mock_resolve, mock_open, mock_exists, *args
    ):
        path = Path("/some/directory/subdir")
        mock_resolve.return_value = path
        gitignore = load_gitignore(path)
        self.assertIsNotNone(gitignore)
        mock_open.assert_called_once_with(Path("/some/.gitignore"))
        self.assertEqual(mock_exists.call_count, 3)
        self.assertTrue(gitignore.match_file("file.jsx"))
        self.assertFalse(gitignore.match_file("file.html"))

    @patch("alpine_formatter.cli.Path.is_dir", return_value=True)
    @patch("alpine_formatter.cli.Path.exists", return_value=False)
    @patch("alpine_formatter.cli.open", new_callable=mock_open, read_data="*.jsx")
    @patch("alpine_formatter.cli.Path.resolve")
    def test_load_gitignore_not_found_when_path_is_directory(
        self, mock_resolve, mock_open, mock_exists, *args
    ):
        path = Path("/some/directory")
        mock_resolve.return_value = path
        gitignore = load_gitignore(path)
        self.assertIsNone(gitignore)
        mock_open.assert_not_called()
        self.assertEqual(mock_exists.call_count, 3)

    @patch("alpine_formatter.cli.Path.is_dir", return_value=False)
    @patch("alpine_formatter.cli.Path.exists", return_value=True)
    @patch("alpine_formatter.cli.open", new_callable=mock_open, read_data="*.jsx")
    @patch("alpine_formatter.cli.Path.resolve")
    def test_load_gitignore_in_current_directory_when_path_is_file(
        self, mock_resolve, mock_open, mock_exists, *args
    ):
        path = Path("/some/directory/file.html")
        mock_resolve.return_value = path
        gitignore = load_gitignore(path)
        self.assertIsNotNone(gitignore)
        mock_open.assert_called_once_with(Path("/some/directory/.gitignore"))
        self.assertEqual(mock_exists.call_count, 1)
        self.assertTrue(gitignore.match_file("file.jsx"))
        self.assertFalse(gitignore.match_file("file.html"))

    @patch("alpine_formatter.cli.Path.is_dir", return_value=False)
    @patch("alpine_formatter.cli.Path.exists", side_effect=[False, False, True])
    @patch("alpine_formatter.cli.open", new_callable=mock_open, read_data="*.jsx")
    @patch("alpine_formatter.cli.Path.resolve")
    def test_load_gitignore_in_parent_directory_when_path_is_file(
        self, mock_resolve, mock_open, mock_exists, *args
    ):
        path = Path("/some/directory/subdir/file.html")
        mock_resolve.return_value = path
        gitignore = load_gitignore(path)
        self.assertIsNotNone(gitignore)
        mock_open.assert_called_once_with(Path("/some/.gitignore"))
        self.assertEqual(mock_exists.call_count, 3)
        self.assertTrue(gitignore.match_file("file.jsx"))
        self.assertFalse(gitignore.match_file("file.html"))

    @patch("alpine_formatter.cli.Path.is_dir", return_value=False)
    @patch("alpine_formatter.cli.Path.exists", return_value=False)
    @patch("alpine_formatter.cli.open", new_callable=mock_open, read_data="*.jsx")
    @patch("alpine_formatter.cli.Path.resolve")
    def test_load_gitignore_not_found_when_path_is_file(
        self, mock_resolve, mock_open, mock_exists, *args
    ):
        path = Path("/some/directory/file.html")
        mock_resolve.return_value = path
        gitignore = load_gitignore(path)
        self.assertIsNone(gitignore)
        mock_open.assert_not_called()
        self.assertEqual(mock_exists.call_count, 3)
