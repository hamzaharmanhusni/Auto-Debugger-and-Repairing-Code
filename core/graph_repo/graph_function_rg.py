from typing import Optional, TypedDict
from langgraph.graph import END, StateGraph
from typing import Optional
from core.graph_repo.data_model_rg import Invoke


class AgentCoder(TypedDict):
    requirement:str
    code:str
    predicted_bug: str
    function_explanation:str
    repair_description: str
    improved_code: str
    refactored_code:str
    token_used: int
    prompt_token: int
    completion_token: int
    cost: float

        

class GraphProcess():
    def __init__(self, model, temperature):
        self.invoker = Invoke(model, temperature)
    
    def upload_code(self, state):
        print('\n'+'----------'*20)
        print(f'\n------Entering in Upload Code------')
        code = state['code']
        print(f"Code : \n{code}")
        return{'code':code }

    def localizer(self, state):
        print('\n' + '----------' * 20)
        print('\n------Entering in Localizer------')
        try : 
            requirement = state['requirement']
            code = state['code']

            localizer_response, localizer_info = self.invoker.localizer_invoke(requirement, code)
            print(localizer_info)
            print(f"Bug analyzed: {localizer_response.predicted_bug}")
            return {
                'predicted_bug': localizer_response.predicted_bug,
                'token_used': localizer_info.total_tokens,
                'prompt_token': localizer_info.prompt_tokens,
                'completion_token':  localizer_info.completion_tokens,
                'cost': localizer_info.total_cost
            }
        except Exception as e:
            print(f"An error occurred in Localizer: {e}")
            return state
            
    def explanation(self, state):
        print('\n'+'----------'*20)
        print(f'\n------Entering in Explanation------')
        try:
            code = state['code']
            explanation_response, explanation_info = self.invoker.explanation_invoke(code)
            print(explanation_response.function_explanation)
            print(explanation_info)
            return {
                'function_explanation':explanation_response.function_explanation,
                'token_used': state['token_used'] + explanation_info.total_tokens,
                'prompt_token': state['prompt_token'] + explanation_info.prompt_tokens,
                'completion_token': state['completion_token'] + explanation_info.completion_tokens,
                'cost': state['cost'] + explanation_info.total_cost        
            }
        except Exception as e:
            print(f"An error occurred in Explanation: {e}")
            return state        

    def repairer(self, state):
        print('\n'+'----------'*20)
        print(f'\n------Entering in Repairer------')
        try :
            code = state['code']
            predicted_bug = state['predicted_bug']
            explanation = state['function_explanation']
            repairer_response, repairer_info = self.invoker.repairer_invoke(code, predicted_bug, explanation)
            print(repairer_response.repair_description)
            print(repairer_info)
            return {
                'repair_description':repairer_response.repair_description,
                'token_used': state['token_used'] + repairer_info.total_tokens,
                'prompt_token': state['prompt_token'] + repairer_info.prompt_tokens,
                'completion_token': state['completion_token'] + repairer_info.completion_tokens,
                'cost': state['cost'] + repairer_info.total_cost          
            }
        except Exception as e:
            print(f"An error occurred in Repairer: {e}")
            return state
        
    def crafter(self, state):
        print('\n' + '----------' * 20)
        print('\n------ Entering Crafter ------')
        
        try:
            code = state['code']
            repair_description = state['repair_description']
            crafter_response, crafter_info = self.invoker.crafter_invoke(code, repair_description)
            
            print(crafter_info)
            return {
                "improved_code": crafter_response.improved_code,
                "token_used": state['token_used'] + crafter_info.total_tokens,
                "prompt_token": state['prompt_token'] + crafter_info.prompt_tokens,
                "completion_token": state['completion_token'] + crafter_info.completion_tokens,
                "cost": state['cost'] + crafter_info.total_cost
            }
        except Exception as e:
            print(f"An error occurred in Crafter: {e}")
            return state


    def developer(self, state):
        print('\n' + '----------' * 20)
        print('\n------ Entering Developer ------')
        
        try:
            if state['improved_code']:
                code = state['improved_code']
            else:
                code = state['code']
                
            developer_response, developer_info = self.invoker.developer_invoke(code, lang="Python")
            
            print(f"The refactored code: \n{developer_response.refactored_code}")
            print(developer_info)
            return {
                'refactored_code': developer_response.refactored_code,
                'token_used': state['token_used'] + developer_info.total_tokens,
                'prompt_token': state['prompt_token'] + developer_info.prompt_tokens,
                'completion_token': state['completion_token'] + developer_info.completion_tokens,
                'cost': state['cost'] + developer_info.total_cost
            }
        except Exception as e:
            print(f"An error occurred in Developer: {e}")
            return state