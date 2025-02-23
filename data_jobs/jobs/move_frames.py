from data_jobs.jobs.job import Job


class MoveFramesJob(Job):
    """ Job for moving frames between locations. """
    PARAMS = ["folder_patterns", "frame_query", "label_query", "source", "destination", "modify"]

    def execute(self):
        folder_patterns = self.params.get('folder_patterns')
        frame_query = self.params.get('frame_query')
        label_query = self.params.get('label_query')
        source = self.params.get('source')
        destination = self.params.get('destination')
        modify = self.params.get('modify', True)

        if not folder_patterns or not destination:
            self.log("Validation failed: 'folder_patterns' or 'destination' is missing.")
            raise ValueError("Missing required parameters.")

        self.log(
            f"Starting: Checking frames with folder_patterns='{folder_patterns}' and frame_query='{frame_query}' label_query='{label_query}'")

        frame_count = 5  # Simulated count
        self.log(f"Found {frame_count} frames matching the criteria.")

        for i in range(frame_count):
            simulated_old_folder = f"{folder_patterns}"
            simulated_new_folder = simulated_old_folder.replace(source, destination) if source else destination
            self.log(f"Simulated frame {i + 1}: Moving from '{simulated_old_folder}' to '{simulated_new_folder}'")

        self.log("Move operation completed successfully.")
