from verbalizing.QuestionDefinition import ManualQuestionDefinition
from armarx_memory.core.MemoryID import MemoryID
from verbalizing.SearchStrategy import SearchStrategy

class LocationDuringSpeechQuestionDefinition(ManualQuestionDefinition):

    def evaluate_success(self, instance=None, input=None, memory_id=None, search_type=None):
        print("Currently checking memory id:", memory_id)
        if memory_id == MemoryID.from_string("Speech/SpeechToText"):
            text = instance.data.to_primitive()["text"]
            print(text)
            if self.semantic_matching_model.semantic_similarity(text, input[0], 0.6):
                return True, instance.metadata.timeStored
            else:
                return False, None
        elif memory_id == MemoryID.from_string("SymbolicScene/SymbolicSceneDescription"):
            timeStored = instance.metadata.timeStored
            if int(input[1]) >= timeStored:
                # if the timestamp is smaller for the first time this is the closest timestamp we have
                return True, None
            else:
                return False, None
        elif memory_id == MemoryID.from_string("RobotState/Description"):
            # we do not care which timestamp as we probably only have one
            return True

        
    def evaluate_return(self, instance, input):
        speech_instance = instance[MemoryID.from_string("Speech/SpeechToText")]
        symbolic_scene_instance = instance[MemoryID.from_string("SymbolicScene/SymbolicSceneDescription")]
        robot_state_instance = instance[MemoryID.from_string("RobotState/Description")]
        current_robot = robot_state_instance.data.to_primitive()["name"]
        robot_location = symbolic_scene_instance.data.to_primitive()["robots"][current_robot]["robotAt"]
        return robot_location

    
    def set_up(self, model, args: dict=None):
        super().set_up(model, args)
        self.question:str = "When you last heard <0>, where were you?"
        self.search_id = [MemoryID.from_string("Speech/SpeechToText"), MemoryID.from_string("SymbolicScene/SymbolicSceneDescription"), MemoryID.from_string("RobotState/Description")]
        self.search_strategy:SearchStrategy = SearchStrategy.LATEST
        self.answer_sentence:str = "When I last heard someone say <0>, I was at [0]."

        print("Set-Up complete")