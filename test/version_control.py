import subprocess


class Git:
    """
    A lightweight object-oriented wrapper around the Git CLI.

    This class provides safe, structured access to common Git operations
    using Python's subprocess module. Each method maps directly to a
    specific Git command.

    Attributes:
        repo_path (str): Path to the Git repository. Defaults to current directory.
    """

    def __init__(self, repo_path="."):
        """
        Initialize the Git client.

        Args:
            repo_path (str): Path to the Git repository.
        """
        self.repo_path = repo_path

    def _run(self, args):
        """
        Execute a Git command.

        Args:
            args (list[str]): List of Git arguments (without the 'git' prefix).

        Returns:
            subprocess.CompletedProcess: Result object containing stdout, stderr,
            and return code.
        """
        return subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

    # ================= BASIC COMMANDS =================

    def init(self):
        """
        Initialize a new Git repository.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["init"])

    def status(self):
        """
        Show the current working tree status.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["status"])

    def add(self, path="."):
        """
        Stage files for commit.

        Args:
            path (str): File or directory to stage. Defaults to all files.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["add", path])

    def commit(self, message):
        """
        Commit staged changes.

        Args:
            message (str): Commit message.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["commit", "-m", message])

    def push(self, remote="origin", branch="main"):
        """
        Push commits to a remote repository.

        Args:
            remote (str): Remote name.
            branch (str): Branch name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["push", remote, branch])

    def pull(self, remote="origin", branch="main"):
        """
        Pull changes from a remote repository.

        Args:
            remote (str): Remote name.
            branch (str): Branch name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["pull", remote, branch])

    # ================= REMOTES =================

    def add_remote(self, name, url):
        """
        Add a new remote repository.

        Args:
            name (str): Remote name.
            url (str): Remote repository URL.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["remote", "add", name, url])

    def remove_remote(self, name):
        """
        Remove an existing remote.

        Args:
            name (str): Remote name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["remote", "remove", name])

    def list_remotes(self):
        """
        List all configured remotes.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["remote", "-v"])

    # ================= BRANCHES =================

    def list_branches(self):
        """
        List local branches.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["branch"])

    def create_branch(self, name):
        """
        Create a new branch.

        Args:
            name (str): Branch name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["branch", name])

    def switch_branch(self, name):
        """
        Switch to an existing branch.

        Args:
            name (str): Branch name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["checkout", name])

    def create_and_switch_branch(self, name):
        """
        Create and switch to a new branch.

        Args:
            name (str): Branch name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["checkout", "-b", name])

    def delete_branch(self, name):
        """
        Delete a local branch (safe).

        Args:
            name (str): Branch name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["branch", "-d", name])

    def force_delete_branch(self, name):
        """
        Force delete a local branch.

        Args:
            name (str): Branch name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["branch", "-D", name])

    # ================= LOG =================

    def log(self, count=10):
        """
        Show commit history.

        Args:
            count (int): Number of commits to show.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["log", f"-{count}", "--oneline"])

    # ================= RESET / ROLLBACK =================

    def soft_reset(self, commit="HEAD~1"):
        """
        Undo commit but keep changes staged.

        Args:
            commit (str): Commit reference.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["reset", "--soft", commit])

    def mixed_reset(self, commit="HEAD~1"):
        """
        Undo commit and unstage changes.

        Args:
            commit (str): Commit reference.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["reset", "--mixed", commit])

    def hard_reset(self, commit="HEAD~1"):
        """
        Completely discard changes and commits.

        WARNING: This operation is destructive.

        Args:
            commit (str): Commit reference.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["reset", "--hard", commit])

    # ================= STASH =================

    def stash(self):
        """
        Save local changes to stash.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["stash"])

    def stash_pop(self):
        """
        Apply and remove the latest stash.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["stash", "pop"])

    def stash_list(self):
        """
        List all stashes.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["stash", "list"])

    # ================= TAGS =================

    def create_tag(self, name):
        """
        Create a Git tag.

        Args:
            name (str): Tag name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["tag", name])

    def delete_tag(self, name):
        """
        Delete a Git tag.

        Args:
            name (str): Tag name.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["tag", "-d", name])

    # ================= CLEAN =================

    def clean(self, force=False):
        """
        Remove untracked files.

        Args:
            force (bool): Remove directories as well.

        Returns:
            subprocess.CompletedProcess
        """
        return self._run(["clean", "-fd"] if force else ["clean", "-f"])
