from abc import ABC, abstractmethod
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


class Job(ABC):
    def __init__(self, job_id: str, params: dict):
        self.job_id = job_id
        self.params = params
        self.start_time = None
        self.end_time = None
        self.status = 'PENDING'  # Options: PENDING, RUNNING, COMPLETED, FAILED
        self.logs = []

    def log(self, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        self.logs.append(log_message)
        logging.info(log_message)

    def run(self):
        self.start_time = datetime.now()
        self.status = 'RUNNING'
        self.log(f"Job {self.job_id} started with params: {self.params}")
        try:
            self.execute()
            self.status = 'COMPLETED'
            self.log(f"Job {self.job_id} completed successfully.")
        except Exception as e:
            self.status = 'FAILED'
            self.log(f"Job {self.job_id} failed with error: {e}")
        finally:
            self.end_time = datetime.now()

    @abstractmethod
    def execute(self):
        """This method should be implemented by all subclasses to define the job logic."""
        pass

    def get_status(self):
        return {
            'job_id': self.job_id,
            'status': self.status,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'logs': self.logs
        }


@dataclass
class MoveFramesJobParams:
    folder_patterns: str
    frame_query: Optional[str]
    source: str
    destination: str
    modify: bool = True


class MoveFramesJob(Job):
    def execute(self):
        folder_patterns = self.params.get('folder_patterns')
        frame_query = self.params.get('frame_query')
        source = self.params.get('source')
        destination = self.params.get('destination')
        modify = self.params.get('modify', True)

        # def change_folder(frame, frame_index):
        #     if source:
        #         old_folder = frame.meta['folder']
        #         new_folder = old_folder.replace(source, destination)
        #     else:
        #         new_folder = destination
        #
        #     frame.meta['folder'] = new_folder
        #     return modify
        #
        # self.log(
        #     f"Moving frames FROM: {source} TO: {destination}\nframe_query={frame_query} | folder_patterns={folder_patterns}")
        # ng.frames.modify_frames_bulk(
        #     modify_func=change_folder,
        #     folder_patterns=folder_patterns,
        #     frame_query=frame_query
        # )

        # logs to simulate behavior without executing modify_frames_bulk
        if not folder_patterns or not destination:
            self.log("Validation failed: 'folder_patterns' or 'destination' is missing.")
            raise ValueError("Missing required parameters.")

        self.log(
            f"Starting: Checking frames with folder_patterns='{folder_patterns}' and frame_query='{frame_query}'")

        # Simulated log output for dry run
        frame_count = 5  # Assume we found 5 matching frames for the test
        self.log(f"Found {frame_count} frames matching the criteria.")

        for i in range(frame_count):
            simulated_old_folder = f"{folder_patterns}"
            simulated_new_folder = simulated_old_folder.replace(source, destination) if source else destination
            self.log(f"Simulated frame {i + 1}: Moving from '{simulated_old_folder}' to '{simulated_new_folder}'")

        self.log("completed successfully.")


@dataclass
class DeleteFramesJobParams:
    folder_pattern: str
    frame_query: Optional[str]


class DeleteFramesJob(Job):
    def execute(self):
        folder_pattern = self.params.get('folder_pattern')
        frame_query = self.params.get('frame_query')

        # Validation checks
        if not folder_pattern:
            self.log("Validation failed: 'folder_pattern' is missing.")
            raise ValueError("Missing required parameters.")

        # Simulated deletion logs
        self.log(
            f"Simulating deletion for frames with folder_pattern='{folder_pattern}' and frame_query='{frame_query}'")

        simulated_deletion_count = 5  # Example number of frames
        self.log(f"Found {simulated_deletion_count} frames to delete.")

        for i in range(simulated_deletion_count):
            self.log(f"Simulated deletion of frame {i + 1}: From folder '{folder_pattern}'")

        self.log("Deletion simulation completed.")
