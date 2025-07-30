from datetime import datetime
from verbalizing.QuestionDefinition import ManualQuestionDefinition
from armarx_memory.core.MemoryID import MemoryID
from verbalizing.SearchStrategy import SearchStrategy

class LocationAtTimeQuestionDefinition(ManualQuestionDefinition):
    # generated at 2025_05_12-18_24

    def evaluate_success(self, instance=None, input=None, memory_id=None, search_type=None):
        from util.armarx_util import calculate_timestamp_from_natural_description

        if input is None or len(input) == 0:
            return False

        # Extract the natural language point in time from the input
        natural_time = input[0]

        try:
            # Calculate the timestamp from the natural description
            print("Starting evaluation of success condition")
            input_timestamp = calculate_timestamp_from_natural_description(natural_time)
            print("Timestamp:", input_timestamp)
            # Check if the robot's location is present in this snapshot at the time specified
            robots = instance.data.to_primitive().get("robots", None)
            if robots is None:
                return False
            armar7 = robots.get("Armar7", None)
            if armar7 is None:
                return False
            robot_location = armar7.get("robotAt", None)
            if robot_location is None:
                return False
            # Now, check if the time of this snapshot is sufficiently close to the desired time
            snapshot_time = instance.metadata.timeStored
            print("Snapshot timestamp:", snapshot_time)
            # Allow some tolerance (e.g., plus/minus (1 second)), since snapshot may not be down to the second
            tolerance_ns = 1 * 1e8
            if abs(snapshot_time - input_timestamp) <= tolerance_ns:
                return True
            else:
                return False
        except Exception:
            return False
        
    def evaluate_return(self, instance=None, input=None):
        instance = list(instance.values())[0]
        data = instance.data.to_primitive()
        robot_location = data["robots"]["Armar7"]["robotAt"]
        return robot_location
    
    def set_up(self, model, args: dict=None):
        super().set_up(model, args)
        self.question:str = "Where were you at <0>?"
        self.search_id:MemoryID = [MemoryID.from_string("SymbolicScene/SymbolicSceneDescription")]
        self.search_strategy:SearchStrategy = SearchStrategy.LATEST
        self.answer_sentence:str = "I was at [0] at <0>."

        print("Set-Up complete")