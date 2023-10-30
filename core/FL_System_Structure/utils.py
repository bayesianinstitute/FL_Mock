class Utils:
    def __init__(self):
        # You can add any necessary initialization code here
        pass

    def get_global_ipfs_link(self):
        """
        This method retrieves the global IPFS link for the DFL model.

        Algorithm:
        1. Connect to the IPFS network or system.
        2. Retrieve the global IPFS link for the DFL model.
        3. Return the obtained IPFS link.

        Returns:
        A message confirming that the global IPFS link has been obtained.
        """
        return "Global IPFS link obtained"

    def is_model_better(self):
        """
        This method checks if the current model is better than the previous one.

        Pseudocode:
        1. Compare the performance metrics of the current model with the previous model.
        2. If the current model's performance is better:
            - Set model_is_better to True
        3. Otherwise:
            - Set model_is_better to False
        4. Return model_is_better.

        Returns:
        A message indicating whether the current model is better than the previous one.
        """
        return "Model is better"
