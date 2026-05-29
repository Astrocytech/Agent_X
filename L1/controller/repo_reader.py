"""Reads L0 repository state for evolution planning."""


class RepoReader:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def read_manifest(self) -> dict:
        raise NotImplementedError("Repo reader scaffold")
