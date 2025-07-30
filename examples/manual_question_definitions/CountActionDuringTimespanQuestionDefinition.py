from verbalizing.QuestionDefinition import ManualQuestionDefinition
from armarx_memory.core.MemoryID import MemoryID
from verbalizing.SearchStrategy import SearchStrategy
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import re
from util.armarx_util import get_skill_id_for_spoken_name, is_high_level_skill

def extract_number(text):
    match = re.search(r'[-+]?\d*\.?\d+', text)
    if match:
        return float(match.group())
    else:
        return None
    
def diff_greater_than_n_months(ts1_ms, ts2_ms, months=1):
    dt1 = datetime.fromtimestamp(ts1_ms / 1e6)
    dt2 = datetime.fromtimestamp(ts2_ms / 1e6)

    # Ensure dt1 <= dt2
    dt1, dt2 = sorted([dt1, dt2])

    # Add n months to dt1
    dt1_plus_n_months = dt1 + relativedelta(months=months)

    return dt2 < dt1_plus_n_months

class CountActionDuringTimespanQuestionDefinition(ManualQuestionDefinition):

    def evaluate_success(self, instance=None, input=None, memory_id=None, search_type=None):
        currently = datetime.today().date()
        # Convert to Unix timestamp
        
        timestamp = int(currently.timestamp() * 1000000)

        instance_timestamp = instance.metadata.timeStored

        factor = extract_number(input[1])
        
        if "minutes" in input[1] or "Minutes" in input[1]:
            return timestamp - instance_timestamp <= (600_000 * factor)
        elif "hours" in input[1] or "Hours" in input[1]:
            return timestamp - instance_timestamp <= (6_000_000 * factor)
        elif "days" in input[1] or "Days" in input[1]:
            return timestamp - instance_timestamp <= ((6_000_000 * 24) * factor)
        elif "months" in input[1] or "Months" in input[1]:
            return diff_greater_than_n_months(timestamp, instance_timestamp, factor)
        elif "today" in input[1] or "Today" in input[1]:
            end_of_today_timestamp = datetime.combine(currently.date(), time(23,59,59)).timestamp() * 1000000
            start_of_today_timestamp = datetime.combine(currently.date(), time(0,0,1)).timestamp() * 1000000
            return start_of_today_timestamp <= instance_timestamp <= end_of_today_timestamp
        raise Exception("Neither minutes, hours nor days in description of timespan")
        

    def evaluate_return(self, instance, input):
        print("Evaluation started")
        all_actions = []

        if self.skill_id is None:
            self.skill_id = get_skill_id_for_spoken_name(input[0])
            print("Setting self.skill_id to", self.skill_id)

        for i in list(instance.values())[0]:
            status = i.data.to_primitive()["status"]
            name = i.data.to_primitive()["skillId"]['skillName']
            if self.semantic_matching_model.semantic_similarity(name, self.skill_id, 0.8) and (status == "Running"):
                print("Found action:", name, "with status", status, " and name", name)
                all_actions.append(name)

        count = len(all_actions)

        return count
    
    def set_up(self, model, args: dict=None):
        super().set_up(model, args)
        self.skill_id = None
        self.question:str = "How often did you do <0> in the last <1>?"
        self.search_id:MemoryID = [MemoryID.from_string("Skill/SkillEvent")]
        self.search_strategy:SearchStrategy = SearchStrategy.DURING
        self.answer_sentence:str = "During the last <1> I executed <0> [0] times."

        print("Set-Up complete")