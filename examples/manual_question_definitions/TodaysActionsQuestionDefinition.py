from verbalizing.QuestionDefinition import ManualQuestionDefinition
from armarx_memory.core.MemoryID import MemoryID
from verbalizing.SearchStrategy import SearchStrategy
from datetime import datetime, time
import time as t
from util.armarx_util import is_high_level_skill

def remove_duplicates(strings):
    seen = set()
    result = []
    for s in strings:
        if s not in seen:
            seen.add(s)
            result.append(s)
    return result


class TodaysActionsQuestionDefinition(ManualQuestionDefinition):

    def evaluate_success(self, instance=None, input=None, memory_id=None, search_type=None):
        # Get today's date
        today = datetime.today().date()

        # Create datetime object for 00:00:01
        midnight_plus_one = datetime.combine(today, time(0, 0, 1))

        # Convert to Unix timestamp
        timestamp = int(midnight_plus_one.timestamp() * 1000000)

        print(instance.metadata.timeStored)
        return instance.metadata.timeStored > timestamp  #this is true if timeStored was today
        

    def evaluate_return(self, instance, input):
        print("Evaluation started")

        successfull_actions = []
        failed_actions = []
        all_actions = []
        all_high_level_skills = []

        for i in list(instance.values())[0]:
            status = i.data.to_primitive()["status"]
            name = i.data.to_primitive()["skillId"]["skillName"]
            all_actions.append(name)
            if status == "Failed":  # this means the skill failed
                failed_actions.append(name)
            elif status == "Succeeded":  # this means the skill was performed successfull
                successfull_actions.append(name)
            if is_high_level_skill(i.data.to_primitive()):
                all_high_level_skills.append(name)

        all_actions = remove_duplicates(all_actions)
        high_level_skills = remove_duplicates(all_high_level_skills)
        return high_level_skills
    
    def set_up(self, model, args: dict=None):
        super().set_up(model, args)
        self.question:str = "What did you do today?"
        self.search_id:MemoryID = [MemoryID.from_string("Skill/SkillEvent")]
        self.search_strategy:SearchStrategy = SearchStrategy.DURING
        self.answer_sentence:str = "Today I executed the following actions: [:]"  
        print("Set-Up complete")