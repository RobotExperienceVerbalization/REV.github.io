from verbalizing.QuestionDefinition import ManualQuestionDefinition
from armarx_memory.core.MemoryID import MemoryID
from verbalizing.SearchStrategy import SearchStrategy

class AffordancesCurrentSceneQuestionDefinition(ManualQuestionDefinition):

    def evaluate_success(self, instance=None, input=None, memory_id=None, search_type=None):
        # for this we want the most current snapshot which still has the correct entity, which means we just return true
        print("Evaluating return as True")
        return True

    def evaluate_return(self, instance, input):
        all_objects_with_affordance = []
        searched_affordance = input[0]
        instance = list(instance.values())[0]
        data = instance.data.to_primitive()
        all_objects = data['objects']
        for object_name, object_info in all_objects.items():
            all_affordances = object_info['affordances']
            if searched_affordance in all_affordances:
                all_objects_with_affordance.append(object_name)
        if len(all_objects_with_affordance) == 0:
            return None
        return all_objects_with_affordance
    
    def set_up(self, model, args: dict=None):
        super().set_up(model, args)
        self.question = "Which [0] objects do you have?"
        self.search_id = [MemoryID.from_string("SymbolicScene/SymbolicSceneDescription/SymbolicScene/SceneDescription")]
        self.search_strategy = SearchStrategy.CURRENT
        self.answer_sentence = "I remember the following <0> objects: [:]"
        print("Set-Up complete")