from verbalizing.QuestionDefinition import ManualQuestionDefinition
from armarx_memory.core.MemoryID import MemoryID
from verbalizing.SearchStrategy import SearchStrategy
from util.armarx_util import get_spoken_name

class LastKnownLocationObjectQuestionDefinition(ManualQuestionDefinition):
    # generated at 2025_05_12-19_25

    def evaluate_success(self, instance=None, input=None, memory_id=None, search_type=None):
        if input is None or len(input) == 0:
            return False
        object_name = input[0]
        try:
            objects = instance.data.to_primitive()["objects"]
            for object_id, object_data in objects.items():
                
                id_value = object_data.get("id", "")
                name = get_spoken_name(id_value)
                # Use semantic matching instead of strict equality
                if self.semantic_matching_model.semantic_similarity(name, object_name, 0.6):
                    # Object found; now check for last seen location
                    if "objectAt" in object_data and object_data["objectAt"] and object_data["objectAt"] != '(unknown)':
                        return True, id_value
            return False
        except Exception:
            return False
        
    def evaluate_return(self, instance=None, input=None):
        instance = list(instance.values())[0]
        data = instance.data.to_primitive()
        location = data["objects"][input[1]]["objectAt"]
        return location
    
    def set_up(self, model, args: dict=None):
        super().set_up(model, args)
        self.question:str = "Where did you last see the <0>?"
        self.search_id:MemoryID = [MemoryID.from_string("SymbolicScene/SymbolicSceneDescription")]
        self.search_strategy:SearchStrategy = SearchStrategy.LATEST
        self.answer_sentence:str = "I last saw the <0> at [0]"

        print("Set-Up complete")