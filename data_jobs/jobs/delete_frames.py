from data_jobs.jobs.job import Job


class DeleteFramesJob(Job):
    """ Job for deleting frames. """
    PARAMS = ["folder_pattern", "frame_query"]

    def execute(self):
        folder_pattern = self.params.get('folder_pattern')
        frame_query = self.params.get('frame_query')

        if not folder_pattern:
            self.log("Validation failed: 'folder_pattern' is missing.")
            raise ValueError("Missing required parameters.")

        self.log(
            f"Simulating deletion for frames with folder_pattern='{folder_pattern}' and frame_query='{frame_query}'")

        simulated_deletion_count = 5
        self.log(f"Found {simulated_deletion_count} frames to delete.")

        for i in range(simulated_deletion_count):
            self.log(f"Simulated deletion of frame {i + 1}: From folder '{folder_pattern}'")

        self.log("Deletion operation completed successfully.")

