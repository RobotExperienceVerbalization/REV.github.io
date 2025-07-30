from verbalizing.QuestionDefinition import ManualQuestionDefinition
from armarx_memory.core.MemoryID import MemoryID
from verbalizing.SearchStrategy import SearchStrategy
from util.armarx_util import *

class ActionBeforeActionQuestionDefinition(ManualQuestionDefinition):

    def evaluate_success(self, instance=None, input=None, memory_id=None, search_type=None):
        if search_type == SearchStrategy.BEFORE:
            # this continues searching after the original snapshot was found
            # if the original was already a high-level skill we can just take the next high-level skill we find, it will be different due to the evaluator strategy
            # if the original was not a high-level skill we need to skip the first high-level skill we find with the same name, as this will be the high-level skill of this first skill
            high_level = is_high_level_skill(instance.data.to_primitive())
            status = instance.data.to_primitive()['status']
            if high_level and status == "Running":
                print("Found high-level skill:", instance.data.to_primitive()["skillId"]["skillName"])
                if self.parent_skill is None:
                    # this is a high-level skill and the original was already a high-level skill
                    if not self.found_parent_skill:
                        # this is the first time:
                        self.found_parent_skill = True
                        return False
                    else:
                        print("Parent Skill:", self.parent_skill)
                        return True, instance
                else:
                    # the original was not a high-level skill
                    if not self.found_parent_skill and self.parent_skill == instance.data.to_primitive()["skillId"]["skillName"]:
                        # we found the first mention of the parent skill
                        self.found_parent_skill = True
                        return False
                    elif self.found_parent_skill:
                        # we already found the original, so this next high-level skill is the correct one
                        return True, instance
                    else:
                        return False
            else:
                return False
        else:
            status = instance.data.to_primitive()["status"]
            if not status == "Running":
                return False
            action = instance.data.to_primitive()["skillId"]["skillName"]
            # this happens in the beginning
            if not self.action_name:
                action_name = get_skill_id_for_spoken_name(input[0])
                self.action_name = action_name
                print("Name of Skill:", self.action_name)
            same_action = self.semantic_matching_model.semantic_similarity(action, self.action_name, 0.8)
            if same_action and not is_high_level_skill(instance.data.to_primitive()):
                self.parent_skill = extract_parent_skill(instance.data.to_primitive())
                print("Setting Parent Skill:", self.parent_skill)
                return True
            elif same_action:
                return True
            else:
                return False
        

    def evaluate_return(self, instance, input):
        instance = list(instance.values())[0]
        return instance.data.to_primitive()["skillId"]["skillName"]
    
    def set_up(self, model, args: dict=None):
        super().set_up(model, args)
        self.action_name = None
        self.parent_skill = None
        self.found_parent_skill = False
        self.question:str = "What did you do before you last <0>?"
        self.search_id:MemoryID = [MemoryID.from_string("Skill/SkillEvent")]
        self.search_strategy:SearchStrategy = SearchStrategy.BEFORE
        self.answer_sentence:str = "My last action before performing the <0> skill, was performing the [0] skill"

        print("Set-Up complete")