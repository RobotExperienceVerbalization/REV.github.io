from verbalizing.QuestionDefinition import ManualQuestionDefinition
from armarx_memory.core.MemoryID import MemoryID
from verbalizing.SearchStrategy import SearchStrategy
from datetime import datetime, time
from util.armarx_util import *

class LastTimeActionQuestionDefinition(ManualQuestionDefinition):

    def evaluate_success(self, instance=None, input=None, memory_id=None, search_type=None):
        data = instance.data.to_primitive()
        skillName = data["skillId"]["skillName"]
        status = data["status"]
        if self.skill_id is None:
            self.skill_id = get_skill_id_for_spoken_name(input[0])
            print("Setting self.skil_id to", self.skill_id)

        is_match = self.semantic_matching_model.semantic_similarity(skillName, self.skill_id, 0.6)

        return is_match and status == "Running"
        

    def evaluate_return(self, instance, input):
        instance = list(instance.values())[0]
        started = instance.data.to_primitive()["executionStartedTimestamp"]["timeSinceEpoch"]["microSeconds"]
        return datetime.fromtimestamp(int(started)/1e6).strftime("%A, %d %B %Y at %H:%M")
    
    def set_up(self, model, args: dict=None):
        super().set_up(model, args)
        self.skill_id = None
        self.question:str = "When did you last perform the [0] skill?"
        self.search_id:MemoryID = [MemoryID.from_string("Skill/SkillEvent")]
        self.search_strategy:SearchStrategy = SearchStrategy.LATEST
        self.answer_sentence:str = "I last performed the <0>-Skill on [0]"

        print("Set-Up complete")